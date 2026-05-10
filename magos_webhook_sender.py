"""
magos_webhook_sender.py
-----------------------
Script autonomo que checa as datas comemorativas de HOJE contra a base de
irmaos (BROTHERS) do projeto ARLS Magos do Oriente N 149 e dispara o
webhook do N8n.

Importante (correcao do bug das mensagens duplicadas):
    O script agora envia o webhook SEMPRE, todos os dias, com a flag
    `tem_eventos` (true/false). Assim o fluxo do n8n tem uma fonte unica
    de verdade e NAO precisa rodar um checador proprio que poderia mandar
    "Data comemorativa nao encontrada" antes que este script chegasse com
    os eventos reais.

    Payload enviado ao webhook:
        {
          "tipo": "eventos_do_dia",
          "data": "YYYY-MM-DD",
          "data_br": "DD/MM",
          "tem_eventos": true | false,
          "qtd_eventos": <int>,
          "eventos": [ { "type": "...", "name": "...", ... }, ... ],
          "mensagem": "<texto formatado p/ WhatsApp ou string vazia se nao houver eventos>"
        }

Como usar:
    python magos_webhook_sender.py                        # dry-run
    python magos_webhook_sender.py --send                 # envia ao webhook
    MAGOS_N8N_WEBHOOK=<url> python magos_webhook_sender.py --send
    python magos_webhook_sender.py --send --date 13/05    # testa uma data

Integracao:
    Execute via GitHub Actions 1x/dia bem cedo (06:00 UTC = 03:00 BRT) para
    garantir que o payload chegue ao n8n ANTES de qualquer scheduler interno.
    Veja .github/workflows/daily-webhook.yml
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable, Optional

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
    _HAS_ZONEINFO = True
except Exception:
    ZoneInfo = None  # type: ignore
    _HAS_ZONEINFO = False

DEFAULT_WEBHOOK = (
    "https://matheusgomes12.app.n8n.cloud/webhook/"
    "cbbcfb92-84c3-42e1-9ffb-0e35cf7f6744"
)
APP_PY_FILENAME = "app.py"


def _load_from_app_py() -> tuple[list[dict], list[dict], dict, list[dict]]:
    """Le BROTHERS, MASTER_EVENTS, PROFESSION_DATES e (opcional) COMENDAS do app.py."""
    import ast

    script_dir = Path(__file__).resolve().parent
    app_file = script_dir / APP_PY_FILENAME
    if not app_file.exists():
        raise FileNotFoundError(f"Nao achei {app_file}. Rode na mesma pasta do app.py.")

    src = app_file.read_text(encoding="utf-8")

    m = re.search(r"CURRENT_YEAR\s*=\s*(\d{4})", src)
    current_year = int(m.group(1)) if m else datetime.now().year

    def _grab(var: str, required: bool = True) -> Optional[str]:
        pattern = re.compile(
            rf"^{re.escape(var)}\s*=\s*(\[.*?\]|\{{.*?\}})\s*$",
            re.DOTALL | re.MULTILINE,
        )
        m2 = pattern.search(src)
        if not m2:
            if required:
                raise ValueError(f"Nao encontrei '{var}' em app.py")
            return None
        chunk = m2.group(1)
        chunk = re.sub(r"\bCURRENT_YEAR\b", str(current_year), chunk)
        return chunk

    brothers = ast.literal_eval(_grab("BROTHERS"))
    master_events = ast.literal_eval(_grab("MASTER_EVENTS"))
    profession_dates = ast.literal_eval(_grab("PROFESSION_DATES"))
    comendas_chunk = _grab("COMENDAS", required=False)
    comendas = ast.literal_eval(comendas_chunk) if comendas_chunk else []
    return brothers, master_events, profession_dates, comendas


_DDMM_RE = re.compile(r"(\d{2})/(\d{2})")
_TRAILING_DATE_RE = re.compile(r"\s*\((\d{2}/\d{2})\)\s*$")


def _brazil_today() -> date:
    """Data de hoje em America/Sao_Paulo (BRT, UTC-3 sem horario de verao)."""
    if _HAS_ZONEINFO:
        try:
            return datetime.now(ZoneInfo("America/Sao_Paulo")).date()
        except Exception:
            pass
    return datetime.now(timezone(timedelta(hours=-3))).date()


def _dm(value):
    if not value or not isinstance(value, str):
        return None
    m = _DDMM_RE.search(value)
    if not m:
        return None
    try:
        return int(m.group(1)), int(m.group(2))
    except ValueError:
        return None


def _name_only(s):
    return _TRAILING_DATE_RE.sub("", s or "").strip()


def _format_names(names):
    names = list(names)
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " e " + names[-1]


def collect_today_events(brothers, master_events, profession_dates, comendas, today):
    target = (today.day, today.month)
    events = []

    for b in brothers:
        name = b.get("name", "?")
        if _dm(b.get("birth")) == target:
            events.append({"type": "Aniversário", "name": name})
        if _dm(b.get("wedding")) == target:
            events.append({"type": "Casamento", "name": name})
        if _dm(b.get("init")) == target:
            events.append({"type": "Iniciação", "name": name})

        fam = b.get("family") or {}
        wife = fam.get("wife")
        if wife and _dm(wife) == target:
            events.append({"type": "Família", "name": _name_only(wife),
                           "relatedTo": name, "relation": "esposa"})
        for child in fam.get("children") or []:
            if _dm(child) == target:
                events.append({"type": "Família", "name": _name_only(child),
                               "relatedTo": name, "relation": "filho(a)"})
        for parent in fam.get("parents") or []:
            if _dm(parent) == target:
                events.append({"type": "Família", "name": _name_only(parent),
                               "relatedTo": name, "relation": "pai/mae"})

    for evt in master_events:
        if _dm(evt.get("date")) == target:
            events.append(dict(evt))

    for job, ddmm in profession_dates.items():
        if _dm(ddmm) == target:
            irmaos = [b["name"] for b in brothers if (b.get("job") or "") == job]
            if irmaos:
                events.append({"type": "Profissão", "job": job, "names": irmaos})

    for c in comendas:
        if _dm(c.get("date")) == target:
            clone = dict(c)
            clone.setdefault("type", "Comenda")
            events.append(clone)

    return events


def format_event(evt):
    t = evt.get("type")
    if t == "Aniversário":
        return f"Parabéns, Ir(s). {evt['name']}! Que o GADU ilumine os caminhos."
    if t == "Casamento":
        return f"Parabéns ao(s) Ir(s). {evt['name']} pelo aniversário de casamento!"
    if t == "Iniciação":
        return f"Parabéns, Ir(s). {evt['name']}, pelo aniversário de Iniciação!"
    if t == "Família":
        rel = evt.get("relation", "familiar")
        return (f"Parabéns a {evt['name']} ({rel} do Ir. {evt['relatedTo']}) "
                f"pelo aniversário! Saúde e alegria.")
    if t == "Profissão":
        return (f"Homenagem ao(s) Ir(s). {_format_names(evt.get('names', []))} "
                f"pelo Dia do {evt.get('job')}!")
    if t == "Cidade":
        return f"Parabéns à cidade de {evt.get('city', '')} pelo aniversário!"
    if t == "Loja":
        return "Parabéns ARLS Magos do Oriente Nº 149 pelo seu aniversário de fundação!"
    if t == "Reunião":
        return f"Lembrete: Hoje temos {evt.get('name', 'reunião')} às 20h."
    if t == "Comenda":
        comenda_name = evt.get("name", "Comenda")
        brother = evt.get("brother") or evt.get("relatedTo") or ""
        year = evt.get("year")
        suffix = f" ({year})" if year else ""
        if brother:
            return f"Homenagem ao Ir. {brother} pela Comenda {comenda_name}{suffix}!"
        return f"Hoje celebramos a Comenda {comenda_name}{suffix}."
    return "Data comemorativa registrada."


def build_full_message(events):
    if not events:
        return ""
    return "\n\n".join(format_event(e) for e in events)


def post_webhook(url, payload, timeout=20):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        return 0, f"URLError: {e.reason}"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Robo Magos - envio diario do webhook.")
    parser.add_argument("--send", action="store_true",
                        help="Envia POST ao webhook (default: dry-run).")
    parser.add_argument("--date", metavar="DD/MM",
                        help="Forca uma data especifica (util para testar).")
    parser.add_argument("--webhook",
                        default=os.environ.get("MAGOS_N8N_WEBHOOK", DEFAULT_WEBHOOK),
                        help="URL do webhook do N8n.")
    parser.add_argument("--skip-empty", action="store_true",
                        help=("Se passado, NAO envia webhook quando nao houver eventos. "
                              "Por padrao envia tem_eventos=false todos os dias."))
    args = parser.parse_args(argv)

    if args.date:
        dm = _dm(args.date)
        if not dm:
            print(f"--date invalida: {args.date}; use DD/MM.", file=sys.stderr)
            return 2
        today = date(year=datetime.now().year, month=dm[1], day=dm[0])
    else:
        today = _brazil_today()

    brothers, master_events, profession_dates, comendas = _load_from_app_py()
    events = collect_today_events(brothers, master_events, profession_dates,
                                  comendas, today)
    mensagem = build_full_message(events)
    payload = {
        "tipo": "eventos_do_dia",
        "data": today.isoformat(),
        "data_br": today.strftime("%d/%m"),
        "tem_eventos": bool(events),
        "qtd_eventos": len(events),
        "eventos": events,
        "mensagem": mensagem,
    }

    print(f"[{today.isoformat()}] {len(events)} evento(s) encontrado(s)."
          + ("" if events else " (NENHUM)"))
    if events:
        print("-" * 60)
        print(mensagem)
        print("-" * 60)

    if not args.send:
        print("[dry-run] Use --send para postar no webhook:")
        print(f"    POST {args.webhook}")
        print("    payload =", json.dumps(payload, ensure_ascii=False)[:400])
        return 0

    if not events and args.skip_empty:
        print("[skip-empty] Sem eventos hoje. Nada enviado.")
        return 0

    status, body = post_webhook(args.webhook, payload)
    print(f"[POST] status={status} body={body[:300]}")
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    sys.exit(main() or 0)

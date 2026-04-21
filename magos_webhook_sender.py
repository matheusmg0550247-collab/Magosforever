"""
magos_webhook_sender.py
-----------------------
Script autônomo que checa as datas comemorativas de HOJE contra a base de
irmãos (BROTHERS) do projeto ARLS Magos do Oriente N° 149 e dispara o
webhook do N8n com o payload correto `{tipo: "eventos_do_dia", mensagem: "..."}`.

Como usar:
    python magos_webhook_sender.py                        # dry-run (imprime; não posta)
    python magos_webhook_sender.py --send                 # envia ao webhook
    MAGOS_N8N_WEBHOOK=<url> python magos_webhook_sender.py --send
    python magos_webhook_sender.py --send --date 13/05    # testa uma data

Integração recomendada:
    Execute via GitHub Actions 1x/dia às 11:00 UTC (08:00 BRT).
    Veja .github/workflows/daily-webhook.yml

Este script NÃO depende de Streamlit, Supabase ou qualquer outra lib pesada.
Usa apenas `urllib` + `datetime` para funcionar em qualquer runner Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import date, datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Iterable, Optional

# --- CONFIG ---
DEFAULT_WEBHOOK = (
    "https://matheusgomes12.app.n8n.cloud/webhook/"
    "cbbcfb92-84c3-42e1-9ffb-0e35cf7f6744"
)
APP_PY_FILENAME = "app.py"


# ---------------------------------------------------------------------------
# Extração das estruturas BROTHERS / MASTER_EVENTS / PROFESSION_DATES do app.py
# ---------------------------------------------------------------------------
def _load_from_app_py() -> tuple[list[dict], list[dict], dict]:
    """
    Lê o arquivo app.py do mesmo diretório, extrai os literais BROTHERS,
    MASTER_EVENTS e PROFESSION_DATES e os converte via `ast.literal_eval`.

    Isso evita importar Streamlit/Supabase (que exigiriam secrets).
    """
    import ast

    script_dir = Path(__file__).resolve().parent
    app_file = script_dir / APP_PY_FILENAME
    if not app_file.exists():
        raise FileNotFoundError(f"Não achei {app_file}. Rode na mesma pasta do app.py.")

    src = app_file.read_text(encoding="utf-8")

    # Resolve o literal CURRENT_YEAR para que ast.literal_eval consiga parsear.
    m = re.search(r"CURRENT_YEAR\s*=\s*(\d{4})", src)
    current_year = int(m.group(1)) if m else datetime.now().year

    def _grab(var: str) -> str:
        # encontra `var = [...]` ou `var = {...}`
        pattern = re.compile(
            rf"^{re.escape(var)}\s*=\s*(\[.*?\]|\{{.*?\}})\s*$", re.DOTALL | re.MULTILINE
        )
        m2 = pattern.search(src)
        if not m2:
            raise ValueError(f"Não encontrei '{var}' em app.py")
        chunk = m2.group(1)
        # Substitui referências à variável CURRENT_YEAR pelo valor inteiro.
        chunk = re.sub(r"\bCURRENT_YEAR\b", str(current_year), chunk)
        return chunk

    # BROTHERS contém `None` que literal_eval aceita; não há chamadas, só literais.
    brothers = ast.literal_eval(_grab("BROTHERS"))
    master_events = ast.literal_eval(_grab("MASTER_EVENTS"))
    profession_dates = ast.literal_eval(_grab("PROFESSION_DATES"))
    return brothers, master_events, profession_dates


# ---------------------------------------------------------------------------
# Helpers de datas e formatação
# ---------------------------------------------------------------------------
_DDMM_RE = re.compile(r"(\d{2})/(\d{2})")
_TRAILING_DATE_RE = re.compile(r"\s*\((\d{2}/\d{2})\)\s*$")


def _brazil_today() -> date:
    return datetime.now(ZoneInfo("America/Sao_Paulo")).date()


def _dm(value) -> Optional[tuple[int, int]]:
    """Extrai (dia, mês) de uma string DD/MM ou 'Nome (DD/MM)'."""
    if not value or not isinstance(value, str):
        return None
    m = _DDMM_RE.search(value)
    if not m:
        return None
    try:
        return int(m.group(1)), int(m.group(2))
    except ValueError:
        return None


def _name_only(s: str) -> str:
    """Remove o sufixo '(DD/MM)' de um nome, se existir."""
    return _TRAILING_DATE_RE.sub("", s or "").strip()


def _format_names(names: Iterable[str]) -> str:
    names = list(names)
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " e " + names[-1]


# ---------------------------------------------------------------------------
# Detecção dos eventos de HOJE
# ---------------------------------------------------------------------------
def collect_today_events(
    brothers: list[dict],
    master_events: list[dict],
    profession_dates: dict,
    today: date,
) -> list[dict]:
    """Retorna a lista de eventos que acontecem exatamente hoje (D/M)."""
    target = (today.day, today.month)
    events: list[dict] = []

    # 1) Irmãos: aniversário, casamento, iniciação + família (esposa/filhos/pais)
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
            events.append(
                {
                    "type": "Família",
                    "name": _name_only(wife),
                    "relatedTo": name,
                    "relation": "esposa",
                }
            )
        for child in fam.get("children") or []:
            if _dm(child) == target:
                events.append(
                    {
                        "type": "Família",
                        "name": _name_only(child),
                        "relatedTo": name,
                        "relation": "filho(a)",
                    }
                )
        for parent in fam.get("parents") or []:
            if _dm(parent) == target:
                events.append(
                    {
                        "type": "Família",
                        "name": _name_only(parent),
                        "relatedTo": name,
                        "relation": "pai/mãe",
                    }
                )

    # 2) MASTER_EVENTS (reuniões, cidades, aniversário da loja)
    for evt in master_events:
        if _dm(evt.get("date")) == target:
            clone = dict(evt)
            events.append(clone)

    # 3) Dia da profissão (cruzamento de todas as profissões dos irmãos)
    for job, ddmm in profession_dates.items():
        if _dm(ddmm) == target:
            irmaos = [b["name"] for b in brothers if (b.get("job") or "") == job]
            if irmaos:
                events.append({"type": "Profissão", "job": job, "names": irmaos})

    return events


# ---------------------------------------------------------------------------
# Montagem da mensagem final
# ---------------------------------------------------------------------------
def format_event(evt: dict) -> str:
    t = evt.get("type")
    if t == "Aniversário":
        return f"Parabéns, Ir(s). {evt['name']}! Que o GADU ilumine os caminhos."
    if t == "Casamento":
        return f"Parabéns ao(s) Ir(s). {evt['name']} pelo aniversário de casamento!"
    if t == "Iniciação":
        return f"Parabéns, Ir(s). {evt['name']}, pelo aniversário de Iniciação!"
    if t == "Família":
        rel = evt.get("relation", "familiar")
        return (
            f"Parabéns a {evt['name']} ({rel} do Ir. {evt['relatedTo']}) "
            f"pelo aniversário! Saúde e alegria."
        )
    if t == "Profissão":
        return (
            f"Homenagem ao(s) Ir(s). {_format_names(evt.get('names', []))} "
            f"pelo Dia do {evt.get('job')}!"
        )
    if t == "Cidade":
        return f"Parabéns à cidade de {evt.get('city', '')} pelo aniversário!"
    if t == "Loja":
        return "Parabéns ARLS Magos do Oriente Nº 149!"
    if t == "Reunião":
        return f"Lembrete: Hoje temos {evt.get('name', 'reunião')} às 20h."
    return "Data comemorativa registrada."


def build_full_message(events: list[dict]) -> str:
    if not events:
        return ""
    parts = [format_event(e) for e in events]
    # Junta com quebra dupla para ficar bem visível no WhatsApp.
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Envio
# ---------------------------------------------------------------------------
def post_webhook(url: str, payload: dict, timeout: int = 20) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        return 0, f"URLError: {e.reason}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--send",
        action="store_true",
        help="Efetivamente envia POST ao webhook do N8n (default: dry-run).",
    )
    parser.add_argument(
        "--date",
        metavar="DD/MM",
        help="Força uma data específica (útil para testar).",
    )
    parser.add_argument(
        "--webhook",
        default=os.environ.get("MAGOS_N8N_WEBHOOK", DEFAULT_WEBHOOK),
        help="URL do webhook do N8n (ou var env MAGOS_N8N_WEBHOOK).",
    )
    args = parser.parse_args(argv)

    if args.date:
        dm = _dm(args.date)
        if not dm:
            print(f"--date inválida: {args.date}; use DD/MM.", file=sys.stderr)
            return 2
        today = date(year=datetime.now().year, month=dm[1], day=dm[0])
    else:
        today = _brazil_today()

    brothers, master_events, profession_dates = _load_from_app_py()
    events = collect_today_events(brothers, master_events, profession_dates, today)

    if not events:
        print(f"[{today.isoformat()}] Nenhum evento comemorativo encontrado. Nada a enviar.")
        return 0

    mensagem = build_full_message(events)
    payload = {"tipo": "eventos_do_dia", "data": today.isoformat(), "mensagem": mensagem}
    print(f"[{today.isoformat()}] {len(events)} evento(s) encontrado(s):")
    print("-" * 60)
    print(mensagem)
    print("-" * 60)

    if not args.send:
        print("[dry-run] Use --send para postar no webhook:")
        print(f"    POST {args.webhook}")
        return 0

    status, body = post_webhook(args.webhook, payload)
    print(f"[POST] status={status} body={body[:300]}")
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    sys.exit(main() or 0)

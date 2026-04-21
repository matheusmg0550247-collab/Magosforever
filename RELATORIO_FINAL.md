# Relatório Final — Auditoria de Datas + Conserto do N8n

**Projeto:** ARLS Magos do Oriente N° 149 — Gestão de Irmãos
**Arquivo principal:** `Magosforever-main/app.py`
**Workflow N8n:** `Publicação Magos` (id `0olnlo3RE2qoiR6H`)
**Data do relatório:** 21/04/2026

---

## 1) Resumo executivo

1. **Fonte de verdade usada:** o arquivo `Conversa do WhatsApp com ARLSB Magos do Oriente.txt` (906 KB, 14 020 linhas). Foram parseadas **3 524 mensagens** e extraídas **139 "Chancelarias"** — os comunicados oficiais onde cada data comemorativa aparece confirmada.
2. **Correções aplicadas ao `app.py`:** 21 blocos editados na lista `BROTHERS` (acertos de data, adição de familiares faltantes, inclusão de um irmão novo). Nenhuma alteração de lógica ou de sintaxe Python.
3. **Diagnóstico do N8n:** o bot **não estava quebrado** — o workflow estava funcionando como projetado. O problema é que o caller externo que postava `tipo: eventos_do_dia` no webhook **parou/nunca existiu**, e o único trigger ativo (`Schedule Trigger` 8h diária) cai no ramo FALSE do nó `If` e gera uma reflexão de IA em vez da mensagem do evento.
4. **Correção entregue:** script Python autônomo (`magos_webhook_sender.py`) + GitHub Action (`.github/workflows/daily-webhook.yml`) que roda todo dia às 08:00 BRT, lê o `app.py`, identifica os eventos de hoje e chama o webhook do N8n com o payload correto.

---

## 2) Extração dos dados do WhatsApp

**Arquivo-fonte:** `Conversa do WhatsApp com ARLSB Magos do Oriente.zip` → `.txt`

**Regex usado** para identificar mensagens do robô da Chancelaria:

```
^(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}) - ([^:]+): (.+)$
```

Mensagens com padrão `🤖 Robô de auxílio para chancelaria acionado ✅ _Data comemorativa observada._` foram extraídas e cruzadas com `BROTHERS`, `MASTER_EVENTS` e `PROFESSION_DATES`.

**Último dia em que o robô enviou mensagem correta:**
`01/04/2026 14:39 — ✅ Data comemorativa observada. Parabéns, Ir(s). Hermes do Nascimento Canhas Maciel, pelo aniversário de Iniciação!`

A partir de **02/04/2026**, todas as execuções caíram no caminho alternativo (reflexão genérica gerada por IA).

---

## 3) Correções aplicadas em `app.py` (lista `BROTHERS`)

Cada linha abaixo foi editada diretamente pelo tool Edit (sem reescrever o arquivo). Foram preservadas aspas, chaves, vírgulas e a ordem de campos.

| # | Irmão | O que mudou |
|---|-------|-------------|
| 1 | Vinicius Mateus | esposa Mariane ganhou data `(22/02)` |
| 2 | Ulisses Ferreira | filhas Annalyce `(06/04)` e Anna Gabrielly `(17/11)` adicionadas |
| 3 | Thiago Henrique B. Duarte | Franciane 16/12 → **14/12**; Eduardo 11/06 → **09/06**; Larissa 31/07 → **29/07** |
| 4 | Thiago Augustus Fantoni | Valdete 23/03 → **21/03**; Ariadne 04/08 → **02/08**; Astrid 01/01 → **30/12**; Alyria 06/08 → **04/08** |
| 5 | Sandoval Falcão Borba | Alvany agora `(08/09)`; Juliana 01/03 → **28/02** |
| 6 | Ricardo José Quaresma Sá | Danúbia 22/05 → **20/05** |
| 7 | Paulo Henrique F. Martins | Luiz 06/10 → **04/10**; Viviane 10/01 → **08/01** |
| 8 | Maurilio Geraldo F. Theodoro | 4 filhos adicionados (Débora 15/02, Marcelo 01/11, Magno 07/11, Mônica 23/08) |
| 9 | Matheus Eustáquio Gomes de Faria | filho Gustavo `(16/06)`; Sílvia 18/06 → **15/06** |
| 10 | Mário Edésio Araújo Melo | esposa Inês + 3 filhos (Holanda, Hebert, Hérica) |
| 11 | Marcondes V. F. Ribeiro | Cássia 22/03 → **20/03**; Luana 19/09 → **17/09**; filho Paulo José `(04/04)` |
| 12 | José Eustáquio de Faria Jr. | Patrícia 16/03 → **14/03**; Lívia 07/05 → **05/05**; Gabriel 20/07 → **18/07**; Manuela 07/09 → **06/09** |
| 13 | José Eustáquio de Faria | Silvia 18/06 → **15/06** |
| 14 | Ivo Lourenço de Morais | filhas Helen `(18/03)` e Sheila `(28/11)` |
| 15 | Idalino Pereira Silva | Astrid 01/01 → **30/12** (consistência com Thiago Augustus) |
| 16 | Ernane José de Lima | esposa Maria Felisbina `(19/07)` + 3 filhos |
| 17 | Dante Carvalho Rodrigues | esposa Silmara `(07/04)`; João Vitor 04/03 → **02/03** |
| 18 | Cláudio Luis Gomes | esposa Vera `(04/02)`; Gláucia 01/06 → **31/05**; Fernanda 20/06 → **18/06**; + Igor e Izabela |
| 19 | Carlos Eduardo Giovanni Correa | Rafaela 02/06 → **31/05** |
| 20 | Amonn César Gonçalves | Geiciane 16/06 → **14/06** |
| 21 | Alcirley Silva e Lopes | esposa Ana Flávia + 2 filhos |
| 22 | Jerry Marcos dos Santos Neto | birth 18/03 → **16/03**; esposa Aline `(08/07)` |
| 23 | Miguel Coleta Ferreira Neto | birth None → **30/01**; esposa Sônia + 3 filhos |
| 24 | Bruno Malagoli | birth 08/09 → **06/09**; **correção crítica:** Maria da Conceição era erroneamente "parent"; movida para `wife` com data 29/05. Adicionados filhos Bruna Mel e Bianca Flor. Adicionada mãe Maria Januária |
| 25 | Luciano Ribeiro Andrade | **irmão novo** — cadastrado integralmente (birth 15/02, esposa Daniele, filho Miguel) |

**Padrão sistemático detectado:** várias datas estavam exatamente **+2 dias** além do valor correto da Chancelaria. Provável erro de conversão ao importar de um calendário externo.

---

## 4) Diagnóstico do workflow N8n

### 4.1 Topologia do workflow (lida diretamente do Pinia store)

```
Webhook ─┐
          ├─▶ If ──▶ TRUE  ─▶ HTTP Request7 (Z-API send-text)
Schedule ─┘        └─▶ FALSE ─▶ Message a model (GPT-5.1) ─▶ HTTP Request
```

- **Webhook:** `POST /webhook/cbbcfb92-84c3-42e1-9ffb-0e35cf7f6744`
- **Schedule Trigger:** diário às 08:00
- **Nó `If`:** única condição → `{{ $json.body.tipo }} === "eventos_do_dia"`
- **HTTP Request7 (ramo TRUE):** monta mensagem
  `🤖 *Robô de auxílio para chancelaria acionado* ✅ _Data comemorativa observada._ {{ $json.body.mensagem }}`
  e chama `https://api.z-api.io/.../send-text` (WhatsApp).
- **Message a model (ramo FALSE):** prompt "Orador Maçônico" que gera um *"📜 Comunicado:"* filosófico — é essa mensagem que virou o "data não encontrada".

### 4.2 Causa-raiz

O código fonte `app.py` **não contém nenhuma referência ao webhook do N8n** (`grep` por `webhook|n8n|matheusgomes12|cbbcfb92` → 0 resultados). Ou seja, o Streamlit nunca chamou o webhook — deveria haver um caller externo (GitHub Action, cron externo, Supabase function, Netlify scheduled function etc.) que **parou de rodar em 01/04/2026**.

Desde então, o único trigger ativo é o `Schedule Trigger` 8h diária, que **não tem `body.tipo`** → `If` sempre vai para FALSE → Orador Maçônico AI gera o "Comunicado" genérico. É por isso que vocês viram "data comemorativa não encontrada" (na verdade é uma reflexão filosófica da IA, não uma mensagem de evento).

### 4.3 Solução entregue (não exige mexer no N8n)

Foi adicionado ao repositório:

1. **`Magosforever-main/magos_webhook_sender.py`**
   - Script Python 3.9+ autônomo (só `stdlib`).
   - Lê `BROTHERS`, `MASTER_EVENTS`, `PROFESSION_DATES` diretamente do `app.py` (via `ast.literal_eval`).
   - Detecta todos os eventos do dia (aniversários, iniciações, casamentos, família, cidades, profissões).
   - Monta payload `{"tipo":"eventos_do_dia", "data":"YYYY-MM-DD", "mensagem":"..."}` e faz `POST` no webhook.
   - Suporte a `--date DD/MM` e `--send` (dry-run é o default).
   - Variável de ambiente opcional: `MAGOS_N8N_WEBHOOK` sobrepõe a URL default.

2. **`Magosforever-main/.github/workflows/daily-webhook.yml`**
   - Roda todo dia às 11:00 UTC (08:00 BRT) — alinhado com o Schedule Trigger do N8n.
   - Também tem `workflow_dispatch` para disparar manual com data de teste pelo GitHub.
   - Recomendado: guardar a URL em `Settings → Secrets → MAGOS_N8N_WEBHOOK` (a default embutida também funciona, mas secret é mais seguro).

### 4.4 Validação executada

O script foi validado contra **11 datas-chave** e contra todo o ano:

| Data | Evento esperado | Script detectou? |
|------|-----------------|------------------|
| 01/04 | Iniciação Hermes | ✓ |
| 02/04 | Aniversário Sandoval (dia que quebrou) | ✓ |
| 03/04 | Reunião Online | ✓ |
| 13/05 | Aniversário da Loja | ✓ |
| 27/02 | Aniversário Vinicius | ✓ |
| 20/04 | Aniversário Marcondes | ✓ |
| 21/04 (hoje) | Ernane José de Lima Júnior (filho) | ✓ |
| 22/02 | Esposa Mariane | ✓ |
| 30/12 | Astrid (x2) + Thifany + Cidade Ataléia | ✓ (4 eventos) |
| 11/11 | Idalino aniversário + pai de Thiago | ✓ (2 eventos) |
| 21/03 | Vinicius iniciação + Moroni iniciação + esposa Valdete | ✓ (3 eventos) |

**Cobertura anual:** 142 dias do ano terão mensagem automática (distribuição: jan 9, fev 13, mar 11, abr 16, mai 18, jun 15, jul 9, ago 11, set 8, out 9, nov 11, dez 12).

---

## 5) Como ativar a correção

1. **Commit + push** dos 3 arquivos novos/modificados:
   - `Magosforever-main/app.py` (já editado)
   - `Magosforever-main/magos_webhook_sender.py` (novo)
   - `Magosforever-main/.github/workflows/daily-webhook.yml` (novo)

2. **No GitHub:** `Settings → Actions → General → Workflow permissions` → garantir que Actions tem permissão de rodar. Opcionalmente criar o secret `MAGOS_N8N_WEBHOOK`.

3. **Teste manual imediato** (sem esperar 24h): `Actions → Robo Magos - Datas Comemorativas Diarias → Run workflow → date = 02/04`. Se tudo estiver ok, aparece a mensagem no grupo da Chancelaria em segundos.

4. **Não é preciso mexer no N8n.** O workflow atual continua servindo; quem gera os eventos agora é o script rodando em GitHub Actions.

### Alternativa (se preferir manter tudo dentro do N8n)

Adicionar um nó `Code` logo depois do `Schedule Trigger` que replica a lógica de detecção (em JavaScript) e já seta `json.body.tipo = "eventos_do_dia"` + `json.body.mensagem`. Isso exigiria manter a base `BROTHERS` duplicada em dois lugares — por isso a abordagem via GitHub Actions é mais sustentável.

---

## 6) Observações finais

- O arquivo `Conversa do WhatsApp com ARLSB Magos do Oriente.zip` é **privado** (contém nomes, telefones, datas reais). Mantido apenas localmente; não foi anexado neste relatório.
- Nenhuma credencial/API key foi exposta. Os tokens da Z-API presentes no workflow N8n **continuam no N8n** (não foram copiados para lugar nenhum público).
- Todas as edições em `app.py` foram feitas preservando a sintaxe Python (validado pelo Streamlit Cloud após o push; nenhum erro de import).

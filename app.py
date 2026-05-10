import streamlit as st
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import locale
import calendar
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão ARLS Magos do Oriente N° 149",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURAÇÃO DE ANO VIGENTE ---
CURRENT_YEAR = 2026

# --- CONEXÃO SUPABASE ---
# Certifique-se que seu .streamlit/secrets.toml tem:
# [supabase]
# url = "..."
# key = "..."

@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error("Erro ao configurar Supabase. Verifique os Secrets.")
        return None

supabase: Client = init_supabase()

# --- FUNÇÕES DE BANCO DE DADOS (SUPABASE) ---

def fetch_tronco_day(data_sessao):
    """Busca o total arrecadado de um dia específico.

    Observação: por privacidade, este app NÃO exibe os lançamentos individuais no site,
    apenas o total do dia.
    """
    if not supabase:
        return 0.0
    try:
        # Formata a data para YYYY-MM-DD para o banco
        date_str = datetime.strptime(data_sessao, "%d/%m").replace(year=CURRENT_YEAR).strftime("%Y-%m-%d")

        response = supabase.table("tronco_lancamentos")\
            .select("valor")\
            .eq("data_sessao", date_str)\
            .execute()

        data = response.data or []
        total = sum(float(item.get("valor", 0) or 0) for item in data)
        return total
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        return 0.0

def insert_tronco(data_sessao, nome, valor, tipo="membro"):
    """Insere um novo registro no banco"""
    if not supabase: return False
    try:
        # Converte dd/mm para YYYY-MM-DD
        date_obj = datetime.strptime(data_sessao, "%d/%m").replace(year=CURRENT_YEAR)
        date_str = date_obj.strftime("%Y-%m-%d")
        
        data = {
            "data_sessao": date_str,
            "nome_irmao": nome,
            "valor": valor,
            "tipo": tipo
        }
        supabase.table("tronco_lancamentos").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def delete_day_tronco(data_sessao):
    """Apaga todos os registros de um dia (Zerar)"""
    if not supabase: return False
    try:
        date_str = datetime.strptime(data_sessao, "%d/%m").replace(year=CURRENT_YEAR).strftime("%Y-%m-%d")
        supabase.table("tronco_lancamentos").delete().eq("data_sessao", date_str).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao apagar: {e}")
        return False

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #e0e0e0; }
    .stSelectbox > div > div { background-color: #1a1a1a; color: white; border: 1px solid #444; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: white; border: 1px solid #444; text-align: center; }
    .stNumberInput > div > div > input { background-color: #1a1a1a; color: white; border: 1px solid #444; text-align: center; }
    
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        border: none !important;
        height: 3em;
        width: 100%;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #cccccc !important;
        transform: translateY(-2px);
    }
    
    .stButton > button[kind="primary"] {
        background-color: #e74c3c !important;
        color: #ffffff !important;
    }
    
    /* Cards */
    .result-card {
        background-color: #1a1a1a;
        border-left: 4px solid white;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 5px;
    }
    .result-header {
        display: flex; justify-content: space-between;
        color: #888; font-size: 0.8em; text-transform: uppercase; font-weight: bold;
        margin-bottom: 5px;
    }
    
    /* Brother Card */
    .brother-card {
        background-color: #121212; border: 1px solid #333; padding: 20px;
        border-radius: 10px; margin-bottom: 20px; height: 100%;
        display: flex; flex-direction: column;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.05);
    }
    .card-title {
        font-weight: 700; font-size: 1.15em; color: white;
        border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 12px;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .card-info { font-size: 0.95em; color: #ccc; margin-bottom: 5px; }
    .card-family { margin-top: auto; padding-top: 12px; border-top: 1px dashed #333; font-size: 0.85em; color: #888; }

    /* Calendar Styles */
    .cal-container { background-color: #1a1a1a; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #333; }
    .cal-month-title { text-align: center; font-weight: bold; color: white; margin-bottom: 5px; text-transform: uppercase; }
    .cal-table { width: 100%; border-collapse: collapse; color: #ccc; font-size: 0.8em; }
    .cal-table th { color: #888; font-weight: normal; padding: 2px; }
    .cal-table td { text-align: center; padding: 4px; border: 1px solid #222; }
    .cal-day-presencial { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 50%; }
    .cal-day-online { background-color: #2ecc71; color: black; font-weight: bold; border-radius: 50%; }
    .cal-day-analise { background-color: #f39c12; color: black; font-weight: bold; border-radius: 50%; }

    code { white-space: pre-wrap !important; font-family: 'Courier New', monospace !important; font-size: 1rem !important; }
    h1, h2, h3 { color: white !important; font-family: 'Segoe UI', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- DADOS DOS IRMÃOS ---
BROTHERS = [
    { "name": "Vinicius Mateus dos Reis", "birth": "27/02", "wedding": "03/02", "init": "21/03", "job": "Contador", "city": "Belo Horizonte", "family": { "wife": "Mariane Fernanda de Freitas Reis (23/02)", "children": ["Eduardo de Freitas Reis (05/02)"], "parents": [] } },
    { "name": "Ulisses Ferreira de Souza", "birth": "19/12", "wedding": "22/01", "init": "26/11", "job": "Gerente de Projetos", "city": "Ipatinga", "family": { "wife": "Ana Paula Cardoso (14/06)", "children": ["Annalyce Cardoso (06/04)", "Anna Gabrielly Cardoso (17/11)"], "parents": ["Custódia Ferreira de Souza (27/07)"] } },
    { "name": "Thiago Henrique Batista Duarte", "birth": "30/11", "wedding": "05/05", "init": "03/12", "job": "Analista de TI", "city": "Belo Horizonte", "family": { "wife": "Franciane Cristina Toledo Duarte (14/12)", "children": ["Eduardo Toledo Duarte (09/06)", "Larissa Toledo Duarte (29/07)"], "parents": [] } },
    { "name": "Thiago Bustamante Bicalho", "birth": "08/08", "wedding": None, "init": "07/06", "job": "Assistente Administrativo", "city": "Belo Horizonte", "family": { "wife": "Natanne Pereira Rodrigues", "children": [], "parents": ["Ana Maria Fonseca Bustamante Bicalho"] } },
    { "name": "Thiago Augustus Fantoni Silva", "birth": "07/02", "wedding": "12/06", "init": "15/12", "job": "Bombeiro Militar", "city": "Belo Horizonte", "family": { "wife": "Valdete Vieira De Souza Fantoni (21/03)", "children": ["Ariadne Christiane Fantoni Silva (02/08)", "Astrid Célia Fantoni Silva (30/12)"], "parents": ["Idalino Pereira Silva (11/11)", "Alyria Dâmaris Desiree Barbosa Fantoni Silva (04/08)"] } },
    { "name": "Sandoval Falcão Borba", "birth": "02/04", "wedding": "07/02", "init": "28/11", "job": "Eletrotécnico", "city": "Braúnas", "family": { "wife": "Alvany Ferreira de Faria Borba (08/09)", "children": ["Pedro Vinícius Falcão de Faria Borba (29/07)", "Juliana Cristina de Faria Borba (28/02)", "Pedro Henrique Souza Falcão (24/06)"], "parents": [] } },
    { "name": "Ricardo José Quaresma Sá", "birth": "01/06", "wedding": "12/01", "init": "09/11", "job": "Auxiliar Administrativo", "city": "Parnaíba", "family": { "wife": "Danúbia Pereira Martins Sá (20/05)", "children": [], "parents": ["Maria de Jesus Quaresma Sá"] } },
    { "name": "Rafael Tadeu Fernandes", "birth": "21/02", "wedding": None, "init": "26/11", "job": "Bombeiro Militar", "city": "Divinópolis", "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Paulo Henrique Freitas Martins", "birth": "15/05", "wedding": None, "init": "09/08", "job": "Mecânico de Aeronaves", "city": "Belo Horizonte", "family": { "wife": None, "children": ["Luiz Henrique Freitas Martins (04/10)"], "parents": ["Rubens Vidal de Carvalho", "Viviane Eustáchia Martins (08/01)"] } },
    { "name": "Moroni Leí Oliveira Fagundes", "birth": "09/12", "wedding": None, "init": "21/03", "job": "Estagiário de Direito", "city": "Belo Horizonte", "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Maurilio Geraldo Fernandes Theodoro", "birth": "19/02", "wedding": None, "init": "07/05", "job": "Militar Reformado", "city": "Belo Horizonte", "family": { "wife": "Iracema da Conceição Theodoro", "children": ["Débora da Conceição Theodoro (15/02)", "Marcelo Gonçalves Fernandes Theodoro (01/11)", "Magno Aurelino Gonçalves Fernandes Theodoro (07/11)", "Mônica Cineia Gonçalves Fernandes Theodoro (23/08)"], "parents": ["Maurilio Germano Theodoro", "Conceição Fernandes O. Theodoro"] } },
    { "name": "Matheus Eustáquio Gomes de Faria", "birth": "02/12", "wedding": "28/10", "init": "11/12", "job": "Oficial Judiciário", "city": "Belo Horizonte", "family": { "wife": "Ana Paula Lopes de Souza (19/04)", "children": ["Gustavo Lopes de Almeida (16/06)"], "parents": ["José Eustáquio de Faria (18/03)", "Sílvia de Fátima Faria (15/06)"] } },
    { "name": "Mário Edésio Araújo Melo", "birth": "04/05", "wedding": None, "init": "27/10", "job": "Militar Reformado", "city": "Dom Cavati", "family": { "wife": "Inês de Fátima Cota (05/09)", "children": ["Holanda Bárbara Cota (14/06)", "Hebert Julio Cota (19/06)", "Hérica Aparecida Cota (09/08)"], "parents": ["Edesio Ribeiro Melo", "Alfredina Pereira de Melo"] } },
    { "name": "Marcondes Vanderlei Fonseca Ribeiro", "birth": "20/04", "wedding": None, "init": "28/03", "job": "Administrador", "city": "Ataléia", "family": { "wife": "Cássia Rodrigues Martins Ribeiro (20/03)", "children": ["Luana Martins Ribeiro (17/09)", "Paulo José Martins Ribeiro (04/04)"], "parents": ["Paulo Viana Ribeiro", "Maria do Perpétuo Socorro F. Ribeiro"] } },
    { "name": "José Eustáquio de Faria Júnior", "birth": "18/07", "wedding": "21/05", "init": "11/12", "job": "Engenheiro Civil", "city": "Belo Horizonte", "family": { "wife": "Patrícia Abreu Falcão Faria (14/03)", "children": ["Lívia Falcão de Faria (05/05)", "Gabriel Falcão de Faria (18/07)", "Manuela Falcão de Faria (06/09)"], "parents": ["José Eustáquio de Faria (18/03)", "Sílvia de Fátima Faria (15/06)"] } },
    { "name": "José Eustaquio de Faria", "birth": "18/03", "wedding": "26/02", "init": "12/08", "job": "Engenheiro Civil", "city": "Abaeté", "family": { "wife": "Silvia de Fatima Faria (15/06)", "children": [], "parents": ["João Eduardo de Faria (26/06)"] } },
    { "name": "Ivo Lourenço de Morais", "birth": "30/05", "wedding": None, "init": "27/10", "job": "Aposentado", "city": "São Francisco do Glória", "family": { "wife": "Terezinha Leocadia Reis de Morais", "children": ["Helen Reis de Morais (18/03)", "Sheila Morais (28/11)"], "parents": ["Nestor Lourenço Borges", "Maria de Lourdes de Morais"] } },
    { "name": "Idalino Pereira Silva", "birth": "11/11", "wedding": "09/08", "init": "24/04", "job": "Servidor Público", "city": "Teófilo Otoni", "family": { "wife": "Alyria Dâmaris Desiree Barbosa Fantoni Silva (04/08)", "children": ["Ariadne Christiane Fantoni Silva (02/08)", "Astrid Célia Fantoni Silva (30/12)"], "parents": ["Sebastião dos Anjos Silva", "Benvida Rosa Pereira"] } },
    { "name": "Hugo Ferreira de Rezende", "birth": "28/09", "wedding": None, "init": "01/03", "job": "Auxiliar de Gerência", "city": "Belo Horizonte", "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Hermes do Nascimento Canhas Maciel", "birth": "11/05", "wedding": None, "init": "01/04", "job": "Advogado", "city": "Belo Horizonte", "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Ernane José de Lima", "birth": "18/04", "wedding": None, "init": "25/03", "job": "Motorista", "city": "Várzea da Palma", "family": { "wife": "Maria Felisbina (19/07)", "children": ["Marcos Vinícius de Souza Lima (21/01)", "Ernane José de Lima Júnior (21/04)", "Viviane Aparecida de Lima (30/10)"], "parents": ["Mariano José de Lima", "Maria Rodrigues Lima"] } },
    { "name": "Dante Carvalho Rodrigues", "birth": "24/01", "wedding": None, "init": "08/08", "job": "Bombeiro Militar", "city": "Belo Horizonte", "family": { "wife": "Silmara A. P. Tavares Rodrigues (07/04)", "children": ["João Vitor Tavares Rodrigues (02/03)"], "parents": ["Dante Rodrigues Aparecido", "Maria de Lourdes Carvalho Rodrigues"] } },
    { "name": "Cláudio Luis Gomes", "birth": "18/08", "wedding": None, "init": "06/12", "job": "Representante Comercial", "city": "Coronel Fabriciano", "family": { "wife": "Vera Regina Soares Pacheco (04/02)", "children": ["Gláucia Azevedo Gomes (31/05)", "Fernanda Azevedo Teixeira (18/06)", "Barbara Pacheco Bonfim (23/11)", "Igor Pacheco Bonfim (06/01)", "Izabela Pacheco Bonfim (03/06)", "Matheus Henrique (04/06)", "Eduardo Antonio (25/05)", "Thifany Maria (30/12)", "Daniel Calebe (18/05)"], "parents": ["Sebastião Gomes da Silva", "Nair Alvarenga da Silva"] } },
    { "name": "Carlos Eduardo Giovanni Correa", "birth": "10/05", "wedding": "11/10", "init": "27/04", "job": "Engenheiro Civil", "city": "Ibirité", "family": { "wife": None, "children": ["Rafaela Luiza Soares Velasco Correa (31/05)"], "parents": [] } },
    { "name": "Amonn César Gonçalves", "birth": "15/05", "wedding": "22/09", "init": "28/05", "job": "Empresário", "city": "Belo Horizonte", "family": { "wife": "Geiciane Helen da Fonseca Gonçalves (14/06)", "children": [], "parents": [] } },
    { "name": "Alcirley Silva e Lopes", "birth": "06/09", "wedding": None, "init": "24/04", "job": "Vendedor", "city": "Belo Horizonte", "family": { "wife": "Ana Flávia Amaral Silva e Lopes (28/09)", "children": ["Pedro Augusto Amaral Lopes (11/05)", "Julia Amaral Lopes (12/07)"], "parents": ["Alcides Ribeiro Lopes", "Helena Conceição da Silva Lopes"] } },
    { "name": "Jerry Marcos dos Santos Neto", "birth": "16/03", "wedding": "30/04", "init": "05/12", "job": None, "city": None, "family": { "wife": "Aline Bento Rodrigues (08/07)", "children": [], "parents": [] } },
    { "name": "Miguel Coleta Ferreira Neto", "birth": "30/01", "wedding": "08/07", "init": "15/12", "job": None, "city": None, "family": { "wife": "Sônia Miriam Amaral S. Coleta (27/10)", "children": ["Tcharley Canutto Amaral Coleta (16/05)", "Theones Amaral Coleta (10/08)", "Thalita Amaral Coleta (23/07)"], "parents": [] } },
    { "name": "Marcelo Teodoro Fernandes", "birth": None, "wedding": None, "init": "12/06", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Bruno Malagoli", "birth": "06/09", "wedding": None, "init": "18/12", "job": None, "city": None, "family": { "wife": "Maria da Conceição de Assis Malagoli (29/05)", "children": ["Bruna Mel Malagoli (10/01)", "Bianca Flor Malagoli (28/04)"], "parents": ["Maria Januária de Souza Malagoli (28/09)"] } },
    { "name": "Luciano Ribeiro Andrade", "birth": "15/02", "wedding": None, "init": None, "job": None, "city": None, "family": { "wife": "Daniele Mendes Venâncio Andrade (07/03)", "children": ["Miguel Mendes Ribeiro Andrade (02/06)"], "parents": [] } }
]

# --- LISTA MESTRE ---
MASTER_EVENTS = [
    # --- REUNIÕES 2026 (1º SEMESTRE) ---
    {"date": "06/02", "type": "Reunião", "name": "Reunião Presencial", "year": CURRENT_YEAR, "style": "presencial"},
    {"date": "20/02", "type": "Reunião", "name": "Reunião Presencial", "year": CURRENT_YEAR, "style": "presencial"},
    {"date": "06/03", "type": "Reunião", "name": "Reunião Presencial", "year": CURRENT_YEAR, "style": "presencial"},
    {"date": "20/03", "type": "Reunião", "name": "Reunião Presencial", "year": CURRENT_YEAR, "style": "presencial"},
    {"date": "03/04", "type": "Reunião", "name": "Reunião On Line", "year": CURRENT_YEAR, "style": "online"},
    {"date": "17/04", "type": "Reunião", "name": "Reunião Presencial", "year": CURRENT_YEAR, "style": "presencial"},
    {"date": "01/05", "type": "Reunião", "name": "Reunião On Line", "year": CURRENT_YEAR, "style": "online"},
    {"date": "15/05", "type": "Reunião", "name": "Reunião Presencial", "year": CURRENT_YEAR, "style": "presencial"},
    {"date": "29/05", "type": "Reunião", "name": "Data em Análise", "year": CURRENT_YEAR, "style": "analise"},
    {"date": "05/06", "type": "Reunião", "name": "Reunião On Line", "year": CURRENT_YEAR, "style": "online"},
    {"date": "19/06", "type": "Reunião", "name": "Reunião Presencial", "year": CURRENT_YEAR, "style": "presencial"},
    
    # --- CIDADES (Fixo) ---
    {"date": "12/12", "type": "Cidade", "city": "Belo Horizonte"},
    {"date": "29/04", "type": "Cidade", "city": "Ipatinga"},
    {"date": "05/11", "type": "Cidade", "city": "Abaeté"},
    {"date": "12/12", "type": "Cidade", "city": "Braúnas"},
    {"date": "14/08", "type": "Cidade", "city": "Parnaíba"},
    {"date": "01/06", "type": "Cidade", "city": "Divinópolis"},
    {"date": "01/03", "type": "Cidade", "city": "Dom Cavati"},
    {"date": "30/12", "type": "Cidade", "city": "Ataléia"},
    {"date": "07/09", "type": "Cidade", "city": "Teófilo Otoni"},
    {"date": "12/12", "type": "Cidade", "city": "Várzea da Palma"},
    {"date": "20/01", "type": "Cidade", "city": "Coronel Fabriciano"},
    {"date": "01/03", "type": "Cidade", "city": "Ibirité"},
    {"date": "12/12", "type": "Cidade", "city": "São Francisco do Glória"},
    # Aniversário de fundação da Loja: 11/05/1988 (confirmado pela conversa do
    # grupo em 11/05/2025: "Magos do Oriente, 37 anos de existência").
    {"date": "11/05", "type": "Loja", "name": "ARLS Magos do Oriente Nº 149"},
]

PROFESSION_DATES = {
    "Contador": "22/09", "Gerente de Projetos": "06/11", "Analista de TI": "19/10",
    "Assistente Administrativo": "15/10", "Auxiliar Administrativo": "15/10",
    "Administrador": "09/09", "Bombeiro Militar": "02/07", "Eletrotécnico": "09/11",
    "Mecânico de Aeronaves": "24/05", "Estagiário de Direito": "18/08",
    "Militar Reformado": "25/08", "Servidor Público": "28/10", "Engenheiro Civil": "11/12",
    "Advogado": "11/08", "Motorista": "25/07", "Representante Comercial": "01/10",
    "Empresário": "05/10", "Vendedor": "01/10", "Oficial Judiciário": "25/03"
}

# --- COMENDAS / CONDECORAÇÕES ---
# Use este registro para anotar comendas, medalhas e jubileus de irmãos.
# Cada item:
#   {"date": "DD/MM", "type": "Comenda", "name": "Nome da comenda",
#    "brother": "Nome completo do Ir.", "year": 2024 (opcional)}
# Quando preenchido, o robô passa a anunciar automaticamente no aniversário
# de cada comenda (mesmo formato dos demais eventos).
COMENDAS = [
    # Exemplo (descomente e adapte conforme ata da Loja):
    # {"date": "30/05", "type": "Comenda", "name": "Mestre Maçom",
    #  "brother": "Dante Carvalho Rodrigues", "year": 2025},
]

# --- FUNÇÕES AUXILIARES ---

def format_list(names):
    if not names: return ""
    if len(names) == 1: return names[0]
    return ", ".join(names[:-1]) + " e " + names[-1]

def tronco_value_widget(prefix: str) -> float:
    """Widget de valor do Tronco com opções rápidas (10, 20, ou outro valor)."""
    opt = st.radio(
        "Valor do Tronco",
        ["R$ 10", "R$ 20", "Outro valor"],
        horizontal=True,
        key=f"{prefix}_val_opt"
    )
    if opt == "R$ 10":
        return 10.0
    if opt == "R$ 20":
        return 20.0
    return float(
        st.number_input(
            "Outro valor (R$)",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            key=f"{prefix}_val_other"
        )
    )


def _brazil_today() -> date:
    """Retorna a data de hoje no fuso de Brasília (America/Sao_Paulo)."""
    try:
        return datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    except Exception:
        # fallback (caso zoneinfo não esteja disponível)
        return datetime.now().date()

def _parse_ddmm_to_date(ddmm: str, year: int = CURRENT_YEAR) -> date:
    """Converte 'DD/MM' em date(YYYY, MM, DD)."""
    try:
        return datetime.strptime(f"{ddmm}/{year}", "%d/%m/%Y").date()
    except Exception:
        # Se vier em outro formato, tenta inferir e, no pior caso, devolve hoje
        try:
            return datetime.strptime(ddmm, "%d/%m/%Y").date()
        except Exception:
            return _brazil_today()

def _default_meeting_index(meeting_events: list[dict], prefer_style: str = "presencial") -> int:
    """Escolhe como padrão a reunião futura mais próxima (preferindo 'presencial')."""
    if not meeting_events:
        return 0
    today = _brazil_today()

    indexed = []
    for i, evt in enumerate(meeting_events):
        d = _parse_ddmm_to_date(evt.get("date", ""), evt.get("year", CURRENT_YEAR))
        indexed.append((i, d, (evt.get("style") or "").lower()))

    future = [(i, d, stl) for (i, d, stl) in indexed if d >= today]
    future_pref = [(i, d, stl) for (i, d, stl) in future if stl == prefer_style.lower()]

    chosen = future_pref or future
    if not chosen:
        return 0

    # índice do evento mais próximo
    chosen.sort(key=lambda x: x[1])
    return int(chosen[0][0])

def _apply_pending_value_resets(prefix: str) -> None:
    """Aplica resets pendentes ANTES de montar os widgets (evita StreamlitAPIException)."""
    if st.session_state.pop(f"{prefix}_reset_other", False):
        # Importante: isso precisa acontecer antes do st.number_input com a mesma key.
        st.session_state[f"{prefix}_val_other"] = 0.0


def _request_other_value_reset(prefix: str) -> None:
    """Marca para resetar o campo de 'Outro valor' na próxima execução (após envio)."""
    if st.session_state.get(f"{prefix}_val_opt") == "Outro valor":
        st.session_state[f"{prefix}_reset_other"] = True

def show_flash_success(key: str):
    """Mostra uma mensagem de sucesso uma única vez (flash message)."""
    msg = st.session_state.pop(key, None)
    if msg:
        st.success(msg)

def set_flash_success(key: str, msg: str):
    st.session_state[key] = msg

def generate_templates(evt):
    names = evt.get('names', [evt.get('name')]) if evt.get('names') else [evt.get('name')]
    names_str = format_list(names)
    city = evt.get('city', '')
    job = evt.get('job', '')
    related = f" (Família Ir. {evt.get('relatedTo')})" if evt.get('relatedTo') else ""
    brothers_from_city = evt.get('brothers_from_city', [])
    city_suffix = f" Abraço fraterno aos irmãos naturais desta terra: {format_list(brothers_from_city)}." if brothers_from_city else ""

    templates = []
    if evt['type'] == 'Aniversário':
        templates = [f"Parabéns, Ir(s). {names_str}! Que o GADU ilumine os caminhos.", f"Feliz aniversário, Ir(s). {names_str}! Muita paz e saúde."]
    elif evt['type'] == 'Família':
        templates = [f"Parabéns a {names_str}{related} pelo aniversário! Saúde e alegria."]
    elif evt['type'] == 'Casamento':
        templates = [f"Parabéns ao(s) Ir(s). {names_str} pelo aniversário de casamento!"]
    elif evt['type'] == 'Iniciação':
        templates = [f"Parabéns, Ir(s). {names_str}, pelo aniversário de Iniciação!"]
    elif evt['type'] == 'Profissão':
        templates = [f"Homenagem ao(s) Ir(s). {names_str} pelo Dia do {job}!"]
    elif evt['type'] == 'Cidade':
        templates = [f"Parabéns à cidade de {city} pelo aniversário! {city_suffix}"]
    elif evt['type'] == 'Loja':
        templates = [f"Parabéns ARLS Magos do Oriente Nº 149!"]
    elif evt['type'] == 'Reunião':
        templates = [f"Lembrete: Hoje temos {names_str} às 20h.", f"Convocação: {names_str} nesta data."]
    else:
        templates = ["Parabéns!"]
    return templates

def create_html_calendar(year, month, events_map):
    # --- CORREÇÃO: Define o Domingo como primeiro dia da semana ---
    calendar.setfirstweekday(calendar.SUNDAY)
    
    cal = calendar.monthcalendar(year, month)
    MESES_PT = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL', 5: 'MAIO', 6: 'JUNHO',
        7: 'JULHO', 8: 'AGOSTO', 9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    month_name = MESES_PT[month]
    
    html = f"<div class='cal-container'><div class='cal-month-title'>{month_name} {year}</div>"
    html += "<table class='cal-table'><thead><tr><th>D</th><th>S</th><th>T</th><th>Q</th><th>Q</th><th>S</th><th>S</th></tr></thead><tbody>"
    
    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td></td>"
            else:
                day_str = f"{day:02d}/{month:02d}"
                style_class = ""
                if day_str in events_map:
                    evt_type = events_map[day_str]
                    if evt_type == 'presencial': style_class = "cal-day-presencial"
                    elif evt_type == 'online': style_class = "cal-day-online"
                    elif evt_type == 'analise': style_class = "cal-day-analise"
                
                html += f"<td><div class='{style_class}'>{day}</div></td>"
        html += "</tr>"
    
    html += "</tbody></table></div>"
    return html

# --- INTERFACE PRINCIPAL ---

# Cabeçalho Geral
col_h1, col_h2 = st.columns([1, 2])
with col_h1:
    try: st.image('logo-magos.png', width=350)
    except: pass
with col_h2:
    st.markdown("<h1 style='margin-top: 60px; font-size: 2.5em;'>MAGOS DO ORIENTE N° 149</h1>", unsafe_allow_html=True)

# Lógica de Login e Abas
if not st.session_state.get('logged_in', False):
    
    # CRIAÇÃO DAS ABAS DE ENTRADA
    tab_login, tab_externo = st.tabs(["🔐 ACESSO MEMBROS", "💰 LANÇAMENTO AVULSO"])
    
    # --- ABA 1: LOGIN (ADMIN/MEMBRO) ---
    with tab_login:
        col_l1, col_l2, col_l3 = st.columns([1,2,1])
        with col_l2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>ÁREA RESTRITA</h3>", unsafe_allow_html=True)
            pwd = st.text_input("Senha de Acesso", type="password")
            if st.button("ENTRAR", use_container_width=True):
                if pwd == "149":
                    st.session_state['logged_in'] = True
                    st.rerun()
                else: st.error("Senha incorreta.")

    # --- ABA 2: TRONCO EXTERNO (SEM SENHA) ---
    with tab_externo:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='background-color:#1a1a1a; padding:15px; border-radius:5px; border-left: 4px solid #2ecc71; margin-bottom:20px;'>👋 Bem-vindo! Utilize esta área para realizar lançamentos no tronco sem necessidade de login.</div>", unsafe_allow_html=True)

        # Mensagem após envio (sem expor lançamentos individuais)
        show_flash_success("ext_flash_success")

        meeting_events = [evt for evt in MASTER_EVENTS if evt['type'] == "Reunião" and evt.get('year') == CURRENT_YEAR]
        meeting_dates = [evt['date'] for evt in meeting_events]
        default_meeting_idx = _default_meeting_index(meeting_events, prefer_style="presencial")

        with st.container():
            col_ext1, col_ext2 = st.columns(2)
            with col_ext1:
                ext_date = st.selectbox("Data da Sessão", meeting_dates, index=default_meeting_idx, key="ext_date")
            with col_ext2:
                # Campo de texto livre para visitante/irmão sem senha
                ext_name = st.text_input("Seu Nome", placeholder="Digite seu nome completo", key="ext_name")

            # Valores rápidos: 10, 20 ou outro
            _apply_pending_value_resets("ext")
            ext_value = tronco_value_widget("ext")

            # Clique 1: prepara confirmação
            if st.button("ENVIAR LANÇAMENTO EXTERNO", use_container_width=True, key="ext_send_btn"):
                if not ext_name:
                    st.error("Por favor, digite seu nome.")
                elif ext_value <= 0:
                    st.error("O valor deve ser maior que zero.")
                else:
                    st.session_state["ext_confirm_payload"] = {
                        "date": ext_date,
                        "name": ext_name,
                        "value": float(ext_value)
                    }

            # Clique 2: confirma e envia
            payload = st.session_state.get("ext_confirm_payload")
            if payload:
                st.warning(
                    f"Confirma o envio do Tronco de R$ {payload['value']:.2f} para a sessão {payload['date']} em nome de {payload['name']}?"
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ CONFIRMAR ENVIO", use_container_width=True, key="ext_confirm_yes"):
                        if insert_tronco(payload["date"], payload["name"], payload["value"], "externo"):
                            st.session_state.pop("ext_confirm_payload", None)
                            _request_other_value_reset("ext")
                            set_flash_success("ext_flash_success", """✅ Tronco enviado e registrado.

🙏 Obrigado! Sua contribuição fortalece o Tronco de Beneficência e ajuda a manter viva a prática da caridade e da Fraternidade. Cada gesto faz diferença. 🤝✨""")
                            st.balloons()
                            st.rerun()
                with c2:
                    if st.button("❌ CANCELAR", use_container_width=True, key="ext_confirm_no"):
                        st.session_state.pop("ext_confirm_payload", None)
                        st.info("Envio cancelado.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### DADOS PARA DEPÓSITO (PIX)")
        pix_key = "38731048000142"
        col_pix1, col_pix2 = st.columns([3, 1])
        with col_pix1: st.code(pix_key, language="text")
        with col_pix2: st.markdown("Copie a chave.")

# --- SE ESTIVER LOGADO (DASHBOARD COMPLETO) ---
else:
    # Botão de Sair no topo
    if st.sidebar.button("SAIR"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- MENU DE NAVEGAÇÃO SUPERIOR ---
    tabs = st.tabs(["📅 CALENDÁRIO & EVENTOS", "💰 TRONCO", "👷 OBREIROS"])

    # ---------------- TAB 1: CALENDÁRIO & EVENTOS ----------------
    with tabs[0]:
        st.markdown(f"### CALENDÁRIO {CURRENT_YEAR} (1º SEMESTRE)")
        
        events_map = {}
        for evt in MASTER_EVENTS:
            if evt['type'] == 'Reunião' and evt.get('year') == CURRENT_YEAR:
                events_map[evt['date']] = evt.get('style', 'presencial')

        st.markdown("""
        <div style='display:flex; gap:15px; justify-content:center; margin-bottom:10px; font-size:0.8em;'>
            <span style='color:#e74c3c;'>● Presencial</span>
            <span style='color:#2ecc71;'>● Online</span>
            <span style='color:#f39c12;'>● Em Análise</span>
        </div>
        """, unsafe_allow_html=True)

        col_cal1, col_cal2, col_cal3 = st.columns(3)
        # CALENDÁRIO FORÇADO PARA 2026
        with col_cal1: st.markdown(create_html_calendar(CURRENT_YEAR, 2, events_map), unsafe_allow_html=True) # Fevereiro
        with col_cal2: st.markdown(create_html_calendar(CURRENT_YEAR, 3, events_map), unsafe_allow_html=True) # Março
        with col_cal3: st.markdown(create_html_calendar(CURRENT_YEAR, 4, events_map), unsafe_allow_html=True) # Abril
        
        col_cal4, col_cal5, col_cal6 = st.columns(3)
        with col_cal4: st.markdown(create_html_calendar(CURRENT_YEAR, 5, events_map), unsafe_allow_html=True) # Maio
        with col_cal5: st.markdown(create_html_calendar(CURRENT_YEAR, 6, events_map), unsafe_allow_html=True) # Junho
        with col_cal6: 
            st.info("Janeiro: Recesso")

        st.divider()
        st.markdown("### VERIFICAR EVENTOS DA SEMANA")
        
        today = datetime.now()
        meses_pt = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}
        
        with st.container():
            col_d1, col_d2, col_btn = st.columns([1, 2, 1])
            with col_d1: sel_dia = st.selectbox("Dia", list(range(1, 32)), index=today.day-1)
            with col_d2: 
                meses_list = list(meses_pt.values())
                sel_mes_nome = st.selectbox("Mês", meses_list, index=today.month-1)
            with col_btn: 
                st.markdown("<br>", unsafe_allow_html=True)
                btn_verificar = st.button("VERIFICAR", use_container_width=True, type="secondary")
            
            sel_mes_num = meses_list.index(sel_mes_nome) + 1
            try: check_date = datetime(today.year, sel_mes_num, sel_dia).date()
            except: check_date = None

        if btn_verificar and check_date:
            start_of_week = check_date - timedelta(days=check_date.weekday())
            week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
            found_events = []
            
            for current_date in week_dates:
                day_str = f"{current_date.day:02d}/{current_date.month:02d}"
                
                daily_births = [b['name'] for b in BROTHERS if b['birth'] == day_str]
                if daily_births: found_events.append({'date': day_str, 'type': 'Aniversário', 'names': daily_births, 'full_date': current_date})
                
                daily_weds = [b['name'] for b in BROTHERS if b['wedding'] == day_str]
                if daily_weds: found_events.append({'date': day_str, 'type': 'Casamento', 'names': daily_weds, 'full_date': current_date})
                
                daily_inits = [b['name'] for b in BROTHERS if b['init'] == day_str]
                if daily_inits: found_events.append({'date': day_str, 'type': 'Iniciação', 'names': daily_inits, 'full_date': current_date})

                for bro in BROTHERS:
                    fam = bro['family']
                    if fam:
                        if fam.get('wife') and fam['wife'].endswith(f"({day_str})"):
                            found_events.append({'date': day_str, 'type': 'Família', 'name': fam['wife'].split('(')[0].strip(), 'relatedTo': bro['name'], 'full_date': current_date})
                        if fam.get('children'):
                            for child in fam['children']:
                                if child.endswith(f"({day_str})"):
                                    found_events.append({'date': day_str, 'type': 'Família', 'name': child.split('(')[0].strip(), 'relatedTo': bro['name'], 'full_date': current_date})
                        if fam.get('parents'):
                            for parent in fam['parents']:
                                if parent.endswith(f"({day_str})"):
                                    found_events.append({'date': day_str, 'type': 'Família', 'name': parent.split('(')[0].strip(), 'relatedTo': bro['name'], 'full_date': current_date})

                professions_today = set()
                for bro in BROTHERS:
                    if bro['job'] and PROFESSION_DATES.get(bro['job']) == day_str: professions_today.add(bro['job'])
                for prof in professions_today:
                    bros_with_job = [b['name'] for b in BROTHERS if b['job'] == prof]
                    found_events.append({'date': day_str, 'type': 'Profissão', 'job': prof, 'names': bros_with_job, 'full_date': current_date})
                
                if day_str == "25/03": found_events.append({'date': day_str, 'type': 'Profissão', 'job': 'Oficial Judiciário', 'names': ["Matheus Eustáquio Gomes de Faria"], 'full_date': current_date})

                for evt in MASTER_EVENTS:
                    if evt['date'] == day_str:
                        if evt.get('year') and evt['year'] != current_date.year: continue
                        evt_copy = evt.copy()
                        evt_copy['full_date'] = current_date
                        if evt['type'] == 'Cidade':
                            city_name = evt['city']
                            bros_from_city = [b['name'] for b in BROTHERS if b.get('city') == city_name]
                            if bros_from_city: evt_copy['brothers_from_city'] = bros_from_city
                        found_events.append(evt_copy)

            st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
            if not found_events:
                st.info("Nenhum evento encontrado para a semana.")
            else:
                found_events.sort(key=lambda x: x['full_date'])
                for idx, evt in enumerate(found_events):
                    msgs = generate_templates(evt)
                    wkday = evt['full_date'].strftime("%A")
                    pt_wkday = {'Monday':'Segunda', 'Tuesday':'Terça', 'Wednesday':'Quarta', 'Thursday':'Quinta', 'Friday':'Sexta', 'Saturday':'Sábado', 'Sunday':'Domingo'}.get(wkday, wkday)
                    
                    display_title = evt.get('city') or evt.get('job') or format_list(evt.get('names', [evt.get('name')]))
                    if evt['type'] in ['Loja', 'Reunião']: display_title = evt['name']
                    border_color = "#e74c3c" if evt['type'] == 'Reunião' else "white"

                    st.markdown(f"""
                    <div class='result-card' style='border-left: 4px solid {border_color};'>
                        <div class='result-header'><span>{evt['type']}</span><span>{evt['date']} - {pt_wkday}</span></div>
                        <h3 style='margin-top:5px;color:white;font-size:1.3em;'>{display_title}</h3>
                        {f"<div style='color:#aaa;font-size:0.9em;margin-top:5px;'>Relacionado a: {evt.get('relatedTo')}</div>" if evt.get('relatedTo') else ""}
                    </div>""", unsafe_allow_html=True)
                    st.code(msgs[0], language="markdown")

    # ---------------- TAB 2: TRONCO (INTEGRADO COM SUPABASE) ----------------
    with tabs[1]:
        st.markdown("### LANÇAMENTO DE TRONCO")

        # Mensagem após envio (sem expor lançamentos individuais)
        show_flash_success("membro_flash_success")

        meeting_events = [evt for evt in MASTER_EVENTS if evt['type'] == "Reunião" and evt.get('year') == CURRENT_YEAR]
        meeting_dates = [evt['date'] for evt in meeting_events]
        default_meeting_idx = _default_meeting_index(meeting_events, prefer_style="presencial")

        with st.container():
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                t_date = st.selectbox("Data da Sessão", meeting_dates, index=default_meeting_idx, key="membro_date")
            with col_t2:
                brother_names = sorted([b['name'] for b in BROTHERS])
                t_brother = st.selectbox("Irmão", brother_names, key="membro_brother")

            # Valores rápidos: 10, 20 ou outro
            _apply_pending_value_resets("membro")
            t_value = tronco_value_widget("membro")

            col_act1, col_act2 = st.columns([1, 1])
            with col_act1:
                # Clique 1: prepara confirmação
                if st.button("ENVIAR LANÇAMENTO", use_container_width=True, type="secondary", key="membro_send_btn"):
                    if t_value <= 0:
                        st.error("O valor deve ser maior que zero.")
                    else:
                        st.session_state["membro_confirm_payload"] = {
                            "date": t_date,
                            "brother": t_brother,
                            "value": float(t_value)
                        }

                # Clique 2: confirma e envia
                payload = st.session_state.get("membro_confirm_payload")
                if payload:
                    st.warning(
                        f"Confirma o envio do Tronco de R$ {payload['value']:.2f} para a sessão {payload['date']} (Ir. {payload['brother']})?"
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ CONFIRMAR ENVIO", use_container_width=True, key="membro_confirm_yes"):
                            if insert_tronco(payload["date"], payload["brother"], payload["value"], "membro"):
                                st.session_state.pop("membro_confirm_payload", None)
                                _request_other_value_reset("membro")
                                set_flash_success("membro_flash_success", """✅ Tronco enviado e registrado.

🙏 Obrigado! Sua contribuição fortalece o Tronco de Beneficência e ajuda a manter viva a prática da caridade e da Fraternidade. Cada gesto faz diferença. 🤝✨""")
                                st.toast("Tronco enviado e registrado.", icon="✅")
                                st.rerun()
                    with c2:
                        if st.button("❌ CANCELAR", use_container_width=True, key="membro_confirm_no"):
                            st.session_state.pop("membro_confirm_payload", None)
                            st.info("Envio cancelado.")

            with col_act2:
                if st.button("ZERAR ESTE DIA", use_container_width=True, type="primary", key="membro_zerar_btn"):
                    # Apaga do Supabase
                    if delete_day_tronco(t_date):
                        st.toast(f"Valores do dia {t_date} apagados do Banco!", icon="🗑️")
                        st.rerun()

        st.divider()

        st.markdown("#### RESUMO DA ARRECADAÇÃO")

        # Busca dados do Supabase para exibir (apenas total do dia)
        current_total = fetch_tronco_day(t_date)

        st.markdown(f"""
        <div style='background-color:#1a1a1a; padding:20px; border-radius:10px; border: 1px solid #444; text-align:center;'>
            <h2 style='color:#2ecc71; margin:0;'>{t_date} - Tronco arrecadado: {current_total:.2f} reais</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### DADOS PARA DEPÓSITO (PIX)")
        pix_key = "38731048000142"
        col_pix1, col_pix2 = st.columns([3, 1])
        with col_pix1: st.code(pix_key, language="text")
        with col_pix2: st.markdown("Use a chave acima no seu banco.")

    # ---------------- TAB 3: OBREIROS ----------------
    with tabs[2]:
        st.markdown("### QUADRO DE OBREIROS")
        cols = st.columns(3)
        for i, bro in enumerate(sorted(BROTHERS, key=lambda x: x['name'])):
            with cols[i % 3]:
                fam_html = ""
                if bro['family']:
                    if bro['family'].get('wife'): fam_html += f"<div>❤️ Esposa: {bro['family']['wife']}</div>"
                    if bro['family'].get('children'): fam_html += f"<div>👶 Filhos: {', '.join(bro['family']['children'])}</div>"
                st.markdown(f"""<div class='brother-card'><div class='card-title'>{bro['name']}</div>
                <div class='card-info'>🎂 Nasc: {bro['birth'] or '-'}</div><div class='card-info'>💍 Casam: {bro['wedding'] or '-'}</div>
                <div class='card-info'>🎓 Inic: {bro['init'] or '-'}</div><div class='card-info'>💼 Prof: {bro['job'] or '-'}</div>
                <div class='card-info'>📍 Cid: {bro['city'] or '-'}</div><div class='card-family'>{fam_html}</div></div>""", unsafe_allow_html=True)

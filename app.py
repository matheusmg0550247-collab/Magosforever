import streamlit as st
from datetime import datetime, timedelta
import locale
import calendar

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão ARLS Magos do Oriente N° 149",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Tentar configurar locale para português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        pass

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
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #cccccc !important;
        transform: translateY(-2px);
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

    /* Code Block Tweak */
    code { white-space: pre-wrap !important; font-family: 'Courier New', monospace !important; font-size: 1rem !important; }
    h1, h2, h3 { color: white !important; font-family: 'Segoe UI', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- DADOS DOS IRMÃOS ---
BROTHERS = [
    { "name": "Vinicius Mateus dos Reis", "birth": "27/02", "wedding": "03/02", "init": "21/03", "job": "Contador", "city": "Belo Horizonte", "family": { "wife": "Mariane Fernanda de Freitas Reis", "children": ["Eduardo de Freitas Reis"], "parents": [] } },
    { "name": "Ulisses Ferreira de Souza", "birth": "19/12", "wedding": "22/01", "init": "26/11", "job": "Gerente de Projetos", "city": "Ipatinga", "family": { "wife": "Ana Paula Cardoso (14/06)", "children": ["Annalyce Cardoso", "Anna Gabrielly Cardoso"], "parents": ["Custódia Ferreira de Souza (27/07)"] } },
    { "name": "Thiago Henrique Batista Duarte", "birth": "30/11", "wedding": "05/05", "init": "03/12", "job": "Analista de TI", "city": "Belo Horizonte", "family": { "wife": "Franciane Cristina Toledo Duarte (16/12)", "children": ["Eduardo Toledo Duarte (11/06)", "Larissa Toledo Duarte (31/07)"], "parents": [] } },
    { "name": "Thiago Bustamante Bicalho", "birth": "08/08", "wedding": None, "init": "07/06", "job": "Assistente Administrativo", "city": "Belo Horizonte", "family": { "wife": "Natanne Pereira Rodrigues", "children": [], "parents": ["Ana Maria Fonseca Bustamante Bicalho"] } },
    { "name": "Thiago Augustus Fantoni Silva", "birth": "07/02", "wedding": "12/06", "init": "15/12", "job": "Bombeiro Militar", "city": "Belo Horizonte", "family": { "wife": "Valdete Vieira De Souza Fantoni (23/03)", "children": ["Ariadne Christiane Fantoni Silva (04/08)", "Astrid Célia Fantoni Silva (01/01)"], "parents": ["Idalino Pereira Silva (11/11)", "Alyria Dâmaris Desiree Barbosa Fantoni Silva (06/08)"] } },
    { "name": "Sandoval Falcão Borba", "birth": "02/04", "wedding": "07/02", "init": "28/11", "job": "Eletrotécnico", "city": "Braúnas", "family": { "wife": "Alvany Ferreira de Faria Borba", "children": ["Pedro Vinícius Falcão de Faria Borba (29/07)", "Juliana Cristina de Faria Borba (01/03)", "Pedro Henrique Souza Falcão (24/06)"], "parents": [] } },
    { "name": "Ricardo José Quaresma Sá", "birth": "01/06", "wedding": "12/01", "init": "09/11", "job": "Auxiliar Administrativo", "city": "Parnaíba", "family": { "wife": "Danúbia Pereira Martins Sá (22/05)", "children": [], "parents": ["Maria de Jesus Quaresma Sá"] } },
    { "name": "Rafael Tadeu Fernandes", "birth": "21/02", "wedding": None, "init": "26/11", "job": "Bombeiro Militar", "city": "Divinópolis", "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Paulo Henrique Freitas Martins", "birth": "15/05", "wedding": None, "init": "09/08", "job": "Mecânico de Aeronaves", "city": "Belo Horizonte", "family": { "wife": None, "children": ["Luiz Henrique Freitas Martins (06/10)"], "parents": ["Rubens Vidal de Carvalho", "Viviane Eustáchia Martins (10/01)"] } },
    { "name": "Moroni Leí Oliveira Fagundes", "birth": "09/12", "wedding": None, "init": "21/03", "job": "Estagiário de Direito", "city": "Belo Horizonte", "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Maurilio Geraldo Fernandes Theodoro", "birth": "19/02", "wedding": None, "init": "07/05", "job": "Militar Reformado", "city": "Belo Horizonte", "family": { "wife": "Iracema da Conceição Theodoro", "children": [], "parents": ["Maurilio Germano Theodoro", "Conceição Fernandes O. Theodoro"] } },
    { "name": "Matheus Eustáquio Gomes de Faria", "birth": "02/12", "wedding": "28/10", "init": "11/12", "job": "Oficial Judiciário", "city": "Belo Horizonte", "family": { "wife": "Ana Paula Lopes de Souza (19/04)", "children": [], "parents": ["José Eustáquio de Faria (18/03)", "Sílvia de Fátima Faria (18/06)"] } },
    { "name": "Mário Edésio Araújo Melo", "birth": "04/05", "wedding": None, "init": "27/10", "job": "Militar Reformado", "city": "Dom Cavati", "family": { "wife": None, "children": [], "parents": ["Edesio Ribeiro Melo", "Alfredina Pereira de Melo"] } },
    { "name": "Marcondes Vanderlei Fonseca Ribeiro", "birth": "20/04", "wedding": None, "init": "28/03", "job": "Administrador", "city": "Ataléia", "family": { "wife": "Cássia Rodrigues Martins Ribeiro (22/03)", "children": ["Luana Martins Ribeiro (19/09)"], "parents": ["Paulo Viana Ribeiro", "Maria do Perpétuo Socorro F. Ribeiro"] } },
    { "name": "José Eustáquio de Faria Júnior", "birth": "18/07", "wedding": "21/05", "init": "11/12", "job": "Engenheiro Civil", "city": "Belo Horizonte", "family": { "wife": "Patrícia Abreu Falcão Faria (16/03)", "children": ["Lívia Falcão de Faria (07/05)", "Gabriel Falcão de Faria (20/07)", "Manuela Falcão de Faria (07/09)"], "parents": ["José Eustáquio de Faria (18/03)", "Sílvia de Fátima Faria (18/06)"] } },
    { "name": "José Eustaquio de Faria", "birth": "18/03", "wedding": "26/02", "init": "12/08", "job": "Engenheiro Civil", "city": "Abaeté", "family": { "wife": "Silvia de Fatima Faria (18/06)", "children": [], "parents": ["João Eduardo de Faria (26/06)"] } },
    { "name": "Ivo Lourenço de Morais", "birth": "30/05", "wedding": None, "init": "27/10", "job": "Aposentado", "city": "São Francisco do Glória", "family": { "wife": "Terezinha Leocadia Reis de Morais", "children": [], "parents": ["Nestor Lourenço Borges", "Maria de Lourdes de Morais"] } },
    { "name": "Idalino Pereira Silva", "birth": "11/11", "wedding": "09/08", "init": "24/04", "job": "Servidor Público", "city": "Teófilo Otoni", "family": { "wife": "Alyria Dâmaris Desiree Barbosa Fantoni Silva (06/08)", "children": ["Ariadne Christiane Fantoni Silva (04/08)", "Astrid Célia Fantoni Silva (01/01)"], "parents": ["Sebastião dos Anjos Silva", "Benvida Rosa Pereira"] } },
    { "name": "Hugo Ferreira de Rezende", "birth": "28/09", "wedding": None, "init": "01/03", "job": "Auxiliar de Gerência", "city": "Belo Horizonte", "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Hermes do Nascimento Canhas Maciel", "birth": "11/05", "wedding": None, "init": "01/04", "job": "Advogado", "city": "Belo Horizonte", "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Ernane José de Lima", "birth": "18/04", "wedding": None, "init": "25/03", "job": "Motorista", "city": "Várzea da Palma", "family": { "wife": "Maria Felisbina", "children": [], "parents": ["Mariano José de Lima", "Maria Rodrigues Lima"] } },
    { "name": "Dante Carvalho Rodrigues", "birth": "24/01", "wedding": None, "init": "08/08", "job": "Bombeiro Militar", "city": "Belo Horizonte", "family": { "wife": "Silmara A. P. Tavares Rodrigues", "children": ["João Vitor Tavares Rodrigues (04/03)"], "parents": ["Dante Rodrigues Aparecido", "Maria de Lourdes Carvalho Rodrigues"] } },
    { "name": "Cláudio Luis Gomes", "birth": "18/08", "wedding": None, "init": "06/12", "job": "Representante Comercial", "city": "Coronel Fabriciano", "family": { "wife": "Vera Regina Soares Pacheco", "children": ["Gláucia Azevedo Gomes (01/06)", "Fernanda Azevedo Teixeira (20/06)", "Barbara Pacheco Bonfim (23/11)", "Matheus Henrique (04/06)", "Eduardo Antonio (25/05)", "Thifany Maria (30/12)", "Daniel Calebe (18/05)"], "parents": ["Sebastião Gomes da Silva", "Nair Alvarenga da Silva"] } },
    { "name": "Carlos Eduardo Giovanni Correa", "birth": "10/05", "wedding": "11/10", "init": "27/04", "job": "Engenheiro Civil", "city": "Ibirité", "family": { "wife": None, "children": ["Rafaela Luiza Soares Velasco Correa (02/06)"], "parents": [] } },
    { "name": "Amonn César Gonçalves", "birth": "15/05", "wedding": "22/09", "init": "28/05", "job": "Empresário", "city": "Belo Horizonte", "family": { "wife": "Geiciane Helen da Fonseca Gonçalves (16/06)", "children": [], "parents": [] } },
    { "name": "Alcirley Silva e Lopes", "birth": "06/09", "wedding": None, "init": "24/04", "job": "Vendedor", "city": "Belo Horizonte", "family": { "wife": None, "children": [], "parents": ["Alcides Ribeiro Lopes", "Helena Conceição da Silva Lopes"] } },
    { "name": "Jerry Marcos dos Santos Neto", "birth": "18/03", "wedding": "30/04", "init": "05/12", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Miguel Coleta Ferreira Neto", "birth": None, "wedding": "08/07", "init": "15/12", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Marcelo Teodoro Fernandes", "birth": None, "wedding": None, "init": "12/06", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": [] } },
    { "name": "Bruno Malagoli", "birth": "08/09", "wedding": None, "init": "18/12", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": ["Maria da Conceição de Assis Malagoli (31/05)"] } }
]

# --- LISTA MESTRE ---
MASTER_EVENTS = [
    # --- REUNIÕES 2026 (1º SEMESTRE) ---
    # Fevereiro (Adicionado)
    {"date": "06/02", "type": "Reunião", "name": "Reunião Presencial", "year": 2026, "style": "presencial"},
    {"date": "20/02", "type": "Reunião", "name": "Reunião Presencial", "year": 2026, "style": "presencial"},
    # Março (Adicionado)
    {"date": "06/03", "type": "Reunião", "name": "Reunião Presencial", "year": 2026, "style": "presencial"},
    {"date": "20/03", "type": "Reunião", "name": "Reunião Presencial", "year": 2026, "style": "presencial"},
    # Abril
    {"date": "03/04", "type": "Reunião", "name": "Reunião On Line", "year": 2026, "style": "online"},
    {"date": "17/04", "type": "Reunião", "name": "Reunião Presencial", "year": 2026, "style": "presencial"},
    # Maio
    {"date": "01/05", "type": "Reunião", "name": "Reunião On Line", "year": 2026, "style": "online"},
    {"date": "15/05", "type": "Reunião", "name": "Reunião Presencial", "year": 2026, "style": "presencial"},
    {"date": "29/05", "type": "Reunião", "name": "Data em Análise", "year": 2026, "style": "analise"},
    # Junho
    {"date": "05/06", "type": "Reunião", "name": "Reunião On Line", "year": 2026, "style": "online"},
    {"date": "19/06", "type": "Reunião", "name": "Reunião Presencial", "year": 2026, "style": "presencial"},

    # --- CIDADES (Fixo todos os anos) ---
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
    
    # --- LOJA ---
    {"date": "13/05", "type": "Loja", "name": "ARLS Magos do Oriente Nº 149"},
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

# --- FUNÇÕES AUXILIARES ---

def format_list(names):
    if not names: return ""
    if len(names) == 1: return names[0]
    return ", ".join(names[:-1]) + " e " + names[-1]

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
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month].capitalize()
    
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
                # Verifica se há evento neste dia e aplica estilo
                if day_str in events_map:
                    evt_type = events_map[day_str]
                    if evt_type == 'presencial': style_class = "cal-day-presencial"
                    elif evt_type == 'online': style_class = "cal-day-online"
                    elif evt_type == 'analise': style_class = "cal-day-analise"
                
                html += f"<td><div class='{style_class}'>{day}</div></td>"
        html += "</tr>"
    
    html += "</tbody></table></div>"
    return html

# --- INTERFACE ---

if not st.session_state.get('logged_in', False):
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try: st.image('logo-magos.png', width=300)
        except: st.markdown("<div style='text-align:center;'>Logo</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>ACESSO RESTRITO</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Senha", type="password")
        if st.button("ENTRAR", use_container_width=True):
            if pwd == "149":
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("Senha incorreta.")
else:
    col_h1, col_h2 = st.columns([1, 2])
    with col_h1:
        try: st.image('logo-magos.png', width=350)
        except: pass
    with col_h2:
         st.markdown("<h1 style='margin-top: 60px; font-size: 2.5em;'>MAGOS DO ORIENTE N° 149</h1>", unsafe_allow_html=True)

    # --- MENU DE NAVEGAÇÃO SUPERIOR ---
    tabs = st.tabs(["📅 CALENDÁRIO & EVENTOS", "💰 TRONCO", "👷 OBREIROS"])

    # ---------------- TAB 1: CALENDÁRIO & EVENTOS ----------------
    with tabs[0]:
        st.markdown("### CALENDÁRIO 2026 (1º SEMESTRE)")
        
        # Mapa de eventos para o calendário visual
        events_map = {}
        for evt in MASTER_EVENTS:
            if evt['type'] == 'Reunião' and evt.get('year') == 2026:
                events_map[evt['date']] = evt.get('style', 'presencial')

        # Legenda
        st.markdown("""
        <div style='display:flex; gap:15px; justify-content:center; margin-bottom:10px; font-size:0.8em;'>
            <span style='color:#e74c3c;'>● Presencial</span>
            <span style='color:#2ecc71;'>● Online</span>
            <span style='color:#f39c12;'>● Em Análise</span>
        </div>
        """, unsafe_allow_html=True)

        col_cal1, col_cal2, col_cal3 = st.columns(3)
        with col_cal1: st.markdown(create_html_calendar(2026, 2, events_map), unsafe_allow_html=True) # Fevereiro
        with col_cal2: st.markdown(create_html_calendar(2026, 3, events_map), unsafe_allow_html=True) # Março
        with col_cal3: st.markdown(create_html_calendar(2026, 4, events_map), unsafe_allow_html=True) # Abril
        
        col_cal4, col_cal5, col_cal6 = st.columns(3)
        with col_cal4: st.markdown(create_html_calendar(2026, 5, events_map), unsafe_allow_html=True) # Maio
        with col_cal5: st.markdown(create_html_calendar(2026, 6, events_map), unsafe_allow_html=True) # Junho
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
                btn_verificar = st.button("VERIFICAR", use_container_width=True)
            
            sel_mes_num = meses_list.index(sel_mes_nome) + 1
            try: check_date = datetime(today.year, sel_mes_num, sel_dia).date()
            except: check_date = None

        if btn_verificar and check_date:
            start_of_week = check_date - timedelta(days=check_date.weekday())
            week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
            found_events = []
            
            for current_date in week_dates:
                day_str = f"{current_date.day:02d}/{current_date.month:02d}"
                
                # Buscas nos dados (igual código anterior)
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

    # ---------------- TAB 2: TRONCO ----------------
    with tabs[1]:
        st.markdown("### LANÇAMENTO DE TRONCO")
        
        # Inicializa estado para guardar totais
        if 'tronco_totals' not in st.session_state:
            st.session_state.tronco_totals = {}

        # 1. Filtra apenas datas que são reuniões em 2026
        meeting_dates = [evt['date'] + "/2026" for evt in MASTER_EVENTS if evt['type'] == "Reunião" and evt.get('year') == 2026]
        
        with st.container():
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                t_date = st.selectbox("Data da Sessão", meeting_dates)
            with col_t2:
                # Ordena lista de irmãos
                brother_names = sorted([b['name'] for b in BROTHERS])
                t_brother = st.selectbox("Irmão", brother_names)
            
            t_value = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
            
            if st.button("ENVIAR LANÇAMENTO", use_container_width=True):
                # Chave única para o dia
                if t_date not in st.session_state.tronco_totals:
                    st.session_state.tronco_totals[t_date] = 0.0
                
                st.session_state.tronco_totals[t_date] += t_value
                st.toast(f"Lançamento de R$ {t_value:.2f} para {t_brother} realizado com sucesso!", icon="✅")

        st.divider()
        
        # Exibição do Resultado
        st.markdown("#### RESUMO DA ARRECADAÇÃO")
        
        # Mostra o total para a data selecionada atualmente (ou todas se preferir)
        current_total = st.session_state.tronco_totals.get(t_date, 0.0)
        
        st.markdown(f"""
        <div style='background-color:#1a1a1a; padding:20px; border-radius:10px; border: 1px solid #444; text-align:center;'>
            <h2 style='color:#2ecc71; margin:0;'>{t_date} - Tronco arrecadado: {current_total:.2f} reais</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Área do PIX
        st.markdown("#### DADOS PARA DEPÓSITO (PIX)")
        pix_key = "38731048000142"
        
        col_pix1, col_pix2 = st.columns([3, 1])
        with col_pix1:
            st.code(pix_key, language="text")
        with col_pix2:
            st.markdown("Use a chave acima no seu banco.")

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

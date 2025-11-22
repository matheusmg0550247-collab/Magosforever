import streamlit as st
from datetime import datetime, timedelta
import locale
import textwrap

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

# --- ESTILOS CSS (Preto e Branco) ---
st.markdown("""
<style>
    /* Fundo Geral */
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
    }
    
    /* Inputs */
    .stDateInput > div > div > input {
        color: white;
        background-color: #1a1a1a;
        border: 1px solid #444;
        text-align: center;
        font-size: 1.2rem;
    }
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #444;
        text-align: center;
    }
    .stTextArea > div > div > textarea {
        background-color: #111;
        color: #eee;
        border: 1px solid #444;
        font-family: monospace;
    }
    
    /* Botões */
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

    /* Cards de Irmãos */
    .brother-card {
        background-color: #121212;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .card-title {
        font-weight: 700;
        font-size: 1.15em;
        color: white;
        border-bottom: 1px solid #444;
        padding-bottom: 8px;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .card-info {
        font-size: 0.95em;
        color: #ccc;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .card-family {
        margin-top: auto;
        padding-top: 12px;
        border-top: 1px dashed #333;
        font-size: 0.85em;
        color: #888;
    }
    
    /* Cards de Resultado */
    .result-card {
        background-color: #1a1a1a;
        border-left: 4px solid white;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    .result-header {
        display: flex;
        justify-content: space-between;
        color: #888;
        font-size: 0.8em;
        text-transform: uppercase;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: white !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Esconder elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- DADOS DOS IRMÃOS ---

BROTHERS = [
    { 
        "name": "Vinicius Mateus dos Reis", "birth": "27/02", "wedding": "03/02", "init": "21/03", "job": "Contador", "city": "Belo Horizonte",
        "family": { "wife": "Mariane Fernanda de Freitas Reis", "children": ["Eduardo de Freitas Reis"], "parents": [] }
    },
    { 
        "name": "Ulisses Ferreira de Souza", "birth": "19/12", "wedding": "22/01", "init": "26/11", "job": "Gerente de Projetos", "city": "Ipatinga",
        "family": { "wife": "Ana Paula Cardoso (14/06)", "children": ["Annalyce Cardoso", "Anna Gabrielly Cardoso"], "parents": ["Custódia Ferreira de Souza (27/07)"] }
    },
    { 
        "name": "Thiago Henrique Batista Duarte", "birth": "30/11", "wedding": "05/05", "init": "03/12", "job": "Analista de TI", "city": "Belo Horizonte",
        "family": { "wife": "Franciane Cristina Toledo Duarte (16/12)", "children": ["Eduardo Toledo Duarte (11/06)", "Larissa Toledo Duarte (31/07)"], "parents": [] }
    },
    { 
        "name": "Thiago Bustamante Bicalho", "birth": "08/08", "wedding": None, "init": "07/06", "job": "Assistente Administrativo", "city": "Belo Horizonte",
        "family": { "wife": "Natanne Pereira Rodrigues", "children": [], "parents": ["Ana Maria Fonseca Bustamante Bicalho"] }
    },
    { 
        "name": "Thiago Augustus Fantoni Silva", "birth": "07/02", "wedding": "12/06", "init": "15/12", "job": "Bombeiro Militar", "city": "Belo Horizonte",
        "family": { "wife": "Valdete Vieira De Souza Fantoni (23/03)", "children": ["Ariadne Christiane Fantoni Silva (04/08)", "Astrid Célia Fantoni Silva (01/01)"], "parents": ["Idalino Pereira Silva (11/11)", "Alyria Dâmaris Desiree Barbosa Fantoni Silva (06/08)"] }
    },
    { 
        "name": "Sandoval Falcão Borba", "birth": "02/04", "wedding": "07/02", "init": "28/11", "job": "Eletrotécnico", "city": "Braúnas",
        "family": { "wife": "Alvany Ferreira de Faria Borba", "children": ["Pedro Vinícius Falcão de Faria Borba (29/07)", "Juliana Cristina de Faria Borba (01/03)", "Pedro Henrique Souza Falcão (24/06)"], "parents": [] }
    },
    { 
        "name": "Ricardo José Quaresma Sá", "birth": "01/06", "wedding": "12/01", "init": "09/11", "job": "Auxiliar Administrativo", "city": "Parnaíba",
        "family": { "wife": "Danúbia Pereira Martins Sá (22/05)", "children": [], "parents": ["Maria de Jesus Quaresma Sá"] }
    },
    { 
        "name": "Rafael Tadeu Fernandes", "birth": "21/02", "wedding": None, "init": "26/11", "job": "Bombeiro Militar", "city": "Divinópolis",
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Paulo Henrique Freitas Martins", "birth": "15/05", "wedding": None, "init": "09/08", "job": "Mecânico de Aeronaves", "city": "Belo Horizonte",
        "family": { "wife": None, "children": ["Luiz Henrique Freitas Martins (06/10)"], "parents": ["Rubens Vidal de Carvalho", "Viviane Eustáchia Martins (10/01)"] }
    },
    { 
        "name": "Moroni Leí Oliveira Fagundes", "birth": "09/12", "wedding": None, "init": "21/03", "job": "Estagiário de Direito", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Maurilio Geraldo Fernandes Theodoro", "birth": "19/02", "wedding": None, "init": "07/05", "job": "Militar Reformado", "city": "Belo Horizonte",
        "family": { "wife": "Iracema da Conceição Theodoro", "children": [], "parents": ["Maurilio Germano Theodoro", "Conceição Fernandes O. Theodoro"] }
    },
    { 
        "name": "Matheus Eustáquio Gomes de Faria", "birth": "02/12", "wedding": None, "init": "11/12", "job": "Oficial Judiciário", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": ["José Eustáquio de Faria (18/03)", "Sílvia de Fátima Faria (18/06)"] }
    },
    { 
        "name": "Mário Edésio Araújo Melo", "birth": "04/05", "wedding": None, "init": "27/10", "job": "Militar Reformado", "city": "Dom Cavati",
        "family": { "wife": None, "children": [], "parents": ["Edesio Ribeiro Melo", "Alfredina Pereira de Melo"] }
    },
    { 
        "name": "Marcondes Vanderlei Fonseca Ribeiro", "birth": "20/04", "wedding": None, "init": "28/03", "job": "Administrador", "city": "Ataléia",
        "family": { "wife": "Cássia Rodrigues Martins Ribeiro (22/03)", "children": ["Luana Martins Ribeiro (19/09)"], "parents": ["Paulo Viana Ribeiro", "Maria do Perpétuo Socorro F. Ribeiro"] }
    },
    { 
        "name": "José Eustáquio de Faria Júnior", "birth": "18/07", "wedding": "21/05", "init": "11/12", "job": "Engenheiro Civil", "city": "Belo Horizonte",
        "family": { "wife": "Patrícia Abreu Falcão Faria (16/03)", "children": ["Lívia Falcão de Faria (07/05)", "Gabriel Falcão de Faria (20/07)", "Manuela Falcão de Faria (07/09)"], "parents": ["José Eustáquio de Faria (18/03)", "Sílvia de Fátima Faria (18/06)"] }
    },
    { 
        "name": "José Eustaquio de Faria", "birth": "18/03", "wedding": "26/02", "init": "12/08", "job": "Engenheiro Civil", "city": "Abaeté",
        "family": { "wife": "Silvia de Fatima Faria (18/06)", "children": [], "parents": ["João Eduardo de Faria (26/06)"] }
    },
    { 
        "name": "Ivo Lourenço de Morais", "birth": "30/05", "wedding": None, "init": "27/10", "job": "Aposentado", "city": "São Francisco do Glória",
        "family": { "wife": "Terezinha Leocadia Reis de Morais", "children": [], "parents": ["Nestor Lourenço Borges", "Maria de Lourdes de Morais"] }
    },
    { 
        "name": "Idalino Pereira Silva", "birth": "11/11", "wedding": "09/08", "init": "24/04", "job": "Servidor Público", "city": "Teófilo Otoni",
        "family": { "wife": "Alyria Dâmaris Desiree Barbosa Fantoni Silva (06/08)", "children": ["Ariadne Christiane Fantoni Silva (04/08)", "Astrid Célia Fantoni Silva (01/01)"], "parents": ["Sebastião dos Anjos Silva", "Benvida Rosa Pereira"] }
    },
    { 
        "name": "Hugo Ferreira de Rezende", "birth": "28/09", "wedding": None, "init": "01/03", "job": "Auxiliar de Gerência", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Hermes do Nascimento Canhas Maciel", "birth": "11/05", "wedding": None, "init": "01/04", "job": "Advogado", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Ernane José de Lima", "birth": "18/04", "wedding": None, "init": "25/03", "job": "Motorista", "city": "Várzea da Palma",
        "family": { "wife": "Maria Felisbina", "children": [], "parents": ["Mariano José de Lima", "Maria Rodrigues Lima"] }
    },
    { 
        "name": "Dante Carvalho Rodrigues", "birth": "24/01", "wedding": None, "init": "08/08", "job": "Bombeiro Militar", "city": "Belo Horizonte",
        "family": { "wife": "Silmara A. P. Tavares Rodrigues", "children": ["João Vitor Tavares Rodrigues (04/03)"], "parents": ["Dante Rodrigues Aparecido", "Maria de Lourdes Carvalho Rodrigues"] }
    },
    { 
        "name": "Cláudio Luis Gomes", "birth": "18/08", "wedding": None, "init": "06/12", "job": "Representante Comercial", "city": "Coronel Fabriciano",
        "family": { "wife": "Vera Regina Soares Pacheco", "children": ["Gláucia Azevedo Gomes (01/06)", "Fernanda Azevedo Teixeira (20/06)", "Barbara Pacheco Bonfim (25/11)", "Matheus Henrique (04/06)", "Eduardo Antonio (25/05)", "Thifany Maria (30/12)", "Daniel Calebe (18/05)"], "parents": ["Sebastião Gomes da Silva", "Nair Alvarenga da Silva"] }
    },
    { 
        "name": "Carlos Eduardo Giovanni Correa", "birth": "10/05", "wedding": "11/10", "init": "27/04", "job": "Engenheiro Civil", "city": "Ibirité",
        "family": { "wife": None, "children": ["Rafaela Luiza Soares Velasco Correa (02/06)"], "parents": [] }
    },
    { 
        "name": "Amonn César Gonçalves", "birth": "15/05", "wedding": "22/09", "init": "28/05", "job": "Empresário", "city": "Belo Horizonte",
        "family": { "wife": "Geiciane Helen da Fonseca Gonçalves (16/06)", "children": [], "parents": [] }
    },
    { 
        "name": "Alcirley Silva e Lopes", "birth": "06/09", "wedding": None, "init": "24/04", "job": "Vendedor", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": ["Alcides Ribeiro Lopes", "Helena Conceição da Silva Lopes"] }
    },
    { 
        "name": "Jerry Marcos dos Santos Neto", "birth": "18/03", "wedding": "30/04", "init": "05/12", "job": None, "city": None, 
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Miguel Coleta Ferreira Neto", "birth": None, "wedding": "08/07", "init": "15/12", "job": None, "city": None, 
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Marcelo Teodoro Fernandes", "birth": None, "wedding": None, "init": "12/06", "job": None, "city": None, 
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Bruno Malagoli", "birth": "08/09", "wedding": None, "init": "18/12", "job": None, "city": None, 
        "family": { "wife": None, "children": [], "parents": ["Maria da Conceição de Assis Malagoli (31/05)"] }
    }
]

# --- GERADOR DINÂMICO DE EVENTOS (Baseado na lista BROTHERS) ---
def get_master_events():
    events = []
    
    # 1. Eventos dos Irmãos (Aniversário, Casamento, Iniciação)
    for bro in BROTHERS:
        if bro['birth']: events.append({"date": bro['birth'], "type": "Birthday", "name": bro['name']})
        if bro['wedding']: events.append({"date": bro['wedding'], "type": "Wedding", "name": bro['name']})
        if bro['init']: events.append({"date": bro['init'], "type": "Initiation", "name": bro['name']})
        
        # 2. Eventos da Família (Extraídos das strings formatadas "Nome (Data)")
        fam = bro['family']
        if fam:
            # Verifica Esposa
            if fam.get('wife') and '(' in str(fam['wife']):
                name_part = fam['wife'].split('(')[0].strip()
                date_part = fam['wife'].split('(')[1].replace(')', '').strip()
                events.append({"date": date_part, "type": "Family", "name": name_part, "relatedTo": bro['name']})
            
            # Verifica Filhos
            if fam.get('children'):
                for child in fam['children']:
                    if '(' in child:
                        name_part = child.split('(')[0].strip()
                        date_part = child.split('(')[1].replace(')', '').strip()
                        events.append({"date": date_part, "type": "Family", "name": name_part, "relatedTo": bro['name']})
                        
            # Verifica Pais
            if fam.get('parents'):
                for parent in fam['parents']:
                    if '(' in parent:
                        name_part = parent.split('(')[0].strip()
                        date_part = parent.split('(')[1].replace(')', '').strip()
                        events.append({"date": date_part, "type": "Family", "name": name_part, "relatedTo": bro['name']})

    # 3. Eventos de Cidade (Fixos)
    cities = [
        {"city": "Belo Horizonte", "date": "12/12"},
        {"city": "Ipatinga", "date": "29/04"},
        {"city": "Abaeté", "date": "05/11"},
        {"city": "Braúnas", "date": "12/12"},
        {"city": "Parnaíba", "date": "14/08"},
        {"city": "Divinópolis", "date": "01/06"},
        {"city": "Dom Cavati", "date": "01/03"},
        {"city": "Ataléia", "date": "30/12"},
        {"city": "Teófilo Otoni", "date": "07/09"},
        {"city": "Várzea da Palma", "date": "12/12"},
        {"city": "Coronel Fabriciano", "date": "20/01"},
        {"city": "Ibirité", "date": "01/03"},
        {"city": "São Francisco do Glória", "date": "12/12"}
    ]
    for c in cities:
        events.append({"date": c['date'], "type": "City", "city": c['city']})

    # 4. Aniversário da Loja
    events.append({"date": "13/05", "type": "Lodge", "name": "ARLS Magos do Oriente Nº 149"})
    
    return events

MASTER_EVENTS = get_master_events()

PROFESSION_DATES = {
    "Contador": "22/09", "Gerente de Projetos": "06/11", "Analista de TI": "19/10",
    "Assistente Administrativo": "15/10", "Auxiliar Administrativo": "15/10",
    "Administrador": "09/09", "Bombeiro Militar": "02/07", "Eletrotécnico": "09/11",
    "Mecânico de Aeronaves": "24/05", "Estagiário de Direito": "18/08",
    "Militar Reformado": "25/08", "Servidor Público": "28/10", "Engenheiro Civil": "11/12",
    "Advogado": "11/08", "Motorista": "25/07", "Representante Comercial": "01/10",
    "Empresário": "05/10", "Vendedor": "01/10", "Oficial Judiciário": "25/03"
}

# --- FUNÇÕES ---

def generate_templates(evt):
    name = evt.get('name', '')
    city = evt.get('city', '')
    job = evt.get('job', '')
    related = f" (Família Ir. {evt.get('relatedTo')})" if evt.get('relatedTo') else ""
    
    templates = []
    
    if evt['type'] == 'Birthday':
        templates = [
            f"Parabéns, Ir. {name}! Que o Grande Arquiteto do Universo ilumine seus caminhos com muita saúde, paz e sabedoria. Feliz aniversário!",
            f"Hoje celebramos a vida do nosso Ir. {name}. Desejamos muita luz, prosperidade e um novo ciclo repleto de realizações. TFA!",
            f"Grande abraço e feliz aniversário, Ir. {name}! Que a alegria deste dia se estenda por todo o ano. Muita paz e fraternidade.",
            f"Nossas homenagens ao Ir. {name} nesta data querida. Que a vida continue lhe sorrindo com amor, saúde e sucesso.",
            f"Feliz aniversário, meu Irmão {name}! Que tenhas um dia fantástico cercado de carinho, bençãos e união."
        ]
    elif evt['type'] == 'Family':
        templates = [
            f"Parabéns a {name}{related} pelo aniversário! A Loja Magos do Oriente deseja muita saúde e alegrias junto à família.",
            f"Hoje é dia de festa para {name}! Que o GADU abençoe este novo ano de vida com muitas felicidades e harmonia no lar.",
            f"Felicitações a {name} nesta data especial. Que seja um dia repleto de amor e celebração em família.",
            f"Enviamos nosso carinho e votos de feliz aniversário para {name}. Tudo de bom e muitas realizações!",
            f"Celebramos hoje o aniversário de {name}. Muita luz, paz e proteção divina neste novo ciclo!"
        ]
    elif evt['type'] == 'Wedding':
        templates = [
            f"Parabéns ao Ir. {name} e esposa pelo aniversário de casamento! Que a união continue sendo fortalecida pelo amor e cumplicidade.",
            f"Feliz aniversário de casamento, Ir. {name}! Que o GADU continue abençoando essa bela união e a família constituída.",
            f"Celebrando o amor! Parabéns, Ir. {name}, pelas Bodas. Que a felicidade do casal seja eterna e inspiradora para todos nós.",
            f"Hoje comemoramos a união do Ir. {name}. Que a harmonia e o respeito reinem sempre em seu lar. Parabéns ao casal!",
            f"Votos de felicidades infinitas ao Ir. {name} e esposa. Que o laço que os une se torne cada dia mais forte e fraterno."
        ]
    elif evt['type'] == 'Initiation':
        templates = [
            f"Parabéns, Ir. {name}, pelo seu aniversário de Iniciação! Que a Luz recebida continue guiando seus passos na senda da virtude.",
            f"Hoje celebramos o nascimento maçônico do Ir. {name}. Que continue lapidando sua Pedra Bruta com vigor e sabedoria. TFA!",
            f"Feliz aniversário de Iniciação, Ir. {name}! Uma data para recordar o compromisso assumido e renovar os votos de fraternidade.",
            f"Nesta data especial, saudamos o Ir. {name} pelos anos de dedicação à nossa Ordem. Um verdadeiro exemplo de Obreiro!",
            f"Mais um ano de Luz na vida do Ir. {name}. Parabéns pela perseverança e pelo trabalho constante em prol da nossa Instituição."
        ]
    elif evt['type'] == 'Profession':
        templates = [
            f"Homenagem ao Ir. {name} pelo Dia do {job}! Obrigado por construir uma sociedade melhor com seu trabalho digno.",
            f"Parabéns aos profissionais de {job}, em especial ao nosso Ir. {name}. Sucesso e muitas realizações na carreira!",
            f"Dia do {job}! Nossos cumprimentos ao Ir. {name} pela dedicação, ética e excelência profissional.",
            f"Uma homenagem especial ao Ir. {name} nesta data dedicada ao {job}. Reconhecimento merecido pelo seu esforço!",
            f"Celebramos hoje o Dia do {job}. Parabéns, Ir. {name}, por exercer sua profissão com maestria e responsabilidade."
        ]
    elif evt['type'] == 'City':
        templates = [
            f"Parabéns à cidade de {city} pelo seu aniversário! Que continue crescendo e acolhendo a todos com hospitalidade.",
            f"Hoje {city} está em festa! Nossas homenagens a esta terra querida e aos irmãos que nela residem e trabalham.",
            f"Aniversário de {city}! Celebramos a história e o futuro desta cidade que é lar de tantos de nós.",
            f"Parabéns, {city}! Que o progresso, a paz e a harmonia sejam constantes nesta cidade maravilhosa.",
            f"Dia de festa em {city}! Homenagem da ARLS Magos do Oriente Nº 149 a esta comunidade."
        ]
    elif evt['type'] == 'Lodge':
        templates = [f"Parabéns ARLS Magos do Oriente Nº 149! Que a luz continue brilhando.", f"Dia de festa na Loja! Parabéns a todos os Obreiros.", f"Viva a Magos do Oriente! Anos de tradição e fraternidade."]
    else:
        templates = ["Parabéns!"]
        
    return templates

# --- ESTADO DA SESSÃO (LOGIN) ---

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- INTERFACE ---

if not st.session_state['logged_in']:
    # TELA DE LOGIN
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            st.image('logo-magos.png', width=300)
        except:
            st.markdown("<div style='text-align:center;'>Logo</div>", unsafe_allow_html=True)
            
        st.markdown("<h2 style='text-align: center;'>ACESSO RESTRITO</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Magos do Oriente N° 149</p>", unsafe_allow_html=True)
        
        password = st.text_input("Senha", type="password")
        
        if st.button("ENTRAR", use_container_width=True):
            if password == "149":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
else:
    # TELA PRINCIPAL
    
    # Cabeçalho
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        c1, c2 = st.columns([0.5, 3])
        with c1:
            try:
                st.image('logo-magos.png', width=100)
            except:
                pass
        with c2:
             st.markdown("<h3 style='margin-top:35px;'>MAGOS DO ORIENTE N° 149</h3>", unsafe_allow_html=True)

    with col_h2:
        today_str = datetime.now().strftime("%d de %B de %Y")
        st.markdown(f"<div style='text-align: right; color: #888; padding-top: 40px;'>{today_str}</div>", unsafe_allow_html=True)
    
    st.divider()

    # --- SEÇÃO SUPERIOR: VERIFICADOR DE EVENTOS ---
    
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>VERIFICAR EVENTOS DA SEMANA (Seg-Dom)</h3>", unsafe_allow_html=True)
    
    col_v1, col_v2, col_v3 = st.columns([1,1,1])
    with col_v2:
        check_date = st.date_input("Selecione a Data para Verificar", datetime.now(), format="DD/MM/YYYY")
        
        if st.button("VERIFICAR AGORA", use_container_width=True):
            # Calcular início (Segunda) e fim (Domingo) da semana selecionada
            start_of_week = check_date - timedelta(days=check_date.weekday())
            week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
            
            events = []
            
            # Loop para cada dia da semana
            for current_date in week_dates:
                day = current_date.strftime("%d")
                month = current_date.strftime("%m")
                date_str = f"{day}/{month}"
                
                # 1. Lista Mestre
                for evt in MASTER_EVENTS:
                    if evt['date'] == date_str:
                        evt_copy = evt.copy()
                        evt_copy['full_date'] = current_date
                        events.append(evt_copy)
                
                # 2. Profissões (Dinâmico)
                for bro in BROTHERS:
                    if bro['job'] and PROFESSION_DATES.get(bro['job']) == date_str:
                        events.append({
                            'type': 'Profession', 
                            'name': bro['name'], 
                            'job': bro['job'], 
                            'date': date_str,
                            'full_date': current_date
                        })
                
                # 3. Oficial de Justiça (Caso especial Matheus)
                if date_str == "25/03":
                     events.append({ 
                         'type': 'Profession', 
                         'name': "Matheus Eustáquio Gomes de Faria", 
                         'job': "Oficial Judiciário", 
                         'date': date_str,
                         'full_date': current_date
                     })

            st.markdown("<br>", unsafe_allow_html=True)
            
            if not events:
                st.info(f"Nenhum evento encontrado para a semana de {start_of_week.strftime('%d/%m')} a {(start_of_week + timedelta(days=6)).strftime('%d/%m')}.")
            else:
                st.success(f"{len(events)} evento(s) encontrado(s) para a semana!")
                
                # Ordenar eventos por data dentro da semana
                events.sort(key=lambda x: x['full_date'])
                
                for evt in events:
                    msgs = generate_templates(evt)
                    
                    # Mostrar dia da semana
                    weekday_name = evt['full_date'].strftime("%A")
                    # Tradução simples dos dias
                    days_map = {'Monday':'Segunda', 'Tuesday':'Terça', 'Wednesday':'Quarta', 'Thursday':'Quinta', 'Friday':'Sexta', 'Saturday':'Sábado', 'Sunday':'Domingo'}
                    pt_weekday = days_map.get(weekday_name, weekday_name)
                    
                    st.markdown(f"""
                    <div class='result-card'>
                        <div class='result-header'>
                            <span>{evt['type']}</span>
                            <span>{evt['date']} ({pt_weekday})</span>
                        </div>
                        <h3 style='margin-top: 5px; color: white; font-size: 1.3em;'>{evt.get('name') or evt.get('city')}</h3>
                        {f"<div style='color: #aaa; font-size: 0.9em; margin-top:5px;'>Relacionado a: {evt.get('relatedTo')}</div>" if evt.get('relatedTo') else ""}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Usando st.text_area para melhor visualização e cópia
                    st.text_area("Mensagem Principal", value=msgs[0], height=100, key=f"main_{evt.get('name')}_{evt['date']}_{evt['type']}")
                    
                    with st.expander("Ver mais opções de mensagens"):
                        for i, msg in enumerate(msgs[1:]):
                            st.text_area(f"Opção {i+2}", value=msg, height=100, key=f"opt_{i}_{evt.get('name')}_{evt['date']}_{evt['type']}")

    st.divider()
    
    # --- QUADRO DE OBREIROS ---
    st.markdown("#### QUADRO DE OBREIROS")
    
    filtered_brothers = sorted(BROTHERS, key=lambda x: x['name'])
    
    with st.container():
        cols = st.columns(3)
        for i, bro in enumerate(filtered_brothers):
            with cols[i % 3]:
                fam = bro['family']
                fam_html = ""
                if fam:
                    if fam.get('wife'):
                        fam_html += f"<div>❤️ Esposa: {fam['wife']}</div>"
                    if fam.get('children'):
                        children_str = ', '.join(fam['children'])
                        fam_html += f"<div>👶 Filhos: {children_str}</div>"
                    if fam.get('parents'):
                        parents_str = ', '.join(fam['parents'])
                        fam_html += f"<div>👴 Pais: {parents_str}</div>"
                
                html = f"""<div class='brother-card'>
<div class='card-title'>{bro['name']}</div>
<div class='card-info'>🎂 Nasc: {bro['birth'] or '-'}</div>
<div class='card-info'>💍 Casam: {bro['wedding'] or '-'}</div>
<div class='card-info'>🎓 Inic: {bro['init'] or '-'}</div>
<div class='card-info'>💼 Prof: {bro['job'] or '-'}</div>
<div class='card-info'>📍 Cid: {bro['city'] or '-'}</div>
<div class='card-family'>{fam_html}</div>
</div>"""
                st.markdown(html, unsafe_allow_html=True)

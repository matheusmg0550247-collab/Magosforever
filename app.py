import streamlit as st
from datetime import datetime
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
    
    /* Inputs de Data e Texto */
    .stDateInput > div > div > input {
        color: white;
        background-color: #1a1a1a;
        border: 1px solid #444;
        text-align: center;
    }
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #444;
        text-align: center;
    }
    
    /* Botões */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        border: none !important;
        height: 3em;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #cccccc !important;
        transform: translateY(-2px);
    }

    /* Cards Personalizados */
    .brother-card {
        background-color: #121212;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.05);
    }
    .card-title {
        font-weight: bold;
        font-size: 1.1em;
        color: white;
        border-bottom: 1px solid #444;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }
    .card-info {
        font-size: 0.9em;
        color: #bbb;
        margin-bottom: 4px;
    }
    .card-family {
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed #333;
        font-size: 0.8em;
        color: #888;
    }
    
    /* Títulos e Cabeçalhos */
    h1, h2, h3, h4, p, div, span {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h3 {
        color: white !important;
    }

    /* Esconder menu padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- DADOS ---

BROTHERS = [
    { 
        "name": "Vinicius Mateus dos Reis", "birth": "27/02", "wedding": "03/02", "init": "21/03", "job": "Contador", "city": "Belo Horizonte",
        "family": { "wife": "Mariane Fernanda de Freitas Reis", "children": ["Eduardo de Freitas Reis"], "parents": [] }
    },
    { 
        "name": "Ulisses Ferreira de Souza", "birth": "19/12", "wedding": "22/01", "init": "26/11", "job": "Gerente de Projetos", "city": "Ipatinga",
        "family": { "wife": "Ana Paula Cardoso", "children": ["Annalyce Cardoso", "Anna Gabrielly Cardoso"], "parents": ["Custódia Ferreira de Souza"] }
    },
    { 
        "name": "Thiago Henrique Batista Duarte", "birth": "02/12", "wedding": "07/05", "init": "05/12", "job": "Analista de TI", "city": "Belo Horizonte",
        "family": { "wife": "Franciane Cristina Toledo Duarte", "children": ["Eduardo Toledo Duarte", "Larissa Toledo Duarte"], "parents": [] }
    },
    { 
        "name": "Thiago Bustamante Bicalho", "birth": "08/08", "wedding": None, "init": "07/06", "job": "Assistente Administrativo", "city": "Belo Horizonte",
        "family": { "wife": "Natanne Pereira Rodrigues", "children": [], "parents": ["Ana Maria Fonseca Bustamante Bicalho"] }
    },
    { 
        "name": "Thiago Augustus Fantoni Silva", "birth": "09/02", "wedding": "14/06", "init": "17/12", "job": "Bombeiro Militar", "city": "Belo Horizonte",
        "family": { "wife": "Valdete Vieira De Souza Fantoni", "children": ["Ariadne Christiane Fantoni Silva", "Astrid Célia Fantoni Silva"], "parents": ["Idalino Pereira Silva", "Alyria Dâmaris Desiree Barbosa Fantoni Silva"] }
    },
    { 
        "name": "Sandoval Falcão Borba", "birth": "02/04", "wedding": "09/02", "init": "28/11", "job": "Eletrotécnico", "city": "Braúnas",
        "family": { "wife": "Alvany Ferreira de Faria Borba", "children": ["Pedro Vinícius Falcão de Faria Borba", "Juliana Cristina de Faria Borba", "Pedro Henrique Souza Falcão"], "parents": [] }
    },
    { 
        "name": "Ricardo José Quaresma Sá", "birth": "03/06", "wedding": None, "init": "11/11", "job": "Auxiliar Administrativo", "city": "Parnaíba",
        "family": { "wife": "Danúbia Pereira Martins Sá", "children": [], "parents": ["Maria de Jesus Quaresma Sá"] }
    },
    { 
        "name": "Rafael Tadeu Fernandes", "birth": "23/02", "wedding": None, "init": "26/11", "job": "Bombeiro Militar", "city": "Divinópolis",
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Paulo Henrique Freitas Martins", "birth": "17/05", "wedding": None, "init": "11/08", "job": "Mecânico de Aeronaves", "city": "Belo Horizonte",
        "family": { "wife": None, "children": ["Luiz Henrique Freitas Martins"], "parents": ["Rubens Vidal de Carvalho", "Viviane Eustáchia Martins"] }
    },
    { 
        "name": "Moroni Leí Oliveira Fagundes", "birth": "09/12", "wedding": None, "init": "21/03", "job": "Estagiário de Direito", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Maurilio Geraldo Fernandes Theodoro", "birth": "21/02", "wedding": None, "init": "09/05", "job": "Militar Reformado", "city": "Belo Horizonte",
        "family": { "wife": "Iracema da Conceição Theodoro", "children": [], "parents": ["Maurilio Germano Theodoro", "Conceição Fernandes O. Theodoro"] }
    },
    { 
        "name": "Matheus Eustáquio Gomes de Faria", "birth": "04/12", "wedding": "28/10", "init": "13/12", "job": "Servidor Público", "city": "Belo Horizonte",
        "family": { "wife": "Ana Paula Lopes de Souza", "children": [], "parents": ["José Eustáquio de Faria", "Sílvia de Fátima Faria"] }
    },
    { 
        "name": "Mário Edésio Araújo Melo", "birth": "06/05", "wedding": None, "init": "27/10", "job": "Militar Reformado", "city": "Dom Cavati",
        "family": { "wife": None, "children": [], "parents": ["Edesio Ribeiro Melo", "Alfredina Pereira de Melo"] }
    },
    { 
        "name": "Marcondes Vanderlei Fonseca Ribeiro", "birth": "20/04", "wedding": "03/03", "init": "30/03", "job": "Administrador", "city": "Ataléia",
        "family": { "wife": "Cássia Rodrigues Martins Ribeiro", "children": ["Luana Martins Ribeiro"], "parents": ["Paulo Viana Ribeiro", "Maria do Perpétuo Socorro F. Ribeiro"] }
    },
    { 
        "name": "José Eustáquio de Faria Júnior", "birth": "20/07", "wedding": "23/05", "init": "13/12", "job": "Engenheiro Civil", "city": "Belo Horizonte",
        "family": { "wife": "Patrícia Abreu Falcão Faria", "children": ["Livia Falcao de Faria", "Gabriel Falcao de Faria", "Manuela Falcão de faria"], "parents": ["José Eustáquio de Faria", "Sílvia de Fátima Faria"] }
    },
    { 
        "name": "José Eustaquio de Faria", "birth": "20/03", "wedding": "28/02", "init": "14/08", "job": "Engenheiro Civil", "city": "Abaeté",
        "family": { "wife": "Silvia de Fatima Faria", "children": [], "parents": ["João Eduardo de Faria"] }
    },
    { 
        "name": "Ivo Lourenço de Morais", "birth": "01/06", "wedding": None, "init": "27/10", "job": "Aposentado", "city": "São Francisco do Glória",
        "family": { "wife": "Terezinha Leocadia Reis de Morais", "children": [], "parents": ["Nestor Lourenço Borges", "Maria de Lourdes de Morais"] }
    },
    { 
        "name": "Idalino Pereira Silva", "birth": "13/11", "wedding": "09/08", "init": "26/04", "job": "Servidor Público", "city": "Teófilo Otoni",
        "family": { "wife": "Alyria Dâmaris Desiree Barbosa Fantoni Silva", "children": ["Ariadne Christiane Fantoni Silva", "Astrid Célia Fantoni Silva"], "parents": ["Sebastião dos Anjos Silva", "Benvida Rosa Pereira"] }
    },
    { 
        "name": "Hugo Ferreira de Rezende", "birth": "28/09", "wedding": None, "init": "01/03", "job": "Auxiliar de Gerência", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Hermes do Nascimento Canhas Maciel", "birth": "13/05", "wedding": None, "init": "01/04", "job": "Advogado", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Ernane José de Lima", "birth": "20/04", "wedding": None, "init": "27/03", "job": "Motorista", "city": "Várzea da Palma",
        "family": { "wife": "Maria Felisbina", "children": [], "parents": ["Mariano José de Lima", "Maria Rodrigues Lima"] }
    },
    { 
        "name": "Dante Carvalho Rodrigues", "birth": "26/01", "wedding": None, "init": "10/08", "job": "Bombeiro Militar", "city": "Belo Horizonte",
        "family": { "wife": "Silmara A. P. Tavares Rodrigues", "children": ["João Vitor Tavares Rodrigues"], "parents": ["Dante Rodrigues Aparecido", "Maria de Lourdes Carvalho Rodrigues"] }
    },
    { 
        "name": "Cláudio Luis Gomes", "birth": "20/08", "wedding": None, "init": "08/12", "job": "Representante Comercial", "city": "Coronel Fabriciano",
        "family": { "wife": "Vera Regina Soares Pacheco", "children": ["Gláucia Azevedo Gomes", "Fernanda Azevedo Teixeira", "Barbara Pacheco Bonfim", "Izabela Pacheco Bonfim", "Igor Pacheco Bonfim", "Matheus Henrique Pacheco Melo", "Eduardo Antonio Pacheco Melo", "Thifany Maria Dequeiroz", "Viviane Fatima Dequeiroz", "Daniel Calebe de Queiroz"], "parents": ["Sebastião Gomes da Silva", "Nair Alvarenga da Silva"] }
    },
    { 
        "name": "Carlos Eduardo Giovanni Correa", "birth": "12/05", "wedding": "11/10", "init": "29/04", "job": "Engenheiro Civil", "city": "Ibirité",
        "family": { "wife": None, "children": ["Rafaela Luiza Soares Velasco Correa"], "parents": [] }
    },
    { 
        "name": "Amonn César Gonçalves", "birth": "17/05", "wedding": "22/09", "init": "30/05", "job": "Empresário", "city": "Belo Horizonte",
        "family": { "wife": "Geiciane Helen da Fonseca Gonçalves", "children": [], "parents": [] }
    },
    { 
        "name": "Alcirley Silva e Lopes", "birth": "08/09", "wedding": None, "init": "26/04", "job": "Vendedor", "city": "Belo Horizonte",
        "family": { "wife": None, "children": [], "parents": ["Alcides Ribeiro Lopes", "Helena Conceição da Silva Lopes"] }
    },
    { 
        "name": "Jerry Marcos dos Santos Neto", "birth": "18/03", "wedding": "30/04", "init": "05/12", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Miguel Coleta Ferreira Neto", "birth": None, "wedding": "08/07", "init": "15/12", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Marcelo Teodoro Fernandes", "birth": None, "wedding": None, "init": "12/06", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": [] }
    },
    { 
        "name": "Bruno Malagoli", "birth": "08/09", "wedding": None, "init": "18/12", "job": None, "city": None, "family": { "wife": None, "children": [], "parents": ["Maria da Conceição de Assis Malagoli"] }
    }
]

MASTER_EVENTS = [
    # JANEIRO
    { "date": "01/01", "type": "Family", "name": "Astrid Célia Fantoni Silva", "relatedTo": "Thiago Fantoni" },
    { "date": "10/01", "type": "Family", "name": "Viviane Eustáchia Martins", "relatedTo": "Paulo Henrique" },
    { "date": "26/01", "type": "Birthday", "name": "Dante Carvalho Rodrigues" },
    { "date": "20/01", "type": "City", "city": "Coronel Fabriciano" },

    # FEVEREIRO
    { "date": "09/02", "type": "Birthday", "name": "Thiago Augustus Fantoni Silva" },
    { "date": "09/02", "type": "Wedding", "name": "Sandoval Falcão Borba" },
    { "date": "19/02", "type": "Birthday", "name": "Maurilio Geraldo Fernandes Theodoro" },
    { "date": "21/02", "type": "Birthday", "name": "Maurilio Geraldo Fernandes Theodoro" },
    { "date": "23/02", "type": "Birthday", "name": "Rafael Tadeu Fernandes" },
    { "date": "28/02", "type": "Wedding", "name": "José Eustáquio de Faria" },

    # MARÇO
    { "date": "01/03", "type": "Family", "name": "Juliana Cristina de Faria Borba", "relatedTo": "Sandoval Borba" },
    { "date": "01/03", "type": "City", "city": "Dom Cavati" },
    { "date": "01/03", "type": "City", "city": "Ibirité" },
    { "date": "03/03", "type": "Wedding", "name": "Marcondes Vanderlei Fonseca Ribeiro" },
    { "date": "04/03", "type": "Family", "name": "João Vitor Tavares Rodrigues", "relatedTo": "Dante Rodrigues" },
    { "date": "16/03", "type": "Family", "name": "Patrícia Abreu Falcão Faria", "relatedTo": "José Eustáquio Jr" },
    { "date": "18/03", "type": "Birthday", "name": "Jerry Marcos dos Santos Neto" },
    { "date": "20/03", "type": "Birthday", "name": "José Eustaquio de Faria" },
    { "date": "22/03", "type": "Family", "name": "Cássia Rodrigues Martins Ribeiro", "relatedTo": "Marcondes Ribeiro" },
    { "date": "23/03", "type": "Family", "name": "Valdete Vieira de Souza Fantoni", "relatedTo": "Thiago Fantoni" },
    { "date": "27/03", "type": "Initiation", "name": "Ernane José de Lima" },
    { "date": "30/03", "type": "Initiation", "name": "Marcondes Vanderlei Fonseca Ribeiro" },

    # ABRIL
    { "date": "19/04", "type": "Family", "name": "Ana Paula Lopes de Souza", "relatedTo": "Matheus Eustáquio" },
    { "date": "20/04", "type": "Birthday", "name": "Ernane José de Lima" },
    { "date": "26/04", "type": "Initiation", "name": "Alcirley Silva e Lopes" },
    { "date": "26/04", "type": "Initiation", "name": "Idalino Pereira Silva" },
    { "date": "29/04", "type": "Initiation", "name": "Carlos Eduardo Giovanni Correa" },
    { "date": "29/04", "type": "City", "city": "Ipatinga" },
    { "date": "30/04", "type": "Wedding", "name": "Jerry Marcos dos Santos Neto" },

    # MAIO
    { "date": "06/05", "type": "Birthday", "name": "Mário Edésio Araújo Melo" },
    { "date": "07/05", "type": "Family", "name": "Lívia Falcão Faria", "relatedTo": "José Eustáquio Jr" },
    { "date": "07/05", "type": "Wedding", "name": "Thiago Henrique Batista Duarte" },
    { "date": "09/05", "type": "Initiation", "name": "Maurilio Geraldo Fernandes Theodoro" },
    { "date": "12/05", "type": "Birthday", "name": "Carlos Eduardo Giovanni Correa" },
    { "date": "13/05", "type": "Lodge", "name": "ARLS Magos do Oriente Nº 149" },
    { "date": "13/05", "type": "Birthday", "name": "Hermes do Nascimento Canhas Maciel" },
    { "date": "13/05", "type": "Family", "name": "Pedro Augusto Amaral Lopes" },
    { "date": "17/05", "type": "Birthday", "name": "Amonn César Gonçalves" },
    { "date": "17/05", "type": "Birthday", "name": "Paulo Henrique Freitas Martins" },
    { "date": "18/05", "type": "Family", "name": "Daniel Calebe de Queiroz", "relatedTo": "Cláudio Gomes" },
    { "date": "22/05", "type": "Family", "name": "Danúbia Pereira Martins Sá", "relatedTo": "Ricardo Sá" },
    { "date": "23/05", "type": "Wedding", "name": "José Eustáquio de Faria Junior" },
    { "date": "25/05", "type": "Family", "name": "Eduardo Antônio Pacheco Melo", "relatedTo": "Cláudio Gomes" },
    { "date": "30/05", "type": "Initiation", "name": "Amonn César Gonçalves" },
    { "date": "31/05", "type": "Family", "name": "Maria da Conceição de Assis Malagoli", "relatedTo": "Bruno Malagoli" },

    # JUNHO
    { "date": "01/06", "type": "Family", "name": "Gláucia Azevedo Gomes de Queiroz", "relatedTo": "Cláudio Gomes" },
    { "date": "01/06", "type": "Birthday", "name": "Ivo Lourenço de Morais" },
    { "date": "01/06", "type": "City", "city": "Divinópolis" },
    { "date": "02/06", "type": "Family", "name": "Rafaela Luiza Soares Velasco Correa", "relatedTo": "Carlos Eduardo" },
    { "date": "03/06", "type": "Birthday", "name": "Ricardo José Quaresma Sá" },
    { "date": "04/06", "type": "Family", "name": "Matheus Henrique Pacheco Melo", "relatedTo": "Cláudio Gomes" },
    { "date": "11/06", "type": "Family", "name": "Eduardo Toledo Duarte", "relatedTo": "Thiago Duarte" },
    { "date": "12/06", "type": "Initiation", "name": "Marcelo Teodoro Fernandes" },
    { "date": "14/06", "type": "Family", "name": "Ana Paula Cardoso", "relatedTo": "Ulisses Ferreira" },
    { "date": "14/06", "type": "Wedding", "name": "Thiago Augustus Fantoni Silva" },
    { "date": "16/06", "type": "Family", "name": "Geiciane Helen da Fonseca Gonçalves", "relatedTo": "Amonn Gonçalves" },
    { "date": "18/06", "type": "Family", "name": "Silvia de Fatima Faria", "relatedTo": "José Eustáquio" },
    { "date": "19/06", "type": "Family", "name": "Gustavo Lopes de Almeida" },
    { "date": "20/06", "type": "Family", "name": "Fernanda Azevedo Teixeira Gomes", "relatedTo": "Cláudio Gomes" },
    { "date": "24/06", "type": "Family", "name": "Pedro Henrique Souza Falcão", "relatedTo": "Sandoval Borba" },
    { "date": "26/06", "type": "Family", "name": "João Eduardo de Faria", "relatedTo": "José Eustáquio" },

    # JULHO
    { "date": "08/07", "type": "Wedding", "name": "Miguel Coleta Ferreira Neto" },
    { "date": "10/07", "type": "Family", "name": "Aline Bento Rodrigues" },
    { "date": "14/07", "type": "Family", "name": "Julia Amaral Lopes" },
    { "date": "20/07", "type": "Family", "name": "Gabriel Falcão Faria", "relatedTo": "José Eustáquio Jr" },
    { "date": "20/07", "type": "Birthday", "name": "José Eustáquio de Faria Júnior" },
    { "date": "27/07", "type": "Family", "name": "Elenice Claudina Silva Gonçalves" },
    { "date": "27/07", "type": "Family", "name": "Custódia Ferreira de Souza", "relatedTo": "Ulisses Ferreira" },
    { "date": "29/07", "type": "Family", "name": "Pedro Vinícius Falcão de Faria Borba", "relatedTo": "Sandoval Borba" },
    { "date": "31/07", "type": "Family", "name": "Larissa Toledo Duarte", "relatedTo": "Thiago Duarte" },

    # AGOSTO
    { "date": "04/08", "type": "Family", "name": "Ariadne Christiane Fantoni Silva", "relatedTo": "Thiago Fantoni" },
    { "date": "06/08", "type": "Family", "name": "Alyria Dâmaris Desiree Barbosa Fantoni Silva", "relatedTo": "Thiago Fantoni" },
    { "date": "10/08", "type": "Initiation", "name": "Dante Carvalho Rodrigues" },
    { "date": "11/08", "type": "Initiation", "name": "Paulo Henrique Freitas Martins" },
    { "date": "11/08", "type": "Wedding", "name": "Alyria (Esposa Idalino)", "relatedTo": "Idalino Pereira" },
    { "date": "14/08", "type": "Initiation", "name": "José Eustaquio de Faria" },
    { "date": "14/08", "type": "City", "city": "Parnaíba" },
    { "date": "20/08", "type": "Birthday", "name": "Cláudio Luis Gomes" },

    # SETEMBRO
    { "date": "07/09", "type": "Family", "name": "Manuela Falcão Faria", "relatedTo": "José Eustáquio Jr" },
    { "date": "07/09", "type": "City", "city": "Teófilo Otoni" },
    { "date": "08/09", "type": "Birthday", "name": "Alcirley Silva e Lopes" },
    { "date": "08/09", "type": "Birthday", "name": "Bruno Malagoli" },
    { "date": "19/09", "type": "Family", "name": "Luana Martins Ribeiro", "relatedTo": "Marcondes Ribeiro" },

    # NOVEMBRO
    { "date": "05/11", "type": "City", "city": "Abaeté" },
    { "date": "11/11", "type": "Initiation", "name": "Ricardo José Quaresma Sá" },
    { "date": "13/11", "type": "Birthday", "name": "Idalino Pereira Silva" },
    { "date": "25/11", "type": "Family", "name": "Barbara Pacheco Bonfim", "relatedTo": "Cláudio Gomes" },
    { "date": "28/11", "type": "Initiation", "name": "Ulisses Ferreira de Souza" },

    # DEZEMBRO
    { "date": "02/12", "type": "Birthday", "name": "Thiago Henrique Batista Duarte" },
    { "date": "04/12", "type": "Birthday", "name": "Matheus Eustáquio Gomes de Faria" },
    { "date": "05/12", "type": "Initiation", "name": "Thiago Henrique Batista Duarte" },
    { "date": "05/12", "type": "Initiation", "name": "Jerry Marcos dos Santos Neto" },
    { "date": "08/12", "type": "Initiation", "name": "Cláudio Luis Gomes" },
    { "date": "12/12", "type": "City", "city": "Belo Horizonte" },
    { "date": "12/12", "type": "City", "city": "Braúnas" },
    { "date": "12/12", "type": "City", "city": "Várzea da Palma" },
    { "date": "12/12", "type": "City", "city": "São Francisco do Glória" },
    { "date": "13/12", "type": "Initiation", "name": "José Eustáquio de Faria Júnior" },
    { "date": "13/12", "type": "Initiation", "name": "Matheus Eustáquio Gomes de Faria" },
    { "date": "15/12", "type": "Initiation", "name": "Miguel Coleta Ferreira Neto" },
    { "date": "16/12", "type": "Family", "name": "Franciane Cristina Toledo Duarte", "relatedTo": "Thiago Duarte" },
    { "date": "17/12", "type": "Initiation", "name": "Thiago Augustus Fantoni Silva" },
    { "date": "18/12", "type": "Initiation", "name": "Bruno Malagoli" },
    { "date": "21/12", "type": "Birthday", "name": "Ulisses Ferreira de Souza" },
    { "date": "30/12", "type": "Family", "name": "Thifany Maria Dequeiroz", "relatedTo": "Cláudio Gomes" },
    { "date": "30/12", "type": "City", "city": "Ataléia" },
]

PROFESSION_DATES = {
    "Contador": "22/09", "Gerente de Projetos": "06/11", "Analista de TI": "19/10",
    "Assistente Administrativo": "15/10", "Auxiliar Administrativo": "15/10",
    "Administrador": "09/09", "Bombeiro Militar": "02/07", "Eletrotécnico": "09/11",
    "Mecânico de Aeronaves": "24/05", "Estagiário de Direito": "18/08",
    "Militar Reformado": "25/08", "Servidor Público": "28/10", "Engenheiro Civil": "11/12",
    "Advogado": "11/08", "Motorista": "25/07", "Representante Comercial": "01/10",
    "Empresário": "05/10", "Vendedor": "01/10"
}

# --- FUNÇÕES ---

def generate_templates(evt):
    name = evt.get('name', '')
    city = evt.get('city', '')
    job = evt.get('job', '')
    
    templates = []
    
    if evt['type'] == 'Birthday':
        templates = [
            f"Parabéns, Ir. {name}! Que o GADU ilumine seus caminhos com muita saúde, paz e sabedoria. Feliz aniversário!",
            f"Hoje celebramos a vida do Ir. {name}. Muita luz, prosperidade e um novo ciclo repleto de realizações. TFA!",
            f"Grande abraço e feliz aniversário, Ir. {name}! Que a alegria deste dia se estenda por todo o ano.",
            f"Nossas homenagens ao Ir. {name} nesta data querida. Que a vida continue lhe sorrindo com fraternidade e amor.",
            f"Feliz aniversário, meu Irmão {name}! Que tenhas um dia fantástico cercado de carinho e bençãos."
        ]
    elif evt['type'] == 'Family':
        templates = [
            f"Parabéns a {name} pelo aniversário! Desejamos muita saúde e alegrias junto à família.",
            f"Hoje é dia de festa para {name}! Que o GADU abençoe este novo ano de vida com muitas felicidades.",
            f"Felicitações a {name} nesta data especial. Que seja um dia repleto de amor e celebração em família.",
            f"Enviamos nosso carinho e votos de feliz aniversário para {name}. Tudo de bom!",
            f"Celebramos hoje o aniversário de {name}. Muita luz e paz neste novo ciclo!"
        ]
    elif evt['type'] == 'Wedding':
        templates = [
            f"Parabéns ao Ir. {name} e esposa pelo aniversário de casamento! Que a união continue sendo fortalecida pelo amor.",
            f"Feliz aniversário de casamento, Ir. {name}! Que o GADU continue abençoando essa bela união e a família.",
            f"Celebrando o amor! Parabéns, Ir. {name}, pelas Bodas. Que a felicidade do casal seja eterna e inspiradora.",
            f"Hoje comemoramos a união do Ir. {name}. Que a harmonia reine sempre em seu lar. Parabéns ao casal!",
            f"Votos de felicidades infinitas ao Ir. {name} e esposa. Que o laço que os une se torne cada dia mais forte."
        ]
    elif evt['type'] == 'Initiation':
        templates = [
            f"Parabéns, Ir. {name}, pelo aniversário de Iniciação! Que a Luz recebida continue guiando seus passos.",
            f"Hoje celebramos o nascimento maçônico do Ir. {name}. Que continue lapidando sua Pedra Bruta com vigor. TFA!",
            f"Feliz aniversário de Iniciação, Ir. {name}! Uma data para recordar o compromisso assumido e renovar os votos.",
            f"Nesta data especial, saudamos o Ir. {name} pelos anos de dedicação à Ordem. Exemplo de Obreiro!",
            f"Mais um ano de Luz na vida do Ir. {name}. Parabéns pela perseverança e trabalho em prol da nossa Instituição."
        ]
    elif evt['type'] == 'Profession':
        templates = [
            f"Homenagem ao Ir. {name} pelo Dia do {job}! Obrigado por construir uma sociedade melhor com seu trabalho.",
            f"Parabéns aos profissionais de {job}, em especial ao nosso Ir. {name}. Sucesso e realizações!",
            f"Dia do {job}! Nossos cumprimentos ao Ir. {name} pela dedicação e excelência profissional.",
            f"Uma homenagem especial ao Ir. {name} nesta data dedicada ao {job}. Reconhecimento merecido!",
            f"Celebramos hoje o Dia do {job}. Parabéns, Ir. {name}, por exercer sua profissão com maestria."
        ]
    elif evt['type'] == 'City':
        templates = [
            f"Parabéns à cidade de {city} pelo seu aniversário! Que continue crescendo e acolhendo a todos.",
            f"Hoje {city} está em festa! Nossas homenagens a esta terra querida e aos irmãos que nela residem.",
            f"Aniversário de {city}! Celebramos a história desta cidade que é lar de tantos de nós.",
            f"Parabéns, {city}! Que o progresso e a harmonia sejam constantes nesta cidade.",
            f"Dia de festa em {city}! Homenagem da ARLS Magos do Oriente Nº 149."
        ]
    elif evt['type'] == 'Lodge':
        templates = [f"Parabéns ARLS Magos do Oriente Nº 149!", f"Dia de festa na Loja!", f"Viva a Magos do Oriente!"]
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
        # Usando st.image para evitar erro de imagem quebrada
        try:
            st.image('logo-magos.png', width=150)
        except:
            st.markdown("<div style='text-align:center;'>Logo não encontrado</div>", unsafe_allow_html=True)
            
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
        # Layout flex para logo e título
        c1, c2 = st.columns([0.5, 3])
        with c1:
            try:
                st.image('logo-magos.png', width=60)
            except:
                pass
        with c2:
             st.markdown("<h3 style='margin-top:15px;'>MAGOS DO ORIENTE N° 149</h3>", unsafe_allow_html=True)

    with col_h2:
        today_str = datetime.now().strftime("%d de %B de %Y")
        st.markdown(f"<div style='text-align: right; color: #888; padding-top: 20px;'>{today_str}</div>", unsafe_allow_html=True)
    
    st.divider()

    # --- SEÇÃO SUPERIOR: VERIFICADOR DE EVENTOS (Calendário) ---
    
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>VERIFICAR EVENTOS</h3>", unsafe_allow_html=True)
    
    # Container centralizado para o calendário
    col_v1, col_v2, col_v3 = st.columns([1,1,1])
    with col_v2:
        # Calendário para marcar a data
        check_date = st.date_input("Selecione a Data para Verificar", datetime.now())
        
        if st.button("VERIFICAR AGORA", use_container_width=True):
            # Lógica de Verificação
            day = check_date.strftime("%d")
            month = check_date.strftime("%m")
            date_str = f"{day}/{month}"
            
            events = []
            
            # 1. Lista Mestre
            for evt in MASTER_EVENTS:
                if evt['date'] == date_str:
                    events.append(evt)
            
            # 2. Profissões (Dinâmico)
            for bro in BROTHERS:
                if bro['job'] and PROFESSION_DATES.get(bro['job']) == date_str:
                    events.append({ 'type': 'Profession', 'name': bro['name'], 'job': bro['job'], 'date': date_str })
            
            # 3. Loja
            if date_str == "13/05":
                events.append({ 'type': 'Lodge', 'name': 'ARLS Magos do Oriente', 'date': date_str })

            # Exibição dos Resultados (Abaixo do botão)
            st.markdown("<br>", unsafe_allow_html=True)
            if not events:
                st.info(f"Nenhum evento encontrado para {date_str}.")
            else:
                st.success(f"{len(events)} evento(s) encontrado(s) para {date_str}!")
                
                # Exibir Resultados em Cards
                for evt in events:
                    msgs = generate_templates(evt)
                    
                    st.markdown(f"""
                    <div style='background-color: #222; border: 1px solid #555; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                        <div style='display:flex; justify-content:space-between; color: #aaa; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px;'>
                            <span>{evt['type']}</span>
                            <span>{evt['date']}</span>
                        </div>
                        <h3 style='margin-top: 5px; color: white; font-size: 1.2em;'>{evt.get('name') or evt.get('city')}</h3>
                        {f"<div style='color: #888; font-size: 0.8em;'>Relacionado a: {evt.get('relatedTo')}</div>" if evt.get('relatedTo') else ""}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Opções de texto para copiar
                    st.code(msgs[0], language="text")
                    with st.expander("Ver mais opções de mensagens"):
                        st.code(msgs[1], language="text")
                        st.code(msgs[2], language="text")
                        st.code(msgs[3], language="text")
                        st.code(msgs[4], language="text")

    st.divider()
    
    # --- QUADRO DE OBREIROS ---
    st.markdown("#### QUADRO DE OBREIROS")
    
    # Grid de Cards
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
                        fam_html += f"<div>👶 Filhos: {', '.join(fam['children'])}</div>"
                    if fam.get('parents'):
                        fam_html += f"<div>👴 Pais: {', '.join(fam['parents'])}</div>"
                
                # CORREÇÃO DO ERRO DO </div>: 
                # A string HTML agora está colada à margem esquerda (sem indentação)
                # para evitar que o markdown do Streamlit interprete como código.
                html_content = textwrap.dedent(f"""
<div class='brother-card'>
    <div class='card-title'>{bro['name']}</div>
    <div class='card-info'>🎂 Nasc: {bro['birth'] or '-'}</div>
    <div class='card-info'>💍 Casam: {bro['wedding'] or '-'}</div>
    <div class='card-info'>🎓 Inic: {bro['init'] or '-'}</div>
    <div class='card-info'>💼 Prof: {bro['job'] or '-'}</div>
    <div class='card-info'>📍 Cid: {bro['city'] or '-'}</div>
    <div class='card-family'>
        {fam_html}
    </div>
</div>
                """)
                st.markdown(html_content, unsafe_allow_html=True)

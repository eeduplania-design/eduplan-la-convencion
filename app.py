import io
import re
import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── 1. CONFIGURACIÓN DE PÁGINA (ESTILO PREMIUM) ──
st.set_page_config(
    page_title="EDUPLAN IA - Gestión Curricular",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ── 2. ESTILO CALIFICA-STYLE (CSS) ──
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Reset de fuentes */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo de página - Limpio como Califica */
    .stApp {
        background-color: #f8fafc;
    }

    /* Header Superior Minimalista */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: white;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }

    /* Tarjetas de Contenedor */
    .main-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }

    /* Estilo para el área de visualización de documentos */
    .doc-preview {
        background: white;
        padding: 3rem;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        min-height: 600px;
        color: #1e293b;
        line-height: 1.6;
    }

    /* Botones Estilo Califica */
    .stButton > button {
        background-color: #2563eb !important; /* Azul Califica */
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #1e40af !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    }

    /* Tabs modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 0;
        font-weight: 600;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb !important;
    }

    /* Sidebar elegante */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Inputs suaves */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* Badge de estatus */
    .status-badge {
        background: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ── 3. LÓGICA DE DATOS ──
DISTRITOS = ["Santa Ana (Quillabamba)", "Echarati", "Huayopata", "Maranura", "Ocobamba", "Quellouno", "Kimbiri", "Pichari", "Vilcabamba", "Santa Teresa", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Megantoni"]
AREAS_CNEB = {
    "Inicial": {"Personal Social": ["Construye su identidad"], "Comunicación": ["Se comunica oralmente"]},
    "Primaria": {"Matemática": ["Resuelve problemas de cantidad", "Regularidad"], "Comunicación": ["Lee diversos textos", "Escribe textos"]},
    "Secundaria": {"Matemática": ["Resuelve problemas de cantidad"], "Comunicación": ["Lee textos"], "Ciencias Sociales": ["Gestiona responsablemente"]}
}

@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    return ZhipuAI(api_key=api_key) if api_key else None

client = get_client()

def generar_word(tipo, contenido, metadatos):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    
    # Header del Doc
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(tipo.upper())
    r.bold = True
    r.font.size = Pt(14)
    
    # Tabla de datos
    table = doc.add_table(rows=0, cols=2)
    table.style = 'Table Grid'
    for k, v in metadatos.items():
        row = table.add_row().cells
        row[0].text = k
        row[1].text = str(v)
    
    doc.add_paragraph("\n" + contenido)
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ── 4. UI: HEADER PERSONALIZADO ──
st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.8rem; font-weight: 800; color: #2563eb;">EDUPLAN</span>
            <span style="background: #eff6ff; color: #2563eb; padding: 2px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700;">PRO</span>
        </div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <span class="status-badge">● IA Conectada</span>
            <div style="width: 32px; height: 32px; background: #e2e8f0; border-radius: 50%;"></div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ── 5. SIDEBAR (CONFIGURACIÓN DE CONTEXTO) ──
with st.sidebar:
    st.markdown("### ⚙️ Contexto Educativo")
    ie = st.text_input("Institución Educativa", "I.E. La Convención")
    dist = st.selectbox("Distrito", DISTRITOS)
    st.divider()
    niv = st.radio("Nivel", ["Inicial", "Primaria", "Secundaria"], index=1)
    gr = st.text_input("Grado y Sección", "4to Grado 'B'")
    ar = st.selectbox("Área Curricular", list(AREAS_CNEB[niv].keys()))

# ── 6. MAIN CONTENT: TABS TIPO CALIFICA ──
tab_anual, tab_unidad, tab_sesion = st.tabs(["📊 Planificación Anual", "📑 Unidades Didácticas", "📝 Sesiones de Clase"])

def render_editor_area(title, prompt_text, filename, meta):
    col_input, col_preview = st.columns([1, 1.5])
    
    with col_input:
        st.markdown(f'<div class="main-card">', unsafe_allow_html=True)
        st.markdown(f"#### Parámetros de {title}")
        user_input = st.text_area("Descripción o detalles específicos", placeholder="Escribe aquí los temas o retos de esta planificación...", height=200)
        
        generate = st.button(f"✨ Generar {title}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        if generate:
            with st.spinner("La IA está redactando..."):
                if client:
                    full_prompt = f"Como experto pedagogo CNEB, genera: {title}. IE: {ie}, Grado: {gr}, Área: {ar}. Detalles: {user_input}"
                    response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": full_prompt}]).choices[0].message.content
                    
                    st.session_state[f"res_{title}"] = response
                else:
                    st.error("API Key no configurada.")
        
        if f"res_{title}" in st.session_state:
            st.markdown('<div class="doc-preview">', unsafe_allow_html=True)
            st.markdown(st.session_state[f"res_{title}"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            f_word = generar_word(title, st.session_state[f"res_{title}"], meta)
            st.download_button("📥 Exportar a Word (.docx)", f_word, filename)
        else:
            st.info("Configura los parámetros a la izquierda y presiona el botón para visualizar aquí el documento.")

with tab_anual:
    render_editor_area("Planificación Anual", "Genera Plan Anual", "Plan_Anual.docx", {"IE": ie, "Grado": gr, "Área": ar})

with tab_unidad:
    render_editor_area("Unidad de Aprendizaje", "Genera Unidad", "Unidad_Aprendizaje.docx", {"IE": ie, "Grado": gr, "Área": ar})

with tab_sesion:
    render_editor_area("Sesión de Clase", "Genera Sesión", "Sesion_Clase.docx", {"IE": ie, "Grado": gr, "Área": ar})

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #94a3b8; font-size: 0.8rem; border-top: 1px solid #e2e8f0; padding-top: 20px;">
        EDUPLAN IA © 2024 | Diseñado para la Unidad de Gestión Educativa Local La Convención
    </div>
""", unsafe_allow_html=True)

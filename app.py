import io
import re
import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── 1. CONFIGURACIÓN DE PÁGINA ──
st.set_page_config(
    page_title="EDUPLAN IA - LABORATORIO PEDAGÓGICO",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded",
)

# ── 2. INTERFAZ FUTURISTA Y PEDAGÓGICA (CSS AVANZADO) ──
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Syne:wght@400;700;800&display=swap');

    /* Variables de Color */
    :root {
        --primary-glow: #00f2ff;
        --secondary-glow: #7000ff;
        --bg-pedagogico: #0a192f;
        --text-main: #e6f1ff;
    }

    /* Fondo de la Aplicación */
    .stApp {
        background: radial-gradient(circle at top right, #1d2b44, #0a192f);
        color: var(--text-main);
    }

    /* Contenedor de Tarjetas (Glassmorphism) */
    .card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
        margin-bottom: 30px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .card:hover {
        transform: translateY(-8px);
        border: 1px solid var(--primary-glow);
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
    }

    /* Títulos Impactantes */
    h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #00f2ff, #7000ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem !important;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 0px !important;
    }
    
    h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--primary-glow);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 500;
    }

    /* Botones de Acción Futuristas */
    .stButton > button {
        background: linear-gradient(45deg, #00f2ff 0%, #0066ff 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 18px 30px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        width: 100%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.5);
        color: #fff;
    }
    .stButton > button:active {
        transform: scale(0.98);
    }

    /* Estilo de la Sidebar */
    [data-testid="stSidebar"] {
        background: #020c1b;
        border-right: 1px solid rgba(0, 242, 255, 0.2);
    }
    [data-testid="stSidebar"] h3 {
        font-size: 1.2rem;
        color: #ccd6f6;
    }

    /* Tabs (Pestañas) Personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: transparent !important;
        color: #8892b0 !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary-glow) !important;
        border-bottom-color: var(--primary-glow) !important;
    }

    /* Inputs de Texto */
    input, textarea, select {
        background: rgba(0, 0, 0, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Animación de carga personalizada */
    .stSpinner > div {
        border-top-color: var(--primary-glow) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ── 3. CONSTANTES Y DATOS CNEB ──
DISTRITOS = ["Santa Ana (Quillabamba)", "Echarati", "Huayopata", "Maranura", "Ocobamba", "Quellouno", "Kimbiri", "Pichari", "Vilcabamba", "Santa Teresa", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Megantoni"]
AREAS_CNEB = {
    "Inicial": {"Personal Social": ["Construye su identidad", "Convive democráticamente"], "Comunicación": ["Se comunica oralmente", "Lee textos"]},
    "Primaria": {"Matemática": ["Resuelve problemas de cantidad", "Regularidad"], "Comunicación": ["Lee diversos textos", "Escribe textos"], "Ciencia y Tecnología": ["Explica el mundo físico", "Indaga"]},
    "Secundaria": {"Matemática": ["Resuelve problemas de cantidad"], "Comunicación": ["Lee textos"], "Ciencias Sociales": ["Gestiona responsablemente"]}
}

# ── 4. CLIENTE IA ──
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    return ZhipuAI(api_key=api_key) if api_key else None

client = get_client()

# ── 5. MOTOR DE GENERACIÓN WORD ──
def generar_word(tipo, contenido, metadatos):
    doc = Document()
    # Diseño de documento profesional
    section = doc.sections[0]
    section.top_margin = Inches(0.6)
    
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = title.add_run(tipo.upper())
    run_t.bold = True
    run_t.font.size = Pt(16)
    run_t.font.color.rgb = RGBColor(0, 102, 204)

    doc.add_heading("I. DATOS INFORMATIVOS", level=1)
    table = doc.add_table(rows=0, cols=2)
    table.style = 'Table Grid'
    for k, v in metadatos.items():
        row = table.add_row().cells
        row[0].text = k.upper()
        row[1].text = str(v)

    doc.add_heading("II. CUERPO PEDAGÓGICO", level=1)
    doc.add_paragraph(contenido)
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ── 6. HEADER ──
st.markdown("<h1>EDUPLAN IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #8892b0;'>Ecosistema de Planificación Inteligente para el Docente Moderno</p>", unsafe_allow_html=True)

# ── 7. SIDEBAR ──
with st.sidebar:
    st.markdown("### 🛠️ CONFIGURACIÓN")
    ie_nombre = st.text_input("I.E.", "I.E. La Convención")
    distrito = st.selectbox("DISTRITO", DISTRITOS)
    st.divider()
    nivel = st.radio("NIVEL", ["Inicial", "Primaria", "Secundaria"], index=1)
    area = st.selectbox("ÁREA", list(AREAS_CNEB[nivel].keys()))
    grado = st.text_input("GRADO/SECCIÓN", "3ero A")

# ── 8. CUERPO PRINCIPAL ──
tab_anual, tab_unidad, tab_sesion = st.tabs(["📅 PLAN ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

with tab_anual:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Planificación de Largo Plazo")
    cols = st.columns(2)
    pa_duracion = cols[0].text_input("DURACIÓN (AÑO)", "2024", key="pa_dur")
    pa_metodo = cols[1].selectbox("METODOLOGÍA", ["ABP", "Aprendizaje Cooperativo", "Flipped Classroom"], key="pa_met")
    pa_contexto = st.text_area("CONTEXTO DE LA I.E.", "Describe tu realidad escolar...", key="pa_cont")
    
    if st.button("🧬 SINTETIZAR PLAN ANUAL", key="btn_anual"):
        with st.spinner("Procesando estructura curricular..."):
            prompt = f"Genera un Plan Anual CNEB para {ie_nombre}. Área: {area}, Nivel: {nivel}. Contexto: {pa_contexto}."
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                meta = {"IE": ie_nombre, "Área": area, "Nivel": nivel, "Metodología": pa_metodo}
                st.download_button("📥 DESCARGAR PLAN ANUAL", generar_word("Plan Anual", res, meta), "Plan_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_unidad:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Unidad de Aprendizaje")
    u_titulo = st.text_input("NOMBRE DE LA UNIDAD", "Valoramos nuestra cultura", key="u_tit")
    u_situacion = st.text_area("SITUACIÓN SIGNIFICATIVA", key="u_situ")
    
    if st.button("🛸 DISEÑAR UNIDAD", key="btn_unidad"):
        with st.spinner("Generando arquitectura de aprendizaje..."):
            prompt = f"Genera una Unidad Didáctica CNEB. Título: {u_titulo}. Situación: {u_situacion}. Área: {area}."
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                st.download_button("📥 DESCARGAR UNIDAD", generar_word("Unidad", res, {"IE": ie_nombre, "Unidad": u_titulo}), "Unidad.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_sesion:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Sesión de Clase Inmersiva")
    s_titulo = st.text_input("TÍTULO DE SESIÓN", "Indagamos sobre...", key="s_tit")
    s_desempeño = st.text_area("DESEMPEÑO A TRABAJAR", key="s_des")
    
    if st.button("✨ MATERIALIZAR SESIÓN", key="btn_sesion"):
        with st.spinner("Creando procesos cognitivos..."):
            prompt = f"Genera Sesión de Clase. Título: {s_titulo}. Desempeño: {s_desempeño}. Grado: {grado}."
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                st.download_button("📥 DESCARGAR SESIÓN", generar_word("Sesión", res, {"IE": ie_nombre, "Sesión": s_titulo}), "Sesion.docx")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align: center; padding: 20px; opacity: 0.5;'>Sistema Desarrollado para la Excelencia Educativa en La Convención</div>", unsafe_allow_html=True)

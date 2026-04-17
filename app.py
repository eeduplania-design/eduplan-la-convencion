import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
import io

# --- CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🎨")

# --- ESTILOS INSPIRADOS EN EL DISEÑO (GRADIENTES Y MODERNIDAD) ---
st.markdown("""
    <style>
    /* Hero Section con Gradiente de la Imagen */
    .hero-container {
        background: linear-gradient(90deg, #1e3a8a 0%, #7c3aed 50%, #f43f5e 100%);
        padding: 60px 40px;
        border-radius: 0px 0px 30px 30px;
        color: white;
        text-align: left;
        margin-top: -60px;
        margin-bottom: 40px;
    }
    
    .hero-title { font-size: 3.5rem; font-weight: 800; line-height: 1; margin-bottom: 20px; }
    .hero-subtitle { font-size: 1.2rem; opacity: 0.9; max-width: 600px; }
    
    /* Tarjetas de Contenido Limpio */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding-left: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8fafc;
        border-radius: 10px 10px 0 0;
        padding: 10px 25px;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; border-bottom: 3px solid #7c3aed !important; }

    /* Formulario Estilo Card */
    .planner-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
    }
    
    /* Botón Principal Estilo CTA */
    .stButton>button {
        background: #1e3a8a;
        color: white;
        border-radius: 50px;
        padding: 15px 30px;
        font-weight: 700;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background: #7c3aed; transform: translateY(-2px); }
    </style>
""", unsafe_allow_html=True)

# --- COMPONENTE: HERO SECTION ---
st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">Planifica, Gestiona y<br>Transforma tu Aula</div>
        <div class="hero-subtitle">
            Herramienta avanzada de IA para docentes de La Convención. 
            Alineado al CNEB para Inicial, Primaria y Secundaria.
        </div>
    </div>
""", unsafe_allow_html=True)

# --- LÓGICA DE IA Y ARCHIVOS ---
def llamar_ia(tipo, prompt):
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "system", "content": "Experto en CNEB MINEDU Perú."}, 
                      {"role": "user", "content": f"Generar {tipo} con: {prompt}"}]
        )
        return response.choices[0].message.content
    except: return "⚠️ Error de conexión."

def descargar_word(titulo, contenido):
    doc = Document()
    doc.add_heading(titulo, 0)
    doc.add_paragraph(f"Docente: {LIDER}")
    doc.add_paragraph(contenido)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- SIDEBAR (CONFIGURACIÓN) ---
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    ie = st.text_input("Institución Educativa", "IE Virgen del Carmen")
    nivel = st.selectbox("Nivel", ["Inicial", "Primaria", "Secundaria"])
    areas = ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología"]
    area_sel = st.selectbox("Área Principal", areas)

# --- ESTRUCTURA DE TABS (SIN PERDER CONTENIDO) ---
tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "🚀 SESIÓN DE APRENDIZAJE"])

def seccion_planificador(tipo, key_prefix):
    st.markdown('<div class="planner-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    titulo = col1.text_input(f"Título del {tipo}", key=f"tit_{key_prefix}")
    # Solución al error DuplicateElementId: Usar keys únicas
    contexto = st.text_area("Contextualización y Retos Locales", key=f"ctx_{key_prefix}")
    
    if st.button(f"✨ Generar {tipo} Profesional", key=f"btn_{key_prefix}"):
        with st.spinner("Procesando..."):
            res = llamar_ia(tipo, f"IE: {ie}, Área: {area_sel}, Nivel: {nivel}, Título: {titulo}, Contexto: {contexto}")
            st.markdown(res)
            st.download_button("📥 Descargar Word", descargar_word(titulo, res), f"{tipo}.docx", key=f"dl_{key_prefix}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab1: seccion_planificador("Plan Anual", "anual")
with tab2: seccion_planificador("Unidad de Aprendizaje", "unidad")
with tab3:
    # Diseño especial para sesiones basado en la imagen de formularios
    st.markdown('<div class="planner-card">', unsafe_allow_html=True)
    st.subheader("🚀 Nueva Sesión de Aprendizaje")
    c1, c2 = st.columns(2)
    tema = c1.text_input("Tema Central", key="tema_s")
    duracion = c2.text_input("Duración (min)", "90", key="dur_s")
    nee = st.toggle("Adaptación de Inclusión (NEE)", key="nee_s")
    
    if st.button("GENERAR SESIÓN COMPLETA", key="btn_s"):
        res = llamar_ia("Sesión", f"Tema: {tema}, Duración: {duracion}, NEE: {nee}, Nivel: {nivel}")
        st.markdown(res)
        st.download_button("📥 Descargar", descargar_word(tema, res), "Sesion.docx", key="dl_s")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"<br><center><small>{NOMBRE_APP} | © 2026</small></center>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  EDUPLAN IA — LA CONVENCIÓN (Versión Corregida 2026)
#  Gestión: Prof. Percy Tapia
# ══════════════════════════════════════════════════════════════════

import io
import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt

# ── 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero) ──
st.set_page_config(
    page_title="EDUPLAN IA - LA CONVENCIÓN",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# ── 2. IDENTIDAD ──
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"

# ── 3. CLIENTE IA ──
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    if not api_key:
        st.error("🔑 Error: ZHIPU_KEY no encontrada.")
        return None
    return ZhipuAI(api_key=api_key)

client = get_client()

# ── 4. PROMPT MAESTRO (Sintaxis Corregida) ──
PROMPT_SISTEMA = (
    "Eres un asistente pedagógico de élite experto en el CNEB del Perú. "
    "Tu objetivo es ayudar a docentes de La Convención, Cusco, a planificar con excelencia.\n\n"
    "REGLAS DE ORO:\n"
    "1. Usa TABLAS para la secuencia didáctica.\n"
    "2. Incluye Competencias, Capacidades, Desempeños y Criterios.\n"
    "3. Contextualiza con elementos de Cusco (café, cacao, cultura local).\n"
    "4. Tono: Profesional y técnicamente preciso."
)

# ── 5. ESTILOS CSS ──
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Sora', sans-serif !important; }
    .main { background-color: #f8fafc; }
    .bloque-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; border-radius: 8px; font-weight: 700; border: none; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ── 6. HERO HEADER ──
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); 
                padding: 3rem; border-radius: 1.5rem; text-align: center; color: white; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2.5rem; margin: 0;">🏛️ {NOMBRE_APP}</h1>
        <p style="opacity: 0.8; font-size: 1.1rem;">Gestión: {LIDER} | CNEB 2026</p>
    </div>
""", unsafe_allow_html=True)

# ── 7. FUNCIONES LOGICAS ──
def generar_word(titulo, contenido, datos):
    doc = Document()
    doc.add_heading(titulo, level=0).alignment = 1
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    info = [("I.E.", datos['ie']), ("Docente", LIDER), ("Grado", datos['grado']), ("Área", datos['area'])]
    for i, (k, v) in enumerate(info):
        table.cell(i, 0).text = k
        table.cell(i, 1).text = str(v)
    doc.add_paragraph("\n" + contenido)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def llamar_ia(tipo, detalles):
    if not client: return "⚠️ Error de conexión."
    try:
        res = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Genera una {tipo} con estos datos: {detalles}"}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ── 8. SIDEBAR ──
with st.sidebar:
    st.header("⚙️ Configuración")
    ie_nombre = st.text_input("I.E.", "IE La Convención", key="ie_input")
    nivel = st.selectbox("Nivel", ["Primaria", "Secundaria"], key="nivel_select")
    grado_sel = st.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"], key="grado_select")
    area_sel = st.selectbox("Área", ["Matemática", "Comunicación", "CyT", "Personal Social"], key="area_select")

# ── 9. TABS (Corregido DuplicateElementId) ──
t1, t2, t3 = st.tabs(["📅 ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

def render_form(tipo, btn_text, area_key):
    st.markdown('<div class="bloque-card">', unsafe_allow_html=True)
    st.subheader(f"Generar {tipo}")
    # Uso de keys únicas para evitar DuplicateElementId
    user_info = st.text_area("Detalles del tema o contexto:", key=f"text_{area_key}")
    if st.button(btn_text, key=f"btn_{area_key}"):
        if user_info:
            with st.spinner("Redactando..."):
                res = llamar_ia(tipo, f"{area_sel} - {grado_sel}: {user_info}")
                st.markdown(res)
                file = generar_word(tipo, res, {"ie": ie_nombre, "grado": grado_sel, "area": area_sel, "nivel": nivel})
                st.download_button("📥 Descargar Word", file, f"{tipo}.docx", key=f"dl_{area_key}")
        else:
            st.warning("Escribe algo primero.")
    st.markdown('</div>', unsafe_allow_html=True)

with t1: render_form("Programación Anual", "Generar Plan", "anual")
with t2: render_form("Unidad Didáctica", "Generar Unidad", "unidad")
with t3: render_form("Sesión de Aprendizaje", "Generar Sesión", "sesion")

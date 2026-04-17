mport io
import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt

# ── 1. CONFIGURACIÓN DE PÁGINA ──
st.set_page_config(
    page_title="EDUPLAN IA - LA CONVENCIÓN",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# ── 2. CONSTANTES E IDENTIDAD ──
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"

# Diccionario de Competencias por Área (CNEB)
COMPETENCIAS_POR_AREA = {
    "Matemática": [
        "Resuelve problemas de cantidad",
        "Resuelve problemas de regularidad, equivalencia y cambio",
        "Resuelve problemas de gestión de datos e incertidumbre",
        "Resuelve problemas de forma, movimiento y localización"
    ],
    "Comunicación": [
        "Se comunica oralmente en su lengua materna",
        "Lee diversos tipos de textos escritos en su lengua materna",
        "Escribe diversos tipos de textos en su lengua materna"
    ],
    "CyT": [
        "Indaga mediante métodos científicos para construir sus conocimientos",
        "Explica el mundo físico basándose en conocimientos sobre los seres vivos, materia y energía, biodiversidad, Tierra y universo",
        "Diseña y construye soluciones tecnológicas para resolver problemas de su entorno"
    ],
    "Personal Social": [
        "Construye su identidad",
        "Convive y participa democráticamente en la búsqueda del bien común",
        "Interpreta críticamente fuentes diversas",
        "Gestiona responsablemente el espacio y el ambiente",
        "Gestiona responsablemente los recursos económicos"
    ]
}

ENFOQUES_TRANSVERSALES = [
    "Enfoque de Derechos", "Enfoque Inclusivo o de Atención a la diversidad", 
    "Enfoque Intercultural", "Enfoque Igualdad de Género", 
    "Enfoque Ambiental", "Enfoque Orientación al bien común", 
    "Enfoque Búsqueda de la Excelencia"
]

SITUACIONES_CONTEXTO = [
    "Cosecha de Café y Cacao en la provincia",
    "Cuidado de la biodiversidad en ceja de selva",
    "Fenómenos naturales (lluvias e inundaciones)",
    "Identidad cultural y festividades locales",
    "Salud y alimentación nutritiva regional",
    "Uso responsable de la tecnología en el aula"
]

# ── 3. CLIENTE IA ──
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    if not api_key:
        return None
    return ZhipuAI(api_key=api_key)

client = get_client()

# ── 4. PROMPT MAESTRO ──
PROMPT_SISTEMA = (
    "Eres un asistente pedagógico de élite experto en el CNEB del Perú y el Currículo Regional de Cusco. "
    "Tu objetivo es ayudar a docentes de La Convención a planificar con precisión técnica.\n\n"
    "ESTRUCTURA OBLIGATORIA:\n"
    "1. Usa TABLAS detalladas para la secuencia didáctica y matrices.\n"
    "2. Incluye obligatoriamente: Competencias, Capacidades, Desempeños y Criterios de Evaluación.\n"
    "3. Contextualización: Integra el entorno de La Convención (clima, agricultura, historia local).\n"
    "4. Tono: Académico, motivador y respetuoso con la labor docente."
)

# ── 5. ESTILOS CSS ──
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Sora', sans-serif !important; }
    .main { background-color: #f1f5f9; }
    .stSelectbox, .stMultiSelect { margin-bottom: 1rem; }
    .card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%);
        color: white; border-radius: 10px; height: 3em; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ── 6. LÓGICA DE APOYO ──
def generar_word(titulo, contenido, metadatos):
    doc = Document()
    header = doc.add_heading(titulo, level=0)
    header.alignment = 1
    
    table = doc.add_table(rows=5, cols=2)
    table.style = 'Table Grid'
    data = [
        ("I.E.", metadatos['ie']),
        ("Nivel/Grado", f"{metadatos['nivel']} - {metadatos['grado']}"),
        ("Área", metadatos['area']),
        ("Enfoque", metadatos['enfoque']),
        ("Situación", metadatos['situacion'])
    ]
    for i, (label, val) in enumerate(data):
        table.cell(i, 0).text = label
        table.cell(i, 1).text = str(val)
    
    doc.add_paragraph("\n" + contenido)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def procesar_ia(tipo, prompt_user):
    if not client: return "⚠️ Error: Configura tu ZHIPU_KEY en secrets."
    try:
        res = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Genera una {tipo} con estos parámetros:\n{prompt_user}"}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ Error en la IA: {str(e)}"

# ── 7. INTERFAZ DE USUARIO (HEADER) ──
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%); 
                padding: 2.5rem; border-radius: 1.2rem; text-align: center; color: white; margin-bottom: 2rem;">
        <h1 style="color: white; margin:0;">🏛️ {NOMBRE_APP}</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">Planificación Curricular Inteligente 2026</p>
        <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem;">
            Responsable: {LIDER}
        </span>
    </div>
""", unsafe_allow_html=True)

# ── 8. SIDEBAR ──
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/teacher.png", width=80)
    st.header("Datos Generales")
    ie_nombre = st.text_input("Institución Educativa", "I.E. La Convención")
    nivel = st.radio("Nivel Educativo", ["Primaria", "Secundaria"], horizontal=True)
    grado = st.selectbox("Grado", ["1°", "2°", "3°", "4°", "5°", "6°"])
    area = st.selectbox("Área Curricular", list(COMPETENCIAS_POR_AREA.keys()))
    
    st.divider()
    st.caption("EDUPLAN IA utiliza modelos de lenguaje avanzados para asistir al docente.")

# ── 9. CUERPO PRINCIPAL (TABS) ──
tabs = st.tabs(["📅 PROG. ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

# --- TAB 1: PROGRAMACIÓN ANUAL ---
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuración de la Programación Anual")
    col1, col2 = st.columns(2)
    with col1:
        tiempo = st.selectbox("Periodo Académico", ["Trimestral", "Bimestral"], key="anual_periodo")
        situacion = st.selectbox("Situación Eje de Contexto", SITUACIONES_CONTEXTO, key="anual_sit")
    with col2:
        enfoques = st.multiselect("Enfoques Transversales", ENFOQUES_TRANSVERSALES, [ENFOQUES_TRANSVERSALES[0]], key="anual_enf")
    
    competencias = st.multiselect("Seleccione Competencias Priorizadas", COMPETENCIAS_POR_AREA[area], key="anual_comp")
    
    if st.button("🚀 Generar Plan Anual"):
        if not competencias:
            st.warning("Seleccione al menos una competencia.")
        else:
            p_user = f"Área: {area}, Grado: {grado}, Periodo: {tiempo}, Situación: {situacion}, Enfoques: {enfoques}, Competencias: {competencias}. Estructura el plan anual con metas de aprendizaje y organización de unidades."
            with st.spinner("Construyendo visión anual..."):
                res = procesar_ia("Programación Anual", p_user)
                st.markdown(res)
                f = generar_word("Programación Anual", res, {"ie": ie_nombre, "nivel": nivel, "grado": grado, "area": area, "enfoque": enfoques, "situacion": situacion})
                st.download_button("📥 Descargar Word", f, "Plan_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: UNIDAD DIDÁCTICA ---
with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Diseño de la Unidad de Aprendizaje")
    u_titulo = st.text_input("Título de la Unidad", placeholder="Ej. Valoramos la riqueza del cacao convenciano")
    col3, col4 = st.columns(2)
    with col3:
        duracion = st.text_input("Duración (semanas/sesiones)", "4 semanas")
        u_enf = st.selectbox("Enfoque Principal", ENFOQUES_TRANSVERSALES, key="uni_enf")
    with col4:
        evidencia = st.text_input("Producto/Evidencia Final", "Ej. Álbum descriptivo, Prototipo, etc.")
        u_comp = st.multiselect("Competencias de la Unidad", COMPETENCIAS_POR_AREA[area], key="uni_comp")
    
    if st.button("🎨 Generar Unidad"):
        if not u_titulo or not u_comp:
            st.warning("Complete el título y las competencias.")
        else:
            p_user = f"Título: {u_titulo}, Duración: {duracion}, Evidencia: {evidencia}, Competencias: {u_comp}, Enfoque: {u_enf}, Área: {area}. Diseña la situación significativa detallada y la secuencia de sesiones."
            with st.spinner("Diseñando unidad pedagógica..."):
                res = procesar_ia("Unidad de Aprendizaje", p_user)
                st.markdown(res)
                f = generar_word("Unidad Didáctica", res, {"ie": ie_nombre, "nivel": nivel, "grado": grado, "area": area, "enfoque": u_enf, "situacion": u_titulo})
                st.download_button("📥 Descargar Word", f, "Unidad_Aprendizaje.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: SESIÓN DE APRENDIZAJE ---
with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Desarrollo de la Sesión")
    s_titulo = st.text_input("Nombre de la Sesión", placeholder="Ej. Conocemos los procesos de fermentación del café")
    col5, col6 = st.columns(2)
    with col5:
        s_comp = st.selectbox("Competencia a trabajar", COMPETENCIAS_POR_AREA[area], key="ses_comp")
        s_proposito = st.text_area("Propósito de la sesión", placeholder="¿Qué aprenderá el estudiante hoy?")
    with col6:
        s_estrategia = st.selectbox("Metodología Sugerida", ["Aprendizaje Basado en Problemas", "Aprendizaje Basado en Proyectos", "Aula Invertida", "Gamificación", "Indagación Científica"])
        s_momentos = st.multiselect("Momentos a enfatizar", ["Inicio/Motivación", "Recojo de saberes previos", "Conflicto cognitivo", "Procesamiento de información", "Aplicación", "Cierre/Metacognición"], default=["Inicio/Motivación", "Procesamiento de información", "Cierre/Metacognición"])
    
    if st.button("✨ Generar Sesión Detallada"):
        if not s_titulo:
            st.warning("Ingrese un título para la sesión.")
        else:
            p_user = f"Sesión: {s_titulo}, Competencia: {s_comp}, Propósito: {s_proposito}, Metodología: {s_estrategia}, Momentos clave: {s_momentos}. Genera una sesión con tabla de momentos, tiempos estimados, materiales y rúbrica de evaluación."
            with st.spinner("Redactando secuencia didáctica..."):
                res = procesar_ia("Sesión de Aprendizaje", p_user)
                st.markdown(res)
                f = generar_word("Sesión de Aprendizaje", res, {"ie": ie_nombre, "nivel": nivel, "grado": grado, "area": area, "enfoque": "Variable", "situacion": s_titulo})
                st.download_button("📥 Descargar Word", f, "Sesion_Aprendizaje.docx")
    st.markdown('</div>', unsafe_allow_html=True)

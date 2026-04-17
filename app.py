import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, RGBColor
import io

# --- CONFIGURACIÓN DE IDENTIDAD Y SEGURIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="📝")

# --- PROMPT MAESTRO PROFESIONAL (INTEGRADO) ---
PROMPT_SISTEMA = """
Eres un asistente pedagógico inteligente experto en el CNEB del Perú. 
Tu misión es apoyar a docentes de EBR (Inicial, Primaria, Secundaria).
PRINCIPIOS: Claridad técnica, precisión en desempeños y motivación docente.
ESTRUCTURA: Usa siempre TABLAS para Propósitos de Aprendizaje y Secuencia Didáctica.
CONTEXTO: Incorpora la realidad de La Convención, Cusco (café, cacao, cultura local).
"""

# --- ESTILOS CSS PROFESIONALES ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 10px 10px 0 0;
        padding: 12px 25px;
        font-weight: bold;
        border: 1px solid #e0e0e0;
    }
    .stTabs [aria-selected="true"] { background-color: #1e40af !important; color: white !important; }
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 5px solid #1e40af;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4); }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA ---
def generar_word_profesional(titulo, contenido, datos):
    doc = Document()
    # Encabezado
    header = doc.add_heading(titulo, 0)
    header.alignment = 1
    
    # Cuadro de Datos Informativos
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    info = [
        ("Institución Educativa:", datos.get("ie", "---")),
        ("Docente:", LIDER),
        ("Nivel/Grado:", f"{datos.get('nivel')} - {datos.get('grado')}"),
        ("Área:", datos.get("area", "---"))
    ]
    for i, (label, val) in enumerate(info):
        table.cell(i, 0).text = label
        table.cell(i, 1).text = val

    doc.add_paragraph("\n")
    # Contenido
    doc.add_paragraph(contenido)
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def llamar_ia_pedagogica(tipo, detalles):
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Generar {tipo} CNEB detallado con estos datos: {detalles}"}
            ]
        )
        return response.choices[0].message.content
    except:
        return "⚠️ Error de conexión. Verifique su API Key o conexión a internet."

# --- INTERFAZ PRINCIPAL ---
st.markdown(f"<h1 style='text-align: center; color: #1e40af;'>🏛️ {NOMBRE_APP}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>Líder de Innovación: <b>{LIDER}</b> | Alineado al CNEB 2026</p>", unsafe_allow_html=True)

# --- SIDEBAR: DATOS GENERALES (Estructura Limpia) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=100)
    st.header("Configuración")
    ie_nombre = st.text_input("Nombre de la I.E.", "IE La Convención")
    nivel = st.selectbox("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"])
    
    if nivel == "Inicial":
        grados = ["3 años", "4 años", "5 años"]
        areas = ["Personal Social", "Psicomotriz", "Comunicación", "Castellano como segunda lengua", "Descubrimiento del mundo", "Matemática"]
    elif nivel == "Primaria":
        grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
        areas = ["Matemática", "Comunicación", "Inglés", "Personal Social", "Educación Física", "Arte y Cultura", "Ciencia y Tecnología", "Educación Religiosa", "Tutoría"]
    else:
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
        areas = ["Matemática", "Comunicación", "Inglés", "Arte y Cultura", "Ciencias Sociales", "DPCC", "Educación Física", "Educación Religiosa", "Ciencia y Tecnología", "EPT", "Tutoría"]
    
    grado_sel = st.selectbox("Grado/Sección", grados)
    area_sel = st.selectbox("Área Curricular", areas)

# --- CUERPO DE TRABAJO (TABS) ---
tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "🚀 SESIÓN DE APRENDIZAJE"])

# 1. PROGRAMACIÓN ANUAL
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Generador de Programación Anual")
    situacion = st.text_area("Situación Significativa del Año", placeholder="Ej: Fortalecemos nuestra convivencia frente a los retos del cambio climático en nuestra provincia...")
    if st.button("✨ GENERAR PLAN ANUAL"):
        with st.spinner("Diseñando Planificación a largo plazo..."):
            detalles = f"Nivel: {nivel}, Grado: {grado_sel}, Área: {area_sel}, Situación: {situacion}, IE: {ie_nombre}"
            resultado = llamar_ia_pedagogica("Programación Anual", detalles)
            st.markdown(resultado)
            st.download_button("📥 Descargar Plan Anual", generar_word_profesional("Programación Anual", resultado, {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}), "Programacion_Anual.docx")
    st.markdown("</div>", unsafe_allow_html=True)

# 2. UNIDAD DIDÁCTICA
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Generador de Unidad de Aprendizaje / Proyecto")
    titulo_u = st.text_input("Título de la Unidad", placeholder="Ej: Valoramos los productos agrícolas de nuestra zona")
    trimestre = st.selectbox("Periodo", ["I Trimestre / Bimestre", "II Trimestre / Bimestre", "III Trimestre / Bimestre", "IV Bimestre"])
    if st.button("📂 GENERAR UNIDAD"):
        with st.spinner("Estructurando Unidad Didáctica..."):
            detalles = f"Título: {titulo_u}, Periodo: {trimestre}, Área: {area_sel}, Grado: {grado_sel}, Nivel: {nivel}"
            resultado = llamar_ia_pedagogica("Unidad Didáctica", detalles)
            st.markdown(resultado)
            st.download_button("📥 Descargar Unidad", generar_word_profesional(titulo_u, resultado, {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}), "Unidad_Didactica.docx")
    st.markdown("</div>", unsafe_allow_html=True)

# 3. SESIÓN DE APRENDIZAJE
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Generador de Sesión de Aprendizaje (Estructura CNEB)")
    col1, col2 = st.columns(2)
    titulo_s = col1.text_input("Título de la Sesión", placeholder="Ej: Leemos un cuento sobre el origen del cacao")
    duracion = col2.text_input("Duración (min)", "90")
    
    enfoque = st.selectbox("Enfoque Transversal", ["Enfoque de Derechos", "Enfoque Inclusivo", "Enfoque Intercultural", "Enfoque Igualdad de Género", "Enfoque Ambiental", "Enfoque Orientación al Bien Común", "Enfoque Búsqueda de la Excelencia"])
    
    c1, c2 = st.columns(2)
    nee = c1.toggle("Inclusión (NEE)")
    metodologia = c2.selectbox("Metodología", ["Aprendizaje Basado en Proyectos (ABP)", "Aprendizaje Basado en Problemas", "Aula Invertida", "Gamificación"])

    if st.button("🚀 GENERAR SESIÓN COMPLETA"):
        if titulo_s:
            with st.spinner("Creando sesión detallada paso a paso..."):
                detalles = f"Sesión: {titulo_s}, Duración: {duracion}, Enfoque: {enfoque}, NEE: {nee}, Metodología: {metodologia}, Área: {area_sel}, Grado: {grado_sel}, Nivel: {nivel}"
                resultado = llamar_ia_pedagogica("Sesión de Aprendizaje", detalles)
                st.markdown(resultado)
                st.download_button("📥 Descargar Sesión", generar_word_profesional(titulo_s, resultado, {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}), f"Sesion_{grado_sel}.docx")
        else:
            st.error("Por favor, asigne un título a la sesión.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><hr><center><small>EduPlan IA - Innovación para el Magisterio de La Convención, Cusco © 2026</small></center>", unsafe_allow_html=True)

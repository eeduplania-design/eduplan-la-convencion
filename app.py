import io
import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

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
    "1. Usa TABLAS detalladas para la secuencia didáctica y matrices de evaluación.\n"
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

# ── 6. LÓGICA DE APOYO (MEJORADA PARA MINEDU/CNEB) ──
def generar_word(tipo, contenido, metadatos):
    doc = Document()
    
    # Estilo base
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    # Encabezado Oficial
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("“Año de la Unidad, la Paz y el Desarrollo”")
    run.italic = True
    run.font.size = Pt(10)

    title = doc.add_heading(tipo.upper(), level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph() # Espacio
    
    # Tabla de Datos Informativos (Formato MINEDU)
    doc.add_heading("I. DATOS INFORMATIVOS", level=2)
    table = doc.add_table(rows=6, cols=2)
    table.style = 'Table Grid'
    
    items = [
        ("INSTITUCIÓN EDUCATIVA", metadatos['ie']),
        ("NIVEL / GRADO / SECCIÓN", f"{metadatos['nivel']} - {metadatos['grado']}"),
        ("ÁREA CURRICULAR", metadatos['area']),
        ("DOCENTE", LIDER),
        ("ENFOQUES TRANSVERSALES", str(metadatos['enfoque'])),
        ("SITUACIÓN / TEMA", metadatos['situacion'])
    ]
    
    for i, (label, val) in enumerate(items):
        row = table.rows[i].cells
        row[0].text = label
        row[0].paragraphs[0].runs[0].bold = True
        row[1].text = str(val)

    doc.add_paragraph()
    doc.add_heading("II. DESARROLLO DE LA PLANIFICACIÓN", level=2)
    
    # Insertar el contenido de la IA
    # Nota: La IA devuelve markdown, aquí lo pegamos como texto limpio. 
    # Para formatos complejos de tabla se requeriría un parseo más avanzado.
    doc.add_paragraph(contenido)

    # Pie de página para firmas
    doc.add_paragraph("\n\n")
    signature_table = doc.add_table(rows=1, cols=2)
    signature_table.set_distance(Inches(0.5), Inches(0.5), Inches(0.5), Inches(0.5))
    
    c1 = signature_table.cell(0, 0).paragraphs[0]
    c1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c1.add_run("__________________________\nDocente de Aula")
    
    c2 = signature_table.cell(0, 1).paragraphs[0]
    c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c2.add_run("__________________________\nDirector / V°B°")

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

# ── 7. INTERFAZ DE USUARIO ──
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%); 
                padding: 2.5rem; border-radius: 1.2rem; text-align: center; color: white; margin-bottom: 2rem;">
        <h1 style="color: white; margin:0;">🏛️ {NOMBRE_APP}</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">Planificación Curricular Inteligente 2026</p>
    </div>
""", unsafe_allow_html=True)

# ── 8. SIDEBAR ──
with st.sidebar:
    st.header("Datos Generales")
    ie_nombre = st.text_input("Institución Educativa", "I.E. La Convención")
    nivel = st.radio("Nivel Educativo", ["Primaria", "Secundaria"], horizontal=True)
    grado = st.selectbox("Grado", ["1°", "2°", "3°", "4°", "5°", "6°"])
    area = st.selectbox("Área Curricular", list(COMPETENCIAS_POR_AREA.keys()))
    st.divider()
    st.caption(f"Gestión: {LIDER}")

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
                f = generar_word("Programación Anual", res, {"ie": ie_nombre, "nivel": nivel, "grado": grado, "area": area, "enfoque": ", ".join(enfoques), "situacion": situacion})
                st.download_button("📥 Descargar Word Oficial", f, "Plan_Anual.docx")
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
                f = generar_word("Unidad de Aprendizaje", res, {"ie": ie_nombre, "nivel": nivel, "grado": grado, "area": area, "enfoque": u_enf, "situacion": u_titulo})
                st.download_button("📥 Descargar Word Oficial", f, "Unidad_Aprendizaje.docx")
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
                f = generar_word("Sesión de Aprendizaje", res, {"ie": ie_nombre, "nivel": nivel, "grado": grado, "area": area, "enfoque": "Transversal", "situacion": s_titulo})
                st.download_button("📥 Descargar Word Oficial", f, "Sesion_Aprendizaje.docx")
    st.markdown('</div>', unsafe_allow_html=True)

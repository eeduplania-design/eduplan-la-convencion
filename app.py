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

# ── 2. CONSTANTES Y DATOS CNEB ──
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"

# Distritos de la Provincia de La Convención
DISTRITOS_LA_CONVENCION = [
    "Santa Ana (Quillabamba)", "Echarati", "Huayopata", "Maranura", 
    "Ocobamba", "Quellouno", "Kimbiri", "Pichari", "Vilcabamba", 
    "Santa Teresa", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Megantoni"
]

# Áreas y Competencias según CNEB
AREAS_CNEB = {
    "Inicial": {
        "Personal Social": ["Construye su identidad", "Convive y participa democráticamente"],
        "Psicomotriz": ["Se desenvuelve de manera autónoma a través de su motricidad"],
        "Comunicación": ["Se comunica oralmente", "Lee diversos tipos de textos", "Escribe diversos tipos de textos", "Crea proyectos desde los lenguajes artísticos"],
        "Castellano como segunda lengua": ["Se comunica oralmente en castellano"],
        "Matemática": ["Resuelve problemas de cantidad", "Resuelve problemas de forma, movimiento y localización"],
        "Ciencia y Tecnología": ["Indaga mediante métodos científicos"]
    },
    "Primaria": {
        "Personal Social": ["Construye su identidad", "Convive y participa democráticamente", "Interpreta críticamente fuentes diversas", "Gestiona responsablemente el espacio y el ambiente", "Gestiona responsablemente los recursos económicos"],
        "Educación Física": ["Se desenvuelve de manera autónoma a través de su motricidad", "Asume una vida saludable", "Interactúa a través de sus habilidades sociomotrices"],
        "Comunicación": ["Se comunica oralmente", "Lee diversos tipos de textos", "Escribe diversos tipos de textos"],
        "Arte y Cultura": ["Aprecia de manera crítica manifestaciones artístico-culturales", "Crea proyectos desde los lenguajes artísticos"],
        "Castellano como segunda lengua": ["Se comunica oralmente", "Lee diversos tipos de textos", "Escribe diversos tipos de textos"],
        "Inglés": ["Se comunica oralmente", "Lee diversos tipos de textos", "Escribe diversos tipos de textos"],
        "Matemática": ["Resuelve problemas de cantidad", "Resuelve problemas de regularidad, equivalencia y cambio", "Resuelve problemas de forma, movimiento y localización", "Resuelve problemas de gestión de datos e incertidumbre"],
        "Ciencia y Tecnología": ["Indaga mediante métodos científicos", "Explica el mundo físico", "Diseña y construye soluciones tecnológicas"],
        "Educación Religiosa": ["Construye su identidad como persona humana amada por Dios", "Asume la experiencia del encuentro personal y comunitario con Dios"],
        "Competencias Transversales": ["Se desenvuelve en entornos virtuales generados por las TIC", "Gestiona su aprendizaje de manera autónoma"]
    },
    "Secundaria": {
        "Desarrollo Personal, Ciudadanía y Cívica": ["Construye su identidad", "Convive y participa democráticamente"],
        "Ciencias Sociales": ["Interpreta críticamente fuentes diversas", "Gestiona responsablemente el espacio y el ambiente", "Gestiona responsablemente los recursos económicos"],
        "Educación Física": ["Se desenvuelve de manera autónoma", "Asume una vida saludable", "Interactúa a través de sus habilidades sociomotrices"],
        "Comunicación": ["Se comunica oralmente", "Lee diversos tipos de textos", "Escribe diversos tipos de textos"],
        "Arte y Cultura": ["Aprecia de manera crítica", "Crea proyectos"],
        "Inglés": ["Se comunica oralmente", "Lee diversos tipos de textos", "Escribe diversos tipos de textos"],
        "Matemática": ["Resuelve problemas de cantidad", "Resuelve problemas de regularidad, equivalencia y cambio", "Resuelve problemas de forma, movimiento y localización", "Resuelve problemas de gestión de datos e incertidumbre"],
        "Ciencia y Tecnología": ["Indaga mediante métodos científicos", "Explica el mundo físico", "Diseña y construye soluciones tecnológicas"],
        "Educación Religiosa": ["Construye su identidad", "Asume la experiencia del encuentro"],
        "Educación para el Trabajo": ["Gestiona proyectos de emprendimiento económico o social"],
        "Competencias Transversales": ["Se desenvuelve en TIC", "Gestiona su aprendizaje"]
    }
}

ENFOQUES_TRANSVERSALES = [
    "Enfoque de Derechos", "Enfoque Inclusivo o de Atención a la diversidad", 
    "Enfoque Intercultural", "Enfoque Igualdad de Género", 
    "Enfoque Ambiental", "Enfoque Orientación al bien común", 
    "Enfoque Búsqueda de la Excelencia"
]

SITUACIONES_CONTEXTO = [
    "Cosecha de Café y Cacao en la provincia",
    "Turismo vivencial en la selva convenciana",
    "Fenómenos naturales (lluvias e inundaciones)",
    "Identidad cultural y festividades locales",
    "Salud y alimentación nutritiva regional",
    "Uso responsable de la tecnología en el aula",
    "Conservación de suelos y medio ambiente"
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
    "Eres un asistente pedagógico de élite experto en el CNEB del Perú y el Currículo Regional de Cusco (PER). "
    "Tu objetivo es ayudar a docentes de la Provincia de La Convención a planificar con precisión técnica.\n\n"
    "ESTRUCTURA OBLIGATORIA:\n"
    "1. Usa TABLAS detalladas para la secuencia didáctica y matrices de evaluación.\n"
    "2. Incluye obligatoriamente: Competencias, Capacidades, Desempeños y Criterios de Evaluación por cada actividad.\n"
    "3. Contextualización Local: DEBES mencionar el distrito seleccionado y elementos de la selva convenciana.\n"
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

# ── 6. LÓGICA DE APOYO ──
def generar_word(tipo, contenido, metadatos):
    doc = Document()
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
    
    doc.add_paragraph() 
    
    # Tabla de Datos Informativos
    doc.add_heading("I. DATOS INFORMATIVOS", level=2)
    table = doc.add_table(rows=7, cols=2)
    table.style = 'Table Grid'
    
    items = [
        ("INSTITUCIÓN EDUCATIVA", metadatos['ie']),
        ("UBICACIÓN (DISTRITO)", metadatos['distrito']),
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
    doc.add_paragraph(contenido)

    # Espacio para firmas
    doc.add_paragraph("\n\n")
    signature_table = doc.add_table(rows=1, cols=2)
    p1 = signature_table.cell(0, 0).paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.add_run("__________________________\nDocente de Aula").bold = True
    
    p2 = signature_table.cell(0, 1).paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.add_run("__________________________\nDirector / V°B°").bold = True

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
        <p style="font-size: 1.2rem; opacity: 0.9;">Planificación Curricular Inteligente Quillabamba - 2026</p>
    </div>
""", unsafe_allow_html=True)

# ── 8. SIDEBAR ACTUALIZADA ──
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/school.png", width=80)
    st.header("Configuración del Centro")
    ie_nombre = st.text_input("Nombre de la I.E.", "I.E. La Convención")
    distrito_sel = st.selectbox("Distrito de Localización", DISTRITOS_LA_CONVENCION)
    
    st.divider()
    st.header("Datos Curriculares")
    nivel_sel = st.radio("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"], index=1)
    
    # Grados dinámicos según nivel
    if nivel_sel == "Inicial":
        grados_lista = ["3 años", "4 años", "5 años"]
    else:
        grados_lista = ["1°", "2°", "3°", "4°", "5°", "6°"] if nivel_sel == "Primaria" else ["1°", "2°", "3°", "4°", "5°"]
    
    grado_sel = st.selectbox("Grado", grados_lista)
    
    # Áreas dinámicas según nivel
    areas_lista = list(AREAS_CNEB[nivel_sel].keys())
    area_sel = st.selectbox("Área Curricular", areas_lista)
    
    st.divider()
    st.caption(f"Responsable Técnico: {LIDER}")

# ── 9. CUERPO PRINCIPAL (TABS) ──
tabs = st.tabs(["📅 PROG. ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

# --- TAB 1: PROGRAMACIÓN ANUAL ---
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Planificación Anual")
    col1, col2 = st.columns(2)
    with col1:
        tiempo = st.selectbox("Periodo", ["Trimestral", "Bimestral"], key="anual_periodo")
        sit_anual = st.selectbox("Situación de Contexto", SITUACIONES_CONTEXTO, key="anual_sit")
    with col2:
        enf_anual = st.multiselect("Enfoques Transversales", ENFOQUES_TRANSVERSALES, [ENFOQUES_TRANSVERSALES[0]], key="anual_enf")
    
    comp_anual = st.multiselect("Competencias Priorizadas", AREAS_CNEB[nivel_sel][area_sel], key="anual_comp")
    
    if st.button("🚀 Generar Programación Anual"):
        if not comp_anual:
            st.warning("Seleccione competencias.")
        else:
            p_user = f"Nivel: {nivel_sel}, Área: {area_sel}, Grado: {grado_sel}, Distrito: {distrito_sel}, Situación: {sit_anual}, Competencias: {comp_anual}. Elabora el cuadro de organización de unidades por periodos."
            with st.spinner("Construyendo plan anual..."):
                res = procesar_ia("Programación Anual", p_user)
                st.markdown(res)
                f = generar_word("Programación Anual", res, {"ie": ie_nombre, "distrito": distrito_sel, "nivel": nivel_sel, "grado": grado_sel, "area": area_sel, "enfoque": ", ".join(enf_anual), "situacion": sit_anual})
                st.download_button("📥 Descargar Word", f, "Plan_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: UNIDAD DIDÁCTICA ---
with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Unidad de Aprendizaje")
    u_titulo = st.text_input("Título de la Unidad", placeholder="Ej. Promovemos el consumo del cacao en Quillabamba")
    col3, col4 = st.columns(2)
    with col3:
        u_dur = st.text_input("Duración estimada", "4 semanas")
        u_enf = st.selectbox("Enfoque Principal", ENFOQUES_TRANSVERSALES, key="uni_enf")
    with col4:
        u_evid = st.text_input("Evidencia Final", "Ej. Tríptico informativo")
        u_comp = st.multiselect("Competencias", AREAS_CNEB[nivel_sel][area_sel], key="uni_comp")
    
    if st.button("🎨 Diseñar Unidad"):
        if not u_titulo or not u_comp:
            st.warning("Faltan datos obligatorios.")
        else:
            p_user = f"Título: {u_titulo}, Distrito: {distrito_sel}, Nivel: {nivel_sel}, Área: {area_sel}, Grado: {grado_sel}, Duración: {u_dur}, Competencias: {u_comp}. Redacta la situación significativa y la secuencia de sesiones."
            with st.spinner("Diseñando unidad..."):
                res = procesar_ia("Unidad de Aprendizaje", p_user)
                st.markdown(res)
                f = generar_word("Unidad de Aprendizaje", res, {"ie": ie_nombre, "distrito": distrito_sel, "nivel": nivel_sel, "grado": grado_sel, "area": area_sel, "enfoque": u_enf, "situacion": u_titulo})
                st.download_button("📥 Descargar Word", f, "Unidad.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: SESIÓN DE APRENDIZAJE ---
with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Sesión de Aprendizaje")
    s_titulo = st.text_input("Nombre de la Sesión", placeholder="Ej. Investigamos el cultivo del café en Huayopata")
    col5, col6 = st.columns(2)
    with col5:
        s_comp = st.selectbox("Competencia", AREAS_CNEB[nivel_sel][area_sel], key="ses_comp")
        s_prop = st.text_area("Propósito", placeholder="¿Qué aprenderán hoy?")
    with col6:
        s_met = st.selectbox("Estrategia", ["Aprendizaje Basado en Proyectos", "Indagación", "Juego de Roles", "Resolución de Problemas"])
        s_mom = st.multiselect("Momentos", ["Inicio", "Desarrollo", "Cierre"], default=["Inicio", "Desarrollo", "Cierre"])
    
    if st.button("✨ Generar Sesión Detallada"):
        if not s_titulo:
            st.warning("Ingrese título de sesión.")
        else:
            p_user = f"Sesión: {s_titulo}, Distrito: {distrito_sel}, Nivel: {nivel_sel}, Grado: {grado_sel}, Área: {area_sel}, Competencia: {s_comp}, Propósito: {s_prop}. Genera la tabla detallada con procesos pedagógicos y didácticos."
            with st.spinner("Redactando sesión..."):
                res = procesar_ia("Sesión de Aprendizaje", p_user)
                st.markdown(res)
                f = generar_word("Sesión de Aprendizaje", res, {"ie": ie_nombre, "distrito": distrito_sel, "nivel": nivel_sel, "grado": grado_sel, "area": area_sel, "enfoque": "Transversal", "situacion": s_titulo})
                st.download_button("📥 Descargar Word", f, "Sesion.docx")
    st.markdown('</div>', unsafe_allow_html=True)

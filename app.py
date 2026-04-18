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
    page_title="EDUPLAN IA - LA CONVENCIÓN",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# ── 2. CONSTANTES Y DATOS CNEB ──
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"

DISTRITOS_LA_CONVENCION = [
    "Santa Ana (Quillabamba)", "Echarati", "Huayopata", "Maranura", 
    "Ocobamba", "Quellouno", "Kimbiri", "Pichari", "Vilcabamba", 
    "Santa Teresa", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Megantoni"
]

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
    "Eres un asistente pedagógico de élite experto en el CNEB del Perú y el Currículo Regional de Cusco. "
    "Tu objetivo es ayudar a docentes de la Provincia de La Convención a planificar con precisión técnica.\n\n"
    "REGLAS DE FORMATO:\n"
    "1. Usa tablas de Markdown reales para la secuencia didáctica y matrices.\n"
    "2. No uses negritas exageradas dentro de las celdas.\n"
    "3. Contextualiza siempre a la selva convenciana (Quillabamba).\n"
    "4. Separa las secciones con títulos claros usando ###."
)

# ── 5. ESTILOS CSS ──
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;700&family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Sora', sans-serif !important; }
    .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .stButton > button { background: linear-gradient(90deg, #1e3a8a 0%, #2563eb 100%); color: white; border-radius: 10px; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# ── 6. LÓGICA DE APOYO (EXPORTACIÓN WORD MEJORADA) ──

def set_table_borders(table):
    tbl = table._tbl
    for cell in tbl.xpath('.//w:tc'):
        tcPr = cell.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        top = OxmlElement('w:top')
        top.set(qn('w:val'), 'single')
        top.set(qn('w:sz'), '4')
        tcBorders.append(top)
        # Repetir para los 4 lados... (python-docx simplificado abajo)
    
def generar_word(tipo, contenido, metadatos):
    doc = Document()
    
    # Configurar márgenes estrechos para mejor aprovechamiento
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    # Estilo base
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    # 1. Encabezado Centrado
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_header.add_run("“AÑO DE LA UNIDAD, LA PAZ Y EL DESARROLLO”")
    run.bold = True
    run.font.size = Pt(9)

    # 2. Título del Documento
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title.add_run(tipo.upper())
    run_title.bold = True
    run_title.font.size = Pt(14)
    run_title.font.color.rgb = RGBColor(31, 73, 125)

    # 3. Datos Informativos (Tabla Estructurada)
    doc.add_heading("I. DATOS INFORMATIVOS", level=2)
    info_table = doc.add_table(rows=0, cols=2)
    info_table.style = 'Table Grid'
    
    items = [
        ("INSTITUCIÓN EDUCATIVA", metadatos['ie']),
        ("DISTRITO / LOCALIDAD", metadatos['distrito']),
        ("NIVEL / GRADO / SECCIÓN", f"{metadatos['nivel']} - {metadatos['grado']}"),
        ("ÁREA CURRICULAR", metadatos['area']),
        ("DOCENTE", LIDER),
        ("ENFOQUES TRANSVERSALES", str(metadatos['enfoque'])),
        ("SITUACIÓN SIGNIFICATIVA", metadatos['situacion'])
    ]
    
    for label, val in items:
        row_cells = info_table.add_row().cells
        row_cells[0].text = label
        row_cells[0].paragraphs[0].runs[0].bold = True
        row_cells[1].text = str(val)

    doc.add_paragraph()
    doc.add_heading("II. PLANIFICACIÓN PEDAGÓGICA", level=2)

    # 4. Procesamiento de Contenido (Detección de Tablas)
    # Dividimos el contenido por líneas para buscar tablas de markdown
    lines = contenido.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Detectar Títulos (###)
        if line.startswith('###'):
            text = line.replace('#', '').strip()
            h = doc.add_heading(text, level=3)
            i += 1
            continue
            
        # Detectar inicio de Tabla Markdown (| Col | Col |)
        if line.startswith('|') and i + 1 < len(lines) and '-' in lines[i+1]:
            # Extraer encabezados
            headers = [h.strip() for h in line.split('|') if h.strip()]
            i += 2 # Saltar fila de separación (---)
            
            # Crear Tabla en Word
            word_table = doc.add_table(rows=1, cols=len(headers))
            word_table.style = 'Table Grid'
            hdr_cells = word_table.rows[0].cells
            for idx, h_text in enumerate(headers):
                hdr_cells[idx].text = h_text
                hdr_cells[idx].paragraphs[0].runs[0].bold = True
            
            # Agregar filas de datos
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_data = [d.strip() for d in lines[i].split('|') if d.strip()]
                if len(row_data) >= len(headers):
                    row_cells = word_table.add_row().cells
                    for idx, d_text in enumerate(row_data[:len(headers)]):
                        row_cells[idx].text = d_text
                i += 1
            doc.add_paragraph() # Espacio post tabla
        else:
            # Texto normal (limpiando asteriscos de negrita de markdown)
            if line:
                clean_text = line.replace('**', '').replace('*', '')
                doc.add_paragraph(clean_text)
            i += 1

    # 5. Firmas al final
    doc.add_paragraph("\n\n\n")
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    c1 = sig_table.cell(0, 0).paragraphs[0]
    c1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c1.add_run("__________________________\nDOCENTE DE AULA\n" + LIDER)
    
    c2 = sig_table.cell(0, 1).paragraphs[0]
    c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c2.add_run("__________________________\nDIRECTOR / V°B°\nI.E. " + metadatos['ie'])

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def procesar_ia(tipo, prompt_user):
    if not client: return "⚠️ Error: Configura tu ZHIPU_KEY."
    try:
        res = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Genera una {tipo} completa para {distrito_sel}. Parámetros: {prompt_user}"}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ── 7. INTERFAZ DE USUARIO ──
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%); padding: 2.5rem; border-radius: 1.2rem; text-align: center; color: white; margin-bottom: 2rem;">
        <h1 style="color: white; margin:0;">🏛️ {NOMBRE_APP}</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">Planificación Curricular con Formato Oficial para Quillabamba</p>
    </div>
""", unsafe_allow_html=True)

# ── 8. SIDEBAR ──
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/briefcase.png", width=60)
    st.header("Configuración IE")
    ie_nombre = st.text_input("Nombre de la I.E.", "I.E. La Convención")
    distrito_sel = st.selectbox("Distrito", DISTRITOS_LA_CONVENCION)
    st.divider()
    nivel_sel = st.radio("Nivel", ["Inicial", "Primaria", "Secundaria"], index=1)
    
    if nivel_sel == "Inicial":
        grados = ["3 años", "4 años", "5 años"]
    elif nivel_sel == "Primaria":
        grados = ["1°", "2°", "3°", "4°", "5°", "6°"]
    else:
        grados = ["1°", "2°", "3°", "4°", "5°"]
    
    grado_sel = st.selectbox("Grado", grados)
    area_sel = st.selectbox("Área", list(AREAS_CNEB[nivel_sel].keys()))
    st.caption(f"Docente: {LIDER}")

# ── 9. TABS PRINCIPALES ──
tabs = st.tabs(["📅 ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

# --- TAB SESIÓN (EJEMPLO) ---
with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Nueva Sesión de Aprendizaje")
    s_titulo = st.text_input("Título de la Sesión", "Ej. Conocemos los beneficios del café convenciano")
    s_comp = st.selectbox("Competencia", AREAS_CNEB[nivel_sel][area_sel])
    s_prop = st.text_area("Propósito del día")
    
    if st.button("✨ Generar y Previsualizar"):
        with st.spinner("Generando estructura profesional..."):
            p_user = f"Sesión: {s_titulo}. Competencia: {s_comp}. Propósito: {s_prop}. Usa tablas para los momentos."
            res = procesar_ia("Sesión de Aprendizaje", p_user)
            st.markdown(res)
            
            # Preparar metadatos para el Word
            meta = {
                "ie": ie_nombre, "distrito": distrito_sel, "nivel": nivel_sel, 
                "grado": grado_sel, "area": area_sel, "enfoque": "Ambiental / Intercultural", 
                "situacion": s_titulo
            }
            f = generar_word("Sesión de Aprendizaje", res, meta)
            st.download_button("📥 DESCARGAR WORD LISTO PARA IMPRIMIR", f, f"Sesion_{s_titulo}.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB UNIDAD ---
with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Unidad de Aprendizaje")
    u_titulo = st.text_input("Nombre de la Unidad")
    u_comp = st.multiselect("Competencias", AREAS_CNEB[nivel_sel][area_sel])
    
    if st.button("🚀 Crear Unidad Completa"):
        p_user = f"Unidad: {u_titulo}. Competencias: {u_comp}. Distrito: {distrito_sel}. Incluye cuadro de sesiones."
        res = procesar_ia("Unidad de Aprendizaje", p_user)
        st.markdown(res)
        meta = {"ie": ie_nombre, "distrito": distrito_sel, "nivel": nivel_sel, "grado": grado_sel, "area": area_sel, "enfoque": "Varios", "situacion": u_titulo}
        f = generar_word("Unidad de Aprendizaje", res, meta)
        st.download_button("📥 Descargar Unidad en Word", f, "Unidad_Aprendizaje.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB ANUAL ---
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Programación Anual")
    sit_anual = st.selectbox("Contexto Eje", SITUACIONES_CONTEXTO)
    
    if st.button("📅 Generar Plan Anual"):
        p_user = f"Programación Anual. Área: {area_sel}. Contexto: {sit_anual}. Distrito: {distrito_sel}. Organiza en 4 unidades."
        res = procesar_ia("Programación Anual", p_user)
        st.markdown(res)
        meta = {"ie": ie_nombre, "distrito": distrito_sel, "nivel": nivel_sel, "grado": grado_sel, "area": area_sel, "enfoque": "CNEB", "situacion": sit_anual}
        f = generar_word("Programación Anual", res, meta)
        st.download_button("📥 Descargar Plan Anual", f, "Programacion_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

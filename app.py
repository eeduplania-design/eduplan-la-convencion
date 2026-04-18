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
    "Enfoque de Derechos", "Enfoque Inclusivo", "Enfoque Intercultural", 
    "Enfoque Igualdad de Género", "Enfoque Ambiental", 
    "Enfoque Orientación al bien común", "Enfoque Búsqueda de la Excelencia"
]

ESTRATEGIAS_METODOLOGICAS = [
    "Aprendizaje Basado en Proyectos (ABP)", "Aprendizaje Basado en Problemas", 
    "Aula Invertida (Flipped Classroom)", "Gamificación", 
    "Aprendizaje Cooperativo", "Pensamiento de Diseño (Design Thinking)"
]

PRODUCTOS_ESPERADOS = [
    "Portafolio de evidencias", "Prototipo tecnológico", "Ensayo argumentativo",
    "Infografía de síntesis", "Maqueta o modelo", "Podcast educativo",
    "Campaña de sensibilización", "Informe de indagación"
]

# ── 3. CLIENTE IA ──
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    if not api_key: return None
    return ZhipuAI(api_key=api_key)

client = get_client()

# ── 4. LÓGICA DE EXPORTACIÓN (WORD CON FORMATO CELESTE) ──
def set_table_header_bg(cell, color_hex):
    """Aplica color de fondo a una celda (Sombreado)"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def generar_word(tipo, contenido, metadatos):
    doc = Document()
    
    # Configuración de márgenes profesionales
    section = doc.sections[0]
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    # Estilo base
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    # Lema del año
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_h = p_header.add_run("“AÑO DE LA UNIDAD, LA PAZ Y EL DESARROLLO”")
    run_h.italic = True
    run_h.font.size = Pt(9)

    # Título Principal
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = title.add_run(tipo.upper())
    run_t.bold = True
    run_t.font.size = Pt(14)
    run_t.font.color.rgb = RGBColor(30, 58, 138) # Azul Oscuro

    # I. Datos Informativos
    doc.add_heading("I. DATOS INFORMATIVOS", level=1)
    table_info = doc.add_table(rows=0, cols=2)
    table_info.style = 'Table Grid'
    
    for key, value in metadatos.items():
        row = table_info.add_row().cells
        row[0].text = key.upper().replace("_", " ")
        set_table_header_bg(row[0], "BDE5F2") # Celeste Claro
        row[0].paragraphs[0].runs[0].bold = True
        row[1].text = str(value)

    doc.add_paragraph()
    doc.add_heading("II. PLANIFICACIÓN CURRICULAR", level=1)

    # Procesamiento de Contenido (Tablas Markdown -> Tablas Word)
    lines = contenido.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        if line.startswith('###'):
            doc.add_heading(line.replace('#', '').strip(), level=2)
            i += 1
        elif line.startswith('|') and i+1 < len(lines) and '-' in lines[i+1]:
            # Extracción de encabezados
            headers = [h.strip() for h in line.split('|') if h.strip()]
            i += 2 # Saltamos la línea de separación |---|
            
            word_table = doc.add_table(rows=1, cols=len(headers))
            word_table.style = 'Table Grid'
            
            # Formatear encabezados de la tabla con Celeste
            for idx, h_text in enumerate(headers):
                cell = word_table.rows[0].cells[idx]
                cell.text = h_text
                set_table_header_bg(cell, "BDE5F2") # Celeste Claro CNEB
                run = cell.paragraphs[0].runs[0]
                run.bold = True
                run.font.size = Pt(9)
            
            # Llenar datos de la tabla
            while i < len(lines) and lines[i].strip().startswith('|'):
                data = [d.strip() for d in lines[i].split('|') if d.strip()]
                if len(data) >= len(headers):
                    row_cells = word_table.add_row().cells
                    for idx, d_text in enumerate(data[:len(headers)]):
                        row_cells[idx].text = d_text
                        row_cells[idx].paragraphs[0].font.size = Pt(9)
                i += 1
            doc.add_paragraph()
        else:
            # Párrafos normales
            p = doc.add_paragraph(line.replace('**', '').replace('*', ''))
            i += 1

    # Firmas
    doc.add_paragraph("\n\n")
    sig_table = doc.add_table(rows=1, cols=2)
    c1 = sig_table.cell(0, 0).paragraphs[0]
    c1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c1.add_run("__________________________\nDOCENTE DE AULA\n" + LIDER)
    
    c2 = sig_table.cell(0, 1).paragraphs[0]
    c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c2.add_run("__________________________\nDIRECTOR / V°B°")

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ── 5. ESTILOS CSS STREAMLIT ──
st.markdown("""
    <style>
    .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .stButton > button { background: #1e3a8a; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3em; }
    h1, h2, h3 { color: #1e3a8a; }
    </style>
""", unsafe_allow_html=True)

# ── 6. INTERFAZ Y SIDEBAR ──
st.title("🏛️ EDUPLAN IA - LA CONVENCIÓN")
st.caption("Planificación Curricular con Formato Oficial CNEB Perú - Tablas Celeste Claro")

with st.sidebar:
    st.header("Datos Generales")
    ie_nombre = st.text_input("Institución Educativa", "I.E. La Convención")
    distrito_sel = st.selectbox("Distrito", DISTRITOS_LA_CONVENCION)
    st.divider()
    nivel_sel = st.radio("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"], index=1)
    
    if nivel_sel == "Inicial": grados = ["3 años", "4 años", "5 años"]
    elif nivel_sel == "Primaria": grados = ["1°", "2°", "3°", "4°", "5°", "6°"]
    else: grados = ["1°", "2°", "3°", "4°", "5°"]
    
    grado_sel = st.selectbox("Grado", grados)
    area_sel = st.selectbox("Área Curricular", list(AREAS_CNEB[nivel_sel].keys()))
    st.divider()
    st.info(f"Docente: {LIDER}")

# ── 7. TABS ──
tab_anual, tab_unidad, tab_sesion = st.tabs(["📅 PROG. ANUAL", "📂 UNIDAD DIDÁCTICA", "🚀 SESIÓN"])

# --- SECCIÓN 1: PROGRAMACIÓN ANUAL ---
with tab_anual:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Planificación Curricular Anual")
    
    col1, col2 = st.columns(2)
    with col1:
        pa_ciclo = st.selectbox("Ciclo", ["II", "III", "IV", "V", "VI", "VII"])
        pa_periodo = st.selectbox("Organización", ["Bimestral", "Trimestral"], key="pa_per")
        pa_horas = st.number_input("Horas Semanales", 1, 10, 4)
    
    with col2:
        pa_comp = st.multiselect("Competencias", AREAS_CNEB[nivel_sel][area_sel])
        pa_trans = st.multiselect("Enfoques", ENFOQUES_TRANSVERSALES)
        pa_metod = st.multiselect("Metodologías", ESTRATEGIAS_METODOLOGICAS)

    pa_unidades = st.text_area("Proyección de Unidades (Título y propósito breve)", placeholder="U1: ...\nU2: ...")

    if st.button("🚀 Generar Programación Anual"):
        with st.spinner("Generando documento oficial..."):
            prompt = f"""
            Genera una PROGRAMACIÓN ANUAL CNEB completa para:
            - IE: {ie_nombre}, Grado: {grado_sel}, Área: {area_sel}, Ciclo: {pa_ciclo}.
            - Metodología: {pa_metod}. Enfoques: {pa_trans}.
            
            ESTRUCTURA OBLIGATORIA (USA TABLAS MARKDOWN):
            1. Tabla de Propósitos de Aprendizaje (Competencias, Capacidades, Criterios).
            2. Tabla de Organización de Unidades (Título, duración, competencias priorizadas).
            3. Estrategias metodológicas y Recursos.
            4. Evaluación (Diagnóstica, Formativa, Sumativa).
            """
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                meta = {"IE": ie_nombre, "Grado": grado_sel, "Área": area_sel, "Ciclo": pa_ciclo, "Docente": LIDER}
                f = generar_word("Programación Anual", res, meta)
                st.download_button("📥 Descargar Programación Anual", f, "Prog_Anual_Celeste.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECCIÓN 2: UNIDAD DIDÁCTICA ---
with tab_unidad:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Unidad de Aprendizaje")
    
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        u_titulo = st.text_input("Título de la Unidad", placeholder="Ej. Valoremos nuestra biodiversidad")
        u_duracion = st.text_input("Duración", "4 semanas")
        u_producto = st.selectbox("Producto Principal", PRODUCTOS_ESPERADOS)
        
    with u_col2:
        u_sit = st.text_area("Situación Significativa", placeholder="Descripción del reto...")
        u_comp = st.multiselect("Competencias de la Unidad", AREAS_CNEB[nivel_sel][area_sel])

    u_sesiones = st.text_area("Secuencia de Sesiones", "Sesión 1: ...\nSesión 2: ...")

    if st.button("📂 Generar Unidad Didáctica"):
        with st.spinner("Diseñando unidad pedagógica..."):
            prompt = f"""
            Genera una UNIDAD DE APRENDIZAJE CNEB:
            - Título: {u_titulo} | Duración: {u_duracion}
            - Situación Significativa detallada.
            - Tabla de Propósitos (Competencias, Capacidades, Desempeños, Criterios de evaluación).
            - Producto: {u_producto}.
            - Tabla de Secuencia de Sesiones basadas en: {u_sesiones}.
            - Materiales y Recursos.
            """
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                meta = {"IE": ie_nombre, "Unidad": u_titulo, "Grado": grado_sel, "Área": area_sel}
                f = generar_word("Unidad Didáctica", res, meta)
                st.download_button("📥 Descargar Unidad Didáctica", f, "Unidad_Celeste.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECCIÓN 3: SESIÓN DE APRENDIZAJE ---
with tab_sesion:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Sesión de Aprendizaje")
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        s_titulo = st.text_input("Título de la Sesión", placeholder="Ej. Resolvemos problemas de cantidad")
        s_duracion = st.selectbox("Duración", [45, 90, 135], index=1)
        s_fecha = st.date_input("Fecha")
    
    with s_col2:
        s_comp = st.selectbox("Competencia", AREAS_CNEB[nivel_sel][area_sel])
        s_metodo = st.selectbox("Estrategia", ESTRATEGIAS_METODOLOGICAS)

    if st.button("✨ Generar Sesión Detallada"):
        with st.spinner("Redactando procesos pedagógicos..."):
            prompt = f"""
            Genera una SESIÓN DE APRENDIZAJE profesional:
            - Título: {s_titulo} | Área: {area_sel} | Grado: {grado_sel}
            - Tabla de Propósito de Aprendizaje (Competencia, Capacidad, Desempeño, Criterio, Evidencia, Instrumento).
            - Secuencia Didáctica (Inicio, Desarrollo, Cierre) con actividades detalladas y tiempos.
            - Evaluación formativa.
            Contexto: Provincia de La Convención.
            """
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                meta = {"IE": ie_nombre, "Sesión": s_titulo, "Área": area_sel, "Fecha": s_fecha}
                f = generar_word("Sesión de Aprendizaje", res, meta)
                st.download_button("📥 Descargar Sesión Celeste", f, "Sesion_Celeste.docx")
    st.markdown('</div>', unsafe_allow_html=True)

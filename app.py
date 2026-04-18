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
    if not api_key: return None
    return ZhipuAI(api_key=api_key)

client = get_client()

# ── 4. LÓGICA DE EXPORTACIÓN (WORD) ──
def generar_word(tipo, contenido, metadatos):
    doc = Document()
    
    # Márgenes de impresión
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)

    # Estilos
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    # Encabezado
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
    run_t.font.color.rgb = RGBColor(0, 51, 153)

    # I. Datos Informativos
    doc.add_heading("I. DATOS INFORMATIVOS", level=2)
    table_info = doc.add_table(rows=0, cols=2)
    table_info.style = 'Table Grid'
    
    for key, value in metadatos.items():
        row = table_info.add_row().cells
        row[0].text = key.upper().replace("_", " ")
        row[0].paragraphs[0].runs[0].bold = True
        row[1].text = str(value)

    doc.add_paragraph()
    doc.add_heading("II. DESARROLLO DE LA PLANIFICACIÓN", level=2)

    # Procesar Contenido (Conversión de Tablas Markdown a Word)
    lines = contenido.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Títulos
        if line.startswith('###'):
            doc.add_heading(line.replace('#', '').strip(), level=3)
            i += 1
        # Detección de Tablas Markdown
        elif line.startswith('|') and i+1 < len(lines) and '-' in lines[i+1]:
            headers = [h.strip() for h in line.split('|') if h.strip()]
            i += 2
            word_table = doc.add_table(rows=1, cols=len(headers))
            word_table.style = 'Table Grid'
            # Header row
            for idx, h_text in enumerate(headers):
                word_table.rows[0].cells[idx].text = h_text
                word_table.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
            
            # Data rows
            while i < len(lines) and lines[i].strip().startswith('|'):
                data = [d.strip() for d in lines[i].split('|') if d.strip()]
                if len(data) >= len(headers):
                    row_cells = word_table.add_row().cells
                    for idx, d_text in enumerate(data[:len(headers)]):
                        row_cells[idx].text = d_text
                i += 1
            doc.add_paragraph()
        else:
            doc.add_paragraph(line.replace('**', '').replace('*', ''))
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

# ── 5. ESTILOS CSS ──
st.markdown("""
    <style>
    .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .stButton > button { background: #1e3a8a; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3em; }
    h1, h2, h3 { color: #1e3a8a; }
    </style>
""", unsafe_allow_html=True)

# ── 6. INTERFAZ Y SIDEBAR ──
st.title("🏛️ EDUPLAN IA - LA CONVENCIÓN")
st.caption("Planificación Curricular con Formato CNEB Perú - 2026")

with st.sidebar:
    st.header("Datos del Plantel")
    ie_nombre = st.text_input("I.E.", "I.E. La Convención")
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

# ── 7. CUERPO PRINCIPAL (TABS) ──
tab_anual, tab_unidad, tab_sesion = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

with tab_anual:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuración Técnica de la Programación Anual")
    
    col1, col2 = st.columns(2)
    with col1:
        p_periodo = st.selectbox("Periodo Académico", ["Trimestral", "Bimestral", "Anual"])
        p_contexto = st.selectbox("Situación de Contexto", SITUACIONES_CONTEXTO)
        p_competencias = st.multiselect("Competencias Priorizadas", AREAS_CNEB[nivel_sel][area_sel])
    with col2:
        p_enfoques = st.multiselect("Enfoques Transversales", ENFOQUES_TRANSVERSALES)
        p_estandar = st.text_area("Estándares de Aprendizaje (Ciclo)", placeholder="Describa el nivel esperado...")
        p_evidencias = st.text_input("Evidencias de Aprendizaje Eje", "Portafolios, Proyectos, Feria...")

    col3, col4 = st.columns(2)
    with col3:
        p_hitos = st.text_area("Calendario de Hitos", "Ej. Abril: Día del Café, Julio: Aniversario Provincia...")
    with col4:
        p_adapt = st.text_area("Adaptaciones / Diversificación", "Atención a NEE, Lengua Originaria, etc.")

    if st.button("🚀 Generar Programación Anual Completa"):
        if not p_competencias:
            st.warning("Debe seleccionar al menos una competencia.")
        else:
            with st.spinner("Generando plan técnico..."):
                prompt = f"""
                Genera una Programación Anual para {ie_nombre} en {distrito_sel}.
                Nivel: {nivel_sel}, Grado: {grado_sel}, Área: {area_sel}.
                Periodo: {p_periodo}. Contexto: {p_contexto}. 
                Competencias: {p_competencias}.
                Enfoques: {p_enfoques}.
                Estándar: {p_estandar}.
                Evidencias: {p_evidencias}.
                Hitos: {p_hitos}.
                Adaptaciones: {p_adapt}.
                Organiza la información en una tabla de unidades y explica los desempeños por unidad.
                """
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown(res)
                    meta = {
                        "Institución": ie_nombre, "Distrito": distrito_sel, "Área": area_sel,
                        "Nivel_Grado": f"{nivel_sel} - {grado_sel}", "Periodo": p_periodo,
                        "Contexto": p_contexto, "Docente": LIDER
                    }
                    f = generar_word("Programación Anual", res, meta)
                    st.download_button("📥 Descargar Plan Anual (Word)", f, "Programacion_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_unidad:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Diseño de Unidad de Aprendizaje")
    u_tit = st.text_input("Título de la Unidad")
    u_dur = st.text_input("Duración", "4 semanas")
    if st.button("🎨 Generar Unidad"):
        with st.spinner("Trabajando..."):
            prompt = f"Unidad: {u_tit}. Nivel: {nivel_sel}, Grado: {grado_sel}, Área: {area_sel}, Distrito: {distrito_sel}. Incluye situación significativa y cuadro de sesiones."
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                f = generar_word("Unidad de Aprendizaje", res, {"IE": ie_nombre, "Unidad": u_tit, "Area": area_sel})
                st.download_button("📥 Descargar Unidad", f, "Unidad.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_sesion:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Sesión de Aprendizaje Detallada")
    s_tit = st.text_input("Nombre de la Sesión")
    s_mom = st.multiselect("Momentos a incluir", ["Inicio", "Desarrollo", "Cierre"], default=["Inicio", "Desarrollo", "Cierre"])
    if st.button("✨ Generar Sesión"):
        with st.spinner("Generando pasos didácticos..."):
            prompt = f"Sesión: {s_tit}. Área: {area_sel}, Grado: {grado_sel}, Distrito: {distrito_sel}. Crea una tabla detallada con procesos pedagógicos y didácticos."
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                f = generar_word("Sesión de Aprendizaje", res, {"IE": ie_nombre, "Sesión": s_tit, "Área": area_sel})
                st.download_button("📥 Descargar Sesión", f, "Sesion.docx")
    st.markdown('</div>', unsafe_allow_html=True)

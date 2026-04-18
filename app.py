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

    # Procesar Contenido
    lines = contenido.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        if line.startswith('###'):
            doc.add_heading(line.replace('#', '').strip(), level=3)
            i += 1
        elif line.startswith('|') and i+1 < len(lines) and '-' in lines[i+1]:
            headers = [h.strip() for h in line.split('|') if h.strip()]
            i += 2
            word_table = doc.add_table(rows=1, cols=len(headers))
            word_table.style = 'Table Grid'
            for idx, h_text in enumerate(headers):
                word_table.rows[0].cells[idx].text = h_text
                word_table.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
            
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
st.caption("Planificación Curricular con Formato Oficial CNEB Perú - 2026")

with st.sidebar:
    st.header("Datos Generales")
    ie_nombre = st.text_input("Institución Educativa", "I.E. La Convención")
    distrito_sel = st.selectbox("Distrito / Ubicación", DISTRITOS_LA_CONVENCION)
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

with tab_anual:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuración de la Programación Anual")
    col1, col2 = st.columns(2)
    with col1:
        pa_periodo = st.selectbox("Periodo", ["Trimestral", "Bimestral", "Anual"], key="pa_periodo")
        pa_contexto = st.selectbox("Situación de Contexto", SITUACIONES_CONTEXTO, key="pa_contexto")
    with col2:
        pa_comp = st.multiselect("Competencias Priorizadas", AREAS_CNEB[nivel_sel][area_sel], key="pa_comp")
        pa_enfoques = st.multiselect("Enfoques Transversales", ENFOQUES_TRANSVERSALES, key="pa_enfoque")
    
    if st.button("🚀 Generar Plan Anual"):
        with st.spinner("Generando..."):
            prompt = f"Genera Programación Anual. IE: {ie_nombre}, Distrito: {distrito_sel}, Grado: {grado_sel}, Área: {area_sel}. Contexto: {pa_contexto}. Competencias: {pa_comp}."
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                f = generar_word("Programación Anual", res, {"IE": ie_nombre, "Área": area_sel, "Grado": grado_sel})
                st.download_button("📥 Descargar Word", f, "Prog_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_unidad:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuración de la Unidad Didáctica (CNEB)")
    
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        u_titulo = st.text_input("Título de la Unidad", placeholder="Ej. Valoramos la cosecha del cacao")
        u_duracion = st.text_input("Duración", "4 semanas (10 sesiones)")
        u_comp = st.multiselect("Competencias de la Unidad", AREAS_CNEB[nivel_sel][area_sel], key="u_comp")
    with u_col2:
        u_sit = st.text_area("Situación Significativa", placeholder="Descripción del problema o reto local...")
        u_evidencia = st.text_input("Evidencias de Aprendizaje", "Prototipo, Álbum, Informe...")
    
    st.divider()
    u_col3, u_col4 = st.columns(2)
    with u_col3:
        u_desempenos = st.text_area("Desempeños Esperados", placeholder="Indicadores concretos de logro...")
        u_recursos = st.text_input("Recursos y Materiales", "Libros MED, Fichas, Tabletas, Material local...")
    with u_col4:
        u_eval = st.selectbox("Estrategias de Evaluación", ["Rúbricas", "Listas de Cotejo", "Portafolio", "Pruebas escritas"])
        u_adapt = st.text_input("Adaptaciones / Diversificación", "Ajustes para NEE o realidad local")

    if st.button("📂 Generar Unidad Didáctica"):
        with st.spinner("Diseñando Unidad Didáctica..."):
            prompt = f"""
            Genera una UNIDAD DIDÁCTICA completa siguiendo este formato:
            - Título: {u_titulo}
            - Duración: {u_duracion}
            - Área: {area_sel}, Grado: {grado_sel}
            - Competencias y Capacidades: {u_comp}
            - Desempeños: {u_desempenos}
            - Situación Significativa: {u_sit}
            - Evaluación: {u_eval} con Evidencias: {u_evidencia}
            - Secuencia de Sesiones: Genera una tabla con 8 sesiones (Número, Título breve, Descripción).
            - Recursos: {u_recursos}
            - Adaptaciones: {u_adapt}
            Contexto: Provincia de La Convención, {distrito_sel}.
            """
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                meta_u = {
                    "IE": ie_nombre, "Unidad": u_titulo, "Área": area_sel, 
                    "Grado": grado_sel, "Duración": u_duracion, "Distrito": distrito_sel
                }
                f = generar_word("Unidad Didáctica", res, meta_u)
                st.download_button("📥 Descargar Unidad Didáctica (Word)", f, f"Unidad_{u_titulo}.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_sesion:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Sesión de Aprendizaje")
    s_titulo = st.text_input("Título de la Sesión", key="s_tit")
    if st.button("✨ Generar Sesión"):
        with st.spinner("Generando..."):
            prompt = f"Genera Sesión de Aprendizaje. Título: {s_titulo}. Nivel: {nivel_sel}, Grado: {grado_sel}, Área: {area_sel}. Incluye momentos (Inicio, Desarrollo, Cierre)."
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                st.markdown(res)
                f = generar_word("Sesión de Aprendizaje", res, {"IE": ie_nombre, "Sesión": s_titulo})
                st.download_button("📥 Descargar Sesión", f, "Sesion.docx")
    st.markdown('</div>', unsafe_allow_html=True)

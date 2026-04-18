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

# ── 4. LÓGICA DE EXPORTACIÓN (WORD CON COLOR CELESTE) ──
def set_table_header_bg(cell, color_hex):
    """Aplica color de fondo a una celda de tabla Word"""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def generar_word(tipo, contenido, metadatos):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.6), Inches(0.6)
    section.left_margin, section.right_margin = Inches(0.7), Inches(0.7)

    # Lema
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
    run_t.font.color.rgb = RGBColor(30, 58, 138)

    # I. DATOS INFORMATIVOS
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
    doc.add_heading("II. DESARROLLO PEDAGÓGICO", level=1)

    # Procesar Tablas Markdown
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
            headers = [h.strip() for h in line.split('|') if h.strip()]
            i += 2
            word_table = doc.add_table(rows=1, cols=len(headers))
            word_table.style = 'Table Grid'
            
            for idx, h_text in enumerate(headers):
                cell = word_table.rows[0].cells[idx]
                cell.text = h_text
                set_table_header_bg(cell, "BDE5F2")
                run = cell.paragraphs[0].runs[0]
                run.bold = True
                run.font.size = Pt(9)
            
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
            doc.add_paragraph(line.replace('**', '').replace('*', ''))
            i += 1

    # Firmas
    doc.add_paragraph("\n\n")
    sig_table = doc.add_table(rows=1, cols=2)
    for j in range(2):
        p = sig_table.cell(0, j).paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        text = "__________________________\nDOCENTE DE AULA" if j==0 else "__________________________\nDIRECTOR / V°B°"
        p.add_run(text + ("\n"+LIDER if j==0 else ""))

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

# ── 6. SIDEBAR ──
with st.sidebar:
    st.header("🏛️ Datos Generales")
    ie_nombre_val = st.text_input("I.E.", "I.E. La Convención")
    distrito_val = st.selectbox("Distrito", DISTRITOS_LA_CONVENCION)
    st.divider()
    nivel_val = st.radio("Nivel", ["Inicial", "Primaria", "Secundaria"], index=1)
    grados_dict = {"Inicial": ["3 años", "4 años", "5 años"], "Primaria": ["1°", "2°", "3°", "4°", "5°", "6°"], "Secundaria": ["1°", "2°", "3°", "4°", "5°"]}
    grado_val = st.selectbox("Grado", grados_dict[nivel_val])
    area_val = st.selectbox("Área", list(AREAS_CNEB[nivel_val].keys()))

# ── 7. TABS ──
tab_anual, tab_unidad, tab_sesion = st.tabs(["📅 P. ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

# SECCIÓN: PROGRAMACIÓN ANUAL
with tab_anual:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Planificación Anual")
    c1, c2 = st.columns(2)
    with c1:
        # Se capturan los valores directamente en variables, NO mediante st.session_state directo
        p_ciclo = st.selectbox("Ciclo", ["II", "III", "IV", "V", "VI", "VII"], key="k_ciclo")
        p_per = st.selectbox("Organización", ["Bimestral", "Trimestral"], key="k_per")
    with c2:
        p_trans = st.multiselect("Enfoques Transversales", ENFOQUES_TRANSVERSALES, key="k_trans")
        p_metod = st.multiselect("Metodologías", ESTRATEGIAS_METODOLOGICAS, key="k_metod")
    
    p_unidades = st.text_area("Unidades planteadas", placeholder="U1: ..., U2: ...", key="k_units")

    if st.button("🚀 Generar Programación Anual", key="b_anual"):
        if not p_unidades:
            st.warning("Ingrese las unidades.")
        else:
            with st.spinner("Generando..."):
                prompt = f"Genera Programación Anual CNEB para {ie_nombre_val}. Grado: {grado_val}, Área: {area_val}. Ciclo: {p_ciclo}. Organización: {p_per}. Unidades: {p_unidades}. Enfoques: {p_trans}. Usa tablas Markdown."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown(res)
                    f = generar_word("Programación Anual", res, {"IE": ie_nombre_val, "Grado": grado_val, "Área": area_val, "Ciclo": p_ciclo, "Docente": LIDER})
                    st.download_button("📥 Descargar Word", f, "Plan_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN: UNIDAD
with tab_unidad:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Unidad de Aprendizaje")
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        u_tit = st.text_input("Título", key="k_u_tit")
        u_dur = st.text_input("Duración", "4 semanas", key="k_u_dur")
    with u_col2:
        u_prod = st.selectbox("Producto", PRODUCTOS_ESPERADOS, key="k_u_prod")
        u_comps = st.multiselect("Competencias", AREAS_CNEB[nivel_val][area_val], key="k_u_comp")
    
    u_situ = st.text_area("Situación Significativa", key="k_u_sit")

    if st.button("📂 Generar Unidad", key="b_unidad"):
        if not u_tit or not u_situ:
            st.error("Complete Título y Situación.")
        else:
            with st.spinner("Diseñando..."):
                prompt = f"Genera Unidad de Aprendizaje CNEB. Título: {u_tit}. Situación: {u_situ}. Grado: {grado_val}, Área: {area_val}. Producto: {u_prod}. Competencias: {u_comps}. Usa tablas."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown(res)
                    f = generar_word("Unidad Didáctica", res, {"IE": ie_nombre_val, "Unidad": u_tit, "Área": area_val})
                    st.download_button("📥 Descargar Word", f, "Unidad.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN: SESIÓN
with tab_sesion:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Sesión de Aprendizaje")
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        s_tit = st.text_input("Título de Sesión", key="k_s_tit")
        s_dur = st.selectbox("Minutos", [45, 90, 135], index=1, key="k_s_dur")
    with s_col2:
        s_comp = st.selectbox("Competencia Principal", AREAS_CNEB[nivel_val][area_val], key="k_s_comp")
        s_des = st.text_area("Desempeño", key="k_s_des")

    if st.button("✨ Generar Sesión", key="b_sesion"):
        if not s_tit:
            st.warning("Asigne un título.")
        else:
            with st.spinner("Redactando..."):
                prompt = f"Genera Sesión de Aprendizaje CNEB. Título: {s_tit}. Área: {area_val}, Grado: {grado_val}. Competencia: {s_comp}. Desempeño: {s_des}. Estructura: Inicio, Desarrollo, Cierre. Usa tablas."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown(res)
                    f = generar_word("Sesión de Aprendizaje", res, {"IE": ie_nombre_val, "Sesión": s_tit, "Área": area_val})
                    st.download_button("📥 Descargar Word", f, "Sesion.docx")
    st.markdown('</div>', unsafe_allow_html=True)

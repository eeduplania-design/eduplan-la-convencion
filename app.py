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

# ── 4. FUNCIONES DE APOYO ──
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

    # Procesar Contenido
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
    st.header("🏛️ Configuración")
    ie_nombre = st.text_input("I.E.", "I.E. La Convención")
    distrito_sel = st.selectbox("Distrito", DISTRITOS_LA_CONVENCION)
    st.divider()
    nivel_sel = st.radio("Nivel", ["Inicial", "Primaria", "Secundaria"], index=1)
    
    grados_map = {"Inicial": ["3 años", "4 años", "5 años"], "Primaria": ["1°", "2°", "3°", "4°", "5°", "6°"], "Secundaria": ["1°", "2°", "3°", "4°", "5°"]}
    grado_sel = st.selectbox("Grado", grados_map[nivel_sel])
    area_sel = st.selectbox("Área", list(AREAS_CNEB[nivel_sel].keys()))

# ── 7. TABS (CON MANEJO SEGURO DE VARIABLES) ──
tab_anual, tab_unidad, tab_sesion = st.tabs(["📅 P. ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

# SECCIÓN: PROGRAMACIÓN ANUAL
with tab_anual:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Planificación Anual")
    c1, c2 = st.columns(2)
    with c1:
        # Se usan variables locales para evitar que el cambio de tab cause KeyError
        pa_ciclo = st.selectbox("Ciclo", ["II", "III", "IV", "V", "VI", "VII"], key="pa_ciclo_widget")
        pa_per = st.selectbox("Periodo", ["Bimestral", "Trimestral"], key="pa_per_widget")
    with c2:
        pa_trans = st.multiselect("Enfoques", ENFOQUES_TRANSVERSALES, key="pa_trans_widget")
        pa_metod = st.multiselect("Metodologías", ESTRATEGIAS_METODOLOGICAS, key="pa_metod_widget")
    
    pa_unidades = st.text_area("Título de Unidades", placeholder="U1: ..., U2: ...", key="pa_unidades_widget")

    if st.button("🚀 Generar Anual", key="btn_anual_gen"):
        if not pa_unidades:
            st.warning("Ingrese las unidades.")
        else:
            with st.spinner("Generando..."):
                prompt = f"Genera Programación Anual CNEB para {ie_nombre}. Grado: {grado_sel}, Área: {area_sel}. Ciclo: {pa_ciclo}. Organización: {pa_per}. Unidades: {pa_unidades}."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown(res)
                    meta = {"IE": ie_nombre, "Grado": grado_sel, "Área": area_sel, "Ciclo": pa_ciclo}
                    st.download_button("📥 Descargar Word", generar_word("Programación Anual", res, meta), "Plan_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN: UNIDAD
with tab_unidad:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Unidad de Aprendizaje")
    u_c1, u_c2 = st.columns(2)
    with u_c1:
        u_titulo = st.text_input("Título de Unidad", key="u_tit_widget")
        u_dur = st.text_input("Duración", "4 semanas", key="u_dur_widget")
    with u_c2:
        u_prod = st.selectbox("Producto", PRODUCTOS_ESPERADOS, key="u_prod_widget")
        u_comps = st.multiselect("Competencias", AREAS_CNEB[nivel_sel][area_sel], key="u_comp_widget")
    
    u_situ = st.text_area("Situación Significativa", key="u_situ_widget")

    if st.button("📂 Generar Unidad", key="btn_unidad_gen"):
        if not u_titulo:
            st.error("Ingrese un título.")
        else:
            with st.spinner("Diseñando..."):
                prompt = f"Genera Unidad de Aprendizaje CNEB. Título: {u_titulo}. Situación: {u_situ}. Producto: {u_prod}. Área: {area_sel}."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown(res)
                    meta = {"IE": ie_nombre, "Unidad": u_titulo, "Grado": grado_sel}
                    st.download_button("📥 Descargar Word", generar_word("Unidad de Aprendizaje", res, meta), "Unidad.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN: SESIÓN
with tab_sesion:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Sesión de Aprendizaje")
    s_c1, s_c2 = st.columns(2)
    with s_c1:
        s_titulo = st.text_input("Título de Sesión", key="s_tit_widget")
        s_dur = st.selectbox("Duración", [45, 90, 135], index=1, key="s_dur_widget")
    with s_c2:
        s_comp = st.selectbox("Competencia", AREAS_CNEB[nivel_sel][area_sel], key="s_comp_widget")
        s_des = st.text_area("Criterio/Desempeño", key="s_des_widget")

    if st.button("✨ Generar Sesión", key="btn_sesion_gen"):
        if not s_titulo:
            st.warning("Ingrese título.")
        else:
            with st.spinner("Redactando..."):
                prompt = f"Genera Sesión CNEB. Título: {s_titulo}. Competencia: {s_comp}. Desempeño: {s_des}."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown(res)
                    meta = {"IE": ie_nombre, "Sesión": s_titulo, "Área": area_sel}
                    st.download_button("📥 Descargar Word", generar_word("Sesión de Aprendizaje", res, meta), "Sesion.docx")
    st.markdown('</div>', unsafe_allow_html=True)

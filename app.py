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
    page_title="EDUPLAN IA - FUTURISTA",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

# ── 2. ESTILOS FUTURISTAS (CSS AVANZADO) ──
st.markdown("""
    <style>
    /* Fondo general y fuentes */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    
    .main {
        background-color: #f0f4f8;
    }
    
    /* Tarjetas con efecto Glassmorphism */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        border: 1px solid #1e3a8a;
    }

    /* Botones Futuristas */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 25px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #3b82f6 0%, #1e3a8a 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        transform: scale(1.02);
        color: #ffffff;
    }

    /* Títulos y Subtítulos */
    h1 {
        font-family: 'Orbitron', sans-serif;
        color: #1e3a8a;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    h2, h3 {
        font-family: 'Rajdhani', sans-serif;
        color: #1e40af;
        border-left: 5px solid #3b82f6;
        padding-left: 15px;
    }

    /* Sidebar personalizada */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Tabs Interactivas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.5);
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a8a !important;
        color: white !important;
    }

    /* Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }
    </style>
""", unsafe_allow_html=True)

# ── 3. DATOS CNEB ──
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

# ── 4. CLIENTE IA ──
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    if not api_key: return None
    return ZhipuAI(api_key=api_key)

client = get_client()

# ── 5. FUNCIONES DE APOYO ──
def set_table_header_bg(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def generar_word(tipo, contenido, metadatos):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.6), Inches(0.6)
    
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_h = p_header.add_run("“AÑO DE LA UNIDAD, LA PAZ Y EL DESARROLLO”")
    run_h.italic = True
    run_h.font.size = Pt(9)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = title.add_run(tipo.upper())
    run_t.bold = True
    run_t.font.size = Pt(14)
    run_t.font.color.rgb = RGBColor(30, 58, 138)

    doc.add_heading("I. DATOS INFORMATIVOS", level=1)
    table_info = doc.add_table(rows=0, cols=2)
    table_info.style = 'Table Grid'
    for key, value in metadatos.items():
        row = table_info.add_row().cells
        row[0].text = key.upper()
        set_table_header_bg(row[0], "BDE5F2")
        row[0].paragraphs[0].runs[0].bold = True
        row[1].text = str(value)

    doc.add_paragraph()
    doc.add_heading("II. DESARROLLO PEDAGÓGICO", level=1)

    lines = contenido.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line: i += 1; continue
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
                cell.paragraphs[0].runs[0].bold = True
            while i < len(lines) and lines[i].strip().startswith('|'):
                data = [d.strip() for d in lines[i].split('|') if d.strip()]
                if len(data) >= len(headers):
                    row_cells = word_table.add_row().cells
                    for idx, d_text in enumerate(data[:len(headers)]):
                        row_cells[idx].text = d_text
                i += 1
        else:
            doc.add_paragraph(line.replace('**', '').replace('*', ''))
            i += 1

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ── 6. HEADER PRINCIPAL ──
st.markdown(f"<h1>{NOMBRE_APP}</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-family: Rajdhani; color: #64748b;'>Potenciando la labor docente con Inteligencia Artificial Avanzada</p>", unsafe_allow_html=True)

# ── 7. SIDEBAR ──
with st.sidebar:
    st.markdown("### 💠 NÚCLEO DE CONFIGURACIÓN")
    ie_nombre = st.text_input("NOMBRE I.E.", "I.E. La Convención")
    distrito_sel = st.selectbox("DISTRITO UBICACIÓN", DISTRITOS_LA_CONVENCION)
    st.divider()
    nivel_sel = st.radio("NIVEL EDUCATIVO", ["Inicial", "Primaria", "Secundaria"], index=1)
    grados_map = {"Inicial": ["3 años", "4 años", "5 años"], "Primaria": ["1°", "2°", "3°", "4°", "5°", "6°"], "Secundaria": ["1°", "2°", "3°", "4°", "5°"]}
    grado_sel = st.selectbox("GRADO / SECCIÓN", grados_map[nivel_sel])
    area_sel = st.selectbox("ÁREA CURRICULAR", list(AREAS_CNEB[nivel_sel].keys()))
    st.markdown(f"<div style='margin-top: 50px; text-align: center; opacity: 0.6;'>{LIDER}</div>", unsafe_allow_html=True)

# ── 8. CUERPO INTERACTIVO (TABS) ──
tab_anual, tab_unidad, tab_sesion = st.tabs(["📅 PROG. ANUAL", "📂 UNIDAD DIDÁCTICA", "🚀 SESIÓN DE CLASE"])

# PESTAÑA 1: ANUAL
with tab_anual:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Planificación Curricular de Largo Plazo")
    c1, c2 = st.columns(2)
    with c1:
        pa_ciclo = st.selectbox("CICLO EDUCATIVO", ["II", "III", "IV", "V", "VI", "VII"], key="pa_ciclo")
        pa_per = st.selectbox("ORGANIZACIÓN TEMPORAL", ["Bimestral", "Trimestral"], key="pa_per")
    with c2:
        pa_trans = st.multiselect("ENFOQUES TRANSVERSALES", ENFOQUES_TRANSVERSALES, key="pa_trans")
        pa_metod = st.multiselect("METODOLOGÍAS CLAVE", ESTRATEGIAS_METODOLOGICAS, key="pa_metod")
    
    pa_unidades = st.text_area("PROYECCIÓN DE UNIDADES (Títulos y temas clave)", placeholder="Ej: Unidad 1: Nos adaptamos..., Unidad 2: Valoramos la agricultura...", key="pa_units")

    if st.button("🧬 GENERAR ESTRUCTURA ANUAL", key="btn_anual"):
        if not pa_unidades:
            st.warning("Debe ingresar la proyección de unidades.")
        else:
            with st.spinner("Sincronizando con redes neuronales..."):
                prompt = f"Genera Programación Anual CNEB para {ie_nombre}. Grado: {grado_sel}, Área: {area_sel}. Ciclo: {pa_ciclo}. Organización: {pa_per}. Unidades: {pa_unidades}. Enfoques: {pa_trans}."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown("### 🖥️ VISTA PREVIA")
                    st.markdown(res)
                    meta = {"IE": ie_nombre, "Grado": grado_sel, "Área": area_sel, "Ciclo": pa_ciclo}
                    st.download_button("📥 DESCARGAR DOCUMENTO MAESTRO", generar_word("Programación Anual", res, meta), "Plan_Anual_IA.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# PESTAÑA 2: UNIDAD
with tab_unidad:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Diseño de la Unidad de Aprendizaje")
    u_c1, u_c2 = st.columns(2)
    with u_c1:
        u_titulo = st.text_input("TÍTULO DE LA UNIDAD", key="u_tit")
        u_dur = st.text_input("DURACIÓN ESTIMADA", "4 semanas", key="u_dur")
    with u_c2:
        u_prod = st.selectbox("PRODUCTO FINAL", PRODUCTOS_ESPERADOS, key="u_prod")
        u_comps = st.multiselect("COMPETENCIAS PRIORIZADAS", AREAS_CNEB[nivel_sel][area_sel], key="u_comp")
    
    u_situ = st.text_area("SITUACIÓN SIGNIFICATIVA (Contexto y Reto)", key="u_situ")

    if st.button("🛸 GENERAR UNIDAD DIDÁCTICA", key="btn_unidad"):
        if not u_titulo:
            st.error("El título de la unidad es obligatorio.")
        else:
            with st.spinner("Procesando arquitectura de unidad..."):
                prompt = f"Genera Unidad de Aprendizaje CNEB. Título: {u_titulo}. Situación: {u_situ}. Producto: {u_prod}. Competencias: {u_comps}."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown("### 🖥️ VISTA PREVIA")
                    st.markdown(res)
                    meta = {"IE": ie_nombre, "Unidad": u_titulo, "Producto": u_prod}
                    st.download_button("📥 DESCARGAR UNIDAD (WORD)", generar_word("Unidad de Aprendizaje", res, meta), "Unidad_IA.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# PESTAÑA 3: SESIÓN
with tab_sesion:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Arquitectura de la Sesión de Clase")
    s_c1, s_c2 = st.columns(2)
    with s_c1:
        s_titulo = st.text_input("TÍTULO DE LA SESIÓN", key="s_tit")
        s_dur = st.selectbox("TIEMPO (MINUTOS)", [45, 90, 135], index=1, key="s_dur")
    with s_c2:
        s_comp = st.selectbox("COMPETENCIA CENTRAL", AREAS_CNEB[nivel_sel][area_sel], key="s_comp")
        s_met = st.selectbox("METODOLOGÍA DE SESIÓN", ESTRATEGIAS_METODOLOGICAS, key="s_met")
    
    s_des = st.text_area("DESEMPEÑO O CRITERIO ESPECÍFICO", key="s_des")

    if st.button("⚡ GENERAR SESIÓN DE APRENDIZAJE", key="btn_sesion"):
        if not s_titulo:
            st.warning("Defina un título para la sesión.")
        else:
            with st.spinner("Materializando procesos pedagógicos..."):
                prompt = f"Genera Sesión CNEB detallada. Título: {s_titulo}. Competencia: {s_comp}. Desempeño: {s_des}. Estructura: Inicio (Motivación, saberes, propósito), Desarrollo (Gestión y acompañamiento), Cierre (Meta-cognición)."
                if client:
                    res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
                    st.markdown("### 🖥️ VISTA PREVIA")
                    st.markdown(res)
                    meta = {"IE": ie_nombre, "Sesión": s_titulo, "Competencia": s_comp}
                    st.download_button("📥 DESCARGAR SESIÓN (WORD)", generar_word("Sesión de Aprendizaje", res, meta), "Sesion_IA.docx")
    st.markdown('</div>', unsafe_allow_html=True)

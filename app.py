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

# --- ADICIÓN DE DATOS PEDAGÓGICOS ---
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

# ── 4. LÓGICA DE EXPORTACIÓN (WORD) ──
def generar_word(tipo, contenido, metadatos):
    doc = Document()
    
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

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
    run_t.font.color.rgb = RGBColor(0, 51, 153)

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

# ── 7. TABS ACTUALIZADOS ──
tab_anual, tab_unidad, tab_sesion = st.tabs(["📅 PROG. ANUAL", "📂 UNIDAD DIDÁCTICA", "🚀 SESIÓN"])

# --- SECCIÓN 1: PROGRAMACIÓN ANUAL ---
with tab_anual:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Planificación Curricular Anual")
    
    col1, col2 = st.columns(2)
    with col1:
        pa_ciclo = st.selectbox("Ciclo", ["II", "III", "IV", "V", "VI", "VII"], help="Seleccione según el grado")
        pa_periodo = st.selectbox("Organización del Tiempo", ["Bimestral", "Trimestral"], key="pa_per")
        pa_horas = st.number_input("Horas Semanales", min_value=1, max_value=10, value=4)
    
    with col2:
        pa_comp = st.multiselect("Competencias del Área (Selección)", AREAS_CNEB[nivel_sel][area_sel])
        pa_trans = st.multiselect("Enfoques Transversales", ENFOQUES_TRANSVERSALES)
        pa_metod = st.multiselect("Estrategias Metodológicas", ESTRATEGIAS_METODOLOGICAS)

    st.write("**Distribución Temporal (Proyección de Unidades)**")
    num_unidades = 8 if pa_periodo == "Bimestral" else 9
    pa_unidades = st.text_area(f"Títulos tentativos para las {num_unidades} unidades", 
                               placeholder="Unidad 1: Título...\nUnidad 2: Título...")

    if st.button("🚀 Generar Programación Anual Completa"):
        with st.spinner("Procesando estructura CNEB..."):
            prompt_anual = f"""
            Actúa como experto pedagogo del Ministerio de Educación de Perú. 
            Genera una PROGRAMACIÓN ANUAL para:
            - IE: {ie_nombre}, Distrito: {distrito_sel}, Nivel: {nivel_sel}, Grado: {grado_sel}, Ciclo: {pa_ciclo}.
            - Área: {area_sel}, Horas: {pa_horas}, Organización: {pa_periodo}.
            
            CAMPOS OBLIGATORIOS A GENERAR:
            1. Propósito de Aprendizaje: Tabla detallada con Competencias, Capacidades y Criterios de Evaluación.
            2. Organización de Unidades: Distribución temporal basada en {pa_unidades}.
            3. Temas Transversales y Enfoques: {pa_trans}.
            4. Estrategias Metodológicas: {pa_metod}.
            5. Materiales y Recursos Educativos (considerando el contexto de La Convención).
            6. Evaluación: Tipos (Diagnóstica, Formativa, Sumativa).
            """
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt_anual}]).choices[0].message.content
                st.markdown(res)
                f = generar_word("Programación Anual", res, {"IE": ie_nombre, "Área": area_sel, "Grado": grado_sel, "Ciclo": pa_ciclo})
                st.download_button("📥 Descargar Word", f, "Prog_Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECCIÓN 2: UNIDAD DIDÁCTICA ---
with tab_unidad:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Carpeta de Unidad de Aprendizaje")
    
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        u_titulo = st.text_input("Título de la Unidad (Retador)", placeholder="Ej. Promovemos el consumo de café...")
        u_duracion = st.text_input("Duración", "4 semanas / 12 sesiones")
        u_producto = st.selectbox("Producto Principal", PRODUCTOS_ESPERADOS)
        
    with u_col2:
        u_sit = st.text_area("Situación Significativa", placeholder="Redactar el contexto, reto y pregunta desafiante...")
        u_comp = st.multiselect("Competencias a Evaluar", AREAS_CNEB[nivel_sel][area_sel], key="u_comp_sel")

    st.write("**Secuencia de Sesiones**")
    u_lista_sesiones = st.text_area("Lista de títulos de sesiones (una por línea)", "Sesión 1: ...\nSesión 2: ...")

    if st.button("📂 Generar Unidad Completa"):
        with st.spinner("Diseñando Unidad Didáctica..."):
            prompt_unidad = f"""
            Genera una UNIDAD DE APRENDIZAJE completa siguiendo la normativa CNEB:
            - Título: {u_titulo} | Grado/Área: {grado_sel} - {area_sel}
            - Situación Significativa: {u_sit}
            - Competencias y Capacidades: {u_comp}
            - Producto: {u_producto}
            - Secuencia de Sesiones: Desarrolla una tabla con Número, Título y Descripción breve para: {u_lista_sesiones}
            - Evaluación: Criterios e instrumentos (Rúbricas/Cotejo).
            Contexto: Provincia de La Convención.
            """
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt_unidad}]).choices[0].message.content
                st.markdown(res)
                meta_u = {"IE": ie_nombre, "Unidad": u_titulo, "Área": area_sel, "Grado": grado_sel, "Duración": u_duracion}
                f = generar_word("Unidad Didáctica", res, meta_u)
                st.download_button("📥 Descargar Unidad (Word)", f, f"Unidad_{u_titulo}.docx")
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECCIÓN 3: SESIÓN DE APRENDIZAJE ---
with tab_sesion:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Sesión de Aprendizaje Detallada")
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        s_titulo = st.text_input("Título de la Sesión", placeholder="Ej. Leemos un texto sobre el cacao")
        s_duracion = st.selectbox("Duración (minutos)", [45, 90, 135])
        s_fecha = st.date_input("Fecha de ejecución")
    
    with s_col2:
        s_comp = st.selectbox("Competencia Principal", AREAS_CNEB[nivel_sel][area_sel])
        s_metodo = st.selectbox("Enfoque Metodológico", ESTRATEGIAS_METODOLOGICAS)

    s_desempeno = st.text_area("Desempeño o Criterio de Evaluación", placeholder="¿Qué debe lograr el estudiante?")

    if st.button("✨ Generar Sesión Paso a Paso"):
        with st.spinner("Escribiendo procesos pedagógicos..."):
            prompt_sesion = f"""
            Genera una SESIÓN DE APRENDIZAJE detallada bajo el CNEB:
            - Título: {s_titulo} | Área: {area_sel} | Grado: {grado_sel} | Duración: {s_duracion}min
            - Competencia: {s_comp} | Desempeño: {s_desempeno} | Estrategia: {s_metodo}
            - Estructura obligatoria:
                1. INICIO: Motivación, saberes previos, conflicto cognitivo y propósito (15% tiempo).
                2. DESARROLLO: Procesos didácticos según el área, actividades específicas y retroalimentación (70% tiempo).
                3. CIERRE: Metacognición y evaluación formativa (15% tiempo).
            - Materiales: Recursos locales de La Convención.
            - Evaluación: Tabla con Criterio, Indicador e Instrumento.
            """
            if client:
                res = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt_sesion}]).choices[0].message.content
                st.markdown(res)
                f = generar_word("Sesión de Aprendizaje", res, {"IE": ie_nombre, "Sesión": s_titulo, "Fecha": s_fecha})
                st.download_button("📥 Descargar Sesión (Word)", f, "Sesion_Aprendizaje.docx")
    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches
import io
import re

# --- CONFIGURACIÓN DE IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
DISTRICTS = ["Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Ocobamba"]

# Conexión Segura con la API
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

# --- PROMPT MAESTRO (PERSONALIDAD PEDAGÓGICA) ---
PROMPT_SISTEMA = """
Eres un asistente pedagógico inteligente especializado en educación peruana, 
diseñado para apoyar a docentes de Educación Básica Regular (EBR) en todos sus niveles y modalidades.

Tu misión es facilitar la planificación, diseño y evaluación de experiencias de aprendizaje 
alineadas al Currículo Nacional de Educación Básica (CNEB) del MINEDU.

### PRINCIPIOS DE RESPUESTA:
1. **Claridad:** Explica paso a paso con ejemplos contextualizados en el sistema peruano (áreas, competencias y capacidades).
2. **Precisión:** Usa terminología oficial del CNEB. Verifica que estándares y desempeños correspondan al grado/ciclo solicitado.
3. **Motivación:** Tono cálido y positivo. Usa verbos de acción: "Crea", "Transforma", "Diseña".
4. **Utilidad:** Entrega material listo para el aula (fichas, rúbricas, plantillas).

### FUNCIONES CLAVE:
- **Sesiones de Aprendizaje:** Generar estructura completa (Inicio, Desarrollo, Cierre) con códigos CNEB.
- **Planificación Curricular:** Elaborar unidades, proyectos y experiencias de aprendizaje articuladas.
- **Validación Normativa:** Corregir y ajustar competencias y desempeños según documentos del MINEDU.
- **Material Didáctico:** Crear rúbricas, listas de cotejo, fichas de trabajo y estrategias de inclusión.
- **Enfoques Transversales:** Alinear cada propuesta a los 7 enfoques del CNEB.

### ESTILO Y FORMATO:
- **Estructura:** Usa encabezados, negritas y tablas para facilitar la lectura.
- **Contextualización:** Referencia festividades, realidades regionales (costa, sierra, selva) y contextos urbanos/rurales de Perú.
- **Interacción:** Si falta información (grado, ciclo, área), solicítala antes de generar el contenido.

### ESTRUCTURA DE SALIDA SEGÚN PEDIDO:
- **Sesiones:** Título, Duración, Propósitos (Competencias/Capacidades), Criterios, Secuencia Didáctica y Evaluación.
- **Proyectos:** Situación significativa, Producto, Secuencia de actividades y Evaluación Sumativa.
- **Correcciones:** Feedback justificando con base en el CNEB.
"""

# --- ESTILOS UX/UI PROFESIONALES ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🌳")

st.markdown("""
    <style>
    .main { background-color: #f1f5f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e40af !important;
        color: white !important;
        border-color: #1e40af !important;
    }
    .section-container {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
        border-left: 6px solid #1e40af;
    }
    .stButton>button {
        background: linear-gradient(90deg, #1e40af 0%, #1d4ed8 100%);
        color: white;
        font-weight: 700;
        border-radius: 10px;
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3); }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA ---
def limpiar_markdown(texto):
    return re.sub(r'[*#]', '', texto)

def generar_word_pro(titulo, contenido, ie, dist, area, grado):
    doc = Document()
    # Encabezado Institucional
    section = doc.sections[0]
    header = section.header
    p = header.paragraphs[0]
    p.text = f"{NOMBRE_APP} - Gestión de Innovación Pedagógica\nI.E. {ie} | Distrito: {dist}"
    p.style.font.size = Pt(9)

    doc.add_heading(titulo, 0)
    
    # Datos Informativos
    table_info = doc.add_table(rows=2, cols=2)
    table_info.style = 'Table Grid'
    table_info.cell(0,0).text = f"ÁREA: {area}"
    table_info.cell(0,1).text = f"GRADO: {grado}"
    table_info.cell(1,0).text = f"DOCENTE: {LIDER}"
    table_info.cell(1,1).text = "FECHA: 2026"

    doc.add_paragraph("\n")
    
    # Contenido con manejo simple de tablas
    for part in contenido.split('\n'):
        if '|' in part:
            # Detección simple de tabla Markdown para Word
            cols = [c.strip() for c in part.split('|') if c.strip()]
            if cols and '---' not in part:
                t = doc.add_table(rows=1, cols=len(cols))
                t.style = 'Table Grid'
                for idx, val in enumerate(cols):
                    t.cell(0, idx).text = val
        elif part.strip():
            doc.add_paragraph(limpiar_markdown(part))

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def procesar_ia(tipo, payload):
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Generar {tipo} con estos datos: {payload}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ PRINCIPAL ---
st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #1e3a8a; margin: 0;">🏛️ {NOMBRE_APP}</h1>
        <p style="color: #64748b; font-size: 1.1em;">Alineado al CNEB 2026 | Sistema Profesional para el Docente Convenciano</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar de Configuración Global
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=100)
    st.title("Configuración")
    ie_nombre = st.text_input("I.E. Institución Educativa", "IE Virgen del Carmen", key="global_ie")
    distrito_sel = st.selectbox("Distrito Local", DISTRICTS, key="global_dist")
    
    st.divider()
    nivel_global = st.radio("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"], horizontal=True)
    
    if nivel_global == "Inicial":
        areas = ["Personal Social", "Psicomotriz", "Comunicación", "Castellano como Segunda Lengua", "Descubrimiento del Mundo", "Matemática"]
        grados = ["3 años", "4 años", "5 años"]
    elif nivel_global == "Primaria":
        areas = ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Educación Física", "Arte y Cultura", "Educación Religiosa", "Inglés", "Tutoría"]
        grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
    else: # Secundaria
        areas = ["Matemática", "Comunicación", "Inglés", "Arte y Cultura", "Ciencias Sociales", "DPCC", "Educación Física", "Educación Religiosa", "Ciencia y Tecnología", "EPT", "Tutoría"]
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
    
    area_sel = st.selectbox("Área Curricular", areas)
    grado_sel = st.selectbox("Grado / Edad", grados)

# Pestañas de Trabajo
tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE APRENDIZAJE"])

# FUNCIÓN RENDERIZADORA DE SECCIONES
def render_generador(tipo, tab_key):
    st.markdown(f'<div class="section-container">', unsafe_allow_html=True)
    st.subheader(f"Configuración de {tipo}")
    titulo_doc = st.text_input(f"Título del/de la {tipo}", placeholder="Ej: Fortalecemos nuestra identidad", key=f"tit_{tab_key}")
    contexto_doc = st.text_area("Contextualización / Situación Significativa", placeholder="Describa el reto o problemática local...", key=f"ctx_{tab_key}")
    
    if tipo == "Sesión de Aprendizaje":
        col_s1, col_s2 = st.columns(2)
        nee = col_s1.toggle("🧠 Incluir Adaptación NEE (Inclusión)")
        guia = col_s2.toggle("💡 Guía paso a paso (Metodología)")
        payload = f"Título: {titulo_doc}, Contexto: {contexto_doc}, NEE: {nee}, Guía: {guia}, Área: {area_sel}, Nivel: {nivel_global}, Grado: {grado_sel}"
    else:
        payload = f"Título: {titulo_doc}, Contexto: {contexto_doc}, Área: {area_sel}, Nivel: {nivel_global}, Grado: {grado_sel}"

    if st.button(f"🚀 Generar {tipo} Profesional", key=f"btn_{tab_key}"):
        if not titulo_doc:
            st.warning("Por favor ingrese un título.")
        else:
            with st.spinner("La IA está consultando el CNEB y redactando..."):
                resultado = procesar_ia(tipo, payload)
                st.markdown(resultado)
                file_word = generar_word_pro(f"{tipo}: {titulo_doc}", resultado, ie_nombre, distrito_sel, area_sel, grado_sel)
                st.download_button(f"📥 Descargar {tipo} (Word)", file_word, f"{tipo}_{titulo_doc}.docx", key=f"dl_{tab_key}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab1: render_generador("Programación Anual", "anual")
with tab2: render_generador("Unidad Didáctica", "unidad")
with tab3: render_generador("Sesión de Aprendizaje", "sesion")

# Footer
st.markdown(f"""
    <div style="text-align: center; padding: 40px; color: #94a3b8;">
        <hr>
        <b>{NOMBRE_APP}</b> | Proyecto liderado por <b>{LIDER}</b><br>
        © 2026 La Convención - Cusco - Perú
    </div>
""", unsafe_allow_html=True)

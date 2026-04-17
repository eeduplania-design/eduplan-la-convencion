import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
import io

# --- CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="📝")

# --- PROMPT MAESTRO INTEGRADO ---
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

# --- ESTILOS ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f5;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #1e88e5 !important; color: white !important; }
    .group-container { border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; background-color: white; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def generar_word(titulo, contenido):
    doc = Document()
    doc.add_heading(titulo, 0)
    # Lógica simple para insertar texto (se puede mejorar para tablas reales)
    doc.add_paragraph(contenido)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def llamar_ia(tipo, detalles):
    prompt_user = f"Genera un/a {tipo} con estos detalles: {detalles}. Sigue el formato CNEB y usa tablas."
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "system", "content": PROMPT_SISTEMA}, {"role": "user", "content": prompt_user}]
        )
        return response.choices[0].message.content
    except:
        return "⚠️ Error de conexión con la IA."

# --- INTERFAZ PRINCIPAL ---
st.title("🏛️ Portal de Planificación Curricular")
st.write(f"Gestión: **{LIDER}** | Innovación Pedagógica 2026")

tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "🚀 SESIÓN DE APRENDIZAJE"])

# --- SECCIÓN 1: PROGRAMACIÓN ANUAL ---
with tab1:
    st.markdown("### 📅 Configuración de la Programación Anual")
    with st.container():
        col1, col2 = st.columns(2)
        ie_anual = col1.text_input("Institución Educativa", key="ie_a")
        grado_anual = col2.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"], key="gr_a")
        
        situacion_anual = st.text_area("Descripción de la Situación Significativa Anual", placeholder="Ej: Problemas de alimentación, cuidado del ambiente local, etc.")
        areas_anual = st.multiselect("Áreas a integrar", ["Comunicación", "Matemática", "Personal Social", "Ciencia y Tecnología"], default=["Comunicación"])

    if st.button("✨ Generar Programación Anual", key="btn_a"):
        with st.spinner("Procesando planificación anual..."):
            detalles = f"IE: {ie_anual}, Grado: {grado_anual}, Situación: {situacion_anual}, Áreas: {areas_anual}"
            resultado = llamar_ia("Programación Anual", detalles)
            st.markdown(resultado)
            st.download_button("📥 Descargar Word", generar_word("Programación Anual", resultado), "Anual.docx")

# --- SECCIÓN 2: UNIDAD DIDÁCTICA ---
with tab2:
    st.markdown("### 📂 Configuración de la Unidad de Aprendizaje")
    with st.container():
        titulo_u = st.text_input("Título de la Unidad", placeholder="Ej: Valoramos nuestras costumbres convencianas")
        duracion_u = st.text_input("Duración aproximada (semanas/sesiones)", "4 semanas")
        proposito_u = st.text_area("Propósito de la Unidad", placeholder="¿Qué competencias queremos lograr?")
        
    if st.button("✨ Generar Unidad Didáctica", key="btn_u"):
        with st.spinner("Diseñando unidad didáctica..."):
            detalles = f"Título: {titulo_u}, Duración: {duracion_u}, Propósito: {proposito_u}"
            resultado = llamar_ia("Unidad Didáctica", detalles)
            st.markdown(resultado)
            st.download_button("📥 Descargar Word", generar_word(titulo_u, resultado), "Unidad.docx")

# --- SECCIÓN 3: SESIÓN DE APRENDIZAJE (INTERFAZ TIPO FORMULARIO) ---
with tab3:
    st.markdown("### 🚀 Generador de Sesión de Aprendizaje")
    
    # 1. Datos de la sesión
    st.markdown('<div class="group-container"><b>1. Identificación</b>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    mod_s = c1.selectbox("Modalidad", ["EBR Regular", "EBA"], key="mod_s")
    niv_s = c2.selectbox("Nivel", ["Primaria", "Secundaria"], key="niv_s")
    gra_s = c3.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"], key="gra_s")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Propósitos
    st.markdown('<div class="group-container"><b>2. Propósitos de Aprendizaje</b>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    area_s = ca.selectbox("Área Curricular", ["Comunicación", "Matemática", "Personal Social", "Ciencia y Tecnología"], key="area_s")
    enf_s = cb.selectbox("Enfoque Transversal", ["Ambiental", "Intercultural", "Derechos", "Inclusivo"], key="enf_s")
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Metodología y Título
    st.markdown('<div class="group-container"><b>3. Desarrollo y Título</b>', unsafe_allow_html=True)
    titulo_s = st.text_input("Título de la Sesión", placeholder="Ej: Conocemos el ciclo de vida del cacao")
    duracion_s = st.text_input("Duración (minutos)", "90")
    nee_s = st.toggle("🧠 Incluir Adaptación NEE (Inclusión)")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 GENERAR SESIÓN COMPLETA", key="btn_s"):
        if titulo_s:
            with st.spinner("Generando sesión completa..."):
                detalles = f"Título: {titulo_s}, Grado: {gra_s}, Área: {area_s}, Enfoque: {enf_s}, NEE: {nee_s}, Duración: {duracion_s}"
                resultado = llamar_ia("Sesión de Aprendizaje", detalles)
                st.markdown(resultado)
                st.download_button("📥 Descargar Word", generar_word(titulo_s, resultado), f"Sesion_{titulo_s}.docx")
        else:
            st.warning("Por favor, ingrese un título para la sesión.")

# --- FOOTER ---
st.markdown("<br><hr><center><small>EduPlan IA - Provincia de La Convención, Cusco</small></center>", unsafe_allow_html=True)

import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt
import io

# --- CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="📝")

# --- PROMPT MAESTRO (EL CEREBRO PEDAGÓGICO) ---
PROMPT_SISTEMA = """
Eres un asistente pedagógico inteligente especializado en educación peruana (CNEB/MINEDU). 
Tu misión es facilitar la planificación de docentes de EBR. 
PRINCIPIOS: Claridad técnica, Precisión en códigos CNEB, Motivación y Utilidad inmediata.
ESTRUCTURA: Siempre usa TABLAS para Propósitos de Aprendizaje y Secuencia Didáctica (Inicio, Desarrollo, Cierre).
CONTEXTO: Usa referencias a La Convención, Cusco (café, cacao, festividades) y realidades rurales/urbanas del Perú.
"""

# --- ESTILOS AVANZADOS (INTERFAZ INTUITIVA) ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    /* Contenedores tipo Ficha */
    .section-box {
        border: 1px solid #cbd5e1;
        border-left: 8px solid #1e88e5;
        border-radius: 12px;
        padding: 20px;
        background-color: white;
        margin-bottom: 20px;
    }
    .section-title {
        color: #1e3a8a;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 15px;
    }
    /* Botón Generar (Azul) */
    .stButton>button {
        background-color: #1d4ed8;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 3.5em;
    }
    /* Botón Magia (Amarillo) */
    .magic-btn>div>button {
        background-color: #facc15 !important;
        color: #1e3a8a !important;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def crear_word(titulo, contenido):
    doc = Document()
    doc.add_heading(titulo, 0)
    # Lógica de inserción de párrafos
    for linea in contenido.split('\n'):
        if linea.strip():
            doc.add_paragraph(linea.replace('#', '').replace('*', ''))
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def llamar_ia(tipo, detalles):
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Genera un/a {tipo} con estos datos: {detalles}. Obligatorio: Usa tablas Markdown."}
            ]
        )
        return response.choices[0].message.content
    except:
        return "⚠️ Error: Verifica tu API KEY en los Secrets de Streamlit."

# --- CUERPO DE LA PÁGINA ---
st.title("🏛️ Portal de Planificación Curricular")
st.write(f"Gestión: **{LIDER}** | Innovación Pedagógica 2026")

tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "🚀 SESIÓN DE APRENDIZAJE"])

# --- TAB 3: SESIÓN (DISEÑO SEGÚN IMAGEN DEL USUARIO) ---
with tab3:
    # 1. Modalidad y Grado
    st.markdown('<div class="section-box"><div class="section-title">🏠 1. Modalidad y Grado</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    mod = c1.selectbox("Modalidad", ["EBR Regular", "EBA", "EBE"], key="mod_s")
    niv = c2.selectbox("Nivel/Ciclo", ["Primaria / Ciclo III", "Primaria / Ciclo IV", "Primaria / Ciclo V"], key="niv_s")
    gra = c3.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"], key="gra_s")
    st.markdown('</div>', unsafe_allow_html=True)

    # Botón IA Intermedio
    st.markdown('<div class="magic-btn">', unsafe_allow_html=True)
    st.button("🪄 ¡IA, determina las Competencias por mí!", key="magic")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Propósito
    st.markdown('<div class="section-box"><div class="section-title">🎯 2. Propósito de Aprendizaje</div>', unsafe_allow_html=True)
    ca, cb = st.columns(2)
    area = ca.selectbox("Área Curricular", ["Comunicación", "Matemática", "Personal Social", "Ciencia y Tecnología"], key="area_s")
    comp = cb.text_input("Competencia", placeholder="Ej: Se comunica oralmente en su lengua materna", key="comp_s")
    enfoque = st.selectbox("Seleccione Enfoque Transversal", ["Ambiental", "Intercultural", "Orientación al bien común"], key="enf_s")
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Contexto y Metodología
    st.markdown('<div class="section-box"><div class="section-title">🛠️ 3. Contexto, Recursos y Metodología</div>', unsafe_allow_html=True)
    cx, cy, cz = st.columns(3)
    estudiantes = cx.text_input("Cant. Estudiantes", "25")
    espacio = cy.selectbox("Espacio", ["Aula de clase", "Patio", "AIP / Laboratorio"])
    equipo = cz.selectbox("Trabajo en Equipo", ["Grupos de 4", "Parejas", "Individual"])
    
    st.write("**Materiales disponibles**")
    m1, m2, m3 = st.columns(3)
    m1.checkbox("Tabletas / Laptops")
    m2.checkbox("Pizarra Interactiva")
    m3.checkbox("Material Concreto")

    nee = st.toggle("🧠 Adaptación de Inclusión (NEE)")
    guia = st.toggle("⚠️ Requiero guía paso a paso (No soy del área)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Título y Generación
    st.markdown('<div class="section-box"><div class="section-title">📌 4. Tema o Título de la Sesión</div>', unsafe_allow_html=True)
    titulo = st.text_input("Ej: Conocemos el sistema digestivo", key="tit_s")
    duracion = st.text_input("Duración (Minutos)", "90")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 GENERAR SESIÓN COMPLETA", key="gen_s"):
        if titulo:
            with st.spinner("Construyendo sesión pedagógica..."):
                datos = f"Título: {titulo}, Área: {area}, Grado: {gra}, NEE: {nee}, Guía: {guia}, Recursos: {espacio}"
                res = llamar_ia("Sesión de Aprendizaje", datos)
                st.markdown(res)
                st.download_button("📥 Descargar Sesión (Word)", crear_word(titulo, res), f"{titulo}.docx")
        else:
            st.error("Por favor, ingrese un título.")

# --- SECCIONES ANUAL Y UNIDAD (SIMPLIFICADAS PARA FLUJO) ---
with tab1:
    st.info("Complete los datos en la barra lateral o aquí para su Programación Anual.")
    # (Aquí iría la lógica similar a la Sesión pero para el Plan Anual)

with tab2:
    st.info("Diseñe aquí sus Unidades de Aprendizaje articuladas.")

# --- FOOTER ---
st.markdown("<br><hr><center><small>EduPlan IA - Provincia de La Convención | Quillabamba 2026</small></center>", unsafe_allow_html=True)

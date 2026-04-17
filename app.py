import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
import io
import re

# --- CONFIGURACIÓN DE IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
DISTRICTS = ["Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Ocobamba"]

# Conexión Segura con la API
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

# --- DISEÑO DE LA INTERFAZ (UI) ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🌳")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8fafc; }}
    .main-header {{ text-align: center; padding: 2rem; background: linear-gradient(90deg, #1e3a8a, #2e7d32); color: white; border-radius: 15px; margin-bottom: 2rem; }}
    .stButton>button {{ width: 100%; background-color: #2e7d32; color: white; font-weight: bold; border-radius: 10px; height: 3.5em; border: none; }}
    .footer {{ text-align: center; padding: 2rem; font-size: 0.8rem; color: #64748b; border-top: 1px solid #e2e8f0; margin-top: 3rem; }}
    </style>
    <div class="main-header">
        <h1>🌳 {NOMBRE_APP}</h1>
        <p>Especialista en Planificación Curricular - UGEL La Convención</p>
    </div>
    """, unsafe_allow_html=True)

# --- PANEL LATERAL: CONFIGURACIÓN PEDAGÓGICA ---
with st.sidebar:
    st.header("📍 Configuración")
    ie_nombre = st.text_input("Institución Educativa", placeholder="Ej: Virgen del Carmen")
    distrito_sel = st.selectbox("Distrito", DISTRICTS)
    st.divider()
    nivel = st.selectbox("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"])
    grado = st.selectbox("Grado/Año", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
    area = st.selectbox("Área Curricular", ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Religión", "Arte y Cultura", "Educación Física", "Inglés", "Tutoría"])
    st.info(f"Liderazgo Digital: {LIDER}")

# --- MOTOR DE INTELIGENCIA ARTIFICIAL (PROMPT MAESTRO) ---
def ia_engine(tipo_doc, tema, contexto_extra=""):
    prompt_maestro = f"""
    Actúa como un Especialista de Acompañamiento Pedagógico de la UGEL La Convención, experto en el CNEB y normativas del MINEDU (RVM N° 094-2020).
    
    TAREA: Generar un/a {tipo_doc} detallado para el nivel {nivel}, grado {grado}, área de {area}.
    
    DIVERSIFICACIÓN CURRICULAR: 
    Contextualiza la planificación a la Provincia de La Convención, Cusco. Usa ejemplos reales de la zona: producción de café, cacao, biodiversidad, turismo en Santa Teresa, historia de Vilcabamba o la realidad del distrito de {distrito_sel}.
    
    ESTRUCTURA OBLIGATORIA:
    1. DATOS INFORMATIVOS: I.E. {ie_nombre}, Distrito {distrito_sel}.
    2. SITUACIÓN SIGNIFICATIVA: Contexto local, Reto (pregunta desafiante) y Producto esperado.
    3. PROPÓSITOS DE APRENDIZAJE: Competencias, Capacidades y Desempeños precisados del CNEB.
    4. ENFOQUES TRANSVERSALES.
    5. SECUENCIA DIDÁCTICA: Inicio, Desarrollo y Cierre, respetando los procesos pedagógicos y procesos didácticos específicos de {area}.
    6. EVALUACIÓN FORMATIVA: Técnicas, criterios e instrumentos coherentes.
    
    TEMA ESPECÍFICO: {tema}. 
    CONTEXTO ADICIONAL DEL DOCENTE: {contexto_extra}.
    
    Responde en formato claro, profesional y usa tablas donde sea necesario.
    """
    try:
        response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt_maestro}])
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: Asegúrese de haber configurado correctamente su API KEY en Secrets. Detalle: {e}"

# --- FUNCIÓN DE DESCARGA E IMPRESIÓN ---
def crear_word(contenido, titulo_doc):
    doc = Document()
    doc.add_heading(titulo_doc, 0)
    doc.add_paragraph(f"I.E.: {ie_nombre} | Distrito: {distrito_sel}").bold = True
    doc.add_paragraph(f"Proyecto: {NOMBRE_APP} | Responsable: {LIDER}")
    doc.add_paragraph("-" * 45)
    
    # Limpieza de Markdown para Word
    limpio = re.sub(r'[*#]', '', contenido)
    doc.add_paragraph(limpio)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- CUERPO DE LA PÁGINA: PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["📅 Prog. Anual", "📂 Unidades", "📄 Sesiones", "📊 Evaluación & NEE"])

with tab1:
    st.subheader("Planificación a Largo Plazo: Programación Anual")
    t_anual = st.text_input("Título de la Programación Anual", placeholder="Ej: Fortalecemos nuestra identidad convenciana")
    if st.button("✨ Generar Plan Anual"):
        with st.spinner("IA trabajando para la UGEL La Convención..."):
            resultado = ia_engine("Programación Curricular Anual", t_anual)
            st.markdown(resultado)
            st.download_button("🖨️ Descargar para Imprimir", crear_word(resultado, "PROG_ANUAL"), f"Anual_{grado}.docx")

with tab2:
    st.subheader("Planificación a Corto Plazo: Unidades de Aprendizaje")
    t_unidad = st.text_input("Título de la Unidad / Proyecto")
    if st.button("✨ Generar Unidad Didáctica"):
        with st.spinner("Estructurando Unidad CNEB..."):
            resultado = ia_engine("Unidad de Aprendizaje / Proyecto", t_unidad)
            st.markdown(resultado)
            st.download_button("🖨️ Descargar para Imprimir", crear_word(resultado, "UNIDAD"), f"Unidad_{grado}.docx")

with tab3:
    st.subheader("Desarrollo Diario: Sesión de Aprendizaje")
    t_sesion = st.text_input("Título de la Sesión")
    ctx_sesion = st.text_area("Describa brevemente la necesidad o problemática observada en el aula")
    if st.button("✨ Generar Sesión Completa"):
        with st.spinner("Redactando procesos pedagógicos..."):
            resultado = ia_engine("Sesión de Aprendizaje Detallada", t_sesion, ctx_sesion)
            st.markdown(resultado)
            st.download_button("🖨️ Descargar para Imprimir", crear_word(resultado, "SESION"), f"Sesion_{grado}.docx")

with tab4:
    st.subheader("Instrumentos de Evaluación e Inclusión")
    col1, col2 = st.columns(2)
    with col1:
        instrumento = st.selectbox("Seleccione el Instrumento", ["Lista de Cotejo", "Rúbrica Analítica", "Escala de Valoración"])
    with col2:
        es_nee = st.checkbox("¿Adaptar para Estudiantes con NEE?")
    
    desempeno = st.text_input("Escriba la competencia o desempeño a evaluar")
    if st.button("✨ Generar Evaluación"):
        tipo = f"{instrumento} " + ("con Adaptación para NEE" if es_nee else "")
        with st.spinner("Creando tabla de evaluación formativa..."):
            resultado = ia_engine(tipo, desempeno)
            st.markdown(resultado)
            st.download_button("🖨️ Descargar para Imprimir", crear_word(resultado, "EVALUACION"), "Evaluacion.docx")

# --- PIE DE PÁGINA ---
st.markdown(f"""
    <div class="footer">
        <p><b>{NOMBRE_APP}</b> - Innovación Pedagógica para la Provincia de La Convención</p>
        <p>Desarrollado por: <b>{LIDER}</b> | 2026</p>
    </div>
    """, unsafe_allow_html=True)

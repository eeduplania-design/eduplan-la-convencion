import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
import io
import re

# --- IDENTIDAD PROVINCIAL ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER_PROYECTO = "Prof. Percy Tapia"
REGION = "Cusco - Perú"

# Conexión con la API
API_KEY = st.secrets.get("ZHIPU_KEY", "TU_API_KEY_AQUI")
client = ZhipuAI(api_key=API_KEY)

# --- DISEÑO VISUAL ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🌳")

st.markdown(f"""
    <style>
    .main {{ background-color: #f4f7f6; }}
    .stButton>button {{ background: linear-gradient(90deg, #2e7d32, #1b5e20); color: white; border-radius: 10px; height: 3.5em; width: 100%; font-weight: bold; border: none; }}
    .header-box {{ text-align: center; padding: 25px; background-color: white; border-radius: 15px; border-bottom: 5px solid #2e7d32; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px; }}
    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; margin-top: 50px; border-top: 1px solid #ddd; }}
    </style>
    <div class="header-box">
        <h1 style="color: #2e7d32; margin-bottom: 0;">🌳 {NOMBRE_APP}</h1>
        <p style="font-size: 1.1em; color: #555;">Transformando la Planificación Curricular en la Provincia de La Convención</p>
    </div>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (DATOS DEL DOCENTE) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=80)
    st.header("📍 Datos del Docente")
    ie_usuario = st.text_input("Nombre de su I.E.", placeholder="Ej. Virgen del Carmen")
    distrito = st.selectbox("Distrito", ["Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Ocobamba"])
    st.markdown("---")
    nivel = st.selectbox("Nivel", ["Inicial", "Primaria", "Secundaria"])
    grado = st.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
    area = st.selectbox("Área", ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Religión", "Arte", "EF", "Inglés"])
    instrumento = st.selectbox("Instrumento", ["Lista de Cotejo", "Rúbrica Analítica", "Escala de Valoración"])

# --- LÓGICA DE IA ---
def consultar_ia(tipo, tema, contexto=""):
    prompt = f"""
    Eres un especialista curricular de la UGEL La Convención, Cusco. Genera un/a {tipo} para el nivel {nivel}, grado {grado}, área de {area}.
    CONTEXTO PROVINCIAL: Si es posible, usa ejemplos relacionados a la cultura, geografía (café, cacao, ceja de selva) o historia de La Convención.
    ESTRUCTURA:
    1. SITUACIÓN SIGNIFICATIVA: Contexto local, Reto (pregunta) y Producto.
    2. PROPÓSITOS: Competencia, Capacidad y Desempeño CNEB.
    3. SECUENCIA: Inicio, Desarrollo y Cierre (procesos didácticos).
    4. EVALUACIÓN: Tabla detallada de {instrumento}.
    Tema: {tema}. Contexto adicional: {contexto}.
    """
    try:
        response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def crear_docx(contenido, titulo):
    doc = Document()
    doc.add_heading(titulo, 0)
    doc.add_paragraph(f"I.E.: {ie_usuario} | Distrito: {distrito}").bold = True
    doc.add_paragraph(f"Responsable del Proyecto: {LIDER_PROYECTO}")
    doc.add_paragraph("-" * 30)
    limpio = re.sub(r'[*#]', '', contenido)
    doc.add_paragraph(limpio)
    stream = io.BytesIO()
    doc.save(stream)
    stream.seek(0)
    return stream

# --- PESTAÑAS ---
t1, t2, t3 = st.tabs(["📄 Sesiones", "📂 Unidades", "📊 Evaluación"])

with t1:
    tema = st.text_input("Título de la Sesión de Aprendizaje")
    extra = st.text_area("Contexto específico del aula (Opcional)")
    if st.button("🚀 Generar Sesión Convenciana"):
        with st.spinner("EduPlan IA está redactando su sesión..."):
            res = consultar_ia("Sesión de Aprendizaje", tema, extra)
            st.markdown(res)
            file = crear_docx(res, f"SESIÓN - {tema}")
            st.download_button("📥 Descargar Word", file, file_name=f"Sesion_{tema}.docx")

# (La lógica se repite para Unidades y Evaluación de forma similar)

# --- FOOTER ---
st.markdown(f"""
    <div class="footer">
        <p><b>{NOMBRE_APP}</b> | Una iniciativa para la Provincia de La Convención</p>
        <p>Liderazgo Pedagógico: <b>{LIDER_PROYECTO}</b> | 2026</p>
    </div>
    """, unsafe_allow_html=True)

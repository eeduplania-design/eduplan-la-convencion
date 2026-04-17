import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt
import io
import re

# --- CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA"
SUBTITULO = "Portal de Planificación Curricular - La Convención"
LIDER = "Prof. Percy Tapia"
API_KEY = st.secrets.get("ZHIPU_KEY", "")
client = ZhipuAI(api_key=API_KEY)

# --- DISEÑO ESTILO PORTAL (CSS) ---
st.set_page_config(page_title=f"{NOMBRE_APP} | La Convención", layout="wide", page_icon="📝")

st.markdown(f"""
    <style>
    /* Estilo General tipo Planifica.net */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Poppins', sans-serif; background-color: #f0f2f5; }}
    
    /* Barra Superior Estilo Portal */
    .navbar {{
        background-color: #ffffff;
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #2e7d32;
        margin-bottom: 25px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}
    
    /* Contenedores de Instrumentos */
    .instrumento-card {{
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-top: 5px solid #2e7d32;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }}
    
    /* Botones Profesionales */
    .stButton>button {{
        background: #2e7d32;
        color: white;
        border-radius: 8px;
        padding: 10px 25px;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: 0.3s;
    }}
    .stButton>button:hover {{ background: #1b5e20; transform: scale(1.02); }}
    
    /* Títulos */
    h1, h2, h3 {{ color: #1e3a8a; }}
    </style>
    
    <div class="navbar">
        <div>
            <span style="font-size: 24px; font-weight: 700; color: #2e7d32;">📝 {NOMBRE_APP}</span>
            <span style="margin-left: 10px; color: #666; font-size: 14px;">| Provincia de La Convención</span>
        </div>
        <div style="font-size: 12px; color: #999;">Proyecto de Innovación Pedagógica</div>
    </div>
    """, unsafe_allow_html=True)

# --- PANEL DE FILTROS (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛠️ Configuración Global")
    ie_nombre = st.text_input("Nombre de la I.E.", "IE Virgen del Carmen")
    distrito = st.selectbox("Distrito", ["Santa Ana", "Santa Teresa", "Echarati", "Maranura", "Huayopata", "Otros"])
    nivel = st.radio("Nivel Educativo", ["Primaria", "Secundaria"], horizontal=True)
    grado = st.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
    area = st.selectbox("Área Curricular", ["Comunicación", "Matemática", "Personal Social", "Ciencia y Tecnología", "Arte", "EF", "Inglés"])
    st.divider()
    st.caption(f"Administrado por: {LIDER}")

# --- MOTOR DE GENERACIÓN ---
def generar_documento(tipo, tema, contexto=""):
    prompt = f"""Actúa como experto en CNEB del MINEDU Perú. Genera un/a {tipo} detallado para {nivel}, {grado} grado, área {area}. 
    I.E. {ie_nombre}, Distrito {distrito}. Tema: {tema}. Contexto local: {contexto}.
    Estructura profesional con Situación Significativa, Competencias, Desempeños y Secuencia Didáctica."""
    try:
        response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except: return "⚠️ Error: Revisa tu API KEY."

def descargar_word(contenido, titulo):
    doc = Document()
    doc.add_heading(titulo, 0)
    doc.add_paragraph(f"I.E. {ie_nombre} - {distrito}").bold = True
    doc.add_paragraph(re.sub(r'[*#]', '', contenido))
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- CUERPO PRINCIPAL (ESTRUCTURA DE PLANIFICA.NET) ---
st.markdown(f"## 🏛️ Bienvenido al Portal de Planificación")
st.write("Seleccione el instrumento que desea generar para su jornada pedagógica.")

# Usamos pestañas pero con estilo de tarjeta
tab1, tab2, tab3, tab4 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE CLASE", "📊 EVALUACIÓN"])

with tab1:
    st.markdown('<div class="instrumento-card">', unsafe_allow_html=True)
    st.subheader("Configuración de Programación Anual")
    t_anual = st.text_input("Nombre del Año Escolar / Título Anual")
    if st.button("Generar Programación Anual ✨"):
        res = generar_documento("Programación Anual", t_anual)
        st.markdown(res)
        st.download_button("📥 Descargar Word", descargar_word(res, "PROG_ANUAL"), "Anual.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="instrumento-card">', unsafe_allow_html=True)
    st.subheader("Diseño de Unidad de Aprendizaje")
    t_unidad = st.text_input("Título de la Unidad")
    if st.button("Generar Unidad Didáctica ✨"):
        res = generar_documento("Unidad de Aprendizaje", t_unidad)
        st.markdown(res)
        st.download_button("📥 Descargar Word", descargar_word(res, "UNIDAD"), "Unidad.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="instrumento-card">', unsafe_allow_html=True)
    st.subheader("Desarrollo de Sesión de Aprendizaje")
    t_sesion = st.text_input("Título de la Sesión")
    ctx = st.text_area("Contexto o problemática específica")
    if st.button("Generar Sesión de Clase ✨"):
        res = generar_documento("Sesión de Aprendizaje", t_sesion, ctx)
        st.markdown(res)
        st.download_button("📥 Descargar Word", descargar_word(res, "SESION"), "Sesion.docx")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="instrumento-card">', unsafe_allow_html=True)
    st.subheader("Instrumentos de Evaluación")
    t_inst = st.selectbox("Tipo", ["Lista de Cotejo", "Rúbrica Analítica"])
    tema_eval = st.text_input("Competencia a evaluar")
    if st.button("Generar Instrumento ✨"):
        res = generar_documento(t_inst, tema_eval)
        st.markdown(res)
        st.download_button("📥 Descargar Word", descargar_word(res, "EVALUACION"), "Evaluacion.docx")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"""
    <div style="text-align:center; padding: 40px; color: #888; font-size: 13px;">
        Desarrollado para la Provincia de La Convención por el <b>{LIDER}</b><br>
        © 2026 - Todos los derechos reservados.
    </div>
    """, unsafe_allow_html=True)

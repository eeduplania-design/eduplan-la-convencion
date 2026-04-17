import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
import io
import re

# --- CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
DISTRITOS = ["Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Ocobamba"]

# Conexión con la API
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

# --- ESTILOS VISUALES (UX/UI) ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #2e7d32; color: white; border-radius: 10px; font-weight: bold; height: 3em; }
    .header-box { background: white; padding: 25px; border-bottom: 5px solid #1e3a8a; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 10px; }
    </style>
    <div class="header-box">
        <h1 style="color: #1e3a8a; margin:0;">🏛️ SISTEMA DE PLANIFICACIÓN CURRICULAR</h1>
        <p style="color: #666;">Alineado al CNEB | Provincia de La Convención, Cusco</p>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE EXPORTACIÓN A WORD CON TABLAS ---
def exportar_a_word(titulo_doc, contenido, ie, dist):
    doc = Document()
    doc.add_heading(titulo_doc, 0)
    doc.add_paragraph(f"I.E.: {ie} | Distrito: {dist}").bold = True
    doc.add_paragraph(f"Responsable: {LIDER}").italic = True
    
    lineas = contenido.split('\n')
    tabla_pendiente = []
    
    for linea in lineas:
        if '|' in linea and '---' not in linea:
            cols = [c.strip() for c in linea.split('|') if c.strip()]
            if cols: tabla_pendiente.append(cols)
        else:
            if tabla_pendiente:
                table = doc.add_table(rows=len(tabla_pendiente), cols=len(tabla_pendiente[0]))
                table.style = 'Table Grid'
                for i, fila in enumerate(tabla_pendiente):
                    for j, valor in enumerate(fila):
                        table.cell(i, j).text = valor
                tabla_pendiente = []
            if linea.strip():
                doc.add_paragraph(linea.replace('#', '').replace('*', ''))
                
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- MOTOR DE IA ---
def consultar_ia(tipo, tema, contexto, grado, area):
    prompt = f"Actúa como experto CNEB. Genera un/a {tipo} para {area}, {grado}. Tema: {tema}. Contexto: {contexto}. Usa TABLAS para propósitos y secuencia didáctica."
    try:
        response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except: return "⚠️ Error de conexión. Revisa tu API KEY."

# --- INTERFAZ ---
with st.sidebar:
    st.header("⚙️ Datos Generales")
    ie = st.text_input("I.E.", "Virgen del Carmen")
    dist = st.selectbox("Distrito", DISTRITOS)
    area = st.selectbox("Área", ["Comunicación", "Matemática", "Personal Social", "Ciencia y Tecnología"])
    grado = st.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"])

tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE APRENDIZAJE"])

# Sección 1: Programación Anual
with tab1:
    st.markdown("<div class='card'><h3>Planificación Anual</h3></div>", unsafe_allow_html=True)
    tema_anual = st.text_input("Título Anual", key="t1")
    ctx_anual = st.text_area("Contexto/Metas", key="c1")
    if st.button("✨ Generar Anual", key="b1"):
        res = consultar_ia("Programación Anual", tema_anual, ctx_anual, grado, area)
        st.markdown(res)
        st.download_button("📥 Descargar Word", exportar_a_word("Plan Anual", res, ie, dist), f"Anual_{tema_anual}.docx", key="d1")

# Sección 2: Unidad Didáctica
with tab2:
    st.markdown("<div class='card'><h3>Unidad Didáctica</h3></div>", unsafe_allow_html=True)
    tema_uni = st.text_input("Título de la Unidad", key="t2")
    ctx_uni = st.text_area("Situación Significativa", key="c2")
    if st.button("✨ Generar Unidad", key="b2"):
        res = consultar_ia("Unidad Didáctica", tema_uni, ctx_uni, grado, area)
        st.markdown(res)
        st.download_button("📥 Descargar Word", exportar_a_word("Unidad", res, ie, dist), f"Unidad_{tema_uni}.docx", key="d2")

# Sección 3: Sesión de Aprendizaje
with tab3:
    st.markdown("<div class='card'><h3>Sesión de Aprendizaje</h3></div>", unsafe_allow_html=True)
    tema_ses = st.text_input("Título de la Sesión", key="t3")
    ctx_ses = st.text_area("Reto del día", key="c3")
    if st.button("✨ Generar Sesión", key="b3"):
        res = consultar_ia("Sesión de Aprendizaje", tema_ses, ctx_ses, grado, area)
        st.markdown(res)
        st.download_button("📥 Descargar Word", exportar_a_word("Sesion", res, ie, dist), f"Sesion_{tema_ses}.docx", key="d3")

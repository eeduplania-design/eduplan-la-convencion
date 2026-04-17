import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt
import io
import re

# --- CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
DISTRITOS = ["Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Ocobamba"]

client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

# --- ESTILOS VISUALES (UX/UI) ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #2e7d32; color: white; border-radius: 10px; font-weight: bold; }
    .header-box { background: white; padding: 25px; border-bottom: 5px solid #1e3a8a; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
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
    p = doc.add_paragraph()
    p.add_run(f"I.E.: {ie} | Distrito: {dist}").bold = True
    doc.add_paragraph(f"Responsable: {LIDER} | Fuente: EduPlan IA").italic = True
    
    # Procesar texto y tablas
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
    prompt = f"""
    Actúa como experto pedagógico del MINEDU Perú. Genera un/a {tipo} para el nivel Primaria, {grado}, área de {area}.
    TEMA/TÍTULO: {tema}.
    CONTEXTO PEDAGÓGICO: {contexto}.
    
    REQUISITOS CNEB:
    1. Propósitos de aprendizaje (Competencias, Capacidades, Desempeños) en TABLA.
    2. Enfoques transversales.
    3. Situación significativa contextualizada a La Convención (Cusco).
    4. Secuencia didáctica (Inicio, Desarrollo, Cierre) en TABLA detallando procesos pedagógicos.
    5. Criterios de evaluación en TABLA.
    """
    try:
        response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except: return "⚠️ Error: Verifica la API Key."

# --- INTERFAZ DE USUARIO ---
with st.sidebar:
    st.header("⚙️ Datos Generales")
    ie = st.text_input("Nombre de la I.E.", "Virgen del Carmen")
    dist = st.selectbox("Distrito", DISTRITOS)
    area = st.selectbox("Área Curricular", ["Comunicación", "Matemática", "Personal Social", "Ciencia y Tecnología", "Religión"])
    grado = st.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
    st.info(f"Gestión: {LIDER}")

# PESTAÑAS FUNCIONALES
tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE APRENDIZAJE"])

def seccion_planificador(tipo, placeholder_tema):
    st.markdown(f"<div class='card'><h3>Generar {tipo}</h3></div>", unsafe_allow_html=True)
    tema = st.text_input(f"Título de la {tipo}", placeholder=placeholder_tema)
    ctx = st.text_area(f"Contextualización (Ej: Problemas de aprendizaje, realidad local del café/cacao, etc.)")
    
    if st.button(f"✨ Crear {tipo} ahora"):
        if tema:
            with st.spinner(f"Redactando {tipo} según el CNEB..."):
                resultado = consultar_ia(tipo, tema, ctx, grado, area)
                st.markdown(resultado)
                file_word = exportar_a_word(f"{tipo.upper()}: {tema}", resultado, ie, dist)
                st.download_button(f"📥 Descargar {tipo} en Word", file_word, f"{tipo}_{tema}.docx")
        else: st.warning("Por favor, ingresa un título.")

with tab1: seccion_planificador("Programación Anual", "Ej: Fortalecemos nuestra identidad cultural")
with tab2: seccion_planificador("Unidad Didáctica", "Ej: Conocemos la biodiversidad de nuestra provincia")
with tab3: seccion_planificador("Sesión de Aprendizaje", "Ej: Leemos textos instructivos sobre la cosecha de café")

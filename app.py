import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import re

# --- CONFIGURACIÓN E IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA"
LIDER = "Prof. Percy Tapia"
API_KEY = st.secrets.get("ZHIPU_KEY", "")
client = ZhipuAI(api_key=API_KEY)

# --- DISEÑO ESTILO PORTAL ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; background-color: #f4f7f6; }
    .stButton>button { background: #2e7d32; color: white; border-radius: 8px; font-weight: 600; width: 100%; }
    .header-portal { background: white; padding: 20px; border-bottom: 4px solid #2e7d32; border-radius: 0 0 15px 15px; margin-bottom: 20px; text-align: center; }
    </style>
    <div class="header-portal">
        <h1 style="color: #1e3a8a; margin:0;">🏛️ PORTAL PEDAGÓGICO - LA CONVENCIÓN</h1>
        <p style="color: #666;">Planificación Curricular con Formato de Tabla Profesional (CNEB)</p>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE TABLAS PARA WORD ---
def agregar_contenido_al_word(doc, texto):
    """Analiza el texto y crea tablas reales en Word si detecta formato Markdown"""
    lineas = texto.split('\n')
    tabla_activa = False
    datos_tabla = []

    for linea in lineas:
        if '|' in linea and '---' not in linea:
            # Es una línea de tabla
            columnas = [col.strip() for col in linea.split('|') if col.strip()]
            if columnas:
                datos_tabla.append(columnas)
                tabla_activa = True
        elif '---' in linea:
            continue
        else:
            if tabla_activa:
                # Dibujar la tabla acumulada
                if datos_tabla:
                    table = doc.add_table(rows=len(datos_tabla), cols=len(datos_tabla[0]))
                    table.style = 'Table Grid'
                    for i, fila in enumerate(datos_tabla):
                        for j, valor in enumerate(fila):
                            table.cell(i, j).text = valor
                datos_tabla = []
                tabla_activa = False
            
            # Es texto normal
            if linea.strip():
                p = doc.add_paragraph(linea.replace('#', '').replace('*', ''))
                if linea.startswith('###') or linea.startswith('##'):
                    p.style = 'Heading 2'

# --- MOTOR DE IA CON PROMPT DE TABLAS ---
def generar_planificacion(tipo, tema, contexto=""):
    prompt = f"""
    Actúa como experto en CNEB. Genera un/a {tipo} para el área de {area}, grado {grado}.
    I.E. {ie_nombre}. Distrito {distrito_sel}. Tema: {tema}.
    
    REGLA CRÍTICA DE FORMATO: 
    Presenta los Propósitos de Aprendizaje (Competencias, Capacidades, Desempeños) y la Secuencia Didáctica (Inicio, Desarrollo, Cierre) EXCLUSIVAMENTE en TABLAS de Markdown.
    Usa columnas claras. Por ejemplo, para la Sesión: | Momento | Actividades | Tiempo | Recursos |.
    """
    try:
        response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except:
        return "⚠️ Error de conexión."

def descargar_word(contenido, titulo):
    doc = Document()
    header = doc.add_heading(titulo, 0)
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"I.E.: {ie_nombre} | Responsable: {LIDER}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    agregar_contenido_al_word(doc, contenido)
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- INTERFAZ ---
with st.sidebar:
    st.header("⚙️ Configuración")
    ie_nombre = st.text_input("Nombre I.E.", "IE Virgen del Carmen")
    distrito_sel = st.selectbox("Distrito", ["Santa Ana", "Echarati", "Santa Teresa", "Maranura"])
    area = st.selectbox("Área", ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología"])
    grado = st.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"])

tab1, tab2, tab3 = st.tabs(["📅 P. Anual", "📂 Unidad", "📄 Sesión"])

with tab3:
    st.subheader("Generador de Sesión en Tablas")
    t_sesion = st.text_input("Título de la sesión")
    if st.button("Generar Sesión"):
        with st.spinner("Creando tablas pedagógicas..."):
            res = generar_planificacion("Sesión de Aprendizaje", t_sesion)
            st.markdown(res) # Aquí se verá la tabla en la web
            st.download_button("📥 Descargar Word con Tablas", descargar_word(res, "SESIÓN DE APRENDIZAJE"), "Sesion.docx")

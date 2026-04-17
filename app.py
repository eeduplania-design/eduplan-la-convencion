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

# --- DISEÑO UX/UI (ESTILOS PERSONALIZADOS) ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🌳")

st.markdown(f"""
    <style>
    /* Importación de Tipografía */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    
    .stApp {{ background-color: #f8fafc; }}
    
    /* Hero Section */
    .hero-container {{
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #1e3a8a 0%, #2e7d32 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }}
    
    /* Estilo de Botones */
    .stButton>button {{
        width: 100%;
        background-color: #2e7d32;
        color: white;
        font-weight: 700;
        border-radius: 12px;
        padding: 0.75rem;
        border: none;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #1b5e20;
        transform: translateY(-2px);
    }}
    
    /* Tarjetas de Contenido */
    .content-card {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #1e3a8a;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    </style>
    
    <div class="hero-container">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🌳 {NOMBRE_APP}</h1>
        <p style="font-size: 1.25rem; opacity: 0.9;">Planificación Curricular Inteligente para el Docente Convenciano</p>
        <p style="font-size: 1rem; margin-top: 1rem; background: rgba(255,255,255,0.2); display: inline-block; padding: 5px 15px; border-radius: 20px;">Alineado al CNEB 2026</p>
    </div>
    """, unsafe_allow_html=True)

# --- PANEL LATERAL (SIDEBAR UX) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=80)
    st.title("Panel de Control")
    st.subheader("Datos de la I.E.")
    ie_nombre = st.text_input("Institución Educativa", placeholder="Nombre de su colegio")
    distrito_sel = st.selectbox("Distrito Local", DISTRICTS)
    
    st.divider()
    st.subheader("Configuración Pedagógica")
    nivel = st.selectbox("Nivel", ["Inicial", "Primaria", "Secundaria"])
    grado = st.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"])
    area = st.selectbox("Área Curricular", ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Religión", "Arte y Cultura", "Educación Física", "Inglés", "Tutoría"])
    
    st.caption(f"Liderazgo: {LIDER}")

# --- MOTOR DE INTELIGENCIA (PROMPT UX OPTIMIZADO) ---
def ia_engine(tipo_doc, tema, contexto_extra=""):
    # Tu prompt maestro mejorado anteriormente...
    prompt_maestro = f"Actúa como un Especialista de la UGEL La Convención... Genera un {tipo_doc} para {area} en {grado} grado sobre {tema}. Contexto: {contexto_extra}."
    try:
        response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt_maestro}])
        return response.choices[0].message.content
    except:
        return "⚠️ Error: Verifique su API Key en Secrets."

def crear_word(contenido, titulo):
    doc = Document()
    doc.add_heading(titulo, 0)
    doc.add_paragraph(f"I.E.: {ie_nombre} | Distrito: {distrito_sel}").bold = True
    doc.add_paragraph("-" * 50)
    limpio = re.sub(r'[*#]', '', contenido)
    doc.add_paragraph(limpio)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- DISPOSICIÓN DE ELEMENTOS (WIREFRAME TEXTUAL) ---
tab1, tab2, tab3, tab4 = st.tabs(["📅 Programación Anual", "📂 Unidades", "📄 Sesiones", "📊 Evaluación & NEE"])

# Estructura repetible para cada pestaña
def render_tab(tipo, placeholder):
    st.markdown(f"<div class='content-card'><h3>Generar {tipo}</h3></div>", unsafe_allow_html=True)
    tema = st.text_input(f"Título o Tema Central de la {tipo}", placeholder=placeholder)
    extra = ""
    if tipo == "Sesión":
        extra = st.text_area("Describa la situación significativa o reto del aula")
    
    if st.button(f"🚀 Generar {tipo} Profesional"):
        if not ie_nombre:
            st.warning("Por favor, ingrese el nombre de su I.E. en el panel lateral.")
        else:
            with st.spinner("La IA está analizando los lineamientos del CNEB..."):
                res = ia_engine(tipo, tema, extra)
                st.markdown(res)
                file = crear_word(res, tipo.upper())
                st.download_button(f"📥 Descargar {tipo} en Word", file, file_name=f"{tipo}_{tema}.docx")

with tab1: render_tab("Programación Anual", "Ej: Fortalecemos nuestra identidad")
with tab2: render_tab("Unidad Didáctica", "Ej: Conocemos nuestras riquezas naturales")
with tab3: render_tab("Sesión", "Ej: Leemos textos sobre el café")
with tab4:
    st.subheader("Instrumentos de Evaluación")
    inst = st.selectbox("Tipo de instrumento", ["Lista de Cotejo", "Rúbrica Analítica"])
    t_eval = st.text_input("Competencia a evaluar")
    if st.button("📊 Crear Instrumento"):
        with st.spinner("Generando criterios..."):
            res = ia_engine(inst, t_eval)
            st.markdown(res)

# --- FOOTER ---
st.markdown(f"<div class='footer'><b>{NOMBRE_APP}</b> | Proyecto de Innovación Regional | {LIDER}</div>", unsafe_allow_html=True)

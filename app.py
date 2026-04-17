# ══════════════════════════════════════════════════════════════════
#  EDUPLAN IA — LA CONVENCIÓN (Versión Optimizada 2026)
#  Gestión: Prof. Percy Tapia
# ══════════════════════════════════════════════════════════════════

import io
import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt

# ── 1. CONFIGURACIÓN DE PÁGINA ──
st.set_page_config(
    page_title="EDUPLAN IA - LA CONVENCIÓN",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# ── 2. IDENTIDAD ──
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"

# ── 3. CLIENTE IA (Optimizado) ──
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    if not api_key:
        st.error("🔑 Error: ZHIPU_KEY no encontrada en Secrets.")
        return None
    return ZhipuAI(api_key=api_key)

client = get_client()

# ── 4. PROMPT MAESTRO (Ajustado para mayor rigor pedagógico) ──
PROMPT_SISTEMA = (
    "Eres un asistente pedagógico de élite experto en el CNEB del Perú. "
    "Tu objetivo es ayudar a docentes de La Convención, Cusco, a planificar con excelencia.\n\n"
    "REGLAS DE ORO:\n"
    "1. Usa TABLAS para la secuencia didáctica y propósitos.\n"
    "2. Incluye siempre Competencias, Capacidades, Desempeños y Criterios de Evaluación.\n"
    "3. Contextualiza: Menciona elementos de la zona (café, cacao, cultura machiguenga, ecoturismo).\n"
    "4. Tono: Profesional, motivador y técnicamente preciso."
)

# ── 5. ESTILOS CSS (Refinados) ──
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Sora', sans-serif !important; }

    .main { background-color: #f8fafc; }
    
    /* Animaciones */
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    
    /* Tarjetas de Contenido */
    .bloque-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        animation: fadeIn 0.5s ease-in;
    }

    /* Tabs Personalizados */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid #e2e8f0;
        color: #64748b;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #1e40af !important;
        border-bottom: 3px solid #3b82f6 !important;
    }

    /* Botones */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 8px;
        font-weight: 700;
        transition: 0.3s all;
        border: none;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ── 6. HERO HEADER (Modernizado) ──
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); 
                padding: 3rem; border-radius: 1.5rem; text-align: center; color: white; margin-bottom: 2rem;">
        <span style="background: rgba(255,215,0,0.2); color: #fbbf24; padding: 5px 15px; 
                     border-radius: 20px; font-size: 0.8rem; font-weight: 700;">
            TECNOLOGÍA PARA DOCENTES 2026
        </span>
        <h1 style="color: white; font-size: 2.8rem; margin: 1rem 0;">🏛️ {NOMBRE_APP}</h1>
        <p style="opacity: 0.8; font-size: 1.1rem;">
            Líder de Proyecto: <b>{LIDER}</b> | Alineado al CNEB Cusco
        </p>
    </div>
""", unsafe_allow_html=True)

# ── 7. LÓGICA DE NEGOCIO ──
def generar_word(titulo, contenido, datos):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    
    h = doc.add_heading(titulo, level=0)
    h.alignment = 1
    
    # Cuadro informativo
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    data_list = [
        ("I.E.", datos.get("ie")),
        ("Docente", LIDER),
        ("Grado/Nivel", f"{datos.get('grado')} - {datos.get('nivel')}"),
        ("Área", datos.get("area"))
    ]
    for i, (k, v) in enumerate(data_list):
        table.cell(i, 0).text = k
        table.cell(i, 1).text = str(v)
    
    doc.add_paragraph("\n")
    doc.add_paragraph(contenido)
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def llamar_ia(tipo, detalles):
    if not client: return "⚠️ Error: API no configurada."
    try:
        res = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Genera una {tipo} CNEB con estos datos: {detalles}"}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"❌ Error de IA: {str(e)}"

# ── 8. SIDEBAR ──
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    ie_nombre = st.text_input("I.E.", "IE La Convención")
    nivel = st.selectbox("Nivel", ["Inicial", "Primaria", "Secundaria"])
    
    if nivel == "Inicial":
        grados = ["3 años", "4 años", "5 años"]
        areas = ["Psicomotriz", "Personal Social", "Comunicación", "Matemática"]
    elif nivel == "Primaria":
        grados = [f"{i}ro" for i in range(1,7)]
        areas = ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Arte", "Religión"]
    else:
        grados = [f"{i}ro" for i in range(1,6)]
        areas = ["Matemática", "Comunicación", "Ciencias Sociales", "DPCC", "CyT", "EPT"]
        
    grado_sel = st.selectbox("Grado", grados)
    area_sel = st.selectbox("Área", areas)
    st.divider()
    st.info("📍 Ubicación: Quillabamba, Cusco")

# ── 9. TABS PRINCIPALES ──
t1, t2, t3 = st.tabs(["📅 ANUAL", "📂 UNIDAD", "🚀 SESIÓN"])

def render_tab(tipo_doc, label_btn, prompt_label, key_pre):
    st.markdown('<div class="bloque-card">', unsafe_allow_html=True)
    st.subheader(f"Generador de {tipo_doc}")
    user_input = st.text_area(prompt_label, key=f"input_{key_pre}", height=120)
    
    if st.button(label_btn, key=f"btn_{key_pre}"):
        if user_input:
            with st.spinner("🚀 La IA está redactando..."):
                info = f"Área: {area_sel}, Nivel: {nivel}, Grado: {grado_sel}, Contexto: {user_input}"
                resultado = llamar_ia(tipo_doc, info)
                st.markdown("### Resultado Generado")
                st.markdown(resultado)
                
                # Botón de descarga
                data_word = generar_word(tipo_doc, resultado, {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel})
                st.download_button(
                    label="📥 Descargar Documento (.docx)",
                    data=data_word,
                    file_name=f"{tipo_doc}_{grado_sel}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.warning("⚠️ Por favor, ingresa los detalles.")
    st.markdown('</div>', unsafe_allow_html=True)

with t1: render_tab("Programación Anual", "✨ GENERAR PLAN ANUAL", "Describe la situación significativa o retos del año:", "anual")
with t2: render_tab("Unidad Didáctica", "📂 GENERAR UNIDAD", "Título de la unidad y competencias a trabajar:", "unidad")
with t3: render_tab("Sesión de Aprendizaje", "🚀 GENERAR SESIÓN", "Tema de la sesión y propósito específico:", "sesion")

# ── 10. FOOTER ──
st.markdown(f"""
    <div style="text-align:center; padding: 20px; color: #64748b; font-size: 0.8rem;">
        EduPlan IA La Convención © 2026 | Desarrollado para el Magisterio de Cusco
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  EDUPLAN IA — LA CONVENCIÓN
#  Herramienta de Planificación Pedagógica CNEB con IA
#  Gestión: Prof. Percy Tapia | 2026
# ══════════════════════════════════════════════════════════════════

import io
import streamlit as st
from zhipuai import ZhipuAI
from docx import Document

# ── 1. CONFIGURACIÓN DE PÁGINA (debe ser lo primero de Streamlit) ──
st.set_page_config(
    page_title="EDUPLAN IA - LA CONVENCIÓN",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# ── 2. IDENTIDAD ──────────────────────────────────────────────────
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER      = "Prof. Percy Tapia"

# ── 3. CLIENTE IA (protegido contra key ausente) ──────────────────
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    if not api_key:
        st.warning("⚠️ Configura tu ZHIPU_KEY en los secretos de Streamlit para activar la IA.")
    return ZhipuAI(api_key=api_key)

client = get_client()

# ── 4. PROMPT MAESTRO ────────────────────────────────────────────
PROMPT_SISTEMA = (
    "Eres un asistente pedagógico inteligente especializado en educación peruana, "
    "diseñado para apoyar a docentes de Educación Básica Regular (EBR) en todos sus niveles y modalidades.\n\n"
    "Tu misión es facilitar la planificación, diseño y evaluación de experiencias de aprendizaje "
    "alineadas al Currículo Nacional de Educación Básica (CNEB) del MINEDU.\n\n"
    "PRINCIPIOS DE RESPUESTA:\n"
    "1. Claridad: Explica paso a paso con ejemplos contextualizados en el sistema peruano.\n"
    "2. Precisión: Usa terminología oficial del CNEB.\n"
    "3. Motivación: Tono cálido y positivo. Usa verbos de acción.\n"
    "4. Utilidad: Entrega material listo para el aula.\n\n"
    "FUNCIONES CLAVE:\n"
    "- Sesiones de Aprendizaje: Generar estructura completa (Inicio, Desarrollo, Cierre) con códigos CNEB.\n"
    "- Planificación Curricular: Elaborar unidades, proyectos y experiencias de aprendizaje articuladas.\n"
    "- Validación Normativa: Corregir y ajustar competencias y desempeños según el MINEDU.\n"
    "- Material Didáctico: Crear rúbricas, listas de cotejo, fichas de trabajo y estrategias de inclusión.\n"
    "- Enfoques Transversales: Alinear cada propuesta a los 7 enfoques del CNEB.\n\n"
    "ESTRUCTURA DE SALIDA:\n"
    "- Sesiones: Título, Duración, Propósitos, Criterios, Secuencia Didáctica y Evaluación.\n"
    "- Proyectos: Situación significativa, Producto, Secuencia de actividades y Evaluación Sumativa.\n"
    "- Correcciones: Feedback justificando con base en el CNEB.\n\n"
    "Contextualiza siempre en La Convención, Cusco, Perú."
)

# ══════════════════════════════════════════════════════════════════
#  5. ESTILOS CSS PREMIUM
# ══════════════════════════════════════════════════════════════════
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="st-"] {
        font-family: 'DM Sans', sans-serif;
    }
    .main { background: #f0f4ff; }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #ffffff;
        border-bottom: 2px solid #e8ecf4;
        padding: 0 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border-radius: 0;
        padding: 14px 26px;
        font-weight: 600;
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 3px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #1a237e !important;
        border-bottom: 3px solid #4f6ef7 !important;
    }

    /* TARJETA */
    .bloque-card {
        background: #ffffff;
        padding: 30px 28px;
        border-radius: 16px;
        border: 1px solid #e8ecf4;
        border-top: 4px solid #4f6ef7;
        margin-bottom: 20px;
        animation: fadeInUp 0.45s ease-out;
    }
    .bloque-card:hover {
        box-shadow: 0 8px 32px rgba(79,110,247,0.10);
    }

    /* BOTÓN PRINCIPAL */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1a237e 0%, #4f6ef7 100%);
        color: #ffffff;
        border: none;
        padding: 15px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f6ef7 0%, #7c3aed 100%);
        box-shadow: 0 8px 22px rgba(79,110,247,0.35);
        transform: translateY(-2px);
    }

    /* BOTÓN DESCARGA */
    .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(135deg, #f59e0b, #ef4444) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 13px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 18px rgba(239,68,68,0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* INPUTS */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1.5px solid #dde3f0 !important;
        border-radius: 9px !important;
        background: #f8faff !important;
        font-size: 14px !important;
        color: #0a0f2e !important;
    }
    .stSelectbox > div > div {
        border: 1.5px solid #dde3f0 !important;
        border-radius: 9px !important;
        background: #f8faff !important;
    }

    /* TÍTULOS */
    h1, h2, h3 {
        font-family: 'Sora', sans-serif !important;
        color: #0a0f2e !important;
        font-weight: 700 !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0f2e 0%, #0f1a4a 100%) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.80) !important;
    }
    [data-testid="stSidebar"] h2 {
        color: #ffd54f !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 13px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* SPINNER */
    .stSpinner > div {
        border-top-color: #4f6ef7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════
#  6. HERO HEADER — construido con concatenación (sin f-string HTML)
# ══════════════════════════════════════════════════════════════════
hero_html = (
    '<div style="background:linear-gradient(135deg,#0a0f2e 0%,#1a237e 42%,#6d28d9 78%,#db2777 100%);'
    'padding:60px 40px 68px;margin:-1rem -1rem 0 -1rem;position:relative;overflow:hidden;">'
    '<div style="position:absolute;inset:0;background-image:radial-gradient('
    'rgba(255,255,255,0.06) 1px,transparent 1px);background-size:26px 26px;"></div>'
    '<div style="position:relative;z-index:1;text-align:center;max-width:720px;margin:0 auto;">'
    '<div style="display:inline-block;background:rgba(255,255,255,0.12);'
    'border:1px solid rgba(255,255,255,0.22);color:#dde8ff;font-size:10px;font-weight:700;'
    'letter-spacing:2.5px;text-transform:uppercase;padding:6px 18px;border-radius:20px;margin-bottom:18px;">'
    '&#10022; Innovaci&#243;n Educativa 2026</div>'
    '<h1 style="font-family:Sora,sans-serif;font-size:2.6em;color:#ffffff;font-weight:700;'
    'margin:0 0 12px 0;line-height:1.15;letter-spacing:-0.5px;">'
    '&#127963; ' + NOMBRE_APP + '</h1>'
    '<p style="color:rgba(255,255,255,0.70);font-size:1.05em;margin:0 0 30px 0;'
    'letter-spacing:0.3px;line-height:1.6;">'
    'Gesti&#243;n Pedag&#243;gica: <strong style="color:#ffd54f;">' + LIDER + '</strong>'
    '&nbsp;&nbsp;&middot;&nbsp;&nbsp;Planificaci&#243;n CNEB con Inteligencia Artificial</p>'
    '<div style="display:flex;gap:36px;justify-content:center;flex-wrap:wrap;">'
    '<div style="text-align:center;">'
    '<div style="font-family:Sora,sans-serif;font-size:1.7em;font-weight:700;color:#ffd54f;">CNEB</div>'
    '<div style="font-size:10px;color:rgba(255,255,255,0.50);text-transform:uppercase;letter-spacing:1px;">Alineado</div>'
    '</div>'
    '<div style="width:1px;background:rgba(255,255,255,0.18);"></div>'
    '<div style="text-align:center;">'
    '<div style="font-family:Sora,sans-serif;font-size:1.7em;font-weight:700;color:#fb923c;">3</div>'
    '<div style="font-size:10px;color:rgba(255,255,255,0.50);text-transform:uppercase;letter-spacing:1px;">M&#243;dulos</div>'
    '</div>'
    '<div style="width:1px;background:rgba(255,255,255,0.18);"></div>'
    '<div style="text-align:center;">'
    '<div style="font-family:Sora,sans-serif;font-size:1.7em;font-weight:700;color:#a5b4fc;">IA</div>'
    '<div style="font-size:10px;color:rgba(255,255,255,0.50);text-transform:uppercase;letter-spacing:1px;">Generativa</div>'
    '</div>'
    '</div>'
    '</div></div>'
)
st.markdown(hero_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  7. FUNCIONES DE LÓGICA
# ══════════════════════════════════════════════════════════════════
def generar_word(titulo: str, contenido: str, datos: dict) -> io.BytesIO:
    """Genera un archivo .docx en memoria y lo devuelve como BytesIO."""
    doc = Document()
    enc = doc.add_heading(titulo, level=0)
    enc.alignment = 1

    tabla = doc.add_table(rows=4, cols=2)
    tabla.style = "Table Grid"
    filas_info = [
        ("Institución Educativa:", datos.get("ie", "---")),
        ("Docente:",               LIDER),
        ("Nivel / Grado:",         str(datos.get("nivel", "")) + " - " + str(datos.get("grado", ""))),
        ("Área Curricular:",       datos.get("area", "---")),
    ]
    for i, (etiqueta, valor) in enumerate(filas_info):
        tabla.cell(i, 0).text = etiqueta
        tabla.cell(i, 1).text = valor

    doc.add_paragraph("")
    doc.add_paragraph(contenido)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def llamar_ia(tipo: str, detalles: str) -> str:
    """Llama a la API de ZhipuAI y devuelve el texto generado."""
    try:
        respuesta = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {
                    "role": "user",
                    "content": (
                        "Genera un(a) " + tipo + " completo(a) y detallado(a) "
                        "para el CNEB peruano con los siguientes datos:\n\n" + detalles
                    ),
                },
            ],
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return "⚠️ Error al conectar con la IA: " + str(e) + "\n\nVerifica tu API Key en los secretos de Streamlit."


# ══════════════════════════════════════════════════════════════════
#  8. SIDEBAR — Panel de Control
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<h2 style='text-align:center;padding:8px 0 4px;'>&#9881;&#65039; Panel de Control</h2>",
        unsafe_allow_html=True,
    )
    st.divider()

    ie_nombre = st.text_input("Institución Educativa", value="IE La Convención")
    nivel     = st.selectbox("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"])

    if nivel == "Inicial":
        grados = ["3 años", "4 años", "5 años"]
        areas  = ["Personal Social", "Psicomotriz", "Comunicación", "Matemática"]
    elif nivel == "Primaria":
        grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
        areas  = [
            "Matemática", "Comunicación", "Personal Social",
            "Ciencia y Tecnología", "Religión", "Arte y Cultura", "Inglés",
        ]
    else:
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
        areas  = [
            "Matemática", "Comunicación", "Ciencias Sociales",
            "DPCC", "Ciencia y Tecnología", "EPT", "Inglés",
        ]

    grado_sel = st.selectbox("Grado / Sección", grados)
    area_sel  = st.selectbox("Área Curricular", areas)
    st.divider()
    st.info("📍 Contexto: La Convención, Cusco — Perú")


# ══════════════════════════════════════════════════════════════════
#  9. CONTENIDO PRINCIPAL — Tres Tabs
# ══════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "📅  PROGRAMACIÓN ANUAL",
    "📂  UNIDAD DIDÁCTICA",
    "🚀  SESIÓN DE APRENDIZAJE",
])

# ─────────────────────────────────────────
#  TAB 1: PROGRAMACIÓN ANUAL
# ─────────────────────────────────────────
with tab1:
    st.markdown("<div class='bloque-card'>", unsafe_allow_html=True)
    st.subheader("📋 Programación Anual")
    st.caption(
        "Genera tu programación curricular completa alineada al CNEB con situaciones "
        "significativas contextualizadas a La Convención, Cusco."
    )
    st.markdown("---")

    situacion = st.text_area(
        "Situación Significativa (reto del año)",
        placeholder=(
            "Ej: Los estudiantes de La Convención enfrentan la pérdida de biodiversidad "
            "en su comunidad y necesitan proponer soluciones sostenibles..."
        ),
        height=110,
        key="situacion_anual",
    )

    if st.button("✨ GENERAR PROGRAMACIÓN ANUAL", key="btn_anual"):
        if situacion.strip():
            with st.spinner("Generando programación con IA... esto puede tardar unos segundos."):
                detalles = (
                    "Nivel: " + nivel + " | Grado: " + grado_sel + " | "
                    "Área: " + area_sel + " | IE: " + ie_nombre + " | "
                    "Situación significativa: " + situacion
                )
                resultado = llamar_ia("Programación Anual", detalles)

            st.success("✅ Programación generada correctamente.")
            st.markdown(resultado)
            st.download_button(
                label="📥 Descargar Programación Anual (.docx)",
                data=generar_word(
                    "Programación Anual",
                    resultado,
                    {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel},
                ),
                file_name="Plan_Anual_" + nivel + "_" + grado_sel + ".docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        else:
            st.error("⚠️ Por favor, describe la situación significativa antes de generar.")

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  TAB 2: UNIDAD DIDÁCTICA
# ─────────────────────────────────────────
with tab2:
    st.markdown("<div class='bloque-card'>", unsafe_allow_html=True)
    st.subheader("📦 Unidad de Aprendizaje")
    st.caption(
        "Diseña unidades integradas con competencias, capacidades, criterios de evaluación "
        "y actividades secuenciadas listas para el aula."
    )
    st.markdown("---")

    titulo_u = st.text_input(
        "Título de la Unidad",
        placeholder="Ej: Conocemos la biodiversidad de nuestra selva convenciana",
        key="titulo_unidad",
    )

    if st.button("📂 GENERAR UNIDAD DIDÁCTICA", key="btn_unidad"):
        if titulo_u.strip():
            with st.spinner("Estructurando la unidad didáctica..."):
                detalles = (
                    "Título: " + titulo_u + " | Área: " + area_sel + " | "
                    "Grado: " + grado_sel + " | Nivel: " + nivel + " | IE: " + ie_nombre
                )
                resultado = llamar_ia("Unidad Didáctica", detalles)

            st.success("✅ Unidad generada correctamente.")
            st.markdown(resultado)
            st.download_button(
                label="📥 Descargar Unidad Didáctica (.docx)",
                data=generar_word(
                    titulo_u,
                    resultado,
                    {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel},
                ),
                file_name="Unidad_" + nivel + "_" + grado_sel + ".docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        else:
            st.error("⚠️ Ingrese un título para la unidad antes de generar.")

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  TAB 3: SESIÓN DE APRENDIZAJE
# ─────────────────────────────────────────
with tab3:
    st.markdown("<div class='bloque-card'>", unsafe_allow_html=True)
    st.subheader("📝 Sesión de Aprendizaje")
    st.caption(
        "Genera la estructura completa: Inicio, Desarrollo y Cierre con estrategias "
        "diferenciadas, materiales y criterios de evaluación."
    )
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    titulo_s = col1.text_input(
        "Título de la Sesión",
        placeholder="Ej: Elaboramos abono orgánico con residuos domésticos",
        key="titulo_sesion",
    )
    duracion = col2.text_input("Duración (min)", value="90", key="duracion_sesion")

    nee = st.toggle(
        "🧠 Incluir adaptaciones para Necesidades Educativas Especiales (NEE)",
        key="toggle_nee",
    )

    if st.button("🚀 GENERAR SESIÓN DE APRENDIZAJE", key="btn_sesion"):
        if titulo_s.strip():
            with st.spinner("Redactando la sesión de aprendizaje paso a paso..."):
                adaptacion = "Sí, incluir adaptaciones curriculares" if nee else "No"
                detalles = (
                    "Título: " + titulo_s + " | Duración: " + str(duracion) + " minutos | "
                    "Atención NEE: " + adaptacion + " | "
                    "Área: " + area_sel + " | Grado: " + grado_sel + " | "
                    "Nivel: " + nivel + " | IE: " + ie_nombre
                )
                resultado = llamar_ia("Sesión de Aprendizaje", detalles)

            st.success("✅ Sesión generada correctamente.")
            st.markdown(resultado)
            st.download_button(
                label="📥 Descargar Sesión de Aprendizaje (.docx)",
                data=generar_word(
                    titulo_s,
                    resultado,
                    {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel},
                ),
                file_name="Sesion_" + nivel + "_" + grado_sel + ".docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        else:
            st.error("⚠️ Ingrese un título para la sesión antes de generar.")

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  10. FOOTER
# ══════════════════════════════════════════════════════════════════
footer_html = (
    '<br>'
    '<div style="background:#0a0f2e;color:rgba(255,255,255,0.42);text-align:center;'
    'padding:18px 20px;border-radius:12px;font-size:12px;letter-spacing:0.3px;margin-top:12px;">'
    'EduPlan IA &nbsp;&middot;&nbsp; Provincia de La Convenci&#243;n, Cusco, Per&#250; &nbsp;&middot;&nbsp; '
    'Gesti&#243;n <strong style="color:#ffd54f;">' + LIDER + '</strong> &nbsp;&middot;&nbsp; &copy; 2026'
    '</div><br>'
)
st.markdown(footer_html, unsafe_allow_html=True)

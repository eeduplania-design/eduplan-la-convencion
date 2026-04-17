import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, RGBColor
import io

# --- CONFIGURACIÓN DE IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🎓")

# --- PROMPT MAESTRO PROFESIONAL ---
PROMPT_SISTEMA = """
Eres un asistente pedagógico inteligente especializado en educación peruana, 
diseñado para apoyar a docentes de Educación Básica Regular (EBR) en todos sus niveles y modalidades.

Tu misión es facilitar la planificación, diseño y evaluación de experiencias de aprendizaje 
alineadas al Currículo Nacional de Educación Básica (CNEB) del MINEDU.

### PRINCIPIOS DE RESPUESTA:
1. **Claridad:** Explica paso a paso con ejemplos contextualizados en el sistema peruano (áreas, competencias y capacidades).
2. **Precisión:** Usa terminología oficial del CNEB. Verifica que estándares y desempeños correspondan al grado/ciclo solicitado.
3. **Motivación:** Tono cálido y positivo. Usa verbos de acción: "Crea", "Transforma", "Diseña".
4. **Utilidad:** Entrega material listo para el aula (fichas, rúbricas, plantillas).

### FUNCIONES CLAVE:
- **Sesiones de Aprendizaje:** Generar estructura completa (Inicio, Desarrollo, Cierre) con códigos CNEB.
- **Planificación Curricular:** Elaborar unidades, proyectos y experiencias de aprendizaje articuladas.
- **Validación Normativa:** Corregir y ajustar competencias y desempeños según documentos del MINEDU.
- **Material Didáctico:** Crear rúbricas, listas de cotejo, fichas de trabajo y estrategias de inclusión.
- **Enfoques Transversales:** Alinear cada propuesta a los 7 enfoques del CNEB.

### ESTILO Y FORMATO:
- **Estructura:** Usa encabezados, negritas y tablas para facilitar la lectura.
- **Contextualización:** Referencia festividades, realidades regionales (costa, sierra, selva) y contextos urbanos/rurales de Perú.
- **Interacción:** Si falta información (grado, ciclo, área), solicítala antes de generar el contenido.

### ESTRUCTURA DE SALIDA SEGÚN PEDIDO:
- **Sesiones:** Título, Duración, Propósitos (Competencias/Capacidades), Criterios, Secuencia Didáctica y Evaluación.
- **Proyectos:** Situación significativa, Producto, Secuencia de actividades y Evaluación Sumativa.
- **Correcciones:** Feedback justificando con base en el CNEB.
"""

# ══════════════════════════════════════════════════════════════════
#  ESTILOS CSS — DISEÑO PREMIUM (inspirado en agencia digital)
# ══════════════════════════════════════════════════════════════════
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="st-"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* ── FONDO GENERAL ── */
    .main {
        background: #f0f4ff;
    }

    /* ── ANIMACIÓN ENTRADA ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1.5px solid #e8ecf4;
        background: #ffffff;
        padding: 0 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border-radius: 0;
        padding: 16px 28px;
        font-weight: 600;
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        border: none;
        border-bottom: 2.5px solid transparent;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #1a237e !important;
        border-bottom: 2.5px solid #4f6ef7 !important;
    }

    /* ── TARJETAS ── */
    .card {
        background: #ffffff;
        padding: 28px;
        border-radius: 16px;
        border: 1px solid #e8ecf4;
        border-top: 3px solid #4f6ef7;
        margin-bottom: 24px;
        animation: fadeInUp 0.5s ease-out;
        transition: box-shadow 0.3s ease;
    }

    .card:hover {
        box-shadow: 0 8px 30px rgba(79, 110, 247, 0.12);
    }

    /* ── BOTÓN PRINCIPAL ── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1a237e 0%, #4f6ef7 100%);
        color: #ffffff;
        border: none;
        padding: 16px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #4f6ef7 0%, #a855f7 100%);
        box-shadow: 0 8px 24px rgba(79, 110, 247, 0.35);
        transform: translateY(-2px);
    }

    /* ── INPUTS & SELECTS ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background: #f8faff !important;
        font-size: 14px !important;
        color: #0a0f2e !important;
    }

    .stSelectbox > div > div {
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background: #f8faff !important;
    }

    /* ── TÍTULOS ── */
    h1, h2, h3 {
        font-family: 'Sora', sans-serif !important;
        color: #0a0f2e !important;
        font-weight: 700 !important;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #0a0f2e !important;
    }

    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.85) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffd54f !important;
        font-family: 'Sora', sans-serif !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] .stInfo {
        background: rgba(79, 110, 247, 0.15) !important;
        border-left: 3px solid #4f6ef7 !important;
        border-radius: 8px !important;
        color: #a5b4fc !important;
    }

    /* ── DOWNLOAD BUTTON ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #ffd54f, #ff8a65) !important;
        color: #0a0f2e !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    .stDownloadButton > button:hover {
        box-shadow: 0 6px 18px rgba(255, 138, 101, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* ── INFO / ALERT ── */
    .stInfo {
        background: rgba(79, 110, 247, 0.08) !important;
        border-left: 3px solid #4f6ef7 !important;
        border-radius: 8px !important;
    }

    .stError {
        border-left: 3px solid #e53e3e !important;
        border-radius: 8px !important;
    }

    /* ── SPINNER ── */
    .stSpinner > div {
        border-top-color: #4f6ef7 !important;
    }

    /* ── TOGGLE ── */
    .stToggle > label {
        color: #0a0f2e !important;
        font-weight: 500 !important;
    }

    /* ── DIVIDER ── */
    hr {
        border-color: #e8ecf4 !important;
    }
    </style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  HEADER HERO — gradiente azul marino → morado → magenta
# ══════════════════════════════════════════════════════════════════
st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0a0f2e 0%, #1a237e 40%, #7b1fa2 78%, #e91e8c 100%);
        padding: 64px 40px 72px;
        margin: -1rem -1rem 0 -1rem;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position:absolute;inset:0;
            background-image: radial-gradient(rgba(255,255,255,0.07) 1px, transparent 1px);
            background-size: 28px 28px;
        "></div>

        <div style="position:relative;z-index:1;text-align:center;max-width:700px;margin:0 auto;">
            <div style="
                display:inline-block;
                background:rgba(255,255,255,0.12);
                border:1px solid rgba(255,255,255,0.25);
                color:#e0e8ff;
                font-size:11px;font-weight:600;
                letter-spacing:2px;text-transform:uppercase;
                padding:6px 18px;border-radius:20px;margin-bottom:20px;
            ">✦ Innovación Educativa 2026</div>

            <h1 style="
                font-family:'Sora',sans-serif;
                font-size:2.7em;
                color:#ffffff;
                font-weight:700;
                margin:0 0 14px 0;
                line-height:1.15;
                letter-spacing:-0.5px;
            ">🏛️ {NOMBRE_APP}</h1>

            <p style="
                color:rgba(255,255,255,0.72);
                font-size:1.05em;
                margin:0;
                letter-spacing:0.3px;
                line-height:1.6;
            ">Gestión Pedagógica: <strong style='color:#ffd54f;'>{LIDER}</strong>
            &nbsp;·&nbsp; Herramienta de Planificación CNEB con IA</p>

            <div style="display:flex;gap:40px;justify-content:center;margin-top:32px;">
                <div style="text-align:center;">
                    <div style="font-family:'Sora',sans-serif;font-size:1.8em;font-weight:700;color:#ffd54f;">CNEB</div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.55);text-transform:uppercase;letter-spacing:1px;">Alineado</div>
                </div>
                <div style="width:1px;background:rgba(255,255,255,0.15);"></div>
                <div style="text-align:center;">
                    <div style="font-family:'Sora',sans-serif;font-size:1.8em;font-weight:700;color:#ff8a65;">3</div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.55);text-transform:uppercase;letter-spacing:1px;">Módulos</div>
                </div>
                <div style="width:1px;background:rgba(255,255,255,0.15);"></div>
                <div style="text-align:center;">
                    <div style="font-family:'Sora',sans-serif;font-size:1.8em;font-weight:700;color:#a5b4fc;">IA</div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.55);text-transform:uppercase;letter-spacing:1px;">Generativa</div>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  FUNCIONES DE LÓGICA
# ══════════════════════════════════════════════════════════════════
def generar_word_profesional(titulo, contenido, datos):
    doc = Document()
    header = doc.add_heading(titulo, 0)
    header.alignment = 1

    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    info = [
        ("Institución Educativa:", datos.get("ie", "---")),
        ("Docente:", LIDER),
        ("Nivel/Grado:", f"{datos.get('nivel')} - {datos.get('grado')}"),
        ("Área:", datos.get("area", "---"))
    ]
    for i, (label, val) in enumerate(info):
        table.cell(i, 0).text = label
        table.cell(i, 1).text = val

    doc.add_paragraph("\n")
    doc.add_paragraph(contenido)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def llamar_ia_pedagogica(tipo, detalles):
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Generar {tipo} CNEB detallado con estos datos: {detalles}"}
            ]
        )
        return response.choices[0].message.content
    except Exception:
        return "⚠️ Error de conexión. Verifique su API Key o conexión a internet."


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR — Panel de Control
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>⚙️ Panel de Control</h2>", unsafe_allow_html=True)
    st.divider()

    ie_nombre = st.text_input("Institución Educativa", "IE La Convención")
    nivel = st.selectbox("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"])

    if nivel == "Inicial":
        grados = ["3 años", "4 años", "5 años"]
        areas  = ["Personal Social", "Psicomotriz", "Comunicación", "Matemática"]
    elif nivel == "Primaria":
        grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
        areas  = ["Matemática", "Comunicación", "Personal Social",
                  "Ciencia y Tecnología", "Religión", "Arte", "Inglés"]
    else:
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
        areas  = ["Matemática", "Comunicación", "Ciencias Sociales",
                  "DPCC", "Ciencia y Tecnología", "EPT", "Inglés"]

    grado_sel = st.selectbox("Grado / Sección", grados)
    area_sel  = st.selectbox("Área Curricular", areas)

    st.info("📍 Contexto: La Convención, Cusco")


# ══════════════════════════════════════════════════════════════════
#  CONTENIDO PRINCIPAL — Tabs
# ══════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "📅  PROGRAMACIÓN ANUAL",
    "📂  UNIDAD DIDÁCTICA",
    "🚀  SESIÓN DE APRENDIZAJE"
])

# ── TAB 1: PROGRAMACIÓN ANUAL ──────────────────────────────────
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📋 Planificación Anual")
    st.caption("Genera tu programación curricular completa alineada al CNEB con situaciones significativas contextualizadas a La Convención.")

    situacion = st.text_area(
        "Situación Significativa (Reto del año)",
        placeholder="Describa el desafío principal para sus estudiantes este año...",
        height=100
    )

    if st.button("✨ GENERAR PLANIFICACIÓN ANUAL", key="btn_anual"):
        if situacion.strip():
            with st.spinner("🚀 Procesando datos con IA..."):
                detalles  = f"Nivel: {nivel}, Grado: {grado_sel}, Área: {area_sel}, Situación: {situacion}"
                resultado = llamar_ia_pedagogica("Programación Anual", detalles)
                st.markdown(resultado)
                st.download_button(
                    "📥 Descargar Plan Anual (.docx)",
                    generar_word_profesional(
                        "Plan Anual",
                        resultado,
                        {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}
                    ),
                    "Plan_Anual.docx"
                )
        else:
            st.error("⚠️ Ingrese la situación significativa para continuar.")
    st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 2: UNIDAD DIDÁCTICA ────────────────────────────────────
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📦 Unidad de Aprendizaje")
    st.caption("Diseña unidades integradas con competencias, capacidades y criterios de evaluación listos para el aula.")

    titulo_u = st.text_input(
        "Título de la Unidad",
        placeholder="Ej: Conocemos la biodiversidad de nuestra selva"
    )

    if st.button("📂 GENERAR UNIDAD DIDÁCTICA", key="btn_unidad"):
        if titulo_u.strip():
            with st.spinner("🛠️ Estructurando Unidad..."):
                detalles  = f"Unidad: {titulo_u}, Área: {area_sel}, Grado: {grado_sel}, Nivel: {nivel}"
                resultado = llamar_ia_pedagogica("Unidad Didáctica", detalles)
                st.markdown(resultado)
                st.download_button(
                    "📥 Descargar Unidad (.docx)",
                    generar_word_profesional(
                        titulo_u,
                        resultado,
                        {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}
                    ),
                    "Unidad.docx"
                )
        else:
            st.error("⚠️ Ingrese un título para la unidad.")
    st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 3: SESIÓN DE APRENDIZAJE ──────────────────────────────
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Sesión de Aprendizaje")
    st.caption("Estructura completa: Inicio, Desarrollo y Cierre con estrategias diferenciadas y atención a la diversidad.")

    c1, c2 = st.columns([3, 1])
    titulo_s = c1.text_input(
        "Título de la Sesión",
        placeholder="Ej: Elaboramos abono orgánico con residuos domésticos"
    )
    duracion = c2.text_input("Minutos", "90")

    nee = st.toggle("🧠 Atención a la Diversidad (NEE) — Incluir adaptaciones curriculares")

    if st.button("🚀 GENERAR SESIÓN MAESTRA", key="btn_sesion"):
        if titulo_s.strip():
            with st.spinner("🖋️ Redactando sesión paso a paso..."):
                detalles  = (
                    f"Sesión: {titulo_s}, Duración: {duracion} min, "
                    f"NEE: {nee}, Área: {area_sel}, Grado: {grado_sel}, Nivel: {nivel}"
                )
                resultado = llamar_ia_pedagogica("Sesión de Aprendizaje", detalles)
                st.markdown(resultado)
                st.download_button(
                    "📥 Descargar Sesión (.docx)",
                    generar_word_profesional(
                        titulo_s,
                        resultado,
                        {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}
                    ),
                    "Sesion.docx"
                )
        else:
            st.error("⚠️ Ingrese un título para la sesión.")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════
st.markdown(f"""
    <br>
    <div style="
        background: #0a0f2e;
        color: rgba(255,255,255,0.45);
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        font-size: 12px;
        letter-spacing: 0.3px;
        margin-top: 16px;
    ">
        EduPlan IA — Provincia de La Convención, Cusco &nbsp;·&nbsp;
        Gestión <strong style='color:#ffd54f;'>{LIDER}</strong> © 2026
    </div>
""", unsafe_allow_html=True)

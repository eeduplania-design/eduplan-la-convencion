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

# --- ESTILOS CSS CON ANIMACIONES Y COLORES PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif;
    }

    .main { 
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
    }

    /* Animación de entrada para tarjetas */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 12px 12px 0 0;
        padding: 15px 30px;
        font-weight: 600;
        color: #1e3a8a;
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
    }

    .stTabs [aria-selected="true"] { 
        background-color: #1e3a8a !important; 
        color: #fbbf24 !important; /* Dorado alegre */
        box-shadow: 0 -4px 10px rgba(0,0,0,0.1);
    }

    /* Tarjetas con Efecto de Elevación */
    .card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-left: 8px solid #1e3a8a;
        margin-bottom: 25px;
        animation: fadeInUp 0.6s ease-out;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }

    /* Botones con Gradiente y Brillo */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 18px;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.4s ease;
        text-transform: uppercase;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
        transform: scale(1.01);
    }

    /* Títulos Sobrios */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 600;
    }
    
    /* Sidebar Estilizada */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: white;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #fbbf24;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA ---
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
    except:
        return "⚠️ Error de conexión. Verifique su API Key o conexión a internet."

# --- INTERFAZ PRINCIPAL ---
st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <h1 style="font-size: 3em; margin-bottom: 0;">🏛️ {NOMBRE_APP}</h1>
        <p style="color: #64748b; font-size: 1.2em;">Gestión Pedagógica: <b>{LIDER}</b> | Innovación 2026</p>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR PROFESIONAL ---
with st.sidebar:
    st.markdown(f"<h2 style='text-align: center;'>⚙️ Panel de Control</h2>", unsafe_allow_html=True)
    st.divider()
    ie_nombre = st.text_input("Institución Educativa", "IE La Convención")
    nivel = st.selectbox("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"])
    
    # Lógica de Áreas y Grados mejorada
    if nivel == "Inicial":
        grados, areas = ["3 años", "4 años", "5 años"], ["Personal Social", "Psicomotriz", "Comunicación", "Matemática"]
    elif nivel == "Primaria":
        grados, areas = ["1ro", "2do", "3ro", "4to", "5to", "6to"], ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Religión", "Arte", "Inglés"]
    else:
        grados, areas = ["1ro", "2do", "3ro", "4to", "5to"], ["Matemática", "Comunicación", "Ciencias Sociales", "DPCC", "Ciencia y Tecnología", "EPT", "Inglés"]
    
    grado_sel = st.selectbox("Grado/Sección", grados)
    area_sel = st.selectbox("Área Curricular", areas)
    st.info(f"📍 Contexto: La Convención, Cusco")

# --- CONTENIDO DINÁMICO ---
tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "🚀 SESIÓN DE APRENDIZAJE"])

with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📋 Planificación Anual")
    situacion = st.text_area("Situación Significativa (Reto del año)", placeholder="Describa el desafío principal para sus estudiantes...")
    if st.button("✨ GENERAR PLANIFICACIÓN ANUAL"):
        with st.spinner("🚀 Procesando datos con IA..."):
            detalles = f"Nivel: {nivel}, Grado: {grado_sel}, Área: {area_sel}, Situación: {situacion}"
            resultado = llamar_ia_pedagogica("Programación Anual", detalles)
            st.markdown(resultado)
            st.download_button("📥 Descargar Plan Anual", generar_word_profesional("Plan Anual", resultado, {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}), "Plan_Anual.docx")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📦 Unidad de Aprendizaje")
    titulo_u = st.text_input("Título de la Unidad", placeholder="Ej: Conocemos la biodiversidad de nuestra selva")
    if st.button("📂 GENERAR UNIDAD DIDÁCTICA"):
        with st.spinner("🛠️ Estructurando Unidad..."):
            detalles = f"Unidad: {titulo_u}, Área: {area_sel}, Grado: {grado_sel}, Nivel: {nivel}"
            resultado = llamar_ia_pedagogica("Unidad Didáctica", detalles)
            st.markdown(resultado)
            st.download_button("📥 Descargar Unidad", generar_word_profesional(titulo_u, resultado, {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}), "Unidad.docx")
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📝 Sesión de Aprendizaje")
    c1, c2 = st.columns(2)
    titulo_s = c1.text_input("Título de la Sesión", placeholder="Ej: Elaboramos abono orgánico con residuos")
    duracion = c2.text_input("Minutos", "90")
    
    nee = st.toggle("🧠 Atención a la Diversidad (NEE)")
    
    if st.button("🚀 GENERAR SESIÓN MAESTRA"):
        if titulo_s:
            with st.spinner("🖋️ Redactando sesión paso a paso..."):
                detalles = f"Sesión: {titulo_s}, Duración: {duracion}, NEE: {nee}, Área: {area_sel}, Grado: {grado_sel}, Nivel: {nivel}"
                resultado = llamar_ia_pedagogica("Sesión de Aprendizaje", detalles)
                st.markdown(resultado)
                st.download_button("📥 Descargar Sesión", generar_word_profesional(titulo_s, resultado, {"ie": ie_nombre, "nivel": nivel, "grado": grado_sel, "area": area_sel}), f"Sesion.docx")
        else:
            st.error("⚠️ Ingrese un título para continuar.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"<br><hr><center><small>EduPlan IA - Desarrollado para la Provincia de La Convención, Cusco. Gestión {LIDER} © 2026</small></center>", unsafe_allow_html=True)

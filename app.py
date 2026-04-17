# ══════════════════════════════════════════════════════════════════
#  EDUPLAN IA — LA CONVENCIÓN (EDICIÓN PREMIUM)
#  Herramienta de Planificación Pedagógica CNEB con IA
#  Gestión: Prof. Percy Tapia | 2026
# ══════════════════════════════════════════════════════════════════

import io
import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ── 1. CONFIGURACIÓN DE PÁGINA ──
st.set_page_config(
    page_title="EDUPLAN IA - LA CONVENCIÓN",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# ── 2. CONSTANTES E IDENTIDAD ──
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER      = "Prof. Percy Tapia"

# ── 3. CLIENTE IA ──
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ZHIPU_KEY", "")
    if not api_key:
        return None
    return ZhipuAI(api_key=api_key)

client = get_client()

# ── 4. PROMPT MAESTRO (OPTIMIZADO) ──
PROMPT_SISTEMA = ( ""
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
    ""
)

# ── 5. ESTILOS CSS PERSONALIZADOS (UI/UX) ──
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Sora:wght@700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #f7f9fc; }
    
    /* Contenedor de Vista Previa */
    .preview-box {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #e1e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 20px;
        color: #1a202c;
    }

    /* Botones Premium */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; border: none; border-radius: 8px;
        padding: 0.6rem 1rem; font-weight: 600; width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }

    /* Tarjetas de Tabs */
    .tab-content {
        background: white;
        padding: 2rem;
        border-radius: 0 0 15px 15px;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# ── 6. LÓGICA DE ARCHIVOS ──
def generar_word(titulo: str, contenido: str, datos: dict) -> io.BytesIO:
    doc = Document()
    
    # Encabezado institucional
    header = doc.add_heading(NOMBRE_APP, level=1)
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Tabla de datos informativos
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    info = [
        ("I.E.:", datos.get("ie")),
        ("DOCENTE:", LIDER),
        ("ÁREA / GRADO:", f"{datos.get('area')} - {datos.get('grado')}"),
        ("FECHA:", "2026")
    ]
    for i, (label, val) in enumerate(info):
        table.cell(i, 0).text = label
        table.cell(i, 1).text = str(val)

    doc.add_paragraph("\n")
    doc.add_heading(titulo, level=2)
    
    # Limpieza de asteriscos de Markdown para el Word
    limpio = contenido.replace("**", "").replace("#", "")
    doc.add_paragraph(limpio)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ── 7. HEADER ──
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 3rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
        <h1 style="font-family: 'Sora'; margin: 0; font-size: 2.5rem;">🎓 {NOMBRE_APP}</h1>
        <p style="opacity: 0.8; font-size: 1.1rem; margin-top: 10px;">Gestión Pedagógica Avanzada con Inteligencia Artificial</p>
        <div style="display: flex; justify-content: center; gap: 20px; margin-top: 15px;">
            <span style="background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem;">📍 La Convención, Cusco</span>
            <span style="background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 20px; font-size: 0.8rem;">✔️ CNEB 2026</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ── 8. SIDEBAR ──
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=80)
    st.title("Configuración")
    ie_nombre = st.text_input("I.E. / Institución", "IE La Convención")
    nivel = st.selectbox("Nivel", ["Inicial", "Primaria", "Secundaria"])
    
    niveles_map = {
        "Inicial": (["3 años", "4 años", "5 años"], ["Comunicación", "Matemática", "Personal Social", "Psicomotriz"]),
        "Primaria": (["1ro", "2do", "3ro", "4to", "5to", "6to"], ["Comunicación", "Matemática", "Personal Social", "Ciencia y Tecnología", "Arte y Cultura"]),
        "Secundaria": (["1ro", "2do", "3ro", "4to", "5to"], ["Matemática", "Comunicación", "Ciencias Sociales", "DPCC", "Ciencia y Tecnología", "EPT"])
    }
    
    grados, areas = niveles_map[nivel]
    grado_sel = st.selectbox("Grado", grados)
    area_sel = st.selectbox("Área", areas)
    
    st.markdown("---")
    st.caption(f"Desarrollado por {LIDER}")

# ── 9. CUERPO PRINCIPAL (TABS) ──
tab_names = ["📅 Plan Anual", "📦 Unidad", "🚀 Sesión de Aprendizaje"]
tabs = st.tabs(tab_names)

def render_generador(tipo):
    st.subheader(f"Generador de {tipo}")
    
    if tipo == "Sesión de Aprendizaje":
        col_t, col_d = st.columns([3,1])
        tema = col_t.text_input("Tema de la sesión", placeholder="Ej: Las maravillas del Pongo de Mainique")
        tiempo = col_d.text_input("Minutos", "90")
    else:
        tema = st.text_area("Descripción / Situación Significativa", placeholder="Describe brevemente lo que deseas planificar...")
        tiempo = None

    if st.button(f"✨ GENERAR VISTA PREVIA"):
        if not client:
            st.error("❌ API Key no encontrada. Configúrala en secrets.")
            return

        if tema:
            with st.spinner("🧠 La IA está redactando tu documento siguiendo el CNEB..."):
                detalles = f"Tipo: {tipo}, Tema: {tema}, Área: {area_sel}, Nivel: {nivel}, Grado: {grado_sel}, IE: {ie_nombre}"
                if tiempo: detalles += f", Duración: {tiempo} min"
                
                # Llamada a la IA
                try:
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[
                            {"role": "system", "content": PROMPT_SISTEMA},
                            {"role": "user", "content": f"Genera: {detalles}"}
                        ]
                    )
                    contenido_ia = response.choices[0].message.content
                    
                    # --- MOSTRAR VISTA PREVIA ---
                    st.markdown("### 👁️ Vista Previa del Documento")
                    st.markdown(f'<div class="preview-box">{contenido_ia}</div>', unsafe_allow_html=True)
                    
                    # --- OPCIONES DE DESCARGA ---
                    st.markdown("---")
                    col_down1, col_down2 = st.columns(2)
                    
                    word_file = generar_word(tema, contenido_ia, {"ie": ie_nombre, "area": area_sel, "grado": grado_sel})
                    
                    col_down1.download_button(
                        label="📄 Descargar en WORD",
                        data=word_file,
                        file_name=f"{tipo}_{tema[:20]}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    
                    col_down2.button("🖨️ Imprimir (Ctrl + P)", on_click=None, help="Usa el comando del sistema para imprimir la vista previa.")
                    
                except Exception as e:
                    st.error(f"Hubo un error: {e}")
        else:
            st.warning("⚠️ Por favor, ingresa un tema o descripción.")

with tabs[0]: render_generador("Programación Anual")
with tabs[1]: render_generador("Unidad Didáctica")
with tabs[2]: render_generador("Sesión de Aprendizaje")

# ── 10. FOOTER ──
st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 4rem; padding: 2rem; border-top: 1px solid #e2e8f0;">
        © 2026 EDUPLAN IA - LA CONVENCIÓN | Gestión {LIDER} | Versión 2.0 Premium<br>
        Hecho para los docentes del Perú 🇵🇪
    </div>
""", unsafe_allow_html=True)

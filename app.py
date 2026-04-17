import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
import io

# --- CONFIGURACIÓN DE IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
client = ZhipuAI(api_key=st.secrets.get("ZHIPU_KEY", ""))

st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="📝")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { background-color: #1e88e5; color: white; width: 100%; font-weight: bold; border-radius: 8px; }
    .group-container { border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; background-color: white; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .group-title { color: #1e3a8a; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- PROMPT MAESTRO (EL NUEVO "CEREBRO" PEDAGÓGICO) ---
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

def consultar_ia(tipo, tema, datos_formulario):
    # Combinamos el Prompt Maestro con los datos específicos del docente
    prompt_usuario = f"""
    PEDIDO: Generar {tipo}.
    DATOS DEL DOCENTE:
    - Área: {datos_formulario['area']} | Grado: {datos_formulario['grado']}
    - Título: {tema} | Duración: {datos_formulario['duracion']} min.
    - Contexto/Recursos: {datos_formulario['contexto']}
    - Inclusión NEE: {datos_formulario['nee']} | Guía Detallada: {datos_formulario['guia']}
    
    Por favor, responde siguiendo estrictamente tu identidad de asistente pedagógico CNEB.
    """
    try:
        response = client.chat.completions.create(
            model="glm-4-flash", 
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": prompt_usuario}
            ]
        )
        return response.choices[0].message.content
    except:
        return "⚠️ Error: Asegúrese de que su ZHIPU_KEY esté configurada correctamente en los Secrets de Streamlit."

# --- INTERFAZ TIPO FORMULARIO ---
st.title("🏛️ Portal de Planificación Curricular")
st.write(f"Gestión e Innovación: **{LIDER}** | alineado al CNEB 2026")

tab1, tab2, tab3 = st.tabs(["📅 Programación Anual", "📂 Unidad Didáctica", "🚀 SESIÓN DE APRENDIZAJE"])

# --- LÓGICA DE LA SESIÓN (INTERFAZ INTUITIVA) ---
with tab3:
    with st.container():
        st.markdown('<div class="group-title">📋 1. Modalidad y Grado</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        mod = c1.selectbox("Modalidad", ["EBR Regular", "EBA", "EBE"], key="mod_s")
        niv = c2.selectbox("Nivel/Ciclo", ["Primaria", "Secundaria"], key="niv_s")
        gra = c3.selectbox("Grado", ["1ro", "2do", "3ro", "4to", "5to", "6to"], key="gra_s")

    st.button("🪄 ¡IA, determina las Competencias por mí!", key="magic_btn")

    with st.container():
        st.markdown('<div class="group-title">🎯 2. Propósito de Aprendizaje</div>', unsafe_allow_html=True)
        ca, cb = st.columns(2)
        area_s = ca.selectbox("Área Curricular", ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología"], key="area_s")
        comp_s = cb.text_input("Competencia específica (Opcional)", key="comp_s")
        enf_s = st.selectbox("Enfoque Transversal", ["Orientación al bien común", "Inclusivo", "Intercultural", "Ambiental"], key="enf_s")

    with st.container():
        st.markdown('<div class="group-title">⚒️ 3. Contexto, Recursos y Metodología</div>', unsafe_allow_html=True)
        col_x, col_y = st.columns(2)
        espacio = col_x.selectbox("Espacio", ["Aula", "Patio", "AIP / Laboratorio"], key="esp_s")
        metodo = col_y.selectbox("Metodología", ["Aprendizaje basado en proyectos", "Flipped Classroom", "Trabajo en equipo"], key="met_s")
        
        nee_on = st.toggle("🧠 Adaptación de Inclusión (NEE)", key="nee_s")
        guia_on = st.toggle("⚠️ Requiero guía paso a paso (No soy del área)", key="guia_s")

    st.markdown('<div class="group-title">📌 4. Tema o Título de la Sesión</div>', unsafe_allow_html=True)
    titulo_s = st.text_input("Ej: Conocemos la historia de nuestra provincia", key="titulo_s")
    duracion_s = st.text_input("Duración (Minutos)", "90", key="dur_s")

    if st.button("🚀 GENERAR SESIÓN COMPLETA", key="main_gen"):
        if titulo_s:
            datos = {
                "area": area_s, "grado": gra, "duracion": duracion_s,
                "contexto": f"Espacio: {espacio}, Método: {metodo}",
                "nee": "SÍ" if nee_on else "NO", "guia": "SÍ" if guia_on else "NO"
            }
            with st.spinner("Diseñando experiencia de aprendizaje..."):
                resultado = consultar_ia("Sesión de Aprendizaje", titulo_s, datos)
                st.markdown(resultado)
                
                # Botón de descarga simplificado
                st.download_button("📥 Descargar Sesión en Word", resultado, f"{titulo_s}.docx")
        else:
            st.error("Por favor, ingresa el título de la sesión.")

# --- FOOTER ---
st.markdown("<br><center><small>EduPlan IA - Innovación para el Docente del Cusco</small></center>", unsafe_allow_html=True)

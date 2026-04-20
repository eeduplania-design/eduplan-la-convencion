import logging
import os
import re
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Tuple

import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from zhipuai.core._errors import ZhipuAIError

# ==========================================
# 1. CONFIGURACIÓN Y LOGGING PARA PRODUCCIÓN
# ==========================================

# Cargar variables de entorno (desarrollo local)
load_dotenv()

# Configuración de Logging Estructurado
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ==========================================
# 2. CONSTANTES Y DATOS MAESTROS (CACHED)
# ==========================================

@st.cache_data
def get_master_data() -> dict:
    """
    Retorna los datos maestros cacheados para optimizar rendimiento.
    Previene la reasignación de memoria en cada recarga de Streamlit.
    """
    return {
        "NOMBRE_APP": "EDUPLAN IA - LA CONVENCIÓN",
        "LIDER": "PIP Prof. Percy Tapia A",
        "ANIO_ACTUAL": datetime.now().year,
        "DISTRICTS": [
            "Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", 
            "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", 
            "Villa Virgen", "Villa Kintiarina", "Ocobamba"
        ],
        "ENFOQUES_TRANSVERSALES": [
            "De derechos", "Inclusivo o de Atención a la diversidad", 
            "Intercultural", "Igualdad de género", "Ambiental", 
            "Orientación al bien común", "Búsqueda de la Excelencia"
        ],
        "CONTEXTOS_LOCALES": [
            "Cosecha agrícola (Café, Cacao, Cítricos)",
            "Fenómenos climatológicos (Lluvias intensas, friaje)",
            "Festividades locales y aniversarios",
            "Problemática ambiental local",
            "Costumbres y tradiciones culturales"
        ],
        "NIVELES": ["Inicial", "Primaria", "Secundaria"],
        "AREAS_PRIMARIA_SECUNDARIA": [
            "Matemática", "Comunicación", "Ciencia y Tecnología", 
            "Personal Social / Ciencias Sociales", "Desarrollo Personal, Ciudadanía y Cívica",
            "Arte y Cultura", "Educación Física", "Educación Religiosa", "Educación para el Trabajo"
        ]
    }

# ==========================================
# 3. CAPA DE SERVICIO: INTEGRACIÓN CON IA
# ==========================================

class AIService:
    """
    Servicio para manejar la comunicación con ZhipuAI.
    Implementa manejo de errores y timeouts.
    """
    def __init__(self):
        # Preferir secrets de Streamlit en producción, fallback a variables de entorno
        api_key = st.secrets.get("ZHIPUAI_API_KEY", os.getenv("ZHIPUAI_API_KEY"))
        if not api_key:
            logger.critical("ZHIPUAI_API_KEY no configurada.")
            st.error("Error de configuración de servidor: API Key no encontrada.")
            st.stop()
            
        self.client = ZhipuAI(api_key=api_key)
        self.model = os.getenv("ZHIPUAI_MODEL", "glm-4") # Modelo por defecto

    def generar_contenido(self, prompt: str, system_message: str) -> Optional[str]:
        """
        Envía un prompt a la IA y retorna la respuesta.
        Implementa manejo de excepciones robusto.
        """
        try:
            logger.info(f"Enviando petición a ZhipuAI (Modelo: {self.model})")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                timeout=60 # Timeout estricto para evitar bloqueos
            )
            return response.choices[0].message.content
            
        except ZhipuAIError as e:
            logger.error(f"Error de API ZhipuAI: {str(e)}")
            st.error("Ocurrió un error al comunicarse con el servicio de IA. Por favor, intente nuevamente.")
            return None
        except Exception as e:
            logger.exception("Error inesperado en generación de IA")
            st.error("Error interno del servidor. El equipo técnico ha sido notificado.")
            return None

# ==========================================
# 4. CAPA DE NEGOCIO: GENERACIÓN DE DOCUMENTOS
# ==========================================

class DocumentGenerator:
    """
    Clase encargada de generar documentos Word (.docx) con formato profesional.
    Separada de la UI para mantener el Principio de Responsabilidad Única (SRP).
    """
    @staticmethod
    def _add_shading_to_cell(cell, hex_color: str):
        """Método helper seguro para agregar color de fondo a celdas de tabla."""
        try:
            shading_elm = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), hex_color))
            cell._tc.get_or_add_tcPr().append(shading_elm)
        except Exception as e:
            logger.warning(f"No se pudo aplicar shading a la celda: {e}")

    @classmethod
    def create_word_document(cls, titulo: str, contenido: str, ie_nombre: str, distrito: str, area: str, grado: str) -> BytesIO:
        """
        Genera el documento Word en memoria y retorna un buffer.
        """
        try:
            doc = Document()
            
            # --- Metadatos y Estilos Base ---
            data = get_master_data()
            doc.core_properties.title = titulo
            doc.core_properties.author = data["NOMBRE_APP"]
            doc.core_properties.comments = f"Generado para {ie_nombre} - {distrito}"
            
            # --- Encabezado ---
            header = doc.add_paragraph()
            header.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = header.add_run(f"{data['NOMBRE_APP']}\nDocumento Curricular - CNEB Perú\n")
            run.bold = True
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(0, 51, 102) # Azul oscuro profesional
            
            # --- Título Principal ---
            title_par = doc.add_heading(titulo, level=1)
            title_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # --- Datos Informativos (Tabla) ---
            doc.add_heading('I. DATOS INFORMATIVOS', level=2)
            table = doc.add_table(rows=4, cols=2)
            table.style = 'Table Grid'
            
            datos_info = [
                ("Institución Educativa:", ie_nombre),
                ("Lugar / Distrito:", distrito),
                ("Área Curricular:", area),
                ("Grado / Ciclo:", grado)
            ]
            
            for i, (label, value) in enumerate(datos_info):
                row = table.rows[i]
                row.cells[0].text = label
                row.cells[0].paragraphs[0].runs[0].bold = True
                cls._add_shading_to_cell(row.cells[0], "F2F2F2")
                row.cells[1].text = value

            doc.add_paragraph("\n")
            
            # --- Contenido Generado por IA ---
            doc.add_heading('II. DESARROLLO CURRICULAR', level=2)
            
            # Limpiar etiquetas de la vista web
            contenido_limpio = re.sub(r'\[IMAGEN_SUGERIDA:.*?\]', '', contenido)
            
            # Procesar el markdown rudimentario a Word (simplificado para robustez)
            for paragraph in contenido_limpio.split('\n\n'):
                if not paragraph.strip():
                    continue
                    
                if paragraph.startswith('###'):
                    doc.add_heading(paragraph.replace('###', '').strip(), level=3)
                elif paragraph.startswith('**') and paragraph.endswith('**'):
                    p = doc.add_paragraph()
                    r = p.add_run(paragraph.replace('**', ''))
                    r.bold = True
                elif paragraph.startswith('- '):
                    doc.add_paragraph(paragraph[2:], style='List Bullet')
                else:
                    doc.add_paragraph(paragraph.strip())
            
            # --- Pie de página ---
            doc.add_page_break()
            footer = doc.add_paragraph()
            footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
            footer.add_run(f"__________________________________\nFirma del Docente\n{ie_nombre}")
            
            # Guardar en buffer de memoria
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generando documento Word: {e}", exc_info=True)
            raise RuntimeError("Error al generar el archivo .docx")

# ==========================================
# 5. CAPA DE PRESENTACIÓN: COMPONENTES UI
# ==========================================

def render_sidebar() -> Tuple[str, str, str, str]:
    """Renderiza el sidebar y recolecta datos globales del usuario."""
    data = get_master_data()
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3074/3074058.png", width=100) # Placeholder seguro
        st.title(data["NOMBRE_APP"])
        st.markdown(f"**Líder:** {data['LIDER']}")
        st.divider()
        
        st.header("⚙️ Configuración Global")
        ie_nombre = st.text_input("Nombre de la I.E.", placeholder="Ej. 50113", max_chars=100)
        distrito_sel = st.selectbox("Distrito", options=data["DISTRICTS"])
        nivel_sel = st.selectbox("Nivel Educativo", options=data["NIVELES"])
        
        # Lógica dinámica segura
        areas = ["Todas (Docente de Aula)"] if nivel_sel == "Inicial" else data["AREAS_PRIMARIA_SECUNDARIA"]
        area_sel = st.selectbox("Área Curricular", options=areas)
        
        st.info("💡 Estos datos se aplicarán a todos los documentos generados.")
        
        return ie_nombre, distrito_sel, nivel_sel, area_sel

class PromptFactory:
    """
    El 'Cerebro' de la aplicación.
    Contiene la lógica de Prompt Engineering para generar documentos pedagógicos de alta calidad.
    """
    @staticmethod
    def get_system_message() -> str:
        return (
            "Eres un Especialista Pedagógico del Ministerio de Educación del Perú (MINEDU), "
            "experto en el Currículo Nacional de la Educación Básica (CNEB). "
            "Tu objetivo es diseñar documentos curriculares técnicos, precisos y listos para usar en el aula. "
            "Usa un tono formal, académico y pedagógico. Formatea tu respuesta usando Markdown estructurado "
            "(usa ### para títulos de secciones, **negritas** para resaltar y guiones para viñetas)."
        )

    @staticmethod
    def build_prompt(tipo_doc: str, contexto: dict) -> str:
        base_context = (
            f"Diseña un(a) **{tipo_doc}** para el nivel **{contexto.get('nivel')}**, "
            f"área de **{contexto.get('area')}**, para el **{contexto.get('grado')}**.\n"
            f"El contexto sociosanitario/local de los estudiantes es: '{contexto.get('contexto_local')}'.\n\n"
        )

        if tipo_doc == "Programación Anual":
            instrucciones = (
                "La Programación Anual debe contener exactamente la siguiente estructura:\n"
                "### I. Descripción General\n"
                "(Enfoque del área y propósito para este ciclo/grado).\n\n"
                "### II. Propósitos de Aprendizaje\n"
                "(Lista de Competencias y Capacidades del área seleccionada según el CNEB).\n\n"
                "### III. Enfoques Transversales\n"
                "(Selecciona 2 o 3 enfoques relevantes al contexto y explica cómo se aplicarán).\n\n"
                "### IV. Organización de las Unidades Didácticas\n"
                "(Propón 4 unidades para el año. Para cada una, indica: Título, Situación Significativa resumida, y Duración en semanas).\n\n"
                "### V. Estrategias Metodológicas\n"
                "(Estrategias de enseñanza sugeridas para el nivel y área).\n\n"
                "### VI. Evaluación\n"
                "(Evaluación diagnóstica, formativa y sumativa).\n\n"
                "Asegúrate de que la progresión sea coherente para todo un año escolar."
            )
        elif tipo_doc == "Unidad Didáctica":
            instrucciones = (
                "La Unidad Didáctica debe contener exactamente la siguiente estructura:\n"
                "### I. Título de la Unidad\n"
                "(Debe ser motivador y estar relacionado al contexto local).\n\n"
                "### II. Propósitos de Aprendizaje y Evaluación\n"
                "(Detalla 2 competencias del área. Para cada una incluye: Capacidades, Desempeños precisados, Criterios de Evaluación y Evidencia de aprendizaje).\n\n"
                "### III. Situación Significativa\n"
                "(Redacta una situación retadora de 2 párrafos basada en el contexto local proporcionado. Debe terminar con una pregunta retadora).\n\n"
                "### IV. Secuencia de Sesiones\n"
                "(Propón 5 sesiones secuenciales. Para cada una incluye: Título y un breve propósito de la sesión).\n\n"
                "### V. Materiales y Recursos\n"
                "(Recursos educativos y tecnológicos a utilizar)."
            )
        elif tipo_doc == "Sesión de Aprendizaje":
            instrucciones = (
                "La Sesión de Aprendizaje debe contener exactamente la siguiente estructura:\n"
                "### I. Título de la Sesión\n"
                "(Creativo y relacionado al propósito).\n\n"
                "### II. Propósito y Evidencia\n"
                "(Menciona la Competencia, Capacidad, Desempeño precisado, Criterio de evaluación, Evidencia e Instrumento de evaluación).\n\n"
                "### III. Preparación de la Sesión\n"
                "(¿Qué necesitamos hacer antes? ¿Qué recursos o materiales se utilizarán?).\n\n"
                "### IV. Momentos de la Sesión\n"
                "**INICIO (20 min):**\n"
                "- Motivación, recuperación de saberes previos, conflicto cognitivo y declaración del propósito.\n"
                "**DESARROLLO (60 min):**\n"
                "- Gestión y acompañamiento del desarrollo de competencias (procesos didácticos específicos del área seleccionada).\n"
                "**CIERRE (10 min):**\n"
                "- Evaluación y metacognición (preguntas reflexivas).\n\n"
                "Debe ser extremadamente práctica para que un docente pueda dictarla inmediatamente."
            )
        else:
            instrucciones = "Genera el documento siguiendo los lineamientos del CNEB."

        return base_context + instrucciones

def render_generador(tipo_doc: str, tab_key: str, global_context: tuple):
    """
    Renderiza el formulario y maneja la lógica para una pestaña específica.
    Implementa validaciones y sanitización.
    """
    ie_nombre, distrito_sel, nivel_sel, area_sel = global_context
    data = get_master_data()
    
    st.markdown(f"### 📝 Generador de {tipo_doc}")
    
    with st.form(key=f"form_{tab_key}"):
        col1, col2 = st.columns(2)
        with col1:
            grado_sel = st.text_input("Grado / Año", placeholder="Ej. 3ro, 4 años...", max_chars=20)
        with col2:
            contexto_sel = st.selectbox("Situación Significativa / Contexto", options=data["CONTEXTOS_LOCALES"])
            
        submit_btn = st.form_submit_button(f"🚀 Generar {tipo_doc}", use_container_width=True)
        
    if submit_btn:
        # Validación de entrada
        if not ie_nombre.strip() or not grado_sel.strip():
            st.warning("⚠️ Por favor, complete el Nombre de la I.E. y el Grado en el menú lateral y formulario antes de generar.")
            return

        with st.spinner(f"Analizando CNEB y redactando {tipo_doc}... (Esto puede tomar un minuto)"):
            ai_service = AIService()
            contexto = {
                "nivel": nivel_sel, "area": area_sel, 
                "grado": grado_sel, "contexto_local": contexto_sel
            }
            
            prompt = PromptFactory.build_prompt(tipo_doc, contexto)
            system_msg = PromptFactory.get_system_message()
            
            resultado = ai_service.generar_contenido(prompt, system_msg)
            
            if resultado:
                # Guardar en Session State para no perderlo al interactuar con otros widgets
                st.session_state[f"resultado_{tab_key}"] = resultado
                st.session_state[f"meta_{tab_key}"] = contexto

    # Mostrar resultados si existen en el estado de sesión
    if st.session_state.get(f"resultado_{tab_key}"):
        st.success("✅ ¡Documento generado con éxito!")
        
        resultado_actual = st.session_state[f"resultado_{tab_key}"]
        
        # Contenedor seguro con scroll
        with st.container(height=450, border=True):
            # Sanitización visual simple para Streamlit
            vista_web = re.sub(r'\[IMAGEN_SUGERIDA:.*?\]', '*(Aquí se insertará automáticamente una imagen ilustrativa en el documento Word)*', resultado_actual)
            st.markdown(vista_web)
            
        st.divider()
        
        # Generación diferida de Word solo cuando se solicita (Optimización)
        try:
            titulo_doc = f"{tipo_doc.upper()} - {area_sel}"
            file_word = DocumentGenerator.create_word_document(
                titulo=titulo_doc,
                contenido=resultado_actual,
                ie_nombre=ie_nombre,
                distrito=distrito_sel,
                area=area_sel,
                grado=st.session_state[f"meta_{tab_key}"]["grado"]
            )
            
            file_name_clean = re.sub(r'[\\/*?:"<>|]', "", f"{tipo_doc}_{grado_sel}_{area_sel}.docx").replace(" ", "_")
            
            st.download_button(
                label="📥 EXPORTAR A MICROSOFT WORD (.DOCX) - CALIDAD IMPRENTA", 
                data=file_word, 
                file_name=file_name_clean, 
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dl_{tab_key}",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error("Hubo un problema al preparar el archivo Word para descarga.")

# ==========================================
# 6. FUNCIÓN PRINCIPAL (ENTRY POINT)
# ==========================================

def main():
    """Punto de entrada principal de la aplicación Streamlit."""
    data = get_master_data()
    
    # Configuración de página (Seguridad y SEO básico)
    st.set_page_config(
        page_title=data["NOMBRE_APP"],
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Ocultar menú de Streamlit en producción (Seguridad UI)
    if os.getenv("ENVIRONMENT") == "production":
        hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # UI principal
    global_context = render_sidebar()
    
    st.title(f"🤖 {data['NOMBRE_APP']}")
    st.markdown("Plataforma de IA generativa alineada al **CNEB** para la creación de documentos curriculares.")
    
    # Navegación por pestañas
    tab1, tab2, tab3 = st.tabs(["📅 Programación Anual", "📚 Unidad Didáctica", "📝 Sesión de Aprendizaje"])
    
    with tab1:
        render_generador("Programación Anual", "anual", global_context)
    with tab2:
        render_generador("Unidad Didáctica", "unidad", global_context)
    with tab3:
        render_generador("Sesión de Aprendizaje", "sesion", global_context)
        
    # Footer
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: gray;">
            <small>© {data['ANIO_ACTUAL']} {data['NOMBRE_APP']} | Desarrollado bajo estándares del MINEDU</small>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

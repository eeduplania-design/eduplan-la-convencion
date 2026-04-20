import logging
import os
import re
from datetime import datetime
from io import BytesIO
from typing import Tuple, Optional

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
# 1. CONFIGURACIÓN Y LOGGING
# ==========================================
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==========================================
# 2. DATOS MAESTROS Y CSS PREMIUM
# ==========================================
# Nota: NO usamos @st.cache_data aquí para evitar el error "unhashable type: 'dict'"
def get_master_data() -> dict:
    return {
        "NOMBRE_APP": "EduPlan IA Premium",
        "LIDER": "PIP Prof. Percy Tapia A",
        "ANIO_ACTUAL": datetime.now().year,
        "DISTRICTS": [
            "Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", 
            "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", 
            "Villa Virgen", "Villa Kintiarina", "Ocobamba"
        ],
        "CONTEXTOS_LOCALES": [
            "Cosecha agrícola local (Café, Cacao, etc.)",
            "Fenómenos climatológicos (Lluvias, friaje)",
            "Festividades locales y aniversarios",
            "Problemática ambiental local",
            "Costumbres y saberes ancestrales"
        ],
        "NIVELES": ["Inicial", "Primaria", "Secundaria"],
        "AREAS_PRIMARIA_SECUNDARIA": [
            "Matemática", "Comunicación", "Ciencia y Tecnología", 
            "Personal Social / Ciencias Sociales", "Desarrollo Personal, Ciudadanía y Cívica",
            "Arte y Cultura", "Educación Física", "Educación Religiosa", "Educación para el Trabajo"
        ]
    }

def apply_custom_css():
    """Inyecta CSS para darle aspecto de SaaS de pago"""
    st.markdown("""
        <style>
        /* Estilos generales */
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        
        /* Tarjetas de métricas premium */
        div[data-testid="metric-container"] {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        div[data-testid="metric-container"]:hover { transform: translateY(-3px); }
        
        /* Botones primarios (Generar) */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            transform: scale(1.02);
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. EL CEREBRO: PROMPT ENGINEERING
# ==========================================
class PromptFactory:
    @staticmethod
    def get_system_message() -> str:
        return (
            "Eres un Especialista Pedagógico Senior del MINEDU de Perú, experto en CNEB y DUA (Diseño Universal para el Aprendizaje). "
            "Tu misión es superar a cualquier software comercial generando documentos curriculares impecables, "
            "altamente personalizados al contexto rural/local y a las necesidades especiales de los estudiantes. "
            "Usa Markdown rigurosamente. NUNCA inventes competencias que no estén en el CNEB."
        )

    @staticmethod
    def build_prompt(tipo_doc: str, contexto: dict) -> str:
        base = (
            f"Diseña un(a) **{tipo_doc}** para:\n"
            f"- Nivel: {contexto.get('nivel')}\n"
            f"- Área: {contexto.get('area')}\n"
            f"- Grado/Ciclo: {contexto.get('grado')}\n"
            f"- Contexto Sociocultural: '{contexto.get('contexto_local')}'\n"
            f"- Inclusión/DUA (Muy importante): {contexto.get('inclusion', 'Ninguna reportada, aula regular')}.\n\n"
        )

        if tipo_doc == "Sesión de Aprendizaje":
            instrucciones = (
                "ESTRUCTURA OBLIGATORIA:\n"
                "### I. Título de la Sesión\n"
                "### II. Propósitos de Aprendizaje\n"
                "(Competencia, Capacidad, Desempeño precisado, Criterio de evaluación, Evidencia e Instrumento).\n"
                "### III. Adaptaciones DUA (Inclusión)\n"
                "(Explica exactamente cómo adaptarás la clase para la necesidad inclusiva mencionada).\n"
                "### IV. Secuencia Didáctica (Momentos)\n"
                "**INICIO (20 min):** Motivación, Saberes Previos, Conflicto Cognitivo, Propósito.\n"
                "**DESARROLLO (60 min):** Gestión y acompañamiento (Procesos didácticos del área). Agrega sugerencias de imágenes así: [IMAGEN_SUGERIDA: descripción de la imagen].\n"
                "**CIERRE (10 min):** Metacognición.\n"
                "### V. Rúbrica de Evaluación\n"
                "(Crea una matriz de evaluación tipo Rúbrica para esta sesión con 3 niveles de logro: Inicio, Proceso, Logrado)."
            )
        elif tipo_doc == "Unidad Didáctica":
             instrucciones = (
                "ESTRUCTURA OBLIGATORIA:\n"
                "### I. Título de la Unidad\n"
                "### II. Situación Significativa\n"
                "(2 párrafos potentes basados en el contexto local, finalizando con un reto cognitivo).\n"
                "### III. Propósitos y Enfoques Transversales\n"
                "(Matriz de competencias, capacidades y desempeños alineados al reto).\n"
                "### IV. Secuencia de Sesiones\n"
                "(Propón 4-5 sesiones secuenciales con título y propósito).\n"
                "### V. Producto Final de la Unidad\n"
                "(Qué evidencia compleja presentarán los estudiantes)."
            )
        else: # Programación Anual
             instrucciones = (
                "ESTRUCTURA OBLIGATORIA:\n"
                "### I. Datos Generales y Enfoque\n"
                "### II. Propósitos de Aprendizaje (Anual)\n"
                "### III. Organización de las Unidades (Matriz Anual)\n"
                "(Distribución de 4 a 8 unidades en el año, con títulos tentativos y duración).\n"
                "### IV. Orientaciones para la Evaluación Formativa\n"
             )

        return base + instrucciones

class AIService:
    def __init__(self):
        # Manejo robusto de la API Key: 1° Secrets (Cloud), 2° Variables de Entorno (Local)
        api_key = None
        try:
            api_key = st.secrets["ZHIPUAI_API_KEY"]
        except Exception:
            api_key = os.getenv("ZHIPUAI_API_KEY")

        if not api_key:
            st.error("⚠️ Faltan las credenciales. Configura ZHIPUAI_API_KEY en tu archivo .env o en st.secrets.")
            st.stop()
            
        self.client = ZhipuAI(api_key=api_key)
        self.model = os.getenv("ZHIPUAI_MODEL", "glm-4")

    def generar_contenido(self, prompt: str, system_message: str) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                timeout=75
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error AI: {e}")
            st.error("Ocurrió un error al conectar con el cerebro de IA. Por favor, reintenta en unos segundos.")
            return None

# ==========================================
# 4. MOTOR DE EXPORTACIÓN (WORD PRO)
# ==========================================
class DocumentGenerator:
    @staticmethod
    def _add_shading(cell, hex_color: str):
        try:
            shading_elm = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), hex_color))
            cell._tc.get_or_add_tcPr().append(shading_elm)
        except Exception:
            pass

    @classmethod
    def create_word_document(cls, titulo: str, contenido: str, metadata: dict) -> BytesIO:
        doc = Document()
        
        # Meta y Título
        doc.core_properties.title = titulo
        header = doc.add_paragraph()
        header.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = header.add_run(f"MINISTERIO DE EDUCACIÓN DEL PERÚ\n{metadata.get('ie_nombre', '')} - {metadata.get('distrito', '')}\n")
        run.bold = True
        run.font.size = Pt(12)
        
        doc.add_heading(titulo, level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Tabla de Datos Informativos (Estilo Premium)
        table = doc.add_table(rows=4, cols=2)
        table.style = 'Table Grid'
        datos = [
            ("Docente:", metadata.get('docente', '______________')),
            ("Área y Nivel:", f"{metadata.get('area', '')} - {metadata.get('nivel', '')}"),
            ("Grado:", metadata.get('grado', '')),
            ("Contexto Inclusivo:", metadata.get('inclusion', 'Regular'))
        ]
        
        for i, (label, value) in enumerate(datos):
            row = table.rows[i]
            row.cells[0].text = label
            row.cells[0].paragraphs[0].runs[0].bold = True
            cls._add_shading(row.cells[0], "EFEFEF")
            row.cells[1].text = str(value)

        doc.add_paragraph("\n")
        
        # Procesamiento del Markdown (Mejorado para viñetas y negritas)
        contenido_limpio = re.sub(r'\[IMAGEN_SUGERIDA:.*?\]', '\n[Espacio para imagen pedagógica sugerida]\n', contenido)
        
        for linea in contenido_limpio.split('\n'):
            linea = linea.strip()
            if not linea: continue
            
            if linea.startswith('### '):
                doc.add_heading(linea.replace('### ', ''), level=2)
            elif linea.startswith('**') and linea.endswith('**'):
                p = doc.add_paragraph()
                p.add_run(linea.replace('**', '')).bold = True
            elif linea.startswith('- '):
                p = doc.add_paragraph(style='List Bullet')
                partes = linea[2:].split('**')
                for i, parte in enumerate(partes):
                    run = p.add_run(parte)
                    if i % 2 != 0: run.bold = True
            else:
                p = doc.add_paragraph()
                partes = linea.split('**')
                for i, parte in enumerate(partes):
                    run = p.add_run(parte)
                    if i % 2 != 0: run.bold = True

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

# ==========================================
# 5. UI PRINCIPAL Y CONTROLADORES
# ==========================================
def render_sidebar() -> dict:
    data = get_master_data()
    with st.sidebar:
        st.markdown(f"### 🇵🇪 {data['NOMBRE_APP']}")
        st.caption(f"Desarrollado para {data['LIDER']} | La Convención")
        st.divider()
        
        st.subheader("1. Datos de la I.E.")
        ie_nombre = st.text_input("Nombre / Número de I.E.", placeholder="Ej. 50113", max_chars=100)
        distrito = st.selectbox("Distrito", options=data["DISTRICTS"])
        
        st.subheader("2. Perfil del Aula")
        nivel = st.selectbox("Nivel", options=data["NIVELES"])
        areas = ["Todas (Docente de Aula)"] if nivel == "Inicial" else data["AREAS_PRIMARIA_SECUNDARIA"]
        area = st.selectbox("Área", options=areas)
        
        st.subheader("3. Atención a la Diversidad (DUA) 🌟")
        inclusion = st.text_area(
            "Necesidades Especiales en el aula (Opcional)", 
            placeholder="Ej. Tengo 2 alumnos con TDAH y 1 estudiante quechua-hablante...",
            help="Si llenas esto, la IA adaptará las estrategias y evaluaciones automáticamente."
        )
        
        return {
            "ie_nombre": ie_nombre, "distrito": distrito, 
            "nivel": nivel, "area": area, "inclusion": inclusion
        }

def render_generador(tipo_doc: str, tab_key: str, global_data: dict):
    data = get_master_data()
    st.markdown(f"## ⚙️ Generar {tipo_doc}")
    
    with st.form(key=f"form_{tab_key}"):
        col1, col2 = st.columns(2)
        with col1:
            # key es muy importante para que no choquen las pestañas
            grado = st.text_input("Grado / Ciclo", key=f"gr_{tab_key}", placeholder="Ej. 3ro de Secundaria")
        with col2:
            contexto = st.selectbox("Contexto / Situación Significativa", options=data["CONTEXTOS_LOCALES"], key=f"ctx_{tab_key}")
            
        submit = st.form_submit_button(f"✨ Generar {tipo_doc} con IA", use_container_width=True)

    if submit:
        if not global_data["ie_nombre"] or not grado:
            st.error("⚠️ Falta llenar el Nombre de la I.E. (Panel Izquierdo) y el Grado antes de generar.")
            return
            
        with st.spinner(f"El Cerebro Pedagógico está diseñando tu {tipo_doc} y alineando rúbricas... 🧠"):
            local_context = {**global_data, "grado": grado, "contexto_local": contexto}
            
            prompt = PromptFactory.build_prompt(tipo_doc, local_context)
            sys_msg = PromptFactory.get_system_message()
            
            resultado = AIService().generar_contenido(prompt, sys_msg)
            
            if resultado:
                st.session_state[f"res_{tab_key}"] = resultado
                st.session_state[f"meta_{tab_key}"] = local_context

    # Mostrar Resultados y Descarga
    if st.session_state.get(f"res_{tab_key}"):
        st.success("✅ Documento Pedagógico Generado Exitosamente")
        
        resultado_actual = st.session_state[f"res_{tab_key}"]
        
        # Vista Previa
        with st.expander("👁️ Ver Vista Previa del Documento", expanded=True):
            vista_web = re.sub(r'\[IMAGEN_SUGERIDA:.*?\]', '\n> 🖼️ *(Sugerencia de imagen para tu documento Word)*\n', resultado_actual)
            st.markdown(vista_web)
            
        # Exportación PRO
        titulo = f"{tipo_doc.upper()} - {global_data['area']}"
        file_word = DocumentGenerator.create_word_document(
            titulo=titulo, 
            contenido=resultado_actual, 
            metadata=st.session_state[f"meta_{tab_key}"]
        )
        
        safe_filename = f"{tipo_doc}_{grado}_{global_data['area']}.docx".replace(" ", "_")
        safe_filename = re.sub(r'[\\/*?:"<>|]', "", safe_filename)
        
        st.download_button(
            label="📥 DESCARGAR DOCUMENTO EN WORD (.DOCX) LISTO PARA IMPRIMIR", 
            data=file_word, 
            file_name=safe_filename, 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"dl_{tab_key}",
            use_container_width=True,
            type="primary"
        )

def main():
    st.set_page_config(page_title="EduPlan IA Premium", page_icon="🏆", layout="wide")
    apply_custom_css()
    
    # Header Premium
    st.title("🏆 EduPlan IA Premium: La Convención")
    st.markdown("*La plataforma definitiva para docentes. Planifica en segundos con Inteligencia Artificial y alineación exacta al CNEB.*")
    
    # Métricas Dashboard SaaS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alineación CNEB", "100%", "MINEDU")
    col2.metric("Ahorro de Tiempo", "95%", "Automatizado")
    col3.metric("Motor de IA", "GLM-4 / CNEB", "Precisión")
    col4.metric("Diseño Universal", "DUA Integrado", "Inclusivo")
    st.divider()
    
    # Carga de interfaz principal
    global_data = render_sidebar()
    
    tab1, tab2, tab3 = st.tabs(["📅 Programación Anual", "📚 Unidad Didáctica", "📝 Sesión de Aprendizaje"])
    
    with tab1: render_generador("Programación Anual", "anual", global_data)
    with tab2: render_generador("Unidad Didáctica", "unidad", global_data)
    with tab3: render_generador("Sesión de Aprendizaje", "sesion", global_data)

if __name__ == "__main__":
    main()

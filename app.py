import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import re
import datetime
import base64
import os

# --- CONFIGURACIÓN DE IDENTIDAD Y DATOS MAESTROS ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "PIP Prof. Percy Tapia A"
ANIO_ACTUAL = datetime.datetime.now().year

DISTRICTS = [
    "Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", 
    "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", 
    "Villa Virgen", "Villa Kintiarina", "Ocobamba"
]
ENFOQUES_TRANSVERSALES = [
    "De derechos", "Inclusivo o de Atención a la diversidad", 
    "Intercultural", "Igualdad de género", "Ambiental", 
    "Orientación al bien común", "Búsqueda de la Excelencia"
]

CONTEXTOS_LOCALES = [
    "Cosecha agrícola (Café, Cacao, Cítricos)",
    "Fenómenos climatológicos (Lluvias intensas, huaycos)",
    "Prevención de enfermedades endémicas (Dengue, Malaria)",
    "Aniversario de la Institución o Distrito",
    "Prácticas culturales y saberes locales (Machiguenga, andino-amazónico)",
    "Contaminación ambiental y cuidado del agua",
    "Alimentación saludable frente a la anemia local",
    "Uso inadecuado de tecnología y redes sociales",
    "Otro contexto (Especificar brevemente)"
]

# --- DICCIONARIOS MINEDU: ENFOQUES Y PROCESOS DIDÁCTICOS ---
ENFOQUES_AREAS = {
    "Matemática": "Resolución de problemas",
    "Comunicación": "Comunicativo (Textual e intertextual)",
    "Personal Social": "Desarrollo personal y Ciudadanía activa",
    "Ciencias Sociales": "Ciudadanía activa",
    "DPCC": "Desarrollo personal y Ciudadanía activa",
    "Ciencia y Tecnología": "Indagación científica y Alfabetización científica y tecnológica",
    "Educación Física": "Corporeidad",
    "Arte y Cultura": "Multicultural e Interdisciplinario",
    "Educación Religiosa": "Cristocéntrico y Comunitario",
    "Inglés": "Comunicativo",
    "EPT": "Emprendimiento",
    "Tutoría": "Orientación Educativa",
    "Psicomotriz": "Corporeidad",
    "Descubrimiento del Mundo": "Indagación científica"
}

PROCESOS_DIDACTICOS = {
    "Matemática": "1. Familiarización con el problema. 2. Búsqueda y ejecución de estrategias. 3. Socialización de representaciones. 4. Reflexión y formalización. 5. Planteamiento de otros problemas.",
    "Comunicación": "1. Antes del discurso/lectura/escritura (Planificación). 2. Durante el discurso/lectura/escritura (Textualización). 3. Después del discurso/lectura/escritura (Revisión/Reflexión).",
    "Personal Social": "1. Problematización. 2. Búsqueda de la información. 3. Toma de acuerdos o decisiones.",
    "Ciencias Sociales": "1. Problematización. 2. Búsqueda de la información. 3. Toma de acuerdos o decisiones.",
    "DPCC": "1. Problematización. 2. Búsqueda de la información. 3. Toma de acuerdos o decisiones.",
    "Ciencia y Tecnología": "1. Planteamiento del problema. 2. Planteamiento de hipótesis. 3. Elaboración del plan de acción. 4. Recojo de datos y análisis. 5. Estructuración del saber construido como respuesta al problema. 6. Evaluación y comunicación.",
    "Educación Física": "1. Motivación, exploración y calentamiento. 2. Desarrollo de la actividad central. 3. Vuelta a la calma y relajación.",
    "Arte y Cultura": "1. Desafío/Reto. 2. Exploración y experimentación. 3. Producción preliminar. 4. Revisión y afinamiento. 5. Presentación y reflexión.",
    "Educación Religiosa": "1. Ver. 2. Juzgar. 3. Actuar. 4. Revisar. 5. Celebrar.",
    "Inglés": "1. Pre-task (Motivación/Input). 2. Task cycle (Ejecución). 3. Language focus (Análisis/Reflexión).",
    "EPT": "1. Crear/Diseñar (Design Thinking). 2. Planificar. 3. Ejecutar. 4. Evaluar.",
    "Psicomotriz": "1. Asamblea. 2. Expresividad motriz. 3. Relajación. 4. Expresión gráfico-plástica. 5. Cierre.",
    "Descubrimiento del Mundo": "1. Observación. 2. Planteamiento de preguntas. 3. Exploración. 4. Comunicación.",
    "Tutoría": "1. Presentación. 2. Desarrollo. 3. Cierre."
}

# --- CONEXIÓN SEGURA CON LA API ---
try:
    api_key = st.secrets.get("ZHIPU_KEY", "TU_API_KEY_AQUI_SI_NO_USAS_SECRETS")
    client = ZhipuAI(api_key=api_key)
except Exception:
    client = None

# --- MOTOR DE PROMPTS CNEB (CEREBRO PEDAGÓGICO) ---
def obtener_prompt_cneb(tipo_doc, area, nivel):
    enfoque_area = ENFOQUES_AREAS.get(area, "Enfoque por competencias")
    procesos_area = PROCESOS_DIDACTICOS.get(area, "1. Inicio, 2. Desarrollo, 3. Cierre")

    base = f"""Eres un especialista top del MINEDU (Perú), experto en el Currículo Nacional de la Educación Básica (CNEB) y evaluación formativa.
Tu objetivo es redactar un/una '{tipo_doc}' para el nivel {nivel} en el área de {area}.

DATOS CLAVE DEL CNEB PARA ESTA ÁREA QUE DEBES APLICAR ESTRICTAMENTE:
- Enfoque del Área: {enfoque_area}
- Procesos Didácticos del Área: {procesos_area}

TU MISIÓN: El docente te dará información mínima (un tema y un contexto). TÚ DEBES desarrollar todo el documento, redactar la situación significativa completa promoviendo el razonamiento y pensamiento crítico, y deducir las Competencias, Capacidades, y Desempeños del CNEB correspondientes.

REGLAS INQUEBRANTABLES DE FORMATO:
1. Usa Markdown estándar (Títulos con ## y ###). No uses HTML.
2. Construye TABLAS LIMPIAS usando solo `|` y `-`. NUNCA unas celdas, usa filas estándar.
3. El lenguaje debe ser técnico-pedagógico peruano.
"""

    if tipo_doc == "Programación Anual":
        base += f"""
ESTRUCTURA OBLIGATORIA (PROGRAMACIÓN ANUAL - PLANIFICACIÓN DE LARGO PLAZO):
1. **Datos Informativos.**
2. **Descripción General:** Escribe al menos 2 párrafos. Redacta cómo se trabajará bajo el enfoque del área ({enfoque_area}) y vincula las características de los estudiantes con la caracterización del contexto local proporcionado.
3. **Propósitos de Aprendizaje:** TABLA con Competencias, Capacidades y Estándares de Aprendizaje (Alineados al nivel y área).
4. **Organización de las Unidades Didácticas/Proyectos:** TABLA detallando Títulos de unidad, Situación Significativa resumida (basada en el problema local), Duración y Competencias a movilizar por bimestre/trimestre.
5. **Enfoques Transversales:** Priorizados en el año.
6. **Estrategias Metodológicas y Recursos:** Alineados a los procesos didácticos: {procesos_area}.
7. **Evaluación:** Diagnóstica, Formativa y Sumativa.
"""
    elif tipo_doc == "Unidad Didáctica":
        base += f"""
ESTRUCTURA OBLIGATORIA (UNIDAD DIDÁCTICA / EXPERIENCIA DE APRENDIZAJE - CORTO PLAZO):
1. **Datos Informativos.**
2. **Situación Significativa:** Redacta una situación retadora de al menos 2 párrafos, anclada al contexto local dado. Debe promover el PENSAMIENTO CRÍTICO e INDAGACIÓN. Finaliza con un RETO (pregunta motivadora).
3. **Propósitos y Evidencias:** TABLA MAESTRA con: Competencia, Capacidades, Desempeños precisados, Criterios de Evaluación, Evidencia de Aprendizaje, e Instrumento.
4. **Secuencia de Sesiones:** TABLA con Número de Sesión, Título, y Breve descripción (mínimo 4 sesiones secuenciadas lógicamente para resolver el reto planteado).
5. **Materiales y Recursos.**
"""
    elif tipo_doc == "Sesión de Aprendizaje":
        base += f"""
ESTRUCTURA OBLIGATORIA ESTRICTA (SESIÓN DE APRENDIZAJE CNEB - CORTO PLAZO):
**Sesión de Aprendizaje N° 01: [Escribe el título sugerido]**

**I.- Datos Informativos:**
(Nombre de Institución Educativa, Nivel, Grado, Sección, Área curricular, Nombre del docente, Duración, Fecha). Llena los datos con la información proporcionada y usa "___" para la sección y fecha si no se especifican.

**II.- Propósitos de Aprendizaje y Evaluación:**
TABLA con las siguientes columnas: Área | Competencia | Capacidad(es) | Desempeño precisado al grado | Evidencia de aprendizaje | Criterio de evaluación (¿Qué observaré?) | Instrumento de evaluación.

**III.- Enfoques Transversales:**
TABLA o lista con: Enfoque | Valor o actitud que se promueve | Comportamiento observable durante la sesión.

**IV.- Preparación de la Sesión:**
Crea OBLIGATORIAMENTE una TABLA con dos columnas exactas: 
| ¿Qué necesitamos hacer antes de la sesión? | ¿Qué recursos o materiales se utilizarán? |

**V.- Secuencia Didáctica (BAJO EL ENFOQUE: {enfoque_area}):**
Crea OBLIGATORIAMENTE una TABLA con tres columnas exactas:
| Momentos | Estrategias / Actividades (DESCRIPCIÓN SÓLIDA Y PROFESIONAL) | Tiempo |
- En la fila de INICIO: Explica detalladamente y paso a paso cómo se realizará la Motivación, el recojo de Saberes Previos, la Problematización (generación del conflicto cognitivo) y la presentación del Propósito. La redacción debe ser profunda, clara y evidenciar la interacción docente-estudiante.
- En la fila de DESARROLLO (PROCESO): Esta es la parte más importante. DEBES ESCRIBIR EN NEGRITA CADA UNO DE LOS SIGUIENTES PROCESOS DIDÁCTICOS DEL ÁREA: {procesos_area}. Para cada proceso, explica a detalle las acciones del docente (mediación) y las acciones de los estudiantes. Explica cómo se promueve el razonamiento, el pensamiento crítico y la indagación (evita actividades mecánicas).
- En la fila de CIERRE: Explica a detalle la Evaluación formativa (cómo se comprueba el aprendizaje) y la Metacognición (incluye preguntas reflexivas específicas y retadoras que se harán a los estudiantes).

**Firmas:**
(Añade este espacio exacto antes de pasar a los anexos para la validación del documento):

_______________________________________
Docente: [Escribe el nombre del docente]

_______________________________________
V° B° Director(a) / Sub Director(a)


**VI.- Anexos:**
- **Anexo N° 1: Instrumento de Evaluación:** (Crea el instrumento real, ej: lista de cotejo o rúbrica en formato TABLA con los criterios desarrollados).
- **Anexo N° 2: Ficha de Trabajo para el Estudiante:** (Crea una ficha de trabajo alineada al propósito de la sesión, promoviendo el pensamiento crítico según el área).
"""
    return base

# --- ESTILOS UX/UI INSTITUCIONALES ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🇵🇪")

st.markdown("""
    <style>
    :root {
        --minedu-red: #C8102E;
        --minedu-blue: #003366;
        --light-bg: #F4F6F9;
    }
    .main { background-color: var(--light-bg); }
    
    /* Header Container */
    .header-box {
        background: linear-gradient(135deg, var(--minedu-blue) 0%, #1e40af 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0, 51, 102, 0.2);
        border-bottom: 5px solid var(--minedu-red);
    }
    .header-box h1 { color: white; font-size: 2.5rem; margin: 0; font-weight: 800;}
    .header-box p { color: #e2e8f0; font-size: 1.1rem; margin-top: 10px; }
    
    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px 8px 0 0;
        padding: 10px 20px; font-weight: 700; color: var(--minedu-blue);
    }
    .stTabs [aria-selected="true"] { background-color: var(--minedu-red) !important; color: white !important; }
    
    /* Cards */
    .section-container {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-left: 5px solid var(--minedu-blue);
    }
    
    /* Buttons */
    .stButton>button {
        background: var(--minedu-blue); color: white; font-weight: bold;
        border-radius: 8px; border: none; transition: all 0.3s ease; width: 100%;
        text-transform: uppercase;
    }
    .stButton>button:hover { background: var(--minedu-red); transform: translateY(-2px); }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN PARA CARGAR LOGO LOCAL EN BASE64 ---
def get_image_base64(image_path):
    """Convierte la imagen local a Base64 para inyectarla en el HTML."""
    try:
        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        # Fallback en caso no exista el archivo logo.jpg
        return "https://cdn-icons-png.flaticon.com/512/8066/8066104.png"

# --- INICIALIZACIÓN DE ESTADO ---
if 'resultados' not in st.session_state:
    st.session_state.resultados = {"anual": None, "unidad": None, "sesion": None}

# --- FUNCIONES DE EXPORTACIÓN A WORD ---
def construir_tabla_word(doc, matriz_datos):
    if not matriz_datos: return
    num_cols = max(len(fila) for fila in matriz_datos)
    table = doc.add_table(rows=len(matriz_datos), cols=num_cols)
    table.style = 'Table Grid'
    for i, fila in enumerate(matriz_datos):
        for j, celda in enumerate(fila):
            if j < num_cols:
                cell = table.cell(i, j)
                texto_limpio = celda.replace('**', '').replace('*', '')
                cell.text = texto_limpio
                if i == 0:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs: run.font.bold = True
    doc.add_paragraph()

def generar_word_pro(titulo, contenido, ie, dist, area, grado):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # Encabezado
    header = doc.sections[0].header
    p_header = header.paragraphs[0]
    p_header.text = f"SISTEMA EDUPLAN IA - UGEL LA CONVENCIÓN\nI.E. {ie} | Distrito: {dist}"
    p_header.style.font.size = Pt(9)
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    titulo_doc = doc.add_heading(titulo, level=1)
    titulo_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Tabla de Datos Informativos superior
    table_info = doc.add_table(rows=2, cols=2)
    table_info.style = 'Table Grid'
    celdas_info = [
        (0, 0, "ÁREA:", area), (0, 1, "GRADO/EDAD:", grado),
        (1, 0, "DOCENTE:", LIDER), (1, 1, "AÑO LECTIVO:", str(ANIO_ACTUAL))
    ]
    for row, col, etiqueta, valor in celdas_info:
        p = table_info.cell(row, col).paragraphs[0]
        p.add_run(f"{etiqueta} ").bold = True
        p.add_run(valor)

    doc.add_paragraph("\n")
    
    # Parser Simple de Markdown a Word
    lineas = contenido.split('\n')
    tabla_actual = []
    
    for linea in lineas:
        linea = linea.strip()
        if not linea: continue
        if linea.startswith('|') and linea.endswith('|'):
            filas = [celda.strip() for celda in linea.strip('|').split('|')]
            if all(all(c in '-: ' for c in celda) for celda in filas): continue
            tabla_actual.append(filas)
        else:
            if tabla_actual:
                construir_tabla_word(doc, tabla_actual)
                tabla_actual = []
            
            texto_limpio = linea.replace('**', '').replace('*', '')
            if linea.startswith('### '): doc.add_heading(texto_limpio[4:], level=3)
            elif linea.startswith('## '): doc.add_heading(texto_limpio[3:], level=2)
            elif linea.startswith('# '): doc.add_heading(texto_limpio[2:], level=1)
            elif linea.startswith('- '): doc.add_paragraph(texto_limpio[2:], style='List Bullet')
            elif re.match(r'^\d+\.\s', linea): doc.add_paragraph(texto_limpio, style='List Number')
            else: doc.add_paragraph(texto_limpio)
                
    if tabla_actual: construir_tabla_word(doc, tabla_actual)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- LÓGICA DE CONEXIÓN IA ---
def procesar_ia(payload, prompt_sistema):
    if not client:
        return "⚠️ Error: Configura tu API KEY en st.secrets."
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Redacta el documento con rigor pedagógico basándote en esta elección del docente:\n{payload}"}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico: {str(e)}"

# --- INTERFAZ PRINCIPAL ---

logo_url = get_image_base64("logo.jpg")

st.markdown(f"""
    <div class="header-box">
        <img src="{logo_url}" width="130" style="margin-bottom: 15px; border-radius: 50%; box-shadow: 0px 6px 15px rgba(0,0,0,0.4); border: 3px solid white;">
        <h1>{NOMBRE_APP}</h1>
        <p>Generación Automática de Documentos CNEB {ANIO_ACTUAL} con IA</p>
    </div>
""", unsafe_allow_html=True)

# SIDEBAR: Contexto Fijo
with st.sidebar:
    st.title("⚙️ Datos Fijos")
    st.markdown("Selecciona el grado y área a planificar.")
    
    ie_nombre = st.text_input("Institución Educativa", "IE Virgen del Carmen")
    distrito_sel = st.selectbox("Distrito", DISTRICTS)
    nivel_global = st.radio("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"])
    
    if nivel_global == "Inicial":
        areas = ["Personal Social", "Psicomotriz", "Comunicación", "Matemática", "Descubrimiento del Mundo"]
        grados = ["3 años", "4 años", "5 años"]
    elif nivel_global == "Primaria":
        areas = ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Educación Física", "Arte y Cultura", "Educación Religiosa"]
        grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
    else: 
        areas = ["Matemática", "Comunicación", "Inglés", "Arte y Cultura", "Ciencias Sociales", "DPCC", "Educación Física", "Ciencia y Tecnología", "EPT", "Tutoría"]
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
    
    area_sel = st.selectbox("Área Curricular", areas)
    grado_sel = st.selectbox("Grado / Edad", grados)
    enfoque_transversal = st.selectbox("🌱 Enfoque Transversal", ENFOQUES_TRANSVERSALES)
    
    # NUEVO: Mostramos al docente el enfoque del área que aplicará la IA
    st.info(f"📌 **Enfoque CNEB detectado:**\n{ENFOQUES_AREAS.get(area_sel, '')}")

tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE APRENDIZAJE"])

# MOTOR DE RENDERIZADO SIMPLIFICADO PARA EL DOCENTE
def render_generador(tipo_doc, tab_key):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader(f"📝 Opciones para: {tipo_doc}")
    st.info("💡 La IA construirá las competencias y procesos didácticos automáticamente según el área seleccionada.")
    
    col1, col2 = st.columns(2)
    with col1:
        contexto_doc = st.selectbox(
            "Selecciona la Problemática o Contexto Local:", 
            CONTEXTOS_LOCALES, 
            key=f"ctx_{tab_key}"
        )
        if contexto_doc == "Otro contexto (Especificar brevemente)":
            contexto_doc = st.text_input("Escribe el contexto brevemente:", key=f"ctx_custom_{tab_key}")
            
    with col2:
        titulo_doc = st.text_input(
            "Tema o Título sugerido (Breve):", 
            placeholder="Ej: Resolvemos problemas de la cosecha...", 
            key=f"tit_{tab_key}"
        )

    # Ajustes extra si es Sesión
    opciones_extra = ""
    if tipo_doc == "Sesión de Aprendizaje":
        with st.expander("Ajustes Extra (Opcional)", expanded=False):
            nee = st.toggle("Sugerencias para Inclusión (NEE)")
            inst_eval = st.selectbox("Instrumento", ["Lista de Cotejo", "Rúbrica", "Ficha de Observación"])
            opciones_extra = f"\n- Adaptación NEE: {'Sí' if nee else 'No'}\n- Instrumento: {inst_eval}"

    # Payload simplificado
    payload = f"""
- Institución Educativa: {ie_nombre}
- Docente: {LIDER}
- Nivel, Grado y Área: {nivel_global} - {grado_sel} - {area_sel}
- Problema/Contexto Local: {contexto_doc}
- Tema de la clase/unidad: {titulo_doc}
- Enfoque Transversal: {enfoque_transversal}
{opciones_extra}
"""
    prompt_dinamico = obtener_prompt_cneb(tipo_doc, area_sel, nivel_global)

    if st.button(f"🚀 GENERAR {tipo_doc.upper()} MÁGICAMENTE", key=f"btn_{tab_key}"):
        if not titulo_doc:
            st.error("🛑 Ingresa un Tema o Título breve para guiar a la IA.")
        else:
            with st.status(f"🤖 Estructurando bajo el enfoque de {ENFOQUES_AREAS.get(area_sel, '')}...", expanded=True) as status:
                st.write("📖 Diseñando Situación Significativa con pensamiento crítico...")
                st.write(f"⚙️ Estructurando procesos didácticos: {PROCESOS_DIDACTICOS.get(area_sel, '').split('.')[1]}...")
                resultado = procesar_ia(payload, prompt_dinamico)
                st.session_state.resultados[tab_key] = (resultado, titulo_doc)
                status.update(label="¡Documento CNEB Generado!", state="complete", expanded=False)

    # Mostrar Resultados y Descargar
    if st.session_state.resultados[tab_key]:
        resultado_actual, titulo_guardado = st.session_state.resultados[tab_key]
        
        st.divider()
        st.markdown(f"### 📋 Vista Previa")
        with st.container(height=450, border=True):
            st.markdown(resultado_actual) 
        
        st.divider()
        file_word = generar_word_pro(f"{tipo_doc.upper()}: {titulo_guardado}", resultado_actual, ie_nombre, distrito_sel, area_sel, grado_sel)
        
        st.download_button(
            label="📥 EXPORTAR A MICROSOFT WORD (.DOCX)", 
            data=file_word, 
            file_name=f"{tipo_doc.replace(' ', '_')}_{grado_sel}_{area_sel}.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"dl_{tab_key}",
            use_container_width=True
        )
            
    st.markdown('</div>', unsafe_allow_html=True)

with tab1: render_generador("Programación Anual", "anual")
with tab2: render_generador("Unidad Didáctica", "unidad")
with tab3: render_generador("Sesión de Aprendizaje", "sesion")

# Footer 
st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: var(--minedu-blue); color: white; border-radius: 8px;">
        <p style="margin: 0; font-size: 0.9em;">
        <b>EDUPLAN IA</b> - Innovación Pedagógica CNEB | Dirigido por {LIDER} © {ANIO_ACTUAL}
        </p>
    </div>
""", unsafe_allow_html=True)

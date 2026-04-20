import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import io
import re
import datetime
import base64
import requests
import urllib.parse

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
    "Matemática": "1. Comprensión del problema. 2. Búsqueda de estrategias. 3. Representación (concreto → simbólico). 4. Formalización. 5. Reflexión y transferencia.",
    "Comunicación": "1. Antes de la lectura/texto. 2. Durante la lectura/producción. 3. Después de la lectura/revisión.",
    "Personal Social": "1. Problematización. 2. Análisis de información. 3. Acuerdos / Toma de decisiones.",
    "Ciencias Sociales": "1. Problematización. 2. Análisis de información. 3. Acuerdos / Toma de decisiones.",
    "DPCC": "1. Problematización. 2. Análisis de información. 3. Acuerdos / Toma de decisiones.",
    "Ciencia y Tecnología": "1. Planteamiento del problema. 2. Planteamiento de hipótesis. 3. Elaboración del plan de acción. 4. Recojo de datos y análisis de resultados. 5. Estructuración del saber construido. 6. Evaluación y comunicación.",
    "Educación Física": "1. Motivación, exploración y calentamiento. 2. Desarrollo de la actividad central. 3. Vuelta a la calma y relajación.",
    "Arte y Cultura": "1. Desafío/Reto. 2. Exploración y experimentación. 3. Producción preliminar. 4. Revisión y afinamiento. 5. Presentación y reflexión.",
    "Educación Religiosa": "1. Ver. 2. Juzgar. 3. Actuar. 4. Revisar. 5. Celebrar.",
    "Inglés": "1. Pre-task (Motivación/Input). 2. Task cycle (Ejecución). 3. Language focus (Análisis/Reflexión).",
    "EPT": "1. Crear/Diseñar (Design Thinking). 2. Planificar. 3. Ejecutar. 4. Evaluar.",
    "Psicomotriz": "1. Asamblea. 2. Expresividad motriz. 3. Relajación. 4. Expresión gráfico-plástica. 5. Cierre.",
    "Descubrimiento del Mundo": "1. Observación. 2. Planteamiento de preguntas. 3. Exploración. 4. Comunicación.",
    "Tutoría": "1. Presentación. 2. Desarrollo. 3. Cierre."
}

PROCESOS_PEDAGOGICOS = [
    "Motivación", "Saberes previos", "Problematización", 
    "Propósito y organización", "Gestión y acompañamiento", "Evaluación"
]

# --- MATRIZ DE COMPETENCIAS Y CAPACIDADES CNEB ---
MATRIZ_COMPETENCIAS = {
    "Personal Social": "Competencia: Construye su identidad. Capacidades: Se valora a sí mismo / Autorregula sus emociones / Reflexiona y argumenta éticamente / Vive su sexualidad de manera integral.\nCompetencia: Se desenvuelve de manera autónoma a través de su motricidad.\nCompetencia: Asume una vida saludable.\nCompetencia: Interactúa a través de sus habilidades sociomotrices.\nCompetencia: Convive y participa democráticamente en la búsqueda del bien común. Capacidades: Interactúa con todas las personas / Construye normas y asume acuerdos / Maneja conflictos / Delibera sobre asuntos públicos / Participa en acciones que promueven el bienestar común.\nCompetencia: Construye interpretaciones históricas.\nCompetencia: Gestiona responsablemente el espacio y el ambiente.\nCompetencia: Gestiona responsablemente los recursos económicos.",
    "DPCC": "Competencia: Construye su identidad. Capacidades: Se valora a sí mismo / Autorregula sus emociones / Reflexiona y argumenta éticamente / Vive su sexualidad de manera integral.\nCompetencia: Convive y participa democráticamente en la búsqueda del bien común. Capacidades: Interactúa con todas las personas / Construye normas y asume acuerdos / Maneja conflictos / Delibera sobre asuntos públicos / Participa en acciones que promueven el bienestar común.",
    "Ciencias Sociales": "Competencia: Construye interpretaciones históricas.\nCompetencia: Gestiona responsablemente el espacio y el ambiente.\nCompetencia: Gestiona responsablemente los recursos económicos.",
    "Comunicación": "Competencia: Se comunica oralmente en su lengua materna. Capacidades: Obtiene información del texto oral / Infiere e interpreta información / Adecúa, organiza y desarrolla las ideas / Utiliza recursos no verbales / Interactúa estratégicamente / Reflexiona y evalúa.\nCompetencia: Lee diversos tipos de textos escritos en su lengua materna. Capacidades: Obtiene información del texto escrito / Infiere e interpreta información / Reflexiona y evalúa la forma, el contenido y contexto.\nCompetencia: Escribe diversos tipos de textos en su lengua materna. Capacidades: Adecúa el texto a la situación comunicativa / Organiza y desarrolla las ideas de forma coherente / Utiliza convenciones del lenguaje escrito / Reflexiona y evalúa.",
    "Inglés": "Competencia: Se comunica oralmente en inglés. Capacidades: Obtiene información del texto oral / Infiere e interpreta información / Adecúa, organiza y desarrolla las ideas / Utiliza recursos no verbales / Interactúa estratégicamente / Reflexiona y evalúa.\nCompetencia: Lee diversos tipos de textos escritos en inglés. Capacidades: Obtiene información del texto escrito / Infiere e interpreta información / Reflexiona y evalúa la forma, el contenido y contexto.\nCompetencia: Escribe diversos tipos de textos en inglés. Capacidades: Adecúa el texto a la situación comunicativa / Organiza y desarrolla las ideas de forma coherente / Utiliza convenciones del lenguaje escrito / Reflexiona y evalúa.",
    "Arte y Cultura": "Competencia: Aprecia de manera crítica manifestaciones artístico-culturales.\nCompetencia: Crea proyectos desde los lenguajes artísticos. Capacidades: Explora y experimenta los lenguajes del arte / Aplica procesos creativos / Evalúa y comunica sus procesos y proyectos.",
    "Matemática": "Competencia: Resuelve problemas de cantidad. Capacidades: Traduce cantidades a expresiones numéricas / Comunica su comprensión sobre los números / Usa estrategias y procedimientos de estimación / Argumenta afirmaciones.\nCompetencia: Resuelve problemas de regularidad, equivalencia y cambio.\nCompetencia: Resuelve problemas de forma, movimiento y localización.\nCompetencia: Resuelve problemas de gestión de datos e incertidumbre.",
    "Ciencia y Tecnología": "Competencia: Indaga mediante métodos científicos para construir sus conocimientos. Capacidades: Problematiza situaciones / Diseña estrategias para hacer indagación / Genera y registra datos o información / Analiza datos e información / Evalúa y comunica.\nCompetencia: Explica el mundo físico basándose en conocimientos sobre los seres vivos, materia y energía, biodiversidad, Tierra y universo.\nCompetencia: Diseña y construye soluciones tecnológicas para resolver problemas de su entorno.",
    "Educación Religiosa": "Competencia: Construye su identidad como persona humana, amada por Dios, digna, libre y trascendente.\nCompetencia: Asume la experiencia el encuentro personal y comunitario con Dios en su proyecto de vida.",
    "EPT": "Competencia: Gestiona proyectos de emprendimiento económico o social. Capacidades: Crea propuestas de valor / Aplica habilidades técnicas / Trabaja cooperativamente para lograr objetivos / Evalúa los resultados del proyecto.",
    "Descubrimiento del Mundo": "Competencia: Indaga mediante métodos científicos para construir sus conocimientos. Capacidades: Problematiza situaciones / Diseña estrategias para hacer indagación / Genera y registra datos o información / Analiza datos e información / Evalúa y comunica.",
    "Psicomotriz": "Competencia: Se desenvuelve de manera autónoma a través de su motricidad. Capacidades: Comprende su cuerpo / Se expresa corporalmente.",
    "Educación Física": "Competencia: Se desenvuelve de manera autónoma a través de su motricidad.\nCompetencia: Asume una vida saludable.\nCompetencia: Interactúa a través de sus habilidades sociomotrices.",
    "Tutoría": "Dimensión: Desarrollo personal / Desarrollo de los aprendizajes / Desarrollo social comunitario."
}

COMPETENCIAS_TRANSVERSALES = """Competencia: Se desenvuelve en los entornos virtuales generados por las TIC. Capacidades: Personaliza entornos virtuales / Gestiona información del entorno virtual / Interactúa en entornos virtuales / Crea objetos virtuales en diversos formatos.
Competencia: Gestiona su aprendizaje de manera autónoma. Capacidades: Define metas de aprendizaje / Organiza acciones estratégicas para alcanzar sus metas / Monitorea y ajusta su desempeño."""

# --- PROGRESIÓN DE ESTÁNDARES POR CICLO (REFERENCIA CNEB) ---
def obtener_ciclo(nivel, grado):
    if nivel == "Inicial": return "Ciclo II"
    if nivel == "Primaria":
        if grado in ["1ro", "2do"]: return "Ciclo III"
        if grado in ["3ro", "4to"]: return "Ciclo IV"
        if grado in ["5to", "6to"]: return "Ciclo V"
    if nivel == "Secundaria":
        if grado in ["1ro", "2do"]: return "Ciclo VI"
        if grado in ["3ro", "4to", "5to"]: return "Ciclo VII"
    return "Ciclo no definido"

ESTANDARES_LECTURA_CNEB = {
    "Ciclo II": "Lee diversos tipos de textos que tratan temas reales o imaginarios que le son cotidianos, en los que predominan palabras conocidas y que se acompañan con ilustraciones. Construye hipótesis o predicciones sobre la información contenida en los textos...",
    "Ciclo III": "Lee diversos tipos de textos de estructura simple en los que predominan palabras conocidas e ilustraciones que apoyan las ideas centrales. Obtiene información poco evidente distinguiéndola de otra semejante y realiza inferencias locales a partir de información explícita...",
    "Ciclo IV": "Lee diversos tipos de textos que presentan estructura simple con algunos elementos complejos y con vocabulario variado. Obtiene información poco evidente distinguiéndola de otras próximas y semejantes. Realiza inferencias locales a partir de información explícita e implícita...",
    "Ciclo V": "Lee diversos tipos de textos con varios elementos complejos en su estructura y con vocabulario variado. Obtiene información e integra datos que están en distintas partes del texto. Realiza inferencias locales a partir de información explícita e implícita...",
    "Ciclo VI": "Lee diversos tipos de texto con estructuras complejas y vocabulario variado. Integra información contrapuesta que está en distintas partes del texto. Interpreta el texto considerando información relevante y complementaria para construir su sentido global...",
    "Ciclo VII": "Lee diversos tipos de texto con estructuras complejas y vocabulario variado. Integra información contrapuesta que está en distintas partes del texto. Interpreta el texto considerando información relevante y de detalle para construir su sentido global..."
}

# --- CALENDARIO ESCOLAR MINEDU (DIRECTRICES DE PLANIFICACIÓN) ---
CALENDARIO_MINEDU = """CALENDARIZACIÓN ESCOLAR MINEDU (REFERENCIAL 36 SEMANAS LECTIVAS Y 4 DE GESTIÓN):
- Primer bloque de semanas de gestión: 2 semanas (Inicio de marzo).
- Primer bloque de semanas lectivas (I Bimestre): 9 semanas (Aprox. Marzo a Mayo).
- Segundo bloque de semanas lectivas (II Bimestre): 9 semanas (Aprox. Mayo a Julio).
- Segundo bloque de semanas de gestión (Vacaciones de estudiantes): 2 semanas (Fines de Julio / Inicios de Agosto).
- Tercer bloque de semanas lectivas (III Bimestre): 9 semanas (Aprox. Agosto a Octubre).
- Cuarto bloque de semanas lectivas (IV Bimestre): 9 semanas (Aprox. Octubre a Diciembre).
- Tercer bloque de semanas de gestión: 1 a 2 semanas (Fines de Diciembre)."""

# --- ESQUEMA DE EXPERIENCIA DE APRENDIZAJE (EdA) MINEDU ---
ESQUEMA_EDA_MINEDU = """ESTRUCTURA OFICIAL DE LA EXPERIENCIA DE APRENDIZAJE (EdA):
1. Planteamiento de la situación.
2. Propósito de aprendizaje.
3. Enfoques transversales.
4. Producciones / actuaciones.
5. Criterios de evaluación e Instrumentos.
6. Secuencia de actividades sugeridas (Ruta en 3 fases: 1. Planteamos la situación -> 2. Desarrollamos las competencias -> 3. Evaluación y comunicación del producto o resultados)."""

# --- CONEXIÓN SEGURA CON LA API ---
try:
    api_key = st.secrets.get("ZHIPU_KEY", "TU_API_KEY_AQUI_SI_NO_USAS_SECRETS")
    client = ZhipuAI(api_key=api_key)
except Exception:
    client = None

# --- MOTOR DE PROMPTS CNEB (CEREBRO PEDAGÓGICO ACTUALIZADO BADO EN MODELO) ---
def obtener_prompt_cneb(tipo_doc, area, nivel, grado, tema=""):
    ciclo = obtener_ciclo(nivel, grado)
    enfoque_area = ENFOQUES_AREAS.get(area, "Enfoque por competencias")
    procesos_area = PROCESOS_DIDACTICOS.get(area, "1. Inicio, 2. Desarrollo, 3. Cierre")
    procesos_pedagogicos_str = ", ".join(PROCESOS_PEDAGOGICOS)
    competencias_capacidades_area = MATRIZ_COMPETENCIAS.get(area, "Competencias y capacidades del área.")

    info_estandar_extra = ""
    if area == "Comunicación":
        estandar_ciclo = ESTANDARES_LECTURA_CNEB.get(ciclo, "")
        info_estandar_extra = f"\n- ESTÁNDAR DE APRENDIZAJE REFERENCIAL ({ciclo}): {estandar_ciclo}"

    base = f"""Eres "EDUPLAN IA", un Especialista Senior y Mentor Pedagógico del MINEDU con más de 20 años de experiencia en la Educación Básica Regular del Perú.
Tu misión es redactar un/una '{tipo_doc}' de nivel profesional superior, listo para impresión, para el área de {area} enfocado específicamente en estudiantes del nivel {nivel} ({ciclo}).
Tema central solicitado: {tema}

BASE NORMATIVA Y DOCUMENTAL ESTRICTA QUE DEBES APLICAR:
1. Currículo Nacional de la Educación Básica (CNEB).
2. Programa Curricular de Educación {nivel} (Utiliza las competencias, capacidades y estándares correspondientes a la edad/ciclo de los estudiantes de {nivel} y del {ciclo}).
3. RVM N° 094-2020-MINEDU (Obligatorio aplicar la Evaluación Formativa: formulación de criterios de evaluación, evidencias pertinentes e instrumentos claros).

DATOS CLAVE DEL CNEB PARA ESTA ÁREA QUE DEBES APLICAR ESTRICTAMENTE:
- Nivel y Ciclo: {nivel} - {ciclo} (DEBES adaptar la complejidad estrictamente a este ciclo).
- Enfoque del Área: {enfoque_area}
- Procesos Didácticos del Área: {procesos_area}
- Procesos Pedagógicos (Generales): {procesos_pedagogicos_str}
- MATRIZ DE COMPETENCIAS Y CAPACIDADES DEL ÁREA (Obligatorio movilizar estas capacidades simultáneamente):
{competencias_capacidades_area}
- COMPETENCIAS TRANSVERSALES (Afectan a todas las áreas):
{COMPETENCIAS_TRANSVERSALES}{info_estandar_extra}
- ESTRUCTURA DEL CALENDARIO MINEDU VIGENTE:
{CALENDARIO_MINEDU}
- ESQUEMA DE EXPERIENCIA DE APRENDIZAJE (EdA):
{ESQUEMA_EDA_MINEDU}

TU MISIÓN: El docente te dará información mínima. TÚ DEBES desarrollar todo el documento con altísimo rigor académico, pertinencia para el nivel {nivel} y calidad de IMPRENTA/EDITORIAL basándote en modelos de sesiones de alto rendimiento.

REGLAS INQUEBRANTABLES DE FORMATO:
1. Usa Markdown estándar (Títulos con ## y ###). No uses HTML.
2. Construye TABLAS LIMPIAS usando solo `|` y `-`. NUNCA unas celdas.
3. El lenguaje debe ser técnico-pedagógico peruano, adecuado al desarrollo cognitivo de {nivel}, motivador y orientado a la excelencia.
"""

    if tipo_doc == "Programación Anual":
        base += f"""
ESTRUCTURA OBLIGATORIA (PROGRAMACIÓN ANUAL - NIVEL {nivel.upper()}):
1. **DATOS INFORMATIVOS.**
2. **DESCRIPCIÓN GENERAL:** Describe brevemente el contexto y las características de los estudiantes de {nivel}.
3. **PROPÓSITOS DE APRENDIZAJE:** TABLA con Competencias, Capacidades y Estándares precisos para el ciclo correspondiente de {nivel}.
4. **ORGANIZACIÓN DE LAS UNIDADES DIDÁCTICAS/PROYECTOS:** TABLA organizada por bimestres/trimestres con Título, Situación Significativa, Duración y Productos.
5. **ENFOQUES TRANSVERSALES:** Priorizados en el año.
6. **ESTRATEGIAS METODOLÓGICAS Y RECURSOS:** Específicos para el aprendizaje en {nivel}.
7. **EVALUACIÓN:** Según RVM 094-2020 (Diagnóstica, formativa y sumativa).
"""
    elif tipo_doc == "Unidad Didáctica":
        base += f"""
ESTRUCTURA OBLIGATORIA (UNIDAD DIDÁCTICA / EXPERIENCIA DE APRENDIZAJE - NIVEL {nivel.upper()}):
1. **DATOS INFORMATIVOS.**
2. **PLANTEAMIENTO DE LA SITUACIÓN:** Debe contener un Contexto altamente descriptivo, un Problema y el Reto (pregunta movilizadora).
3. **PROPÓSITOS DE APRENDIZAJE Y ENFOQUES TRANSVERSALES:** TABLA relacionando Competencias, Capacidades, Desempeños precisados (para {nivel}) y Enfoques Transversales.
4. **PRODUCCIONES / ACTUACIONES Y CRITERIOS DE EVALUACIÓN:** Define el Producto final esperado adaptado a {nivel}, con sus evidencias, criterios de evaluación e instrumentos.
5. **SECUENCIA DE ACTIVIDADES SUGERIDAS (RUTA DE APRENDIZAJE):** TABLA resumen dividida obligatoriamente en las 3 fases de la EdA: 
   - *Fase 1: Planteamos la situación.*
   - *Fase 2: Desarrollamos las competencias.*
   - *Fase 3: Evaluación y comunicación del producto o resultados.*
   Indica para cada actividad/sesión: N° Sesión, Título, Desempeño y Actividad principal.
6. **MATERIALES Y RECURSOS.**
"""
    elif tipo_doc == "Sesión de Aprendizaje":
        base += f"""
ESTRUCTURA OBLIGATORIA ESTRICTA (BASADO EN MODELO OFICIAL CNEB - NIVEL {nivel.upper()}):

**SESIÓN DE APRENDIZAJE N° [Asigna un número]: [Escribe el título sugerido, atractivo y relacionado al reto]**

**1. DATOS INFORMATIVOS:**
(Llenar con los datos provistos: I.E., Grado, Área, Fecha, Duración. DEBES DEJAR EL ESPACIO DEL DOCENTE EN BLANCO: Docente: ________________________)

**2. TÍTULO DE LA ACTIVIDAD:**
[Repetir el Título]

**3. PROPÓSITOS Y EVIDENCIAS DE APRENDIZAJE:**
TABLA: | Competencias / Capacidades | Desempeños precisados ({nivel}) | Evidencias de aprendizaje | Criterios de evaluación | Instrumento de evaluación |

**4. ENFOQUE TRANSVERSAL:**
TABLA: | Enfoque Transversal | Valor | Actitudes o acciones observables (adaptado a {nivel}) |

**5. PREPARACIÓN DE LA SESIÓN:**
TABLA: | ¿Qué se debe hacer antes de la sesión? | ¿Qué recursos o materiales se utilizarán en la sesión? |

**6. MOMENTOS DE LA SESIÓN:**
OBLIGATORIO: DEBES CREAR UNA TABLA ESTRUCTURADA DE 3 COLUMNAS PARA ESTA SECCIÓN CON EL SIGUIENTE FORMATO EXACTO:
| MOMENTOS | ESTRATEGIAS Y ACTIVIDADES | TIEMPO |
|---|---|---|
| **INICIO** | Saludo y normas de convivencia. Motivación y Saberes previos. Problematización (Conflicto cognitivo). **MUY IMPORTANTE:** Declara explícitamente a los estudiantes el **PROPÓSITO** de la clase y los **CRITERIOS DE EVALUACIÓN** en este momento. | [Aprox] |
| **DESARROLLO** | **PROCESOS DIDÁCTICOS DEL ÁREA:** ({procesos_area}). Escribe en negrita cada proceso didáctico. Detalla minuciosamente la gestión, el acompañamiento docente y la actividad del estudiante. | [Aprox] |
| **CIERRE** | Evaluación formativa. Metacognición con preguntas claras (¿Qué aprendimos?, ¿Cómo lo hicimos?, ¿Para qué sirve?, ¿Qué dificultades tuvimos?). | [Aprox] |

**7. REFLEXIONES DEL APRENDIZAJE:**
(Deja estos espacios en blanco con líneas punteadas para que el docente los llene después de dictar la clase)
- ¿Qué avances tuvieron mis estudiantes? ..............................................................
- ¿Qué dificultades tuvieron mis estudiantes? ..........................................................
- ¿Qué aprendizajes debo reforzar en la siguiente sesión? ..............................................
- ¿Qué actividades, estrategias y materiales funcionaron y cuáles no? ..................................

**Firma:**
_______________________________________                  _______________________________________
V° B° Director(a) / Sub Director(a)                      Docente: _________________________

**8. ANEXOS:**
- **Anexo N° 1: Instrumento de Evaluación:** TABLA PROFESIONAL (Lista de cotejo o Rúbrica) basada estrictamente en los criterios declarados en la sección 3, con un listado simulado (o en blanco) para estudiantes.
- **Anexo N° 2: Ficha de Aplicación / Trabajo para el Estudiante (CALIDAD IMPRENTA/EDITORIAL):** * Diseña una ficha visualmente atractiva exclusiva para el nivel cognitivo de {nivel}. 
  * DEBES INCLUIR OBLIGATORIAMENTE ESTA ETIQUETA EXACTA donde deba ir una imagen ilustrativa atractiva: `[IMAGEN_SUGERIDA: descripción muy detallada de la imagen en inglés, estilo ilustración infantil o juvenil]`. Nuestro sistema la reemplazará por una imagen real.
  * Incluye al final de la ficha un breve cuadro de **Autoevaluación del Estudiante** (Ej. "¡Así evaluó mis aprendizajes!" con criterios "Lo logré", "Lo estoy intentando", "Necesito ayuda").
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
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px 8px 0 0;
        padding: 10px 20px; font-weight: 700; color: var(--minedu-blue);
    }
    .stTabs [aria-selected="true"] { background-color: var(--minedu-red) !important; color: white !important; }
    
    .section-container {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-left: 5px solid var(--minedu-blue);
    }
    
    .stButton>button {
        background: var(--minedu-blue); color: white; font-weight: bold;
        border-radius: 8px; border: none; transition: all 0.3s ease; width: 100%;
        text-transform: uppercase;
    }
    .stButton>button:hover { background: var(--minedu-red); transform: translateY(-2px); }
    </style>
""", unsafe_allow_html=True)

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        return "https://cdn-icons-png.flaticon.com/512/8066/8066104.png"

if 'resultados' not in st.session_state:
    st.session_state.resultados = {"anual": None, "unidad": None, "sesion": None}

# --- FUNCIONES DE EXPORTACIÓN A WORD (CALIDAD IMPRENTA) ---

def aplicar_fondo_celda(cell, color_hex):
    """Aplica color de fondo a una celda de la tabla."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def construir_tabla_word(doc, matriz_datos):
    if not matriz_datos: return
    num_cols = max(len(fila) for fila in matriz_datos)
    table = doc.add_table(rows=len(matriz_datos), cols=num_cols)
    table.style = 'Table Grid'
    table.autofit = True

    for i, fila in enumerate(matriz_datos):
        for j, celda in enumerate(fila):
            if j < num_cols:
                cell = table.cell(i, j)
                texto_limpio = celda.replace('**', '').replace('*', '')
                
                # REQUERIMIENTO CUBIERTO: Detectar y cambiar etiquetas <br>, <br/> o <br > por verdaderos saltos de línea en Word.
                texto_limpio = re.sub(r'<br\s*/?>', '\n', texto_limpio, flags=re.IGNORECASE)
                
                # Asignar el texto a la celda limpiando espacios iniciales o finales innecesarios
                cell.text = texto_limpio.strip()
                
                # Estilo de Imprenta para Cabeceras de Tabla
                if i == 0:
                    aplicar_fondo_celda(cell, "EAEAEA") # Gris claro tipo imprenta
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        for run in paragraph.runs: 
                            run.font.bold = True
                            run.font.color.rgb = RGBColor(0, 51, 102) # Azul institucional
                else:
                    # Justificar contenido interno para mayor limpieza
                    for paragraph in cell.paragraphs:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.add_paragraph()

def insertar_imagen_generada(doc, prompt_imagen):
    """Descarga una imagen por IA generativa basada en el prompt y la inserta en el Word."""
    try:
        # Codificamos el texto para la URL, añadiendo contexto educativo y formato limpio
        query = urllib.parse.quote(prompt_imagen + ", ultra high quality, clean white background, educational vector flat style")
        url = f"https://image.pollinations.ai/prompt/{query}?width=600&height=400&nologo=true"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            image_stream = io.BytesIO(response.content)
            # Insertar imagen centrada
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(image_stream, width=Inches(4.5))
            
            # Pie de imagen
            p_caption = doc.add_paragraph("Ilustración de la Ficha de Trabajo")
            p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_caption.runs[0].font.size = Pt(8)
            p_caption.runs[0].font.italic = True
    except Exception as e:
        # Si falla, simplemente agregamos un marco referencial
        doc.add_paragraph(f"[Espacio para Imagen: {prompt_imagen}]").alignment = WD_ALIGN_PARAGRAPH.CENTER

def generar_word_pro(titulo, contenido, ie, dist, area, grado):
    doc = Document()
    
    # 1. Ajustes Editoriales: Márgenes de hoja (Formato Imprenta)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # 2. Configurar Fuentes Base (Calibri, estilo moderno y limpio)
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # 3. Encabezado Institucional
    header = doc.sections[0].header
    p_header = header.paragraphs[0]
    p_header.text = f"SISTEMA EDUPLAN IA - UGEL LA CONVENCIÓN\nI.E. {ie} | Distrito: {dist}"
    p_header.style.font.size = Pt(8)
    p_header.style.font.bold = True
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # 4. Título Principal
    titulo_doc = doc.add_heading(level=1)
    run_titulo = titulo_doc.add_run(titulo)
    run_titulo.font.name = 'Calibri'
    run_titulo.font.size = Pt(16)
    run_titulo.font.bold = True
    run_titulo.font.color.rgb = RGBColor(0, 51, 102) # Azul Minedu
    titulo_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Tabla de Datos Informativos superior (Estilo limpio)
    table_info = doc.add_table(rows=2, cols=2)
    table_info.style = 'Table Grid'
    # CAMBIO SOLICITADO: Dejar el docente en blanco (libre para llenar)
    celdas_info = [
        (0, 0, "ÁREA:", area), (0, 1, "GRADO/EDAD:", grado),
        (1, 0, "DOCENTE:", "_________________________"), (1, 1, "AÑO LECTIVO:", str(ANIO_ACTUAL))
    ]
    for row, col, etiqueta, valor in celdas_info:
        cell = table_info.cell(row, col)
        aplicar_fondo_celda(cell, "F2F2F2") # Gris super claro
        p = cell.paragraphs[0]
        r1 = p.add_run(f"{etiqueta} ")
        r1.bold = True
        r1.font.color.rgb = RGBColor(0, 51, 102)
        p.add_run(valor)

    doc.add_paragraph("\n")
    
    # Parser de Markdown a Word con Integración de Imágenes
    lineas = contenido.split('\n')
    tabla_actual = []
    
    for linea in lineas:
        linea = linea.strip()
        if not linea: continue
        
        # Detección de Tabla
        if linea.startswith('|') and linea.endswith('|'):
            filas = [celda.strip() for celda in linea.strip('|').split('|')]
            if all(all(c in '-: ' for c in celda) for celda in filas): continue
            tabla_actual.append(filas)
        else:
            if tabla_actual:
                construir_tabla_word(doc, tabla_actual)
                tabla_actual = []
            
            # Detección de Etiqueta de Imagen IA
            if "[IMAGEN_SUGERIDA:" in linea:
                match = re.search(r'\[IMAGEN_SUGERIDA:(.*?)\]', linea)
                if match:
                    prompt_img = match.group(1).strip()
                    insertar_imagen_generada(doc, prompt_img)
                continue # Evita imprimir el texto de la etiqueta
            
            texto_limpio = linea.replace('**', '').replace('*', '')
            
            # Títulos y Subtítulos Estilizados
            if linea.startswith('### '): 
                h = doc.add_heading(level=3)
                r = h.add_run(texto_limpio[4:])
                r.font.name = 'Calibri'
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = RGBColor(200, 16, 46) # Rojo Minedu
            elif linea.startswith('## '): 
                h = doc.add_heading(level=2)
                r = h.add_run(texto_limpio[3:])
                r.font.name = 'Calibri'
                r.font.size = Pt(13)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 51, 102) # Azul Minedu
            elif linea.startswith('# '): 
                h = doc.add_heading(level=1)
                r = h.add_run(texto_limpio[2:])
                r.font.name = 'Calibri'
                r.font.size = Pt(15)
                r.font.bold = True
                h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif linea.startswith('- '): 
                p = doc.add_paragraph(texto_limpio[2:], style='List Bullet')
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            elif re.match(r'^\d+\.\s', linea): 
                p = doc.add_paragraph(texto_limpio, style='List Number')
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            else: 
                # Párrafos normales
                p = doc.add_paragraph(texto_limpio)
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Si quedó alguna tabla pendiente de dibujar al final del texto
    if tabla_actual:
        construir_tabla_word(doc, tabla_actual)

    return doc

# --- INTERFAZ PRINCIPAL DE LA APLICACIÓN ---
st.markdown(f"""
    <div class="header-box">
        <h1>{NOMBRE_APP}</h1>
        <p>Asistente Inteligente de Planificación Curricular - CNEB</p>
    </div>
""", unsafe_allow_html=True)

# Contenedor de configuración inicial
with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📋 Datos Generales")
    col1, col2, col3 = st.columns(3)
    with col1:
        ie = st.text_input("Institución Educativa", value="I.E. ")
    with col2:
        distrito = st.selectbox("Distrito", DISTRICTS)
    with col3:
        nivel = st.selectbox("Nivel", ["Inicial", "Primaria", "Secundaria"])
        
    col4, col5, col6 = st.columns(3)
    with col4:
        # Lógica de grados según el nivel
        if nivel == "Inicial":
            grados_disp = ["3 años", "4 años", "5 años"]
        elif nivel == "Primaria":
            grados_disp = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
        else:
            grados_disp = ["1ro", "2do", "3ro", "4to", "5to"]
        grado = st.selectbox("Grado/Edad", grados_disp)
    with col5:
        area = st.selectbox("Área Curricular", list(ENFOQUES_AREAS.keys()))
    with col6:
        tema = st.text_input("Tema o Situación Significativa (Opcional)", placeholder="Ej. Cuidado del medio ambiente")
    st.markdown('</div>', unsafe_allow_html=True)

# Pestañas de generación
tab1, tab2, tab3 = st.tabs(["Sesión de Aprendizaje", "Unidad Didáctica", "Programación Anual"])

with tab1:
    st.markdown("### Generar Sesión de Aprendizaje Estructurada")
    st.info("Generará una Sesión de Aprendizaje con rúbricas y ficha de trabajo lista para imprimir. El nombre del docente aparecerá en blanco para ser llenado a mano.")
    if st.button("🚀 GENERAR SESIÓN DE APRENDIZAJE"):
        if not client:
            st.error("No se ha configurado correctamente el API KEY de ZhipuAI.")
        else:
            with st.spinner("Construyendo la Sesión de Aprendizaje basada en el CNEB... (Esto tomará unos segundos)"):
                prompt_sistema = obtener_prompt_cneb("Sesión de Aprendizaje", area, nivel, grado, tema)
                try:
                    respuesta = client.chat.completions.create(
                        model="glm-4",  # O el modelo que estés usando
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {"role": "user", "content": f"Redacta la Sesión de Aprendizaje de {area} para {grado} de {nivel}."}
                        ],
                        temperature=0.7
                    )
                    texto_generado = respuesta.choices[0].message.content
                    st.session_state.resultados["sesion"] = texto_generado
                    st.success("¡Sesión generada con éxito!")
                except Exception as e:
                    st.error(f"Error al conectar con la IA: {e}")
                    
    if st.session_state.resultados["sesion"]:
        st.markdown(st.session_state.resultados["sesion"])
        doc_generado = generar_word_pro("SESIÓN DE APRENDIZAJE", st.session_state.resultados["sesion"], ie, distrito, area, grado)
        
        bio = io.BytesIO()
        doc_generado.save(bio)
        
        st.download_button(
            label="📥 DESCARGAR SESIÓN EN WORD (LISTA PARA IMPRENTA)",
            data=bio.getvalue(),
            file_name=f"Sesion_{area}_{grado}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="btn_descarga_sesion"
        )

# Para no alargar el código, puedes replicar fácilmente el botón de "Unidad" y "Programación" guiándote del de "Sesión".
with tab2:
    st.markdown("### Generar Unidad Didáctica / Experiencia de Aprendizaje")
    st.info("Próximamente... Usa la estructura de la pestaña 1 para habilitar este botón.")

with tab3:
    st.markdown("### Generar Programación Anual")
    st.info("Próximamente... Usa la estructura de la pestaña 1 para habilitar este botón.")

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
import os
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

CALENDARIO_MINEDU = """CALENDARIZACIÓN ESCOLAR MINEDU (REFERENCIAL 36 SEMANAS LECTIVAS Y 4 DE GESTIÓN):
- Primer bloque de semanas de gestión: 2 semanas (Inicio de marzo).
- Primer bloque de semanas lectivas (I Bimestre): 9 semanas (Aprox. Marzo a Mayo).
- Segundo bloque de semanas lectivas (II Bimestre): 9 semanas (Aprox. Mayo a Julio).
- Segundo bloque de semanas de gestión (Vacaciones de estudiantes): 2 semanas (Fines de Julio / Inicios de Agosto).
- Tercer bloque de semanas lectivas (III Bimestre): 9 semanas (Aprox. Agosto a Octubre).
- Cuarto bloque de semanas lectivas (IV Bimestre): 9 semanas (Aprox. Octubre a Diciembre).
- Tercer bloque de semanas de gestión: 1 a 2 semanas (Fines de Diciembre)."""

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

# --- MOTOR DE PROMPTS CNEB ---
def obtener_prompt_cneb(tipo_doc, area, nivel, grado):
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

BASE NORMATIVA Y DOCUMENTAL ESTRICTA QUE DEBES APLICAR:
1. Currículo Nacional de la Educación Básica (CNEB).
2. Programa Curricular de Educación {nivel} (Utiliza las competencias, capacidades y estándares correspondientes a la edad/ciclo de los estudiantes de {nivel} y del {ciclo}).
3. RVM N° 094-2020-MINEDU (Obligatorio aplicar la Evaluación Formativa: formulación de criterios de evaluación, evidencias pertinentes e instrumentos claros).

DATOS CLAVE DEL CNEB PARA ESTA ÁREA QUE DEBES APLICAR ESTRICTAMENTE:
- Nivel y Ciclo: {nivel} - {ciclo}
- Enfoque del Área: {enfoque_area}
- Procesos Didácticos del Área: {procesos_area}
- Procesos Pedagógicos (Generales): {procesos_pedagogicos_str}
- MATRIZ DE COMPETENCIAS Y CAPACIDADES DEL ÁREA:
{competencias_capacidades_area}
- COMPETENCIAS TRANSVERSALES:
{COMPETENCIAS_TRANSVERSALES}{info_estandar_extra}

TU MISIÓN: Desarrollar todo el documento con altísimo rigor académico y pertinencia para el nivel {nivel}.

REGLAS INQUEBRANTABLES DE FORMATO:
1. Usa Markdown estándar (Títulos con ## y ###). No uses HTML ni etiquetas <br>.
2. Construye TABLAS LIMPIAS usando solo `|` y `-`. NUNCA unas celdas.
3. El lenguaje debe ser técnico-pedagógico peruano.
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
2. **PLANTEAMIENTO DE LA SITUACIÓN:** Debe contener un Contexto altamente descriptivo, un Problema y el Reto.
3. **PROPÓSITOS DE APRENDIZAJE Y ENFOQUES TRANSVERSALES:** TABLA.
4. **PRODUCCIONES / ACTUACIONES Y CRITERIOS DE EVALUACIÓN:** Producto final esperado, evidencias, criterios e instrumentos.
5. **SECUENCIA DE ACTIVIDADES SUGERIDAS:** TABLA resumen en 3 fases.
6. **MATERIALES Y RECURSOS.**
"""
    elif tipo_doc == "Sesión de Aprendizaje":
        # SOLUCIÓN PROBLEMA 2: Se instruye para que Momentos de la Sesión sea estrictamente una tabla y sin etiquetas br.
        base += f"""
ESTRUCTURA OBLIGATORIA ESTRICTA (BASADO EN MODELO OFICIAL CNEB - NIVEL {nivel.upper()}):

**SESIÓN DE APRENDIZAJE N° [Asigna un número]: [Escribe el título sugerido]**

**1. DATOS INFORMATIVOS:**
(Llenar con los datos provistos: I.E., Docente, Grado, Área, Fecha, Duración)

**2. TÍTULO DE LA ACTIVIDAD:**
[Repetir el Título]

**3. PROPÓSITOS Y EVIDENCIAS DE APRENDIZAJE:**
TABLA: | Competencias / Capacidades | Desempeños precisados ({nivel}) | Evidencias de aprendizaje | Criterios de evaluación | Instrumento de evaluación |

**4. ENFOQUE TRANSVERSAL:**
TABLA: | Enfoque Transversal | Valor | Actitudes o acciones observables (adaptado a {nivel}) |

**5. PREPARACIÓN DE LA SESIÓN:**
TABLA: | ¿Qué se debe hacer antes de la sesión? | ¿Qué recursos o materiales se utilizarán en la sesión? |

**6. MOMENTOS DE LA SESIÓN:**
OBLIGATORIO: ESTA SECCIÓN DEBE SER ESTRICTAMENTE UNA TABLA. PROHIBIDO USAR LISTAS Y PROHIBIDO USAR ETIQUETAS HTML COMO <br> o {{br}}. Usa saltos de línea normales o simplemente separa las ideas con puntos.
TABLA: | Momentos | Estrategias / Actividades (Detallar procesos didácticos en negrita) | Tiempo |
| **INICIO** | Saludo y normas. Motivación y saberes previos. Problematización. Declarar el PROPÓSITO y CRITERIOS de la clase. | [X] min |
| **DESARROLLO** | Desarrollar minuciosamente los procesos didácticos: {procesos_area}. Detallar gestión y acompañamiento. | [X] min |
| **CIERRE** | Evaluación formativa. Metacognición con preguntas claras. | [X] min |

**7. REFLEXIONES DEL APRENDIZAJE:**
(Deja estos espacios en blanco con líneas punteadas)
- ¿Qué avances tuvieron mis estudiantes? ..............................................................
- ¿Qué dificultades tuvieron mis estudiantes? ..........................................................
- ¿Qué aprendizajes debo reforzar en la siguiente sesión? ..............................................
- ¿Qué actividades y estrategias funcionaron? ..................................

**Firma:**
_______________________________________                 _______________________________________
V° B° Director(a) / Sub Director(a)                     Docente: [Escribe el nombre del docente]

**8. ANEXOS:**
- **Anexo N° 1: Instrumento de Evaluación:** TABLA PROFESIONAL (Lista de cotejo o Rúbrica).
- **Anexo N° 2: Ficha de Aplicación / Trabajo para el Estudiante:** * Diseña una ficha visualmente atractiva exclusiva para {nivel}. 
  * INCLUIR ESTA ETIQUETA EXACTA: `[IMAGEN_SUGERIDA: descripción detallada en inglés, estilo flat vectorial educativo]`.
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

if 'resultados' not in st.session_state:
    st.session_state.resultados = {"anual": None, "unidad": None, "sesion": None}

# --- FUNCIONES DE EXPORTACIÓN A WORD (CALIDAD IMPRENTA) ---

def aplicar_fondo_celda(cell, color_hex):
    """Aplica color de fondo a una celda de la tabla."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def limpiar_etiquetas_br(texto):
    """SOLUCIÓN PROBLEMA 1: Elimina cualquier variante de etiqueta <br> o {br} para el documento final"""
    if not texto:
        return ""
    # Remplaza <br>, <br/>, <br />, {br}, {br/} por un salto de línea real para que el Word lo interprete bien
    texto_limpio = re.sub(r'<\s*/?\s*br\s*/?\s*>', '\n', texto, flags=re.IGNORECASE)
    texto_limpio = re.sub(r'\{\s*/?\s*br\s*/?\s*\}', '\n', texto_limpio, flags=re.IGNORECASE)
    # Limpia saltos de línea múltiples que hayan quedado
    texto_limpio = re.sub(r'\n{3,}', '\n\n', texto_limpio)
    return texto_limpio.strip()

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
                # APLICACIÓN SOLUCIÓN 1: Limpieza de celdas
                texto_limpio = limpiar_etiquetas_br(texto_limpio)
                
                cell.text = texto_limpio
                
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
        query = urllib.parse.quote(prompt_imagen + ", ultra high quality, clean white background, educational vector flat style")
        url = f"https://image.pollinations.ai/prompt/{query}?width=600&height=400&nologo=true"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            image_stream = io.BytesIO(response.content)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(image_stream, width=Inches(4.5))
            
            p_caption = doc.add_paragraph("Ilustración de la Ficha de Trabajo")
            p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_caption.runs[0].font.size = Pt(8)
            p_caption.runs[0].font.italic = True
    except Exception as e:
        doc.add_paragraph(f"[Espacio para Imagen: {prompt_imagen}]").alignment = WD_ALIGN_PARAGRAPH.CENTER

def generar_word_pro(titulo, contenido, ie, dist, area, grado):
    doc = Document()
    
    # 1. Ajustes Editoriales: Márgenes de hoja
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # 2. Configurar Fuentes Base (Calibri, estilo moderno)
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
    
    # SOLUCIÓN PROBLEMA 3: Campo Docente se envía completamente vacío (string "")
    celdas_info = [
        (0, 0, "ÁREA:", area), (0, 1, "GRADO/EDAD:", grado),
        (1, 0, "DOCENTE:", ""), (1, 1, "AÑO LECTIVO:", str(ANIO_ACTUAL))
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
    
    # Parser de Markdown a Word con Integración de Imágenes y Limpieza
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
            
            # Limpiamos asteriscos sobrantes si no son parte de negrita
            texto_limpio = linea
            
            # Títulos y Subtítulos Estilizados
            if linea.startswith('### '): 
                h = doc.add_heading(level=3)
                r = h.add_run(limpiar_etiquetas_br(texto_limpio[4:]).replace('*',''))
                r.font.name = 'Calibri'
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 51, 102)
            elif linea.startswith('## '):
                h = doc.add_heading(level=2)
                r = h.add_run(limpiar_etiquetas_br(texto_limpio[3:]).replace('*',''))
                r.font.name = 'Calibri'
                r.font.size = Pt(14)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 51, 102)
            elif linea.startswith('# '):
                h = doc.add_heading(level=1)
                r = h.add_run(limpiar_etiquetas_br(texto_limpio[2:]).replace('*',''))
                r.font.name = 'Calibri'
                r.font.size = Pt(16)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 51, 102)
            else:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                # Procesador simple para negritas (**) dentro del párrafo
                partes = re.split(r'(\*\*.*?\*\*)', linea)
                for parte in partes:
                    if parte.startswith('**') and parte.endswith('**'):
                        texto_parte = parte[2:-2]
                        texto_parte = limpiar_etiquetas_br(texto_parte)
                        r = p.add_run(texto_parte)
                        r.bold = True
                        r.font.name = 'Calibri'
                    else:
                        texto_parte = limpiar_etiquetas_br(parte)
                        r = p.add_run(texto_parte)
                        r.font.name = 'Calibri'

    # En caso el documento termine con una tabla
    if tabla_actual:
        construir_tabla_word(doc, tabla_actual)
        
    return doc

# --- INTERFAZ DE USUARIO PRINCIPAL ---
st.markdown(f'<div class="header-box"><h1>{NOMBRE_APP}</h1><p>Planificación Curricular IA basada en el CNEB</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8066/8066104.png", width=100)
    st.markdown("### Datos del Contexto")
    ie_nombre = st.text_input("Institución Educativa", "IE. Ejemplo")
    distrito = st.selectbox("Distrito", DISTRICTS)
    
    st.markdown("### Configuración Pedagógica")
    nivel = st.selectbox("Nivel Educativo", ["Primaria", "Secundaria", "Inicial"])
    
    if nivel == "Primaria":
        grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
        areas = ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Educación Física", "Arte y Cultura", "Educación Religiosa"]
    elif nivel == "Secundaria":
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
        areas = ["Matemática", "Comunicación", "Ciencias Sociales", "DPCC", "Ciencia y Tecnología", "Inglés", "Educación Física", "Arte y Cultura", "EPT", "Educación Religiosa", "Tutoría"]
    else:
        grados = ["3 años", "4 años", "5 años"]
        areas = ["Comunicación", "Matemática", "Personal Social", "Psicomotriz", "Descubrimiento del Mundo"]
        
    grado = st.selectbox("Grado/Edad", grados)
    area = st.selectbox("Área Curricular", areas)
    
    st.markdown("---")
    st.info("📌 Los documentos generados respetan los Enfoques y Procesos Didácticos del MINEDU.")

tabs = st.tabs(["Sesión de Aprendizaje", "Unidad Didáctica", "Programación Anual"])

# Pestaña: Sesión de Aprendizaje
with tabs[0]:
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.subheader("📝 Generador de Sesión de Aprendizaje")
    tema_sesion = st.text_input("Tema de la Sesión:", placeholder="Ej. Resolvemos problemas de adición con materiales concretos")
    
    if st.button("Generar Sesión con IA", key="btn_sesion"):
        if not client:
            st.error("Error: Configura correctamente tu API KEY de ZhipuAI en los secrets.")
        elif not tema_sesion:
            st.warning("Por favor, ingresa el tema de la sesión.")
        else:
            with st.spinner("🧠 EDUPLAN IA está redactando la sesión..."):
                prompt_sys = obtener_prompt_cneb("Sesión de Aprendizaje", area, nivel, grado)
                prompt_user = f"Tema de la sesión: {tema_sesion}."
                try:
                    response = client.chat.completions.create(
                        model="glm-4",
                        messages=[
                            {"role": "system", "content": prompt_sys},
                            {"role": "user", "content": prompt_user}
                        ]
                    )
                    st.session_state.resultados["sesion"] = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Error de conexión con IA: {str(e)}")
                    
    if st.session_state.resultados["sesion"]:
        st.markdown(st.session_state.resultados["sesion"])
        
        # Generación del Word
        doc_word = generar_word_pro("SESIÓN DE APRENDIZAJE", st.session_state.resultados["sesion"], ie_nombre, distrito, area, grado)
        bio = io.BytesIO()
        doc_word.save(bio)
        
        st.download_button(
            label="📥 Exportar Sesión a Word (Limpiada y Formateada)",
            data=bio.getvalue(),
            file_name=f"Sesion_{area}_{grado}_{ie_nombre}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    st.markdown("</div>", unsafe_allow_html=True)

# Pestaña: Unidad Didáctica
with tabs[1]:
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.subheader("📂 Generador de Unidad Didáctica / EdA")
    st.write("Configuración de Unidad en desarrollo...")
    # (Aquí iría la lógica similar a la sesión para Unidad)
    st.markdown("</div>", unsafe_allow_html=True)

# Pestaña: Programación Anual
with tabs[2]:
    st.markdown("<div class='section-container'>", unsafe_allow_html=True)
    st.subheader("📅 Generador de Programación Anual")
    st.write("Configuración Anual en desarrollo...")
    # (Aquí iría la lógica similar a la sesión para Anual)
    st.markdown("</div>", unsafe_allow_html=True)

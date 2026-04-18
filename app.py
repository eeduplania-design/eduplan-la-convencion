import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import re
import datetime

# --- CONFIGURACIÓN DE IDENTIDAD Y DATOS MAESTROS ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
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

# NUEVO: Contextos locales para automatizar la Situación Significativa
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

# --- CONEXIÓN SEGURA CON LA API ---
try:
    api_key = st.secrets.get("ZHIPU_KEY", "TU_API_KEY_AQUI_SI_NO_USAS_SECRETS")
    client = ZhipuAI(api_key=api_key)
except Exception:
    client = None

# --- MOTOR DE PROMPTS CNEB (CEREBRO PEDAGÓGICO) ---
def obtener_prompt_cneb(tipo_doc, area, nivel):
    """Genera instrucciones hiper-específicas basadas en el CNEB."""
    
    base = f"""Eres un especialista top del MINEDU (Perú), experto en el Currículo Nacional de la Educación Básica (CNEB) y evaluación formativa.
Tu objetivo es redactar un/una '{tipo_doc}' para el nivel {nivel} en el área de {area}.

TU MISIÓN: El docente te dará información mínima (un tema y un contexto). TÚ DEBES desarrollar todo el documento, redactar la situación significativa completa, y deducir las Competencias, Capacidades, y Desempeños del CNEB correspondientes para este grado y área.

REGLAS INQUEBRANTABLES DE FORMATO:
1. Usa Markdown estándar (Títulos con ## y ###). No uses HTML.
2. Construye TABLAS LIMPIAS usando solo `|` y `-`. NUNCA unas celdas, usa filas estándar.
3. El lenguaje debe ser técnico-pedagógico peruano.
"""

    if tipo_doc == "Programación Anual":
        base += """
ESTRUCTURA OBLIGATORIA (PROGRAMACIÓN ANUAL):
1. **Datos Informativos.**
2. **Descripción General:** Enfoque del área y caracterización del contexto local proporcionado.
3. **Propósitos de Aprendizaje:** TABLA con Competencias, Capacidades y Estándares de Aprendizaje. (Debes seleccionarlos según el área).
4. **Organización de las Unidades Didácticas:** TABLA detallando Títulos de unidad, Situación Significativa resumida, Duración y Competencias a movilizar por bimestre/trimestre.
5. **Enfoques Transversales:** Priorizados en el año.
6. **Estrategias Metodológicas y Recursos.**
7. **Evaluación.**
"""
    elif tipo_doc == "Unidad Didáctica":
        base += """
ESTRUCTURA OBLIGATORIA (UNIDAD DIDÁCTICA / EXPERIENCIA DE APRENDIZAJE):
1. **Datos Informativos.**
2. **Situación Significativa:** Redacta una situación retadora y problematizadora de al menos 2 párrafos, basada en el contexto y problema local dado. Finaliza con un RETO (pregunta).
3. **Propósitos y Evidencias:** TABLA MAESTRA con: Competencia, Capacidades, Desempeños precisados, Criterios de Evaluación, Evidencia de Aprendizaje, e Instrumento.
4. **Secuencia de Sesiones:** TABLA con el Número de Sesión, Título, y Breve descripción (mínimo 4 sesiones lógicas que resuelvan el reto).
5. **Materiales y Recursos.**
"""
    elif tipo_doc == "Sesión de Aprendizaje":
        base += f"""
ESTRUCTURA OBLIGATORIA (SESIÓN DE APRENDIZAJE CNEB):
1. **Datos Informativos.**
2. **Propósitos de Aprendizaje:** TABLA con Competencia, Capacidades, Desempeño Precisado, Criterio de Evaluación, Evidencia e Instrumento.
3. **Secuencia Didáctica (El núcleo):**
   - **INICIO (20 min):** Motivación, Saberes Previos, Problematización (Conflicto Cognitivo) y Propósito de la sesión.
   - **DESARROLLO (60 min):** APLICA LOS PROCESOS DIDÁCTICOS DEL ÁREA DE {area}. Detalla las actividades del docente y los estudiantes.
   - **CIERRE (10 min):** Evaluación formativa y Metacognición (¿Qué aprendimos?, etc.).
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

st.markdown(f"""
    <div class="header-box">
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
        areas = ["Matemática", "Comunicación", "Inglés", "Arte y Cultura", "Ciencias Sociales", "DPCC", "Educación Física", "Ciencia y Tecnología", "EPT"]
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
    
    area_sel = st.selectbox("Área Curricular", areas)
    grado_sel = st.selectbox("Grado / Edad", grados)
    enfoque_transversal = st.selectbox("🌱 Enfoque Transversal", ENFOQUES_TRANSVERSALES)

tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE APRENDIZAJE"])

# MOTOR DE RENDERIZADO SIMPLIFICADO PARA EL DOCENTE
def render_generador(tipo_doc, tab_key):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader(f"📝 Opciones para: {tipo_doc}")
    st.info("💡 Solo selecciona el problema local y el tema. La IA construirá las competencias, criterios y la situación significativa completa.")
    
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
            placeholder="Ej: Resolvemos problemas con fracciones...", 
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
            with st.status(f"🤖 Estructurando según el CNEB y contexto de La Convención...", expanded=True) as status:
                st.write("📖 Diseñando Situación Significativa...")
                st.write(f"⚙️ Relacionando Competencias de {area_sel}...")
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

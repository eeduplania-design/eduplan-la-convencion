import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import re
import datetime

# --- CONFIGURACIÓN DE IDENTIDAD ---
NOMBRE_APP = "EDUPLAN IA - LA CONVENCIÓN"
LIDER = "Prof. Percy Tapia"
DISTRICTS = ["Santa Ana", "Echarati", "Huayopata", "Maranura", "Santa Teresa", "Vilcabamba", "Quellouno", "Pichari", "Kimbiri", "Inkawasi", "Villa Virgen", "Villa Kintiarina", "Ocobamba"]
ENFOQUES_TRANSVERSALES = ["De derechos", "Inclusivo o de Atención a la diversidad", "Intercultural", "Igualdad de género", "Ambiental", "Orientación al bien común", "Búsqueda de la Excelencia"]
ANIO_ACTUAL = datetime.datetime.now().year

# --- CONEXIÓN SEGURA CON LA API ---
try:
    api_key = st.secrets.get("ZHIPU_KEY", "")
    client = ZhipuAI(api_key=api_key)
except Exception:
    client = None

# --- MOTOR DE PROMPTS CNEB (EL NUEVO "CEREBRO" DE LA IA) ---
def obtener_prompt_cneb(tipo_doc, area, nivel):
    """Genera instrucciones hiper-específicas basadas en el CNEB según el documento solicitado."""
    
    base = f"""Eres un especialista top del MINEDU (Perú), experto en el Currículo Nacional de la Educación Básica (CNEB) y evaluación formativa.
Tu objetivo es redactar un/una '{tipo_doc}' para el nivel {nivel} en el área de {area}.

REGLAS INQUEBRANTABLES DE FORMATO:
1. Usa Markdown estándar (Títulos con ## y ###). No uses HTML.
2. Construye TABLAS LIMPIAS usando solo `|` y `-`. 
3. NUNCA unas celdas en las tablas, la estructura debe ser simétrica para que sea compatible con MS Word.

CONTEXTO OBLIGATORIO: 
Aterriza las situaciones significativas a la realidad de La Convención, Cusco (agricultura local como café/cacao/cítricos, interculturalidad amazónica-andina, recursos hídricos, cultura machiguenga, etc.).
"""

    if tipo_doc == "Programación Anual":
        base += """
ESTRUCTURA OBLIGATORIA (PROGRAMACIÓN ANUAL):
1. **Datos Informativos.**
2. **Descripción General:** Enfoque del área y caracterización del contexto local.
3. **Propósitos de Aprendizaje:** TABLA con Competencias, Capacidades y Estándares de Aprendizaje del ciclo.
4. **Organización de las Unidades Didácticas:** TABLA detallando Títulos de unidad, Situación Significativa resumida, Duración y Competencias a movilizar por trimestre/bimestre.
5. **Enfoques Transversales:** Priorizados en el año.
6. **Estrategias Metodológicas:** Generales del área.
7. **Materiales y Recursos Educativos.**
8. **Evaluación:** Diagnóstica, formativa y sumativa.
"""
    elif tipo_doc == "Unidad Didáctica":
        base += """
ESTRUCTURA OBLIGATORIA (UNIDAD DIDÁCTICA / EXPERIENCIA DE APRENDIZAJE):
1. **Datos Informativos.**
2. **Situación Significativa:** Descripción del problema/reto del contexto de La Convención que genera el aprendizaje.
3. **Propósitos y Evidencias de Aprendizaje:** TABLA MAESTRA con: Competencia, Capacidades, Desempeños precisados, Criterios de Evaluación, Evidencia de Aprendizaje, e Instrumento.
4. **Secuencia de Sesiones:** TABLA con el Número de Sesión, Título, y Breve descripción de la actividad (minimo 4 sesiones).
5. **Enfoques Transversales:** Acciones observables.
6. **Materiales y Recursos.**
"""
    elif tipo_doc == "Sesión de Aprendizaje":
        base += f"""
ESTRUCTURA OBLIGATORIA (SESIÓN DE APRENDIZAJE CNEB):
1. **Datos Informativos.**
2. **Propósitos de Aprendizaje:** TABLA con Competencia, Capacidades, Desempeño Precisado, Criterio de Evaluación, Evidencia e Instrumento.
3. **Enfoques Transversales:** Valores y actitudes observables.
4. **Secuencia Didáctica (El núcleo):**
   - **INICIO (20 min):** Motivación, Saberes Previos, Problematización (Conflicto Cognitivo) y Propósito de la sesión con los Criterios de Evaluación.
   - **DESARROLLO (60 min):** DEBE APLICAR ESTRICTAMENTE LOS *PROCESOS DIDÁCTICOS* DEL ÁREA DE {area} (Ej: Si es matemática: Familiarización con el problema, búsqueda de estrategias, socialización, reflexión; Si es Comunicación: Antes, durante y después del discurso/lectura). Gestión y acompañamiento del docente.
   - **CIERRE (10 min):** Evaluación formativa y Metacognición (¿Qué aprendimos? ¿Cómo lo aprendimos? ¿Para qué sirve?).
5. **Recursos y Materiales.**
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
    .header-box h1 { color: white; font-size: 2.8rem; margin: 0; font-weight: 800; letter-spacing: 1px;}
    .header-box p { color: #e2e8f0; font-size: 1.2rem; margin-top: 10px; font-weight: 300; }
    
    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px 8px 0 0;
        padding: 12px 24px; font-weight: 700; color: var(--minedu-blue); box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] { background-color: var(--minedu-red) !important; color: white !important; border-color: var(--minedu-red) !important; }
    
    /* Cards for forms */
    .section-container {
        background-color: #ffffff; padding: 30px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-left: 6px solid var(--minedu-blue);
    }
    
    /* Buttons */
    .stButton>button {
        background: var(--minedu-blue); color: white; font-weight: bold;
        border-radius: 8px; height: 3.5em; border: none; transition: all 0.3s ease; width: 100%;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .stButton>button:hover { background: var(--minedu-red); transform: translateY(-2px); box-shadow: 0 6px 15px rgba(200, 16, 46, 0.3); }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
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

    # Encabezado MINEDU/Regional
    header = doc.sections[0].header
    p_header = header.paragraphs[0]
    p_header.text = f"SISTEMA EDUPLAN IA - UGEL LA CONVENCIÓN\nI.E. {ie} | Distrito: {dist}"
    p_header.style.font.size = Pt(9)
    p_header.style.font.color.rgb = RGBColor(100, 100, 100)
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    titulo_doc = doc.add_heading(titulo, level=1)
    titulo_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER

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
    
    # Intérprete de Markdown a Word
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

# --- LÓGICA DE IA ---
def procesar_ia(tipo, payload, prompt_sistema):
    if not client:
        return "⚠️ Error: No se ha configurado la clave API (ZHIPU_KEY). Revisa st.secrets."
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Desarrolla el documento con rigor pedagógico. DATOS DEL USUARIO:\n{payload}"}
            ],
            temperature=0.6 # Un poco más bajo para mayor rigor técnico
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico al conectar con la IA: {str(e)}"

# --- INTERFAZ PRINCIPAL ---

# Header Visual de Alta Gama
st.markdown(f"""
    <div class="header-box">
        <img src="https://cdn-icons-png.flaticon.com/512/8066/8066104.png" width="80" style="margin-bottom:10px; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.3));">
        <h1>{NOMBRE_APP}</h1>
        <p>Sistema Inteligente de Planificación Curricular alineado al MINEDU {ANIO_ACTUAL}</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar de Configuración Global
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10433/10433048.png", width=120)
    st.title("⚙️ Contexto Institucional")
    st.markdown("Defina los parámetros base para la Inteligencia Artificial.")
    
    ie_nombre = st.text_input("Institución Educativa", "IE Virgen del Carmen", key="global_ie")
    distrito_sel = st.selectbox("Distrito Local", DISTRICTS, key="global_dist")
    
    st.divider()
    st.subheader("🎒 Nivel y Grado")
    nivel_global = st.radio("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"])
    
    if nivel_global == "Inicial":
        areas = ["Personal Social", "Psicomotriz", "Comunicación", "Castellano como Segunda Lengua", "Descubrimiento del Mundo", "Matemática"]
        grados = ["3 años", "4 años", "5 años"]
    elif nivel_global == "Primaria":
        areas = ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Educación Física", "Arte y Cultura", "Educación Religiosa", "Inglés", "Tutoría"]
        grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
    else: 
        areas = ["Matemática", "Comunicación", "Inglés", "Arte y Cultura", "Ciencias Sociales", "DPCC", "Educación Física", "Educación Religiosa", "Ciencia y Tecnología", "EPT", "Tutoría"]
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
    
    area_sel = st.selectbox("Área Curricular", areas)
    grado_sel = st.selectbox("Grado / Edad", grados)
    
    enfoque_transversal = st.selectbox("🌱 Enfoque Transversal Priorizado", ENFOQUES_TRANSVERSALES)

# Pestañas de Trabajo
tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE APRENDIZAJE"])

# FUNCIÓN RENDERIZADORA
def render_generador(tipo_doc, tab_key):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader(f"📝 Configurar: {tipo_doc}")
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        titulo_doc = st.text_input(f"Título/Tema Central", placeholder="Ej: Fomentamos el cuidado del agua...", key=f"tit_{tab_key}")
    with col2:
        contexto_doc = st.text_input("Situación Significativa (Breve)", placeholder="Problema, potencialidad local o interés del estudiante...", key=f"ctx_{tab_key}")
    
    # Opciones Específicas
    opciones_extra = f", Enfoque Transversal: {enfoque_transversal}"
    if tipo_doc == "Sesión de Aprendizaje":
        with st.expander("🛠️ Ajustes Pedagógicos Avanzados", expanded=False):
            col_s1, col_s2 = st.columns(2)
            nee = col_s1.toggle("🧠 Sugerencias DUA / NEE (Inclusión)", help="Estrategias para atención a la diversidad")
            inst_eval = col_s2.selectbox("📊 Instrumento de Evaluación", ["Rúbrica", "Lista de Cotejo", "Guía de Observación", "Prueba Escrita"])
            opciones_extra += f", Adaptación NEE: {'Sí' if nee else 'No'}, Instrumento sugerido: {inst_eval}"

    payload = f"Título: {titulo_doc}\nContexto Local: {contexto_doc}\nÁrea: {area_sel}\nNivel: {nivel_global}\nGrado: {grado_sel}{opciones_extra}"
    prompt_dinamico = obtener_prompt_cneb(tipo_doc, area_sel, nivel_global)

    if st.button(f"🚀 GENERAR {tipo_doc.upper()} CON IA", key=f"btn_{tab_key}"):
        if not titulo_doc or not contexto_doc:
            st.error("🛑 Falta información: Debes ingresar un 'Título' y una 'Situación Significativa' para que la IA tenga contexto.")
        else:
            with st.status(f"🤖 El Asistente MINEDU está diseñando tu {tipo_doc}...", expanded=True) as status:
                st.write("📖 Analizando Estándares y Desempeños del CNEB...")
                st.write(f"⚙️ Aplicando Procesos Didácticos de {area_sel}...")
                resultado = procesar_ia(tipo_doc, payload, prompt_dinamico)
                st.session_state.resultados[tab_key] = (resultado, titulo_doc)
                status.update(label="¡Diseño Curricular Completado!", state="complete", expanded=False)

    if st.session_state.resultados[tab_key]:
        resultado_actual, titulo_guardado = st.session_state.resultados[tab_key]
        
        st.divider()
        st.markdown(f"### 📋 Vista Previa del Documento")
        with st.container(height=500, border=True):
            st.markdown(resultado_actual) 
        
        st.divider()
        file_word = generar_word_pro(f"{tipo_doc.upper()}: {titulo_guardado}", resultado_actual, ie_nombre, distrito_sel, area_sel, grado_sel)
        
        st.download_button(
            label="📥 EXPORTAR A MICROSOFT WORD (.DOCX)", 
            data=file_word, 
            file_name=f"{tipo_doc.replace(' ', '_')}_{grado_sel}.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"dl_{tab_key}",
            use_container_width=True
        )
            
    st.markdown('</div>', unsafe_allow_html=True)

with tab1: render_generador("Programación Anual", "anual")
with tab2: render_generador("Unidad Didáctica", "unidad")
with tab3: render_generador("Sesión de Aprendizaje", "sesion")

# Footer Profesional
st.markdown(f"""
    <div style="text-align: center; padding: 25px; margin-top: 30px; background-color: var(--minedu-blue); color: white; border-radius: 10px;">
        <h4 style="margin:0; color: white;">{NOMBRE_APP}</h4>
        <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.8;">
        Innovación en Planificación Pedagógica bajo enfoque CNEB.<br>
        Dirigido por <b>{LIDER}</b> | UGEL La Convención © {ANIO_ACTUAL}
        </p>
    </div>
""", unsafe_allow_html=True)

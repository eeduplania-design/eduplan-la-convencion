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
ANIO_ACTUAL = datetime.datetime.now().year

# Conexión Segura con la API
# Se recomienda usar st.secrets["ZHIPU_KEY"] en producción
try:
    api_key = st.secrets.get("ZHIPU_KEY", "")
    client = ZhipuAI(api_key=api_key)
except Exception:
    client = None

# --- PROMPT MAESTRO (PERSONALIDAD PEDAGÓGICA) ---
PROMPT_SISTEMA = """
Eres un asistente pedagógico experto del MINEDU (Perú), especialista en el Currículo Nacional de la Educación Básica (CNEB).
Tu misión es estructurar la planificación docente para Educación Básica Regular (Inicial, Primaria, Secundaria).

REGLAS ESTRICTAS DE FORMATO:
1. Usa Markdown estándar.
2. Usa títulos (##) y subtítulos (###).
3. Para Propósitos de Aprendizaje, Competencias, Capacidades y Secuencias Didácticas, USA SIEMPRE TABLAS MARKDOWN SIMPLES.
4. NUNCA unas celdas (colspan/rowspan) en las tablas, mantén la misma cantidad de columnas en todas las filas.
5. No uses código HTML.

CONTEXTO OBLIGATORIO: 
Adapta los ejemplos, situaciones significativas y recursos a la realidad de La Convención, Cusco (cultivo de café, cacao, cítricos, biodiversidad amazónica/andina, cultura machiguenga, etc.).
"""

# --- ESTILOS UX/UI PROFESIONALES ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🌳")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; margin-bottom: 20px;}
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        color: #475569;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e40af !important;
        color: white !important;
        border-color: #1e40af !important;
    }
    .section-container {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
        border-top: 6px solid #1e40af;
    }
    .stButton>button {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 3em;
        border: none;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4); }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO (SESSION STATE) ---
# Esto evita que el texto generado se borre si el usuario interactúa con otro botón
if 'resultados' not in st.session_state:
    st.session_state.resultados = {
        "anual": None,
        "unidad": None,
        "sesion": None
    }

# --- FUNCIONES DE LÓGICA Y EXPORTACIÓN ---

def construir_tabla_word(doc, matriz_datos):
    """Convierte una matriz 2D (lista de listas) en una tabla de Word formateada."""
    if not matriz_datos: return
    
    num_cols = max(len(fila) for fila in matriz_datos)
    table = doc.add_table(rows=len(matriz_datos), cols=num_cols)
    table.style = 'Table Grid'
    
    for i, fila in enumerate(matriz_datos):
        for j, celda in enumerate(fila):
            if j < num_cols:
                cell = table.cell(i, j)
                # Limpiar asteriscos de negritas de Markdown
                texto_limpio = celda.replace('**', '').replace('*', '')
                cell.text = texto_limpio
                
                # Formato para la fila de encabezado (primera fila)
                if i == 0:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.bold = True
                            
    doc.add_paragraph() # Espacio después de la tabla

def generar_word_pro(titulo, contenido, ie, dist, area, grado):
    doc = Document()
    
    # 1. Configurar Estilos Globales
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # 2. Encabezado Institucional
    header = doc.sections[0].header
    p_header = header.paragraphs[0]
    p_header.text = f"{NOMBRE_APP} - Innovación Pedagógica\nI.E. {ie} | Distrito: {dist}"
    p_header.style.font.size = Pt(9)
    p_header.style.font.color.rgb = RGBColor(100, 100, 100)
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # 3. Título Principal
    titulo_doc = doc.add_heading(titulo, level=1)
    titulo_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 4. Tabla de Datos Informativos
    table_info = doc.add_table(rows=2, cols=2)
    table_info.style = 'Table Grid'
    
    # Rellenar y poner negrita a las etiquetas
    celdas_info = [
        (0, 0, "ÁREA:", area), (0, 1, "GRADO/EDAD:", grado),
        (1, 0, "DOCENTE:", LIDER), (1, 1, "AÑO LECTIVO:", str(ANIO_ACTUAL))
    ]
    for row, col, etiqueta, valor in celdas_info:
        p = table_info.cell(row, col).paragraphs[0]
        p.add_run(f"{etiqueta} ").bold = True
        p.add_run(valor)

    doc.add_paragraph("\n")
    
    # 5. Procesamiento Inteligente de Markdown a Word
    lineas = contenido.split('\n')
    tabla_actual = []
    
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
            
        # Detección de filas de Tabla Markdown
        if linea.startswith('|') and linea.endswith('|'):
            filas = [celda.strip() for celda in linea.strip('|').split('|')]
            # Ignorar la línea divisoria de markdown (|---|---|)
            if all(all(c in '-: ' for c in celda) for celda in filas):
                continue
            tabla_actual.append(filas)
        else:
            # Renderizar tabla acumulada si la hay
            if tabla_actual:
                construir_tabla_word(doc, tabla_actual)
                tabla_actual = []
            
            # Procesar Textos y Títulos
            texto_limpio = linea.replace('**', '').replace('*', '') # Limpiar negritas
            
            if linea.startswith('### '):
                doc.add_heading(texto_limpio[4:], level=3)
            elif linea.startswith('## '):
                doc.add_heading(texto_limpio[3:], level=2)
            elif linea.startswith('# '):
                doc.add_heading(texto_limpio[2:], level=1)
            elif linea.startswith('- '):
                doc.add_paragraph(texto_limpio[2:], style='List Bullet')
            elif re.match(r'^\d+\.\s', linea): # Listas numeradas (ej. "1. Texto")
                doc.add_paragraph(texto_limpio, style='List Number')
            else:
                doc.add_paragraph(texto_limpio)
                
    # Renderizar la última tabla si el texto terminó en una
    if tabla_actual:
        construir_tabla_word(doc, tabla_actual)

    # 6. Guardar en Memoria
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def procesar_ia(tipo, payload):
    if not client:
        return "⚠️ Error: No se ha configurado la clave API (ZHIPU_KEY). Revisa st.secrets."
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Redacta un(a) {tipo} educativo completo. DATOS DE CONTEXTO: {payload}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error técnico al conectar con la IA: {str(e)}"

# --- INTERFAZ PRINCIPAL ---
st.markdown(f"""
    <div style="text-align: center; padding: 10px 20px 30px 20px;">
        <h1 style="color: #1e3a8a; margin: 0; font-size: 2.8rem;">🏛️ {NOMBRE_APP}</h1>
        <p style="color: #64748b; font-size: 1.2em; font-weight: 500;">Sistema Profesional de Planificación CNEB {ANIO_ACTUAL}</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar de Configuración Global
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=80)
    st.title("⚙️ Datos Institucionales")
    
    ie_nombre = st.text_input("Institución Educativa", "IE Virgen del Carmen", key="global_ie")
    distrito_sel = st.selectbox("Distrito Local", DISTRICTS, key="global_dist")
    
    st.divider()
    st.subheader("Nivel y Grado")
    nivel_global = st.radio("Nivel Educativo", ["Inicial", "Primaria", "Secundaria"], horizontal=True)
    
    # Lógica de Áreas y Grados según Nivel
    if nivel_global == "Inicial":
        areas = ["Personal Social", "Psicomotriz", "Comunicación", "Castellano como Segunda Lengua", "Descubrimiento del Mundo", "Matemática"]
        grados = ["3 años", "4 años", "5 años"]
    elif nivel_global == "Primaria":
        areas = ["Matemática", "Comunicación", "Personal Social", "Ciencia y Tecnología", "Educación Física", "Arte y Cultura", "Educación Religiosa", "Inglés", "Tutoría"]
        grados = ["1ro", "2do", "3ro", "4to", "5to", "6to"]
    else: # Secundaria
        areas = ["Matemática", "Comunicación", "Inglés", "Arte y Cultura", "Ciencias Sociales", "DPCC", "Educación Física", "Educación Religiosa", "Ciencia y Tecnología", "EPT", "Tutoría"]
        grados = ["1ro", "2do", "3ro", "4to", "5to"]
    
    area_sel = st.selectbox("Área Curricular", areas)
    grado_sel = st.selectbox("Grado / Edad", grados)
    
    st.info("💡 **Tip:** Modificar estos datos aplicará el contexto a todas las herramientas.")

# Pestañas de Trabajo
tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE APRENDIZAJE"])

# FUNCIÓN RENDERIZADORA DE SECCIONES
def render_generador(tipo, tab_key):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader(f"⚙️ Configurar {tipo}")
    
    # Entradas de Usuario
    col1, col2 = st.columns([1, 1.5])
    with col1:
        titulo_doc = st.text_input(f"Título del/de la {tipo}", placeholder="Ej: Fomentamos el cuidado del agua...", key=f"tit_{tab_key}")
    with col2:
        contexto_doc = st.text_input("Contexto / Situación (Breve)", placeholder="Problema o potencialidad local a abordar...", key=f"ctx_{tab_key}")
    
    # Opciones Específicas
    opciones_extra = ""
    if tipo == "Sesión de Aprendizaje":
        with st.expander("Opciones Avanzadas de Sesión", expanded=False):
            col_s1, col_s2 = st.columns(2)
            nee = col_s1.toggle("🧠 Incluir Adaptación NEE", help="Sugerencias para estudiantes con Necesidades Educativas Especiales")
            guia = col_s2.toggle("💡 Guía de Rubrica", help="Incluir propuesta de rúbrica de evaluación")
            opciones_extra = f", Adaptación NEE: {'Sí' if nee else 'No'}, Incluir Rúbrica: {'Sí' if guia else 'No'}"

    # Construir Payload
    payload = f"Título: {titulo_doc}, Contexto: {contexto_doc}, Área: {area_sel}, Nivel: {nivel_global}, Grado: {grado_sel}{opciones_extra}"

    # Botón Generar
    if st.button(f"🚀 Generar {tipo}", key=f"btn_{tab_key}"):
        if not titulo_doc or not contexto_doc:
            st.warning("⚠️ Por favor ingresa el **Título** y el **Contexto** para obtener un mejor resultado.")
        else:
            with st.status(f"🤖 Procesando {tipo} con IA...", expanded=True) as status:
                st.write("Analizando competencias del CNEB...")
                st.write("Adaptando al contexto de La Convención...")
                resultado = procesar_ia(tipo, payload)
                st.session_state.resultados[tab_key] = (resultado, titulo_doc) # Guardar en memoria
                status.update(label="¡Generación completada!", state="complete", expanded=False)

    # Mostrar Resultados si existen en memoria
    if st.session_state.resultados[tab_key]:
        resultado_actual, titulo_guardado = st.session_state.resultados[tab_key]
        
        st.divider()
        st.markdown(f"### Vista Previa: {titulo_guardado}")
        st.markdown(resultado_actual) # Mostrar Markdown en la interfaz
        
        # Botón de Descarga
        file_word = generar_word_pro(f"{tipo.upper()}: {titulo_guardado}", resultado_actual, ie_nombre, distrito_sel, area_sel, grado_sel)
        
        col_dl1, col_dl2, col_dl3 = st.columns([1,2,1])
        with col_dl2:
            st.download_button(
                label="📥 DESCARGAR DOCUMENTO WORD", 
                data=file_word, 
                file_name=f"{tipo.replace(' ', '_')}_{grado_sel}.docx", 
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"dl_{tab_key}",
                use_container_width=True
            )
            
    st.markdown('</div>', unsafe_allow_html=True)

# Renderizar cada pestaña
with tab1: render_generador("Programación Anual", "anual")
with tab2: render_generador("Unidad Didáctica", "unidad")
with tab3: render_generador("Sesión de Aprendizaje", "sesion")

# Footer
st.markdown(f"""
    <div style="text-align: center; padding: 30px; margin-top: 20px; color: #64748b; font-size: 0.9em; border-top: 1px solid #e2e8f0;">
        <b>{NOMBRE_APP}</b> <br>
        Desarrollado para la innovación docente. Liderado por <b>{LIDER}</b><br>
        © {ANIO_ACTUAL} La Convención - Cusco - Perú
    </div>
""", unsafe_allow_html=True)

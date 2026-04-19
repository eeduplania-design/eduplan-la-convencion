import streamlit as st
from zhipuai import ZhipuAI
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ROW_HEIGHT_RULE
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
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

# --- DICCIONARIOS MINEDU ---
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
    "Matemática": "1. Comprensión del problema. 2. Estrategias. 3. Representación (concreto → simbólico). 4. Formalización. 5. Reflexión y transferencia.",
    "Comunicación": "1. Aproximación al texto / Contextualización. 2. Comprensión y producción (antes, durante, después). 3. Reflexión y revisión.",
    "Personal Social": "1. Problematización. 2. Análisis de información. 3. Acuerdos / toma de decisiones.",
    "Ciencias Sociales": "1. Problematización. 2. Análisis de información. 3. Acuerdos / toma de decisiones.",
    "DPCC": "1. Problematización. 2. Análisis de información. 3. Acuerdos / toma de decisiones.",
    "Ciencia y Tecnología": "1. Problematización. 2. Diseño de estrategias. 3. Registro de datos. 4. Análisis. 5. Evaluación y comunicación.",
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

# --- CONEXIÓN SEGURA CON LA API ---
try:
    api_key = st.secrets.get("ZHIPU_KEY", "")
    client = ZhipuAI(api_key=api_key) if api_key else None
except Exception:
    client = None

# --- MOTOR DE PROMPTS CNEB ---
def obtener_prompt_cneb(tipo_doc, area, nivel):
    enfoque_area = ENFOQUES_AREAS.get(area, "Enfoque por competencias")
    procesos_area = PROCESOS_DIDACTICOS.get(area, "1. Inicio, 2. Desarrollo, 3. Cierre")
    procesos_pedagogicos_str = ", ".join(PROCESOS_PEDAGOGICOS)

    base = f"""Eres un mentor pedagógico de élite en Perú. Redactarás un(a) '{tipo_doc}' de calidad de publicación/imprenta para {nivel} en {area}.

DATOS CLAVE DEL CNEB:
- Enfoque: {enfoque_area}
- Procesos Didácticos: {procesos_area}
- Procesos Pedagógicos: {procesos_pedagogicos_str}

REGLAS INQUEBRANTABLES:
1. Usa Markdown estricto. NUNCA HTML.
2. Construye TABLAS impecables usando `|` y `-`.
3. El lenguaje debe ser técnico, pulcro y sumamente detallado.
"""
    if tipo_doc == "Programación Anual":
        base += """
ESTRUCTURA (PROGRAMACIÓN ANUAL):
1. **Datos Informativos.**
2. **Descripción General:** Vincula el enfoque con el contexto.
3. **Propósitos de Aprendizaje:** TABLA (Competencias, Capacidades, Estándares).
4. **Organización de Unidades:** TABLA detallada.
5. **Enfoques Transversales.**
6. **Estrategias y Evaluación.**
"""
    elif tipo_doc == "Unidad Didáctica":
        base += """
ESTRUCTURA (UNIDAD DIDÁCTICA):
1. **Datos Informativos.**
2. **Situación Significativa:** Narrativa inmersiva del contexto con un Reto final.
3. **Propósitos y Evidencias:** TABLA MAESTRA completa.
4. **Secuencia de Sesiones:** TABLA secuenciada lógica.
5. **Materiales.**
"""
    elif tipo_doc == "Sesión de Aprendizaje":
        base += f"""
ESTRUCTURA (SESIÓN DE APRENDIZAJE):
**I. Datos Informativos:** Completa con precisión.
**II. Propósitos:** TABLA.
**III. Enfoques Transversales:** TABLA.
**IV. Preparación:** TABLA.
**V. Secuencia Didáctica:** TABLA (Momentos | Estrategias | Tiempo). Detalla explícitamente los procesos: {procesos_area}.
**VI. Anexos:**
- **Anexo 1: Instrumento de Evaluación:** TABLA de lista de cotejo/rúbrica.
- **Anexo 2: Ficha de Trabajo (FORMATO EDITORIAL):** Créala para ser impresa. Usa un encabezado estructurado (Nombre: ______ Fecha: _____), preguntas retadoras, y simulador de renglones como:
____________________________________________________
____________________________________________________
"""
    return base

# --- ESTILOS UX/UI ---
st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🇵🇪")

st.markdown("""
    <style>
    :root { --minedu-red: #C8102E; --minedu-blue: #003366; --light-bg: #F4F6F9; }
    .main { background-color: var(--light-bg); }
    .header-box {
        background: linear-gradient(135deg, var(--minedu-blue) 0%, #1e40af 100%);
        padding: 30px; border-radius: 12px; color: white; text-align: center;
        margin-bottom: 25px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-bottom: 4px solid var(--minedu-red);
    }
    .header-box h1 { font-weight: 800; font-size: 2.2rem; }
    .section-container { background-color: #fff; padding: 25px; border-radius: 10px; border-left: 5px solid var(--minedu-blue); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

if 'resultados' not in st.session_state:
    st.session_state.resultados = {"anual": None, "unidad": None, "sesion": None}

# --- FUNCIONES AVANZADAS DE EXPORTACIÓN A WORD ---
def set_cell_bg_color(cell, color_hex):
    """Agrega color de fondo a una celda de tabla en Word."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcShd = OxmlElement('w:shd')
    tcShd.set(qn('w:fill'), color_hex)
    tcPr.append(tcShd)

def parse_markdown_text(paragraph, text):
    """Procesa el texto para detectar negritas (**texto**) e itálicas (*texto*) y lo añade al párrafo."""
    # Buscar patrones de negrita e itálica
    partes = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
    for parte in partes:
        if parte.startswith('**') and parte.endswith('**'):
            run = paragraph.add_run(parte[2:-2])
            run.bold = True
        elif parte.startswith('*') and parte.endswith('*'):
            run = paragraph.add_run(parte[1:-1])
            run.italic = True
        else:
            if parte:
                paragraph.add_run(parte)

def construir_tabla_word(doc, matriz_datos):
    """Construye una tabla Word con formato profesional (Editorial/Minedu)."""
    if not matriz_datos: return
    num_cols = max(len(fila) for fila in matriz_datos)
    
    # Crear la tabla
    table = doc.add_table(rows=len(matriz_datos), cols=num_cols)
    table.style = 'Table Grid'
    table.autofit = True
    
    for i, fila in enumerate(matriz_datos):
        for j, celda in enumerate(fila):
            if j < num_cols:
                cell = table.cell(i, j)
                # Formato de Encabezado (Primera fila)
                if i == 0:
                    set_cell_bg_color(cell, "003366") # Azul Minedu
                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    # Extraer texto limpio y poner blanco/negrita
                    texto_limpio = celda.replace('**', '').replace('*', '').strip()
                    run = p.add_run(texto_limpio)
                    run.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)
                else:
                    # Celdas normales
                    p = cell.paragraphs[0]
                    parse_markdown_text(p, celda.strip())
                    
                    # Sombreado sutil para filas pares (Efecto cebra)
                    if i % 2 == 0:
                        set_cell_bg_color(cell, "F2F6FA") # Gris/Azul muy claro
                        
    doc.add_paragraph() # Espacio después de la tabla

def generar_word_pro(titulo, contenido, ie, dist, area, grado):
    doc = Document()
    
    # CONFIGURACIÓN DE PÁGINA (Márgenes Estrechos para máximo aprovechamiento)
    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)

    # ESTILOS GLOBALES
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    # ENCABEZADO INSTITUCIONAL
    header = doc.sections[0].header
    p_header = header.paragraphs[0]
    p_header.text = f"SISTEMA EDUPLAN IA - UGEL LA CONVENCIÓN\nI.E. {ie} | Distrito: {dist}"
    p_header.style.font.size = Pt(8)
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_header.runs[0].font.color.rgb = RGBColor(100, 100, 100)

    # TÍTULO PRINCIPAL DEL DOCUMENTO
    doc.add_paragraph("\n")
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_titulo = p_titulo.add_run(titulo.upper())
    run_titulo.bold = True
    run_titulo.font.size = Pt(14)
    run_titulo.font.color.rgb = RGBColor(0, 51, 102) # Azul MINEDU
    doc.add_paragraph()

    # CUADRO DE DATOS INFORMATIVOS PRINCIPAL
    table_info = doc.add_table(rows=2, cols=2)
    table_info.style = 'Table Grid'
    celdas_info = [
        (0, 0, "ÁREA CÚRRICULAR:", area.upper()), (0, 1, "GRADO/EDAD:", grado.upper()),
        (1, 0, "DOCENTE:", LIDER.upper()), (1, 1, "AÑO LECTIVO:", str(ANIO_ACTUAL))
    ]
    for row, col, etiqueta, valor in celdas_info:
        cell = table_info.cell(row, col)
        set_cell_bg_color(cell, "F4F4F4") # Fondo gris claro
        p = cell.paragraphs[0]
        run_etiqueta = p.add_run(f"{etiqueta} ")
        run_etiqueta.bold = True
        run_etiqueta.font.color.rgb = RGBColor(0, 51, 102)
        p.add_run(valor)
    doc.add_paragraph()
    
    # PARSER DE MARKDOWN A WORD ESTRUCTURADO
    lineas = contenido.split('\n')
    tabla_actual = []
    
    for linea in lineas:
        linea_str = linea.strip()
        if not linea_str: 
            continue
            
        # Detectar Tablas Markdown
        if linea_str.startswith('|') and linea_str.endswith('|'):
            filas = [celda.strip() for celda in linea_str.strip('|').split('|')]
            # Ignorar la fila de separador de markdown (---|---)
            if all(all(c in '-: ' for c in celda) for celda in filas): 
                continue
            tabla_actual.append(filas)
        else:
            # Si veníamos construyendo una tabla y se interrumpe, la dibujamos
            if tabla_actual:
                construir_tabla_word(doc, tabla_actual)
                tabla_actual = []
            
            # Detectar y renderizar Encabezados (Headings)
            if linea_str.startswith('### '): 
                h = doc.add_heading(level=3)
                run = h.add_run(linea_str[4:].replace('**', ''))
                run.font.color.rgb = RGBColor(0, 51, 102)
                run.bold = True
            elif linea_str.startswith('## '): 
                h = doc.add_heading(level=2)
                run = h.add_run(linea_str[3:].replace('**', ''))
                run.font.color.rgb = RGBColor(200, 16, 46) # Rojo MINEDU
                run.bold = True
                h.paragraph_format.space_before = Pt(12)
            elif linea_str.startswith('# '): 
                h = doc.add_heading(level=1)
                run = h.add_run(linea_str[2:].replace('**', ''))
                run.font.color.rgb = RGBColor(0, 51, 102)
                run.bold = True
            # Detectar Listas
            elif linea_str.startswith('- ') or linea_str.startswith('* '): 
                p = doc.add_paragraph(style='List Bullet')
                parse_markdown_text(p, linea_str[2:])
            elif re.match(r'^\d+\.\s', linea_str): 
                # Extraer el número y procesar texto
                match = re.match(r'^(\d+\.\s)(.*)', linea_str)
                p = doc.add_paragraph(style='List Number')
                parse_markdown_text(p, match.group(2))
            # Párrafos normales
            else: 
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                parse_markdown_text(p, linea_str)
                
    # Dibujar la última tabla si quedó en memoria
    if tabla_actual: 
        construir_tabla_word(doc, tabla_actual)

    # FINALIZACIÓN: Guardar buffer
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- INTERFAZ PRINCIPAL ---
st.markdown(f"""
    <div class="header-box">
        <h1>{NOMBRE_APP}</h1>
        <p>Documentos CNEB de Alta Calidad Editorial {ANIO_ACTUAL} con IA</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Datos Fijos")
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

tab1, tab2, tab3 = st.tabs(["📅 PROGRAMACIÓN ANUAL", "📂 UNIDAD DIDÁCTICA", "📄 SESIÓN DE APRENDIZAJE"])

def render_generador(tipo_doc, tab_key):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader(f"📝 Opciones para: {tipo_doc}")
    
    col1, col2 = st.columns(2)
    with col1:
        contexto_doc = st.selectbox("Problemática o Contexto Local:", CONTEXTOS_LOCALES, key=f"ctx_{tab_key}")
        if contexto_doc == "Otro contexto (Especificar brevemente)":
            contexto_doc = st.text_input("Escribe el contexto brevemente:", key=f"ctx_custom_{tab_key}")
    with col2:
        titulo_doc = st.text_input("Tema o Título sugerido:", placeholder="Ej: Resolvemos problemas de cosecha...", key=f"tit_{tab_key}")

    opciones_extra = ""
    if tipo_doc == "Sesión de Aprendizaje":
        with st.expander("Ajustes Extra (Opcional)", expanded=False):
            nee = st.toggle("Sugerencias para Inclusión (NEE)", key=f"nee_{tab_key}")
            inst_eval = st.selectbox("Instrumento", ["Lista de Cotejo", "Rúbrica", "Ficha de Observación"], key=f"inst_{tab_key}")
            opciones_extra = f"\n- Adaptación NEE: {'Sí' if nee else 'No'}\n- Instrumento: {inst_eval}"

    payload = f"""
    - I.E.: {ie_nombre}
    - Docente: {LIDER}
    - Grado y Área: {nivel_global} - {grado_sel} - {area_sel}
    - Contexto Local: {contexto_doc}
    - Tema: {titulo_doc}
    - Enfoque: {enfoque_transversal}
    {opciones_extra}
    """
    prompt_dinamico = obtener_prompt_cneb(tipo_doc, area_sel, nivel_global)

    if st.button(f"🚀 GENERAR {tipo_doc.upper()}", key=f"btn_{tab_key}", use_container_width=True):
        if not titulo_doc:
            st.error("🛑 Ingresa un Tema o Título.")
        elif not client:
            st.error("🛑 Falta la API Key en st.secrets (ZHIPU_KEY).")
        else:
            with st.spinner(f"🤖 Redactando documento profesional para {area_sel}..."):
                try:
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[
                            {"role": "system", "content": prompt_dinamico},
                            {"role": "user", "content": payload}
                        ],
                        temperature=0.4
                    )
                    st.session_state.resultados[tab_key] = (response.choices[0].message.content, titulo_doc)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if st.session_state.resultados[tab_key]:
        resultado_actual, titulo_guardado = st.session_state.resultados[tab_key]
        st.divider()
        with st.expander("👀 Vista Previa del Documento", expanded=True):
            st.markdown(resultado_actual) 
        
        file_word = generar_word_pro(f"{tipo_doc.upper()}", resultado_actual, ie_nombre, distrito_sel, area_sel, grado_sel)
        
        st.download_button(
            label="🖨️ DESCARGAR DOCUMENTO EDITORIAL (.DOCX)", 
            data=file_word, 
            file_name=f"{tipo_doc.replace(' ', '_')}_{grado_sel}_{area_sel}.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"dl_{tab_key}",
            use_container_width=True,
            type="primary"
        )
    st.markdown('</div>', unsafe_allow_html=True)

with tab1: render_generador("Programación Anual", "anual")
with tab2: render_generador("Unidad Didáctica", "unidad")
with tab3: render_generador("Sesión de Aprendizaje", "sesion")

# ... (Mantén toda la parte superior: imports, config, estilos y funciones generar_word/llamar_ia)

# ── 9. DEFINICIÓN DE CONTENIDO PRINCIPAL ──

# PRIMERO: Definimos la lista de nombres
tab_names = ["📅 Plan Anual", "📦 Unidad", "🚀 Sesión de Aprendizaje"]

# SEGUNDO: Definimos la función generadora (con el arreglo de keys para evitar el error anterior)
def render_generador(tipo, key_prefix):
    st.subheader(f"Generador de {tipo}")
    
    if tipo == "Sesión de Aprendizaje":
        col_t, col_d = st.columns([3,1])
        tema = col_t.text_input("Tema de la sesión", placeholder="Ej: Las maravillas del Pongo de Mainique", key=f"tema_{key_prefix}")
        tiempo = col_d.text_input("Minutos", "90", key=f"tiempo_{key_prefix}")
    else:
        tema = st.text_area("Descripción / Situación Significativa", placeholder="Describe brevemente lo que deseas planificar...", key=f"area_{key_prefix}")
        tiempo = None

    if st.button(f"✨ GENERAR VISTA PREVIA", key=f"btn_{key_prefix}"):
        if not client:
            st.error("❌ API Key no encontrada en secrets.")
            return

        if tema:
            with st.spinner("🧠 Generando planificación..."):
                detalles = f"Tipo: {tipo}, Tema: {tema}, Área: {area_sel}, Nivel: {nivel}, Grado: {grado_sel}, IE: {ie_nombre}"
                if tiempo: detalles += f", Duración: {tiempo} min"
                
                try:
                    # Usamos la lógica de la IA
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[
                            {"role": "system", "content": PROMPT_SISTEMA},
                            {"role": "user", "content": f"Genera: {detalles}"}
                        ]
                    )
                    contenido_ia = response.choices[0].message.content
                    
                    # Vista Previa
                    st.markdown("### 👁️ Vista Previa")
                    st.markdown(f'<div class="preview-box">{contenido_ia}</div>', unsafe_allow_html=True)
                    
                    # Descarga
                    word_file = generar_word(tema, contenido_ia, {"ie": ie_nombre, "area": area_sel, "grado": grado_sel})
                    st.download_button(
                        label="📄 Descargar en WORD",
                        data=word_file,
                        file_name=f"{tipo}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_{key_prefix}"
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("⚠️ Ingresa un tema.")

# TERCERO: Creamos los tabs usando la variable ya definida
tabs = st.tabs(tab_names)

# CUARTO: Asignamos la función a cada tab
with tabs[0]: 
    render_generador("Programación Anual", "anual")
with tabs[1]: 
    render_generador("Unidad Didáctica", "unidad")
with tabs[2]: 
    render_generador("Sesión de Aprendizaje", "sesion")

# ... (Mantén tu footer al final)

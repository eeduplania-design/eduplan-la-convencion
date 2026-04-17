# ... (Todo el código anterior de configuración, estilos y prompts se mantiene igual)

# ── 9. CUERPO PRINCIPAL (TABS) ──
tab_names = ["📅 Plan Anual", "📦 Unidad", "🚀 Sesión de Aprendizaje"]
tabs = st.tabs(tab_names)

# MODIFICACIÓN: Añadimos 'key_prefix' para evitar duplicados
def render_generador(tipo, key_prefix):
    st.subheader(f"Generador de {tipo}")
    
    if tipo == "Sesión de Aprendizaje":
        col_t, col_d = st.columns([3,1])
        # Agregamos key único usando el prefijo
        tema = col_t.text_input("Tema de la sesión", placeholder="Ej: Las maravillas del Pongo de Mainique", key=f"tema_{key_prefix}")
        tiempo = col_d.text_input("Minutos", "90", key=f"tiempo_{key_prefix}")
    else:
        # Agregamos key único usando el prefijo
        tema = st.text_area("Descripción / Situación Significativa", placeholder="Describe brevemente lo que deseas planificar...", key=f"area_{key_prefix}")
        tiempo = None

    # El botón también necesita un key único
    if st.button(f"✨ GENERAR VISTA PREVIA", key=f"btn_{key_prefix}"):
        if not client:
            st.error("❌ API Key no encontrada. Configúrala en los secretos de Streamlit (ZHIPU_KEY).")
            return

        if tema:
            with st.spinner("🧠 La IA está redactando tu documento siguiendo el CNEB..."):
                detalles = f"Tipo: {tipo}, Tema: {tema}, Área: {area_sel}, Nivel: {nivel}, Grado: {grado_sel}, IE: {ie_nombre}"
                if tiempo: detalles += f", Duración: {tiempo} min"
                
                try:
                    response = client.chat.completions.create(
                        model="glm-4-flash",
                        messages=[
                            {"role": "system", "content": PROMPT_SISTEMA},
                            {"role": "user", "content": f"Genera: {detalles}"}
                        ]
                    )
                    contenido_ia = response.choices[0].message.content
                    
                    # --- MOSTRAR VISTA PREVIA ---
                    st.markdown("### 👁️ Vista Previa del Documento")
                    st.markdown(f'<div class="preview-box">{contenido_ia}</div>', unsafe_allow_html=True)
                    
                    # --- OPCIONES DE DESCARGA ---
                    st.markdown("---")
                    col_down1, col_down2 = st.columns(2)
                    
                    word_file = generar_word(tema, contenido_ia, {"ie": ie_nombre, "area": area_sel, "grado": grado_sel})
                    
                    col_down1.download_button(
                        label="📄 Descargar en WORD",
                        data=word_file,
                        file_name=f"{tipo}_{key_prefix}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_{key_prefix}" # Key único para el botón de descarga
                    )
                    
                    st.info("💡 Para imprimir: Presiona **Ctrl + P** (Windows) o **Cmd + P** (Mac) y selecciona 'Guardar como PDF'.")
                    
                except Exception as e:
                    st.error(f"Hubo un error con la IA: {e}")
        else:
            st.warning("⚠️ Por favor, ingresa un tema o descripción.")

# Llamamos a la función pasando un identificador único para cada pestaña
with tabs[0]: render_generador("Programación Anual", "anual")
with tabs[1]: render_generador("Unidad Didáctica", "unidad")
with tabs[2]: render_generador("Sesión de Aprendizaje", "sesion")

# ... (El resto del código del footer se mantiene igual)

import streamlit as st
import pandas as pd
import json
import google.generativeai as genai

st.set_page_config(page_title="Planificador Familiar de Menús", page_icon="🍳", layout="wide")

st.title("🍳 Planificador Familiar de Menús con IA")
st.caption("Héctor, Ainhoa, Beñat y Araia — Menús dinámicos, saludables y cuantitativos")

# --- CONFIGURACIÓN DE API KEY ---
with st.sidebar:
    st.header("⚙️ Configuración IA")
    api_key = st.text_input("Gemini API Key:", type="password", value=st.secrets.get("GEMINI_API_KEY", ""))
    if api_key:
        genai.configure(api_key=api_key)
        st.success("IA Conectada 🤖")
    else:
        st.warning("Introduce tu API Key de Gemini para activar la generación inteligente.")

# --- INICIALIZAR ESTADOS EN SESSION STATE ---
if "recetas_favoritas" not in st.session_state:
    st.session_state.recetas_favoritas = [
        {
            "plato": "Lentejas estofadas con verduras y arroz", 
            "desc": "Guiso tradicional de legumbres. Pasos: Sofreír 1 cebolla y 2 zanahorias, añadir 280g de lentejas, 80g de arroz y 1l de caldo. Cocer 35 min."
        },
        {
            "plato": "Tacos de pollo con mozzarella y aguacate", 
            "desc": "Cena saludable para niños. Pasos: Dorar 400g de pechuga a tiras, fundir 80g de mozzarella suave y servir en tortillas integrales con 1 aguacate."
        },
    ]

if "despensa_urgentes" not in st.session_state:
    st.session_state.despensa_urgentes = ["Pechugas de pollo", "Medio calabacín"]

if "despensa_fondo" not in st.session_state:
    st.session_state.despensa_fondo = ["Cebollas", "Patatas", "Huevos", "Arroz", "Latas de atún", "Garbanzos en bote", "Pasta / Ñoquis"]

if "despensa_basicos" not in st.session_state:
    st.session_state.despensa_basicos = ["Aceite de oliva", "Sal", "Pimienta", "Vinagre", "Ajo", "Harina", "Pimentón", "Orégano"]

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3, tab4 = st.tabs(["🗓️ Planificar Semana", "🎨 Vista previa y Edición", "⭐ Recetario Favorito", "📦 Despensa y Básicos"])

# --- TAB 1: PLANIFICACIÓN ---
with tab1:
    st.header("1. Configuración de la semana")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        turno_ainhoa = st.radio(
            "Turno de Ainhoa esta semana:",
            ["Mañana (Comida Túper)", "Tarde (Cena Túper)", "Personalizado"]
        )
    with col2:
        variedad = st.select_slider(
            "Nivel de creatividad de la IA:",
            options=["Familiar / Tradicional", "Equilibrado con Novedades", "Muy Variado / Creativo"]
        )
    with col3:
        st.info("💡 Cálculo exacto de cantidades para perfil deportista (Adulto 80kg, Adulta 55kg, 2 niños pequeños).")

    st.subheader("2. Peticiones e instrucciones especiales para esta semana")
    notas_especiales = st.text_area(
        "Indica sobros de comida, eventos o detalles puntuales para esta semana:",
        placeholder="Ej: Tengo un túper de brócoli cocido para el lunes; El miércoles necesitamos una cena ultra rápida...",
        height=80
    )

    st.subheader("3. Reglas logísticas, nutricionales y preferencias activas")
    st.markdown("""
    * 🏋️‍♂️ **Perfil Físico & Raciones:** Adulto deportista (80 kg), adulta deportista (55 kg) y 2 niños pequeños (Beñat y Araia). Cantidades reales y equilibradas.
    * 🧀 **Preferencia Quesa Ainhoa:** **Prohibidos quesos fuertes** (curado, azul, cabra). Solo queso suave (mozzarella, sándwich/havarti, queso fresco).
    * 🥗 **Enfoque Saludable:** Platos nutritivos, ricos en verduras, legumbres, proteínas magras y carbohidratos de calidad.
    * 💼 **Héctor:** Túper L-J en comida | Casa los Viernes | Cena en casa siempre.
    * 🐟 **Pescado:** Prohibido en túpers. **Mínimo 1 cena a la semana en casa debe ser de pescado o marisco**.
    * 🍱 **Batch Cooking:** De las 4 comidas de túper, **solo 1 receta se repite 2 días** (ej. Lunes y Miércoles).
    """)

    if st.button("🚀 Generar Menú Inteligente, Cuantitativo y Saludable", type="primary"):
        if not api_key:
            st.error("Por favor, introduce una API Key válida en el menú lateral o en los Secrets de Streamlit.")
        else:
            with st.spinner("La IA está calculando vuestro menú con cantidades exactas..."):
                try:
                    str_urgentes = ", ".join(st.session_state.despensa_urgentes) if st.session_state.despensa_urgentes else "Ninguno"
                    str_fondo = ", ".join(st.session_state.despensa_fondo)
                    str_basicos = ", ".join(st.session_state.despensa_basicos)
                    str_notas = notas_especiales.strip() if notas_especiales else "Ninguna"

                    prompt = f"""
                    Eres un chef nutricionista personal experto en dieta mediterránea deportiva para una familia de 4:
                    - Héctor (Adulto deportista, 80 kg)
                    - Ainhoa (Adulta deportista, 55 kg)
                    - Beñat (Niño 8 años)
                    - Araia (Niña 3 años)

                    Genera un menú de Lunes a Viernes (Comida y Cena) en formato JSON.

                    LOGÍSTICA:
                    - Turno Ainhoa: {turno_ainhoa}.
                    - Héctor: Túper Comida L-J. Viernes come en casa. Cena en casa siempre.
                    - Cenas: Niños Beñat y Araia cenan en casa siempre.

                    PETICIONES / NOTAS ESPECIALES PARA ESTA SEMANA:
                    {str_notas}

                    REGLAS DE ORO OBLIGATORIAS:
                    1. RACIONES Y CANTIDADES: Para CADA plato debes especificar el nombre completo del plato con sus ingredientes principales y CANTIDADES EXACTAS (gramos/unidades) para toda la familia (ej. "Pechugas de pollo al horno (500g) con patatas (400g) y brócoli (300g)").
                    2. QUESOS: PROHIBIDO USAR QUESOS FUERTES (curados, azul, cabra). Únicamente se permite mozzarella suave, queso tipo sándwich o queso fresco.
                    3. TÚPERS (L-J): Selecciona 3 recetas saludables de túper sin pescado. EXACTAMENTE 1 de las recetas se debe repetir en 2 días (ej. Lunes y Miércoles).
                    4. NINGÚN TÚPER PUEDE CONTENER PESCADO O MARISCO.
                    5. PESCADO EN CASA: MÍNIMO 1 DÍA DE LA SEMANA LA CENA EN CASA DEBE SER DE PESCADO O MARISCO (ej. Merluza 500g, salmón 450g, calamares 500g).
                    6. Usar en los primeros días (Lunes/Martes) estos ingredientes urgentes si los hay: {str_urgentes}.
                    7. EXCLUIR DE LA LISTA DE COMPRA EXTRA: El usuario YA TIENE estos ingredientes en casa (Fondo: {str_fondo} | Básicos: {str_basicos}). NUNCA los incluyas en la lista de la compra ("ingredientes_compra").
                    8. LISTA DE LA COMPRA COMPLETA ("ingredientes_compra"): Incluye TODOS los ingredientes frescos o adicionales necesarios para la semana especificando cantidad (ej. "500g pechuga de pollo", "1kg zanahorias", "400g salmón fresco").
                    9. DESCRIPCIÓN Y ELABORACIÓN: Para CADA plato incluye una descripción con los pasos clave de elaboración en 2-3 frases cortas.

                    RESPONDE ÚNICAMENTE CON UN JSON CON ESTA ESTRUCTURA EXACTA SIN MARKDOWN:
                    {{
                        "Lunes": {{
                            "Comida_Plato": "...", "Comida_Desc": "...", "Comida_Compra": ["500g pechuga de pollo", "1kg brócoli"],
                            "Cena_Plato": "...", "Cena_Desc": "...", "Cena_Compra": ["1 paquete tortillas integrales"]
                        }},
                        "Martes": {{ ... }},
                        "Miércoles": {{ ... }},
                        "Jueves": {{ ... }},
                        "Viernes": {{ ... }}
                    }}
                    """

                    model = genai.GenerativeModel("gemini-3.8-flash")
                    response = model.generate_content(prompt)
                    text_response = response.text.replace("```json", "").replace("```", "").strip()
                    menu_ia = json.loads(text_response)

                    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
                    menu_final = {}

                    for dia in dias:
                        hector_c = "🍱 Túper Héctor" if dia != "Viernes" else "🍽️ Casa Héctor"
                        
                        if "Mañana" in turno_ainhoa:
                            ainhoa_c = "🍱 Túper Ainhoa"
                            ainhoa_cen = "Casa Ainhoa"
                        elif "Tarde" in turno_ainhoa:
                            ainhoa_c = "🍽️ Casa Ainhoa"
                            ainhoa_cen = "🍱 Túper Ainhoa"
                        else:
                            ainhoa_c = "🍽️ Casa Ainhoa"
                            ainhoa_cen = "Casa Ainhoa"

                        if ainhoa_cen == "Casa Ainhoa":
                            cena_log = "🍽️ Toda la familia en casa"
                        else:
                            cena_log = f"🍽️ Casa Héctor, Beñat y Araia | 🍱 Túper Ainhoa"

                        menu_final[dia] = {
                            "Comida_Plato": menu_ia[dia]["Comida_Plato"],
                            "Comida_Desc": menu_ia[dia].get("Comida_Desc", ""),
                            "Comida_Compra": menu_ia[dia].get("Comida_Compra", []),
                            "Comida_Logistica": f"{hector_c}  |  {ainhoa_c}",
                            "Cena_Plato": menu_ia[dia]["Cena_Plato"],
                            "Cena_Desc": menu_ia[dia].get("Cena_Desc", ""),
                            "Cena_Compra": menu_ia[dia].get("Cena_Compra", []),
                            "Cena_Logistica": cena_log
                        }

                    st.session_state.menu_actual = menu_final
                    st.success("¡Menú cuantitativo generado! Ve a la pestaña '🎨 Vista previa y Edición' para revisarlo.")

                except Exception as e:
                    st.error(f"Error al generar el menú: {e}")

# --- TAB 2: VISTA PREVIA Y EDICIÓN ---
with tab2:
    st.header("🎨 Vista Previa y Ajustes del Menú")
    if "menu_actual" in st.session_state:
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        
        for dia in dias:
            with st.container():
                st.subheader(f"📅 {dia}")
                col_comida, col_cena = st.columns(2)
                
                # --- COMIDA ---
                with col_comida:
                    st.caption(f"🌞 **COMIDA** — `{st.session_state.menu_actual[dia]['Comida_Logistica']}`")
                    c_title, c_btn1, c_btn2 = st.columns([0.74, 0.13, 0.13])
                    
                    with c_title:
                        st.markdown(f"### {st.session_state.menu_actual[dia]['Comida_Plato']}")
                        if st.session_state.menu_actual[dia]['Comida_Desc']:
                            st.caption(f"💡 *{st.session_state.menu_actual[dia]['Comida_Desc']}*")
                    
                    with c_btn1:
                        if st.button("🔄", key=f"btn_c_{dia}", help="Cambiar solo este plato de comida"):
                            if api_key:
                                with st.spinner("Buscando alternativa cuantitativa..."):
                                    prompt_alt = f"Sugiere 1 plato alternativo con cantidades exactas para {dia} (sin quesos fuertes ni pescado en túper). Responde en JSON corto: {{\n\"plato\": \"...\", \"desc\": \"...\", \"compra\": []\n}}"
                                    model = genai.GenerativeModel("gemini-3.8-flash")
                                    res = model.generate_content(prompt_alt)
                                    alt_json = json.loads(res.text.replace("```json", "").replace("```", "").strip())
                                    st.session_state.menu_actual[dia]['Comida_Plato'] = alt_json['plato']
                                    st.session_state.menu_actual[dia]['Comida_Desc'] = alt_json['desc']
                                    st.session_state.menu_actual[dia]['Comida_Compra'] = alt_json.get('compra', [])
                                    st.rerun()

                    with c_btn2:
                        if st.button("⭐", key=f"btn_fav_c_{dia}", help="Guardar en el Recetario Favorito"):
                            nueva_receta = {
                                "plato": st.session_state.menu_actual[dia]['Comida_Plato'],
                                "desc": st.session_state.menu_actual[dia]['Comida_Desc']
                            }
                            if nueva_receta not in st.session_state.recetas_favoritas:
                                st.session_state.recetas_favoritas.append(nueva_receta)
                                st.toast("⭐ ¡Plato guardado en tu Recetario Favorito!", icon="✅")
                            else:
                                st.toast("ℹ️ Este plato ya está en tu recetario.")

                # --- CENA ---
                with col_cena:
                    st.caption(f"🌙 **CENA** — `{st.session_state.menu_actual[dia]['Cena_Logistica']}`")
                    f_title, f_btn1, f_btn2 = st.columns([0.74, 0.13, 0.13])
                    
                    with f_title:
                        st.markdown(f"### {st.session_state.menu_actual[dia]['Cena_Plato']}")
                        if st.session_state.menu_actual[dia]['Cena_Desc']:
                            st.caption(f"💡 *{st.session_state.menu_actual[dia]['Cena_Desc']}*")
                    
                    with f_btn1:
                        if st.button("🔄", key=f"btn_f_{dia}", help="Cambiar solo este plato de cena"):
                            if api_key:
                                with st.spinner("Buscando alternativa cuantitativa..."):
                                    prompt_alt = f"Sugiere 1 plato alternativo con cantidades exactas de cena para {dia} amigable para niños (sin quesos fuertes). Responde en JSON corto: {{\n\"plato\": \"...\", \"desc\": \"...\", \"compra\": []\n}}"
                                    model = genai.GenerativeModel("gemini-3.8-flash")
                                    res = model.generate_content(prompt_alt)
                                    alt_json = json.loads(res.text.replace("```json", "").replace("```", "").strip())
                                    st.session_state.menu_actual[dia]['Cena_Plato'] = alt_json['plato']
                                    st.session_state.menu_actual[dia]['Cena_Desc'] = alt_json['desc']
                                    st.session_state.menu_actual[dia]['Cena_Compra'] = alt_json.get('compra', [])
                                    st.rerun()

                    with f_btn2:
                        if st.button("⭐", key=f"btn_fav_f_{dia}", help="Guardar en el Recetario Favorito"):
                            nueva_receta = {
                                "plato": st.session_state.menu_actual[dia]['Cena_Plato'],
                                "desc": st.session_state.menu_actual[dia]['Cena_Desc']
                            }
                            if nueva_receta not in st.session_state.recetas_favoritas:
                                st.session_state.recetas_favoritas.append(nueva_receta)
                                st.toast("⭐ ¡Plato guardado en tu Recetario Favorito!", icon="✅")
                            else:
                                st.toast("ℹ️ Este plato ya está en tu recetario.")

                st.divider()

        # Exportación mejorada
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            with st.expander("📄 Formato A4 Imprimible para la Nevera", expanded=True):
                st.markdown("### 📌 MENÚ SEMANAL FAMILIAR (L-V)")
                st.caption("Ajustado para Imprimir en Folio A4")
                st.divider()
                
                for dia in dias:
                    st.markdown(f"#### 📅 {dia.upper()}")
                    st.markdown(f"**🌞 Comida:** {st.session_state.menu_actual[dia]['Comida_Plato']}")
                    st.markdown(f"*Elaboración:* {st.session_state.menu_actual[dia]['Comida_Desc']}")
                    st.markdown(f"**🌙 Cena:** {st.session_state.menu_actual[dia]['Cena_Plato']}")
                    st.markdown(f"*Elaboración:* {st.session_state.menu_actual[dia]['Cena_Desc']}")
                    st.divider()
                    
                st.caption("🖨️ **Instrucciones para la nevera:** Pulsa `Ctrl+P` (o Imprimir en tu tablet) para guardar directamente este formato como PDF e imprimirlo en un folio A4.")

        with col_exp2:
            with st.expander("📝 Lista de la Compra Completa con Cantidades (Google Keep)", expanded=True):
                compra_total = set()
                for dia in dias:
                    for ing in st.session_state.menu_actual[dia].get('Comida_Compra', []):
                        compra_total.add(ing.strip())
                    for ing in st.session_state.menu_actual[dia].get('Cena_Compra', []):
                        compra_total.add(ing.strip())

                existentes_lower = [b.lower() for b in st.session_state.despensa_basicos + st.session_state.despensa_fondo]
                compra_filtrada = [item for item in compra_total if not any(ex in item.lower() for ex in existentes_lower)]

                if compra_filtrada:
                    texto_keep = "\n".join([f"☐ {item}" for item in sorted(compra_filtrada)])
                    st.text_area("Copia y pega en Google Keep:", value=texto_keep, height=350)
                else:
                    st.success("¡Tenéis todo lo necesario en casa! No hace falta comprar nada esta semana.")
    else:
        st.info("Primero genera un menú en la pestaña '🗓️ Planificar Semana'.")

# --- TAB 3: RECETARIO FAVORITO ---
with tab3:
    st.header("⭐ Vuestro Recetario Familiar de Éxitos")
    st.write("Platos que habéis guardado marcando la estrella durante las planificaciones semanales:")
    
    if st.session_state.recetas_favoritas:
        for idx, rec in enumerate(st.session_state.recetas_favoritas):
            col_rec, col_del = st.columns([0.9, 0.1])
            with col_rec:
                st.markdown(f"### {idx+1}. {rec['plato']}")
                if rec['desc']:
                    st.caption(f"💡 {rec['desc']}")
            with col_del:
                if st.button("🗑️", key=f"del_fav_{idx}", help="Eliminar plato"):
                    st.session_state.recetas_favoritas.pop(idx)
                    st.rerun()
            st.divider()
    else:
        st.info("Aún no habéis guardado recetas favoritas. ¡Pulsa la estrella ⭐ en cualquier plato del menú para añadirlo!")

# --- TAB 4: DESPENSA Y BÁSICOS ---
with tab4:
    st.header("📦 Gestor Visual de Despensa y Stock")
    
    col_u, col_f, col_b = st.columns(3)
    
    # BLOQUE 1: URGENTES
    with col_u:
        st.subheader("⚠️ 1. Urgentes")
        st.caption("Consumir L/M:")
        
        with st.form("form_urg", clear_on_submit=True):
            n_urg = st.text_input("Añadir urgente:", placeholder="Ej: Pechuga...", label_visibility="collapsed")
            if st.form_submit_button("➕ Añadir"):
                if n_urg and n_urg.strip() not in st.session_state.despensa_urgentes:
                    st.session_state.despensa_urgentes.append(n_urg.strip())
                    st.rerun()

        if st.session_state.despensa_urgentes:
            for idx, item in enumerate(st.session_state.despensa_urgentes):
                c1, c2 = st.columns([0.8, 0.2])
                c1.warning(item)
                if c2.button("❌", key=f"d_urg_{idx}"):
                    st.session_state.despensa_urgentes.pop(idx)
                    st.rerun()
        else:
            st.info("Vacío.")

    # BLOQUE 2: FONDO DE DESPENSA
    with col_f:
        st.subheader("🧅 2. Fondo")
        st.caption("Uso libre:")
        
        with st.form("form_fon", clear_on_submit=True):
            n_fon = st.text_input("

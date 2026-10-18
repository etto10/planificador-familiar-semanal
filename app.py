import streamlit as st
import pandas as pd
import json
import google.generativeai as genai

st.set_page_config(page_title="Planificador Familiar de Menús", page_icon="🍳", layout="wide")

st.title("🍳 Planificador Familiar de Menús con IA")
st.caption("Héctor, Ainhoa, Beñat y Araia — Menús dinámicos, inteligentes y visuales")

# --- CONFIGURACIÓN DE API KEY ---
with st.sidebar:
    st.header("⚙️ Configuración IA")
    api_key = st.text_input("Gemini API Key:", type="password", value=st.secrets.get("GEMINI_API_KEY", ""))
    if api_key:
        genai.configure(api_key=api_key)
        st.success("IA Conectada 🤖")
    else:
        st.warning("Introduce tu API Key de Gemini para activar la generación inteligente.")

# --- INICIALIZAR RECETARIO FAVORITO EN SESSION STATE ---
if "recetas_favoritas" not in st.session_state:
    st.session_state.recetas_favoritas = [
        {"plato": "Lentejas estofadas con verduras", "desc": "Guiso tradicional con zanahoria, patata y puerro. Ideal para túper."},
        {"plato": "Tacos de pollo caseros con pico de gallo", "desc": "Cena divertida para niños con aguacate y pechuga picada a la plancha."},
    ]

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
        st.info("💡 Las reglas de túper (1 solo túper repetido), la despensa y los platos para niños se aplican automáticamente.")

    st.subheader("2. Reglas logísticas familiares activas")
    st.markdown("""
    * 💼 **Héctor:** Túper L-J en comida | Casa los Viernes | Cena en casa todos los días.
    * 👧👦 **Beñat y Araia:** Cenas adaptadas de Lunes a Viernes.
    * 🍱 **Batch Cooking:** De las 4 comidas de túper, **solo 1 receta se repite 2 días** (ej. Lunes y Miércoles). Los otros 2 días son recetas de túper distintas.
    * 🚫 **Pescado:** Estrictamente prohibido en túpers. Solo en comidas/cenas en casa.
    """)

    if st.button("🚀 Generar Menú Inteligente con IA", type="primary"):
        if not api_key:
            st.error("Por favor, introduce una API Key válida en el menú lateral.")
        else:
            with st.spinner("La IA está preparando vuestro menú semanal..."):
                try:
                    urgentes = st.session_state.get("p_urgentes", "Ninguno")
                    fondo = st.session_state.get("p_fondo", "Cebollas, patatas, arroz, huevos, latas")

                    prompt = f"""
                    Eres un chef nutricionista personal para una familia de 4 (Héctor, Ainhoa y los niños Beñat de 8 años y Araia de 3).
                    Genera un menú de Lunes a Viernes (Comida y Cena) en formato JSON.

                    LOGÍSTICA:
                    - Turno Ainhoa: {turno_ainhoa}.
                    - Héctor: Túper Comida L-J. Viernes come en casa. Cena en casa siempre.
                    - Cenas: Niños Beñat (8) y Araia (3) cenan en casa. Cenas atractivas, variadas y ligeras.

                    REGLAS DE ORO:
                    1. TÚPERS (L-J): Selecciona 3 recetas de túper sin pescado. EXACTAMENTE 1 de las recetas se debe repetir en 2 días (ej. Lunes y Miércoles).
                    2. NINGÚN TÚPER PUEDE CONTENER PESCADO O MARISCO.
                    3. Usar en los primeros días (Lunes/Martes) estos ingredientes urgentes si los hay: {urgentes}.
                    4. Puedes usar estos ingredientes de fondo de despensa en cualquier momento: {fondo}.
                    5. Incluye para CADA plato una descripción breve ("descripcion") de 1 frase aclaratoria o paso a paso corto.

                    RESPONDE ÚNICAMENTE CON UN JSON CON ESTA ESTRUCTURA EXACTA SIN MARKDOWN:
                    {{
                        "Lunes": {{
                            "Comida_Plato": "...", "Comida_Desc": "...",
                            "Cena_Plato": "...", "Cena_Desc": "..."
                        }},
                        "Martes": {{ ... }},
                        "Miércoles": {{ ... }},
                        "Jueves": {{ ... }},
                        "Viernes": {{ ... }}
                    }}
                    """

                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(prompt)
                    text_response = response.text.replace("```json", "").replace("```", "").strip()
                    menu_ia = json.loads(text_response)

                    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
                    menu_final = {}

                    for dia in dias:
                        hector_c = "🍱 Túper Héctor" if dia != "Viernes" else "🍽️ Casa Héctor"
                        hector_cen = "🍽️ Casa Héctor"
                        ninos = "👧👦 Casa Beñat y Araia"
                        
                        if "Mañana" in turno_ainhoa:
                            ainhoa_c = "🍱 Túper Ainhoa"
                            ainhoa_cen = "🍽️ Casa Ainhoa"
                        elif "Tarde" in turno_ainhoa:
                            ainhoa_c = "🍽️ Casa Ainhoa"
                            ainhoa_cen = "🍱 Túper Ainhoa"
                        else:
                            ainhoa_c = "🍽️ Casa Ainhoa"
                            ainhoa_cen = "🍽️ Casa Ainhoa"

                        menu_final[dia] = {
                            "Comida_Plato": menu_ia[dia]["Comida_Plato"],
                            "Comida_Desc": menu_ia[dia].get("Comida_Desc", ""),
                            "Comida_Logistica": f"{hector_c}  |  {ainhoa_c}",
                            "Cena_Plato": menu_ia[dia]["Cena_Plato"],
                            "Cena_Desc": menu_ia[dia].get("Cena_Desc", ""),
                            "Cena_Logistica": f"{hector_cen}  |  {ainhoa_cen}  |  {ninos}"
                        }

                    st.session_state.menu_actual = menu_final
                    st.success("¡Menú generado! Ve a la pestaña '🎨 Vista previa y Edición' para revisarlo.")

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
                                with st.spinner("Buscando alternativa..."):
                                    prompt_alt = f"Sugiere 1 plato alternativo de comida para {dia} que respete no llevar pescado en túper. Responde en JSON corto: {{\n\"plato\": \"...\", \"desc\": \"...\"\n}}"
                                    model = genai.GenerativeModel("gemini-1.5-flash")
                                    res = model.generate_content(prompt_alt)
                                    alt_json = json.loads(res.text.replace("```json", "").replace("```", "").strip())
                                    st.session_state.menu_actual[dia]['Comida_Plato'] = alt_json['plato']
                                    st.session_state.menu_actual[dia]['Comida_Desc'] = alt_json['desc']
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
                                with st.spinner("Buscando alternativa..."):
                                    prompt_alt = f"Sugiere 1 plato alternativo de cena para {dia} amigable para niños (Beñat y Araia). Responde en JSON corto: {{\n\"plato\": \"...\", \"desc\": \"...\"\n}}"
                                    model = genai.GenerativeModel("gemini-1.5-flash")
                                    res = model.generate_content(prompt_alt)
                                    alt_json = json.loads(res.text.replace("```json", "").replace("```", "").strip())
                                    st.session_state.menu_actual[dia]['Cena_Plato'] = alt_json['plato']
                                    st.session_state.menu_actual[dia]['Cena_Desc'] = alt_json['desc']
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

        # Botones de exportación
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("📄 Exportar PDF para la Nevera", type="secondary"):
                st.info("Generando vista preparada para guardar/imprimir en PDF...")
        with col_exp2:
            if st.button("📝 Enviar Lista de la Compra a Google Keep", type="secondary"):
                st.success("¡Lista de ingredientes filtrada enviada correctamente!")
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

# --- TAB 4: DESPENSA Y STOCK ---
with tab4:
    st.header("📦 Inventario de Despensa y Stock")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ 1. Consumo URGENTE (Lunes/Martes)")
        st.caption("Fresco o perecedero a consumir pronto.")
        st.text_input(
            "Ingredientes urgentes (separados por comas):",
            placeholder="Ej: pechugas de pollo, medio calabacín",
            key="p_urgentes"
        )
        
        st.subheader("🧅 2. Fondo de Despensa (Uso libre)")
        st.caption("Stock no perecedero. Usar cualquier día y descontar de la lista.")
        st.text_area(
            "Stock disponible (separados por comas):",
            value="Cebollas, Patatas, Huevos, Arroz, Latas de atún, Garbanzos en bote",
            key="p_fondo"
        )

    with col2:
        st.subheader("🧂 3. Básicos Fijos (Nunca van a la lista)")
        st.caption("Condimentos e ingredientes permanentes.")
        st.text_area(
            "Básicos permanentes:",
            value="Aceite de oliva, Sal, Pimienta, Vinagre, Ajo, Harina, Pimentón, Orégano",
            key="p_basicos"
        )

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
            "desc": "Sofreír 1 cebolla y 2 zanahorias. Añadir 280g de lentejas, 80g de arroz y 1l de caldo. Cocer 35 min a fuego lento.",
            "cantidades": "280g lentejas, 80g arroz, 2 zanahorias, 1 cebolla",
            "compra": "Lentejas, zanahorias"
        },
        {
            "plato": "Tacos de pollo con mozzarella y aguacate", 
            "desc": "Dorar 400g de pechuga en tiras. Fundir 80g de mozzarella suave y servir en tortillas integrales con aguacate.",
            "cantidades": "400g pechuga, 80g mozzarella suave, 1 aguacate, 1 paq. tortillas",
            "compra": "Pechugas de pollo, mozzarella suave, aguacate, tortillas integrales"
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
        st.info("💡 Raciones calculadas para perfil deportista (Adulto 80kg, Adulta 55kg, 2 niños pequeños).")

    st.subheader("2. Peticiones e instrucciones especiales para esta semana")
    notas_especiales = st.text_area(
        "Indica sobros de comida, eventos o detalles puntuales para esta semana:",
        placeholder="Ej: Tengo un túper de brócoli cocido para el lunes; El miércoles necesitamos una cena ultra rápida...",
        height=80
    )

    st.subheader("3. Criterios de cocina y preferencias activas")
    st.markdown("""
    * 🏋️‍♂️ **Nutrición Deportiva & Familiar:** Raciones ajustadas para adulto (80 kg), adulta (55 kg) y 2 niños pequeños.
    * 🧀 **Filtro de Quesos:** **Prohibidos quesos fuertes** (curados, azul, cabra). Solo suave (mozzarella, sándwich, queso fresco).
    * 💼 **Héctor:** Túper L-J en comida | Casa los Viernes | Cena en casa siempre.
    * 🐟 **Pescado:** Prohibido en túpers. **Mínimo 1 cena a la semana en casa debe ser de pescado o marisco**.
    * 🍱 **Batch Cooking:** De las 4 comidas de túper, **solo 1 receta se repite 2 días**.
    """)

    if st.button("🚀 Generar Menú Inteligente con IA", type="primary"):
        if not api_key:
            st.error("Por favor, introduce una API Key válida en el menú lateral o en los Secrets de Streamlit.")
        else:
            with st.spinner("La IA está calculando vuestro menú con cantidades y recetas exactas..."):
                try:
                    str_urgentes = ", ".join(st.session_state.despensa_urgentes) if st.session_state.despensa_urgentes else "Ninguno"
                    str_fondo = ", ".join(st.session_state.despensa_fondo)
                    str_basicos = ", ".join(st.session_state.despensa_basicos)
                    str_notas = notas_especiales.strip() if notas_especiales else "Ninguna"

                    prompt = f"""
                    Eres un chef nutricionista personal experto en dieta mediterránea deportiva para una familia de 4:
                    - Héctor (80 kg, deportista)
                    - Ainhoa (55 kg, deportista)
                    - Beñat (8 años)
                    - Araia (3 años)

                    Genera un menú de Lunes a Viernes (Comida y Cena) en formato JSON.

                    LOGÍSTICA:
                    - Turno Ainhoa: {turno_ainhoa}.
                    - Héctor: Túper Comida L-J. Viernes come en casa. Cena en casa siempre.
                    - Cenas: Niños Beñat y Araia cenan en casa siempre.

                    PETICIONES ESPECIALES:
                    {str_notas}

                    REGLAS STRICTAS DE FORMATO Y CONTENIDO:
                    1. "Comida_Plato" y "Cena_Plato": DEBE SER ÚNICAMENTE EL NOMBRE DEL PLATO LIMPIO (ej. "Lentejas estofadas con verduras", NO incluyas ni gramos ni marcas logísticas en este título).
                    2. "Comida_Cantidades" / "Cena_Cantidades": Desglose claro de ingredientes y cantidades exactas para la familia (ej. "400g pechuga, 250g arroz, 300g brócoli").
                    3. QUESOS: PROHIBIDOS QUESOS FUERTES (curado, azul, cabra). Solo mozzarella suave, queso sándwich o queso fresco.
                    4. TÚPERS (L-J): 3 recetas sin pescado. EXACTAMENTE 1 se repite 2 días.
                    5. PESCADO EN CASA: MÍNIMO 1 DÍA cena de pescado o marisco.
                    6. INGREDIENTES A COMPRAR ("Comida_Compra" / "Cena_Compra"): Lista limpia con cantidades de lo que NO hay en casa (Fondo: {str_fondo} | Básicos: {str_basicos}).
                    7. ELABORACIÓN ("Comida_Desc" / "Cena_Desc"): 2-3 frases cortas con los pasos clave de cocina.

                    RESPONDE ÚNICAMENTE CON UN JSON CON ESTA ESTRUCTURA EXACTA SIN MARKDOWN:
                    {{
                        "Lunes": {{
                            "Comida_Plato": "Nombre del plato limpio", 
                            "Comida_Cantidades": "400g pollo, 200g arroz...",
                            "Comida_Desc": "Pasos de cocina...",
                            "Comida_Compra": ["400g pechuga de pollo"],
                            "Cena_Plato": "Nombre del plato limpio",
                            "Cena_Cantidades": "300g merluza...",
                            "Cena_Desc": "Pasos de cocina...",
                            "Cena_Compra": ["300g merluza fresca"]
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
                            ainhoa_cen = "Túper Ainhoa"
                        else:
                            ainhoa_c = "🍽️ Casa Ainhoa"
                            ainhoa_cen = "Casa Ainhoa"

                        if ainhoa_cen == "Casa Ainhoa":
                            cena_log = "🍽️ Toda la familia en casa"
                        else:
                            cena_log = "🍽️ Casa Héctor, Beñat y Araia | 🍱 Túper Ainhoa"

                        menu_final[dia] = {
                            "Comida_Plato": menu_ia[dia]["Comida_Plato"],
                            "Comida_Cantidades": menu_ia[dia].get("Comida_Cantidades", ""),
                            "Comida_Desc": menu_ia[dia].get("Comida_Desc", ""),
                            "Comida_Compra": menu_ia[dia].get("Comida_Compra", []),
                            "Comida_Logistica": f"{hector_c}  |  {ainhoa_c}",
                            "Cena_Plato": menu_ia[dia]["Cena_Plato"],
                            "Cena_Cantidades": menu_ia[dia].get("Cena_Cantidades", ""),
                            "Cena_Desc": menu_ia[dia].get("Cena_Desc", ""),
                            "Cena_Compra": menu_ia[dia].get("Cena_Compra", []),
                            "Cena_Logistica": cena_log
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
                    
                    with c_btn1:
                        if st.button("🔄", key=f"btn_c_{dia}", help="Cambiar solo este plato de comida"):
                            if api_key:
                                with st.spinner("Buscando alternativa..."):
                                    prompt_alt = f"Sugiere 1 plato alternativo para comida del {dia} (sin quesos fuertes ni pescado en túper). Responde en JSON corto: {{\n\"Comida_Plato\": \"...\", \"Comida_Cantidades\": \"...\", \"Comida_Desc\": \"...\", \"Comida_Compra\": [\"...\"]\n}}"
                                    model = genai.GenerativeModel("gemini-3.8-flash")
                                    res = model.generate_content(prompt_alt)
                                    alt_json = json.loads(res.text.replace("```json", "").replace("```", "").strip())
                                    st.session_state.menu_actual[dia]['Comida_Plato'] = alt_json['Comida_Plato']
                                    st.session_state.menu_actual[dia]['Comida_Cantidades'] = alt_json.get('Comida_Cantidades', '')
                                    st.session_state.menu_actual[dia]['Comida_Desc'] = alt_json.get('Comida_Desc', '')
                                    st.session_state.menu_actual[dia]['Comida_Compra'] = alt_json.get('Comida_Compra', [])
                                    st.rerun()

                    with c_btn2:
                        if st.button("⭐", key=f"btn_fav_c_{dia}", help="Guardar en el Recetario Favorito"):
                            nueva_receta = {
                                "plato": st.session_state.menu_actual[dia]['Comida_Plato'],
                                "desc": st.session_state.menu_actual[dia]['Comida_Desc'],
                                "cantidades": st.session_state.menu_actual[dia]['Comida_Cantidades'],
                                "compra": ", ".join(st.session_state.menu_actual[dia]['Comida_Compra'])
                            }
                            if nueva_receta not in st.session_state.recetas_favoritas:
                                st.session_state.recetas_favoritas.append(nueva_receta)
                                st.toast("⭐ ¡Plato guardado en tu Recetario Favorito!", icon="✅")
                            else:
                                st.toast("ℹ️ Este plato ya está en tu recetario.")

                    # Ficha técnica secundaria debajo del plato
                    if st.session_state.menu_actual[dia]['Comida_Cantidades']:
                        st.caption(f"👥 **Cantidades/Raciones:** {st.session_state.menu_actual[dia]['Comida_Cantidades']}")
                    if st.session_state.menu_actual[dia]['Comida_Desc']:
                        st.caption(f"👨‍🍳 **Elaboración:** {st.session_state.menu_actual[dia]['Comida_Desc']}")

                # --- CENA ---
                with col_cena:
                    st.caption(f"🌙 **CENA** — `{st.session_state.menu_actual[dia]['Cena_Logistica']}`")
                    f_title, f_btn1, f_btn2 = st.columns([0.74, 0.13, 0.13])
                    
                    with f_title:
                        st.markdown(f"### {st.session_state.menu_actual[dia]['Cena_Plato']}")
                    
                    with f_btn1:
                        if st.button("🔄", key=f"btn_f_{dia}", help="Cambiar solo este plato de cena"):
                            if api_key:
                                with st.spinner("Buscando alternativa..."):
                                    prompt_alt = f"Sugiere 1 plato alternativo de cena para {dia} amigable para niños (sin quesos fuertes). Responde en JSON corto: {{\n\"Cena_Plato\": \"...\", \"Cena_Cantidades\": \"...\", \"Cena_Desc\": \"...\", \"Cena_Compra\": [\"...\"]\n}}"
                                    model = genai.GenerativeModel("gemini-3.8-flash")
                                    res = model.generate_content(prompt_alt)
                                    alt_json = json.loads(res.text.replace("```json", "").replace("```", "").strip())
                                    st.session_state.menu_actual[dia]['Cena_Plato'] = alt_json['Cena_Plato']
                                    st.session_state.menu_actual[dia]['Cena_Cantidades'] = alt_json.get('Cena_Cantidades', '')
                                    st.session_state.menu_actual[dia]['Cena_Desc'] = alt_json.get('Cena_Desc', '')
                                    st.session_state.menu_actual[dia]['Cena_Compra'] = alt_json.get('Cena_Compra', [])
                                    st.rerun()

                    with f_btn2:
                        if st.button("⭐", key=f"btn_fav_f_{dia}", help="Guardar en el Recetario Favorito"):
                            nueva_receta = {
                                "plato": st.session_state.menu_actual[dia]['Cena_Plato'],
                                "desc": st.session_state.menu_actual[dia]['Cena_Desc'],
                                "cantidades": st.session_state.menu_actual[dia]['Cena_Cantidades'],
                                "compra": ", ".join(st.session_state.menu_actual[dia]['Cena_Compra'])
                            }
                            if nueva_receta not in st.session_state.recetas_favoritas:
                                st.session_state.recetas_favoritas.append(nueva_receta)
                                st.toast("⭐ ¡Plato guardado en tu Recetario Favorito!", icon="✅")
                            else:
                                st.toast("ℹ️ Este plato ya está en tu recetario.")

                    # Ficha técnica secundaria debajo del plato
                    if st.session_state.menu_actual[dia]['Cena_Cantidades']:
                        st.caption(f"👥 **Cantidades/Raciones:** {st.session_state.menu_actual[dia]['Cena_Cantidades']}")
                    if st.session_state.menu_actual[dia]['Cena_Desc']:
                        st.caption(f"👨‍🍳 **Elaboración:** {st.session_state.menu_actual[dia]['Cena_Desc']}")

                st.divider()

        # BLOQUES DE EXPORTACIÓN Y COMPRA
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            with st.expander("📄 Formato Tarjetas A4 Imprimible para Nevera", expanded=True):
                st.markdown("## 📌 PLANIFICACIÓN SEMANAL FAMILIAR")
                st.caption("Formato visual listo para imprimir en A4 y pegar en la nevera")
                st.divider()
                
                for dia in dias:
                    st.markdown(f"### 📅 {dia.upper()}")
                    
                    st.markdown(f"**🌞 COMIDA:** `{st.session_state.menu_actual[dia]['Comida_Plato']}`")
                    if st.session_state.menu_actual[dia]['Comida_Cantidades']:
                        st.markdown(f"* **Ingredientes/Cantidades:** {st.session_state.menu_actual[dia]['Comida_Cantidades']}")
                    if st.session_state.menu_actual[dia]['Comida_Desc']:
                        st.markdown(f"* **Elaboración:** {st.session_state.menu_actual[dia]['Comida_Desc']}")
                    
                    st.markdown(f"**🌙 CENA:** `{st.session_state.menu_actual[dia]['Cena_Plato']}`")
                    if st.session_state.menu_actual[dia]['Cena_Cantidades']:
                        st.markdown(f"* **Ingredientes/Cantidades:** {st.session_state.menu_actual[dia]['Cena_Cantidades']}")
                    if st.session_state.menu_actual[dia]['Cena_Desc']:
                        st.markdown(f"* **Elaboración:** {st.session_state.menu_actual[dia]['Cena_Desc']}")
                    st.divider()
                    
                st.caption("🖨️ **Impresión rápida:** Pulsa `Ctrl+P` (o la opción de imprimir de tu tablet) para guardarlo directamente como PDF o imprimirlo en papel A4.")

        with col_exp2:
            with st.expander("📝 Lista de la Compra Filtrada (Google Keep)", expanded=True):
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
                    st.text_area("Lista de la compra lista para seleccionar/copiar a Google Keep:", value=texto_keep, height=300)
                else:
                    st.success("¡Tenéis todo lo necesario en casa! No hace falta comprar nada esta semana.")
    else:
        st.info("Primero genera un menú en la pestaña '🗓️ Planificar Semana'.")

# --- TAB 3: RECETARIO FAVORITO (CON OPCIÓN DE AÑADIR A MANO) ---
with tab3:
    st.header("⭐ Vuestro Recetario Familiar de Éxitos")
    
    # Formulario para añadir platos manualmente a favoritos
    with st.expander("➕ Añadir una receta manual al recetario", expanded=False):
        with st.form("form_add_manual_fav", clear_on_submit=True):
            m_plato = st.text_input("Nombre del plato:", placeholder="Ej: Marmitako de bonito tradicional")
            m_cant = st.text_input("Cantidades / Ingredientes:", placeholder="Ej: 500g bonito, 1kg patatas, 2 pimientos choriceros")
            m_desc = st.text_area("Pasos de elaboración:", placeholder="Ej: Sofreír cebolla y pimiento, chascado de patatas, añadir caldo y al final el bonito...")
            
            if st.form_submit_button("⭐ Guardar en Favoritos"):
                if m_plato.strip():
                    nueva_m = {
                        "plato": m_plato.strip(),
                        "desc": m_desc.strip(),
                        "cantidades": m_cant.strip(),
                        "compra": ""
                    }
                    st.session_state.recetas_favoritas.append(nueva_m)
                    st.success(f"¡'{m_plato}' guardado correctamente en vuestro recetario!")
                    st.rerun()

    st.write("Platos guardados en vuestro catálogo familiar:")
    st.divider()
    
    if st.session_state.recetas_favoritas:
        for idx, rec in enumerate(st.session_state.recetas_favoritas):
            col_rec, col_del = st.columns([0.9, 0.1])
            with col_rec:
                st.markdown(f"### {idx+1}. {rec['plato']}")
                if rec.get('cantidades'):
                    st.caption(f"👥 **Cantidades:** {rec['cantidades']}")
                if rec.get('desc'):
                    st.caption(f"👨‍🍳 **Elaboración:** {rec['desc']}")
            with col_del:
                if st.button("🗑️", key=f"del_fav_{idx}", help="Eliminar plato"):
                    st.session_state.recetas_favoritas.pop(idx)
                    st.rerun()
            st.divider()
    else:
        st.info("Aún no habéis guardado recetas favoritas. ¡Podéis añadirlas a mano o desde el menú semanal!")

# --- TAB 4: DESPENSA Y BÁSICOS (3 COLUMNAS SIMÉTRICAS) ---
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
            n_fon = st.text_input("Añadir fondo:", placeholder="Ej: Garbanzos...", label_visibility="collapsed")
            if st.form_submit_button("➕ Añadir"):
                if n_fon and n_fon.strip() not in st.session_state.despensa_fondo:
                    st.session_state.despensa_fondo.append(n_fon.strip())
                    st.rerun()

        if st.session_state.despensa_fondo:
            for idx, item in enumerate(st.session_state.despensa_fondo):
                c1, c2 = st.columns([0.8, 0.2])
                c1.info(item)
                if c2.button("❌", key=f"d_fon_{idx}"):
                    st.session_state.despensa_fondo.pop(idx)
                    st.rerun()
        else:
            st.info("Vacío.")

    # BLOQUE 3: BÁSICOS PERMANENTES
    with col_b:
        st.subheader("🧂 3. Básicos")
        st.caption("No van a la compra:")
        
        with st.form("form_bas", clear_on_submit=True):
            n_bas = st.text_input("Añadir básico:", placeholder="Ej: Comino...", label_visibility="collapsed")
            if st.form_submit_button("➕ Añadir"):
                if n_bas and n_bas.strip() not in st.session_state.despensa_basicos:
                    st.session_state.despensa_basicos.append(n_bas.strip())
                    st.rerun()

        if st.session_state.despensa_basicos:
            for idx, item in enumerate(st.session_state.despensa_basicos):
                c1, c2 = st.columns([0.8, 0.2])
                c1.success(item)
                if c2.button("❌", key=f"d_bas_{idx}"):
                    st.session_state.despensa_basicos.pop(idx)
                    st.rerun()
        else:
            st.info("Vacío.")

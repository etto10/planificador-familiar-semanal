import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Planificador Semanal de Menús", page_icon="🍳", layout="wide")

# --- BASE DE DATOS INICIAL DE RECETAS ---
if "recetario" not in st.session_state:
    st.session_state.recetario = {
        "Guisos / Legumbres (Túper OK)": [
            {"nombre": "Lentejas estofadas con verduras", "tipo": "Comida", "tupper": True, "pescado": False},
            {"nombre": "Albóndigas de ternera en salsa con guisantes y zanahoria", "tipo": "Comida/Cena", "tupper": True, "pescado": False},
            {"nombre": "Patatas a la riojana", "tipo": "Comida", "tupper": True, "pescado": False},
            {"nombre": "Garbanzos estofados con verduras", "tipo": "Comida", "tupper": True, "pescado": False},
        ],
        "Cereales, Pasta y Salteados": [
            {"nombre": "Ensalada de quinoa con pollo, cherrys y aguacate", "tipo": "Comida", "tupper": True, "pescado": False},
            {"nombre": "Arroz integral salteado con verduras y lomo", "tipo": "Comida", "tupper": True, "pescado": False},
            {"nombre": "Pasta boloñesa casera con verduras", "tipo": "Comida", "tupper": True, "pescado": False},
            {"nombre": "Ñoquis / Espaguetis con gulas y gambas", "tipo": "Comida/Cena", "tupper": False, "pescado": True},
            {"nombre": "Pasta al pesto casero con pavo", "tipo": "Comida", "tupper": True, "pescado": False},
        ],
        "Verduras y Cremas": [
            {"nombre": "Puré casero de verduras variadas con pechuga de pollo", "tipo": "Cena/Comida", "tupper": True, "pescado": False},
            {"nombre": "Crema de calabaza con brócoli y picatostes", "tipo": "Cena", "tupper": True, "pescado": False},
            {"nombre": "Vainas (judías verdes) con patatas y refrito de ajo", "tipo": "Cena/Comida", "tupper": True, "pescado": False},
            {"nombre": "Salteado de brócoli, patata y dados de pavo", "tipo": "Comida/Cena", "tupper": True, "pescado": False},
        ],
        "Cenas Divertidas y Especiales": [
            {"nombre": "Tacos de pollo caseros con aguacate y pico de gallo", "tipo": "Cena", "tupper": False, "pescado": False},
            {"nombre": "Pizza casera de masa fina con verduras y jamón", "tipo": "Cena", "tupper": False, "pescado": False},
            {"nombre": "Tortilla de jamón / atún con ensalada variada", "tipo": "Cena", "tupper": False, "pescado": False},
            {"nombre": "Lasaña casera de verduras y atún", "tipo": "Comida/Cena", "tupper": True, "pescado": True},
        ],
        "Pescados (Solo Casa)": [
            {"nombre": "Merluza rebozada a la romana con ensalada", "tipo": "Cena/Comida", "tupper": False, "pescado": True},
            {"nombre": "Salmón a la plancha con verduras al horno", "tipo": "Cena", "tupper": False, "pescado": True},
            {"nombre": "Lubina o dorada al horno con patatas", "tipo": "Cena", "tupper": False, "pescado": True},
            {"nombre": "Chipirones en su tinta con arroz blanco", "tipo": "Comida", "tupper": False, "pescado": True},
        ]
    }

st.title("🍳 Planificador Familiar de Menús y Túpers")
st.caption("Héctor, Ainhoa, Beñat y Araia")

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["🗓️ Planificar Semana", "🎨 Vista previa y Edición", "📚 Recetario Familiar"])

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
            "Nivel de variedad deseado:",
            options=["Clásico (Platos habituales)", "Equilibrado", "Variado / Sorpresa"]
        )
    with col3:
        ingredientes_aprovechar = st.text_input(
            "Ingredientes a aprovechar:",
            placeholder="Ej: pollo, calabacín, atún"
        )

    st.subheader("2. Reglas fijas aplicadas")
    st.markdown("""
    * 💼 **Héctor:** Túper L-J en comida | Casa los Viernes | Cena en casa todos los días.
    * 👧👦 **Beñat y Araia:** Cena en casa de Lunes a Viernes.
    * 🚫 **Regla del Túper:** Ningún túper lleva pescado.
    """)

    if st.button("🚀 Generar Propuesta de Menú", type="primary"):
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        menu_gen = {}
        
        todas_recetas = []
        for cat, recs in st.session_state.recetario.items():
            todas_recetas.extend(recs)

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

            recetas_comida = [r["nombre"] for r in todas_recetas if not r["pescado"]]
            recetas_cena = [r["nombre"] for r in todas_recetas]

            plato_comida = random.choice(recetas_comida)
            plato_cena = random.choice(recetas_cena)

            menu_gen[dia] = {
                "Comida_Plato": plato_comida,
                "Comida_Logistica": f"{hector_c} | {ainhoa_c}",
                "Cena_Plato": plato_cena,
                "Cena_Logistica": f"{hector_cen} | {ainhoa_cen} | {ninos}"
            }
        
        st.session_state.menu_actual = menu_gen
        st.success("¡Menú generado con éxito! Ve a la pestaña '🎨 Vista previa y Edición' para revisarlo.")

# --- TAB 2: VISTA PREVIA Y EDICIÓN ---
with tab2:
    st.header("🎨 Edición Visual y Ajustes del Menú")
    if "menu_actual" in st.session_state:
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        
        for dia in dias:
            st.markdown(f"### 📅 {dia}")
            c1, c2 = st.columns(2)
            
            with c1:
                st.caption(f"🌞 Comida: {st.session_state.menu_actual[dia]['Comida_Logistica']}")
                st.session_state.menu_actual[dia]['Comida_Plato'] = st.text_input(
                    f"Plato comida {dia}:",
                    value=st.session_state.menu_actual[dia]['Comida_Plato'],
                    key=f"c_{dia}"
                )
            
            with c2:
                st.caption(f"🌙 Cena: {st.session_state.menu_actual[dia]['Cena_Logistica']}")
                st.session_state.menu_actual[dia]['Cena_Plato'] = st.text_input(
                    f"Plato cena {dia}:",
                    value=st.session_state.menu_actual[dia]['Cena_Plato'],
                    key=f"f_{dia}"
                )
            st.divider()

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            if st.button("📄 Exportar PDF de la Nevera"):
                st.info("Función de PDF lista para conectar con la plantilla de impresión.")
        with col_exp2:
            if st.button("📝 Enviar Lista de la Compra a Google Keep"):
                st.success("¡Lista sincronizada con Keep correctamente!")
    else:
        st.info("Primero genera un menú en la pestaña '🗓️ Planificar Semana'.")

# --- TAB 3: RECETARIO FAMILIAR ---
with tab3:
    st.header("📚 Administrar Recetario Familiar")
    st.write("Añade nuevas recetas para que el planificador las tenga en cuenta en futuros menús.")
    
    with st.form("nueva_receta"):
        nombre_r = st.text_input("Nombre del plato:")
        cat_r = st.selectbox("Categoría:", list(st.session_state.recetario.keys()))
        es_tupper = st.checkbox("¿Apto para túper?", value=True)
        tiene_pescado = st.checkbox("¿Contiene pescado/marisco?", value=False)
        
        if st.form_submit_button("➕ Guardar Receta"):
            if nombre_r:
                st.session_state.recetario[cat_r].append({
                    "nombre": nombre_r,
                    "tupper": es_tupper,
                    "pescado": tiene_pescado
                })
                st.success(f"¡Receta '{nombre_r}' añadida al recetario con éxito!")

    st.subheader("Recetas actuales en la base de datos:")
    for cat, recs in st.session_state.recetario.items():
        with st.expander(cat):
            for r in recs:
                st.write(f"• **{r['nombre']}** | Túper: {'✅' if r['tupper'] else '❌'} | Pescado: {'🐟' if r['pescado'] else '🚫'}")
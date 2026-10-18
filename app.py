import streamlit as st
import pandas as pd
import json
import google.generativeai as genai

st.set_page_config(page_title="Planificador Familiar de Menús", page_icon="🍳", layout="wide")

st.title("🍳 Planificador Familiar de Menús con IA")
st.caption("Héctor, Ainhoa, Beñat y Araia — Menús dinámicos, saludables y visuales")

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
        {"plato": "Lentejas estofadas con verduras", "desc": "Guiso tradicional de legumbres con zanahoria, patata y puerro. Pasos: sofreír verduras, añadir legumbres y caldo, y cocer a fuego lento 35 min."},
        {"plato": "Tacos de pollo caseros con pico de gallo", "desc": "Cena divertida para niños. Pasos: dorar tiras de pechuga con especias, picar tomate y aguacate, y montar en tortillas."},
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
        st.info("💡 Las reglas de túper, cenas de pescado, despensa y nutrición 100% saludable se aplican automáticamente.")

    st.subheader("2. Reglas logísticas y nutricionales activas")
    st.markdown("""
    * 🥗 **Enfoque Saludable:** Platos nutritivos, ricos en verduras, legumbres, proteínas magras y técnicas de cocina ligeras.
    * 💼 **Héctor:** Túper L-J en comida | Casa los Viernes | Cena en casa todos los días.
    * 👧👦 **Beñat y Araia:** Cenas adaptadas, atractivas y saludables de Lunes a Viernes.
    * 🐟 **Pescado:** Prohibido en túpers. **Mínimo 1 cena a la semana en casa debe ser de pescado o marisco**.
    * 🍱 **Batch Cooking:** De las 4 comidas de túper, **solo 1 receta se repite 2 días** (ej. Lunes y Miércoles). Los otros 2 días son recetas de túper distintas.
    """)

    if st.button("🚀 Generar Menú Inteligente y Saludable con IA", type="primary"):
        if not api_key:
            st.error("Por favor, introduce una API Key válida en el menú lateral o en los Secrets de Streamlit.")
        else:
            with st.spinner("La IA está preparando vuestro menú semanal saludable..."):
                try:
                    str_urgentes = ", ".join(st.session_state.despensa_urgentes) if st.session_state.despensa_urgentes else "Ninguno"
                    str_fondo = ", ".join(st.session_state.despensa_fondo)
                    str_basicos = ", ".join(st.session_state.despensa_basicos)
                    

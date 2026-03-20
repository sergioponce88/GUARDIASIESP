import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import os
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IESP - GESTIÓN DE DIAGRAMACIÓN DE GUARDIA",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- ESTILO CSS PRO 2026 ---
def inject_modern_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main { background-color: #f8fafc; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important; border-right: 1px solid rgba(255,255,255,0.05); }
        [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
        .header-container { background: white; padding: 1.5rem 2.5rem; border-radius: 32px; box-shadow: 0 10px 40px rgba(0,0,0,0.02); margin-bottom: 2rem; border: 1px solid #f1f5f9; }
        .header-title { color: #0f172a; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.03em; }
        div.stButton > button { background: #ef4444 !important; color: white !important; border: none !important; padding: 0.8rem 1.5rem !important; font-weight: 700 !important; border-radius: 18px !important; text-transform: uppercase; width: 100% !important; box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.2); }
        .metric-card { background: white; padding: 1.5rem; border-radius: 28px; border: 1px solid #f1f5f9; box-shadow: 0 4px 20px rgba(0,0,0,0.01); }
        .alert-banner { background: #fef2f2; border: 1px solid #fee2e2; padding: 1.2rem; border-radius: 20px; color: #991b1b; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #ef4444; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- LÓGICA DE NUBE (Sincronización entre dispositivos) ---
def get_cloud_config():
    try:
        config = json.loads(st.secrets["__firebase_config"])
        return config.get("projectId"), st.secrets.get("__app_id", "iesp-guardia-2026")
    except: return None, "default"

PROJECT_ID, APP_ID = get_cloud_config()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_cloud_state():
    if not BASE_URL: return None
    try:
        r = requests.get(f"{BASE_URL}/persistence/current_state", timeout=5)
        if r.status_code == 200:
            return json.loads(r.json().get("fields", {}).get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def sync_to_cloud():
    if not BASE_URL: return
    data = {
        "overrides": st.session_state.overrides,
        "role_overrides": st.session_state.role_overrides,
        "statuses": st.session_state.statuses,
        "swaps": st.session_state.swaps,
        "punishments": st.session_state.punishments,
        "start_date": str(st.session_state.start_date)
    }
    try:
        body = {"fields": {"json_data": {"stringValue": json.dumps(data)}}}
        requests.patch(f"{BASE_URL}/persistence/current_state", json=body, timeout=5)
    except: pass

# --- NÓMINA COMPLETA 138 CADETES ---
DATOS_GRUPOS_BASE = [
    {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Abregú Francisco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Acosta Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Agüero Alexis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Albarracín Federico", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Albornoz Lautaro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Aranda Héctor", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Bazán Hernán", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Brizuela Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Bustamante Marcelo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Cantos Núñez Javier", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Castro Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Cequeira Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ibarra Martina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Issa Tiara", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Medina Emilse", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Coronel Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Cruz Braian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Fernández Adrián", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Figueroa Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "González Ignacio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "González Salomón Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Guevara Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Ibáñez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Jaime Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [{"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Jiménez Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Juárez Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Lagarde Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Lazarte José", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Maldonado Clemente", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Medina Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Medina Vélez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Medrano Ángel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Mena Aníbal", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Monteros Mateo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Montes Nahuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [{"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Monteros Brenda", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Montes Eugenia", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Núñez Luciano", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Paliza Joaquín", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Ponze de León Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Quiroga López Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Reyes Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Reyes Alan", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Reynoso Martínez Luciano", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Roja Tomás", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Silva Axel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Sueldo Rodrigo Gastón", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 15, "nombre": "Soria José Lionel", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juárez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Abregú Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Argañaraz Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Ávila José", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Bazán Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Brandan Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Coronel Carlos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Diaz Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G6", "name": "GRUPO N° 2 de III° Año", "cadets": [{"n": 1, "nombre": "Carrillo Victoria", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Salas Murua", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ocaranza Sofia", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Paz María", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Carrizo Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Chávez Máximo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Del Lugo Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Del Lugo Guillermo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Dib Jorge", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Fernández Ariel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Frías Ariel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Gerez Víctor", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Girvau Mauricio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Gómez Enrique", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G7", "name": "GRUPO N° 3 de III° Año", "cadets": [{"n": 1, "nombre": "Alvarado Mauricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Valdez Federico", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Gómez Ramirez Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Guardia Cesar", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Iramain Guillermo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Juárez Tomás", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Las Heras Cabocota Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Lazarte Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Luna Jorge", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Medina Nicolás", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Miro Gastón", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Nieva Juan", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Páez Fernández Manuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G8", "name": "GRUPO N° 4 de III° Año", "cadets": [{"n": 1, "nombre": "Suárez Franco", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Alabarce Sergio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Salas Josefina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Quinteros Flabia", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Palomar Esteban", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Ramos Tobías", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Rodríguez Matías", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Rojas Leonel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Ruiz Felipe", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Ruiz Elio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Ruiz Fabricio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Ruiz Lozano Emanuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Soria Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G9", "name": "GRUPO N° 5 de III° Año", "cadets": [{"n": 1, "nombre": "Aybar Eduardo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Quiroga Melina", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Montero Irina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Moreno Karen", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Sotelo Leandro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Sotelo Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Verón González", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Villagra Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Villalba David", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Vizcarra José", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Ybarra Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Zamorano Sergio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Zarate Medina Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}]}
]

# --- INICIALIZACIÓN ---
if 'initialized' not in st.session_state:
    cloud = load_cloud_state()
    if cloud:
        st.session_state.overrides = cloud.get("overrides", {})
        st.session_state.role_overrides = cloud.get("role_overrides", {})
        st.session_state.statuses = cloud.get("statuses", {})
        st.session_state.swaps = cloud.get("swaps", [])
        st.session_state.punishments = cloud.get("punishments", {})
        st.session_state.start_date = datetime.strptime(cloud.get("start_date"), "%Y-%m-%d").date()
    else:
        st.session_state.overrides, st.session_state.role_overrides = {}, {}
        st.session_state.statuses, st.session_state.swaps = {}, []
        st.session_state.punishments = {}
        st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.groups = DATOS_GRUPOS_BASE
    st.session_state.initialized = True

def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    processed = []
    
    overrides = st.session_state.overrides.get(date_key, {})
    statuses = st.session_state.statuses.get(date_key, {})
    role_overrides = st.session_state.role_overrides.get(date_key, {})

    for i, c in enumerate(base_group['cadets']):
        # Verificar si hoy salió de este grupo por cambio autorizado
        if any(s for s in st.session_state.swaps if s['cadet_id'] == c['nombre'] and s['date'] == date_key and s['orig_group'] == base_group['name']):
            continue
        cd = c.copy()
        titular_original = cd['nombre']
        if str(i) in overrides:
            suplente = overrides[str(i)]
            cd['nombre'] = f"🔄 {suplente['nombre']}"
            cd['situacion'] = f"SUPLENTE POR {titular_original.upper()}"
            cd['is_sub'] = True
        else:
            cd['situacion'] = statuses.get(str(i), "PRESENTE")
            cd['is_sub'] = False
        if str(i) in role_overrides: cd['funcion'] = role_overrides[str(i)]
        processed.append(cd)

    for s in st.session_state.swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"CAMBIO AUTORIZADO (DE {s['orig_group']})"
            processed.append(cad_swap)
    return {"name": base_group['name'], "cadets": processed}

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>SISTEMA DE GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE", type="password")
        if st.button("ENTRAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Denegado")
else:
    with st.sidebar:
        menu = st.radio("MENÚ", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Cambios Autorizados", "📂 Reportes PDF", "⚙️ Ajustes"])
        if st.button("SALIR"): st.session_state.logged_in = False; st.rerun()

    st.markdown("""<div class="header-container"><h1 class="header-title">I.E.S.P. Diagramación de Guardia 2026</h1></div>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        today_key = str(datetime.now().date())
        expired = [s for s in st.session_state.swaps if s['date'] < today_key]
        for ex in expired:
            st.markdown(f"<div class='alert-banner'>⚠️ RESTAURACIÓN: El cambio de <b>{ex['cadet_id']}</b> caducó. Eliminar de 'Cambios Autorizados'.</div>", unsafe_allow_html=True)

        sel_date = st.date_input("FECHA SELECCIONADA", datetime.now().date()); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><b>Guardia Hoy</b><br>{gi['name']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><b>Suplencias</b><br>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><b>Novedades</b><br>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'] and 'CAMBIO' not in c['situacion'])}</div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 Nómina del Personal")
        df_display = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] or 'CAMBIO' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                c_idx = st.selectbox("Personal", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'])
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"])
                if st.button("ACTUALIZAR ESTADO"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][str(c_idx)] = nuevo_st; sync_to_cloud(); st.rerun()
        with col_m2:
            with st.container(border=True):
                st.write("**🎭 Función**")
                c_idx_f = st.selectbox("Cadete", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="f_sel")
                n_f = st.text_input("Nueva Función")
                if st.button("ASIGNAR FUNCIÓN"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][str(c_idx_f)] = n_f; sync_to_cloud(); st.rerun()
        with col_m3:
            with st.container(border=True):
                st.write("**🔄 Suplente**")
                target = st.selectbox("Titular", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="t_sel")
                all_c = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_c.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
                suplente = st.selectbox("Buscar Suplente", range(len(all_c)), format_func=lambda x: all_c[x]['label'])
                if st.button("APLICAR REEMPLAZO"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][str(target)] = all_c[suplente]['obj']; sync_to_cloud(); st.rerun()

    elif menu == "🔄 Cambios Autorizados":
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                swap_date = st.date_input("Fecha", datetime.now().date())
                all_list = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_list.append({"label": f"{c['nombre']} (Orig: {g['name']})", "obj": c, "oname": g['name']})
                sel_c = st.selectbox("Cadete", range(len(all_list)), format_func=lambda x: all_list[x]['label'])
                target_g = st.selectbox("Guardia Destino", [g['name'] for g in st.session_state.groups])
                if st.button("REGISTRAR CAMBIO"):
                    st.session_state.swaps.append({"date": str(swap_date), "cadet_id": all_list[sel_c]['obj']['nombre'], "cadet_obj": all_list[sel_c]['obj'], "orig_group": all_list[sel_c]['oname'], "target_group": target_g})
                    sync_to_cloud(); st.rerun()
        with cb:
            for idx, s in enumerate(st.session_state.swaps):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📅 {s['date']} | **{s['cadet_id']}** -> {s['target_group']}")
                if c2.button("🗑️", key=f"sw_{idx}"): st.session_state.swaps.pop(idx); sync_to_cloud(); st.rerun()

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Fecha Inicio Ciclo", st.session_state.start_date)
        if st.button("GUARDAR CONFIGURACIÓN"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Sincronizado")

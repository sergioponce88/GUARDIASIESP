import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import requests
import time
import random
import string

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IESP - GESTIÓN DE GUARDIA PRO",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- AJUSTE DE HORA TUCUMÁN (UTC-3) ---
def get_now_tucuman():
    # Streamlit Cloud usa UTC, restamos 3 horas para Argentina
    return datetime.now() - timedelta(hours=3)

# --- CONSTANTES INSTITUCIONALES ---
ESCUDO_URL_ESTABLE = "https://upload.wikimedia.org/wikipedia/commons/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"
LOGO_LOCAL = "logo_iesp.png"

def get_logo_path():
    if os.path.exists(LOGO_LOCAL): return LOGO_LOCAL
    return ESCUDO_URL_ESTABLE

# --- DISEÑO UI ---
def inject_modern_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main { background-color: #f8fafc; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important; }
        [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
        .metric-card { 
            background: white; padding: 1.5rem; border-radius: 24px; 
            border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); 
        }
        .metric-card h3 { color: #0f172a; font-weight: 800; font-size: 1.3rem; margin: 0; }
        div.stButton > button { 
            background: #ef4444 !important; color: white !important; 
            font-weight: 700 !important; border-radius: 16px !important; 
            width: 100% !important; text-transform: uppercase; 
        }
        [data-testid="stDataFrame"] > div { border-radius: 20px !important; border: 1px solid #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- MOTOR DE SINCRONIZACIÓN (BLINDADO) ---
def get_cloud_params():
    try:
        conf = json.loads(st.secrets["__firebase_config"])
        real_app_id = "iesp-v2026-final-oficial"
        return conf.get("projectId"), real_app_id, conf.get("apiKey")
    except: return None, None, None

PROJECT_ID, APP_ID, API_KEY = get_cloud_params()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_from_cloud():
    if not BASE_URL or not API_KEY: return None
    try:
        # Bypass de caché con token aleatorio
        cb = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
        url = f"{BASE_URL}/persistence/current_state?key={API_KEY}&refresh={cb}"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            doc_data = resp.json().get("fields", {})
            return json.loads(doc_data.get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def sync_to_cloud():
    if not BASE_URL or not API_KEY: return
    # Sello de tiempo de Tucumán para el archivo de datos
    st.session_state.data_timestamp = get_now_tucuman().strftime("%H:%M:%S")
    payload = {
        "groups": st.session_state.groups,
        "statuses": st.session_state.statuses,
        "overrides": st.session_state.overrides,
        "swaps": st.session_state.swaps,
        "role_overrides": st.session_state.role_overrides,
        "start_date": str(st.session_state.start_date),
        "data_timestamp": st.session_state.data_timestamp
    }
    try:
        url = f"{BASE_URL}/persistence/current_state?key={API_KEY}"
        body = {"fields": {"json_data": {"stringValue": json.dumps(payload)}}}
        res = requests.patch(url, json=body, timeout=10)
        if res.status_code == 200:
            st.session_state.last_op_time = get_now_tucuman().strftime("%H:%M:%S")
            st.toast(f"✅ PC GUARDADA: {st.session_state.data_timestamp}")
    except: st.error("❌ Fallo de red")

# --- NÓMINA (138 INTEGRANTES) ---
DATOS_GRUPOS_BASE = [
    {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete G1-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ibarra Martina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Issa Tiara", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Medina Emilse", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Coronel Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Cruz Braian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Fernández Adrián", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Figueroa Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "González Ignacio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "González Salomón Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Guevara Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Ibáñez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Jaime Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    # ... (G3-G9 se mantienen igual)
]

# --- INICIALIZACIÓN ---
if 'initialized' not in st.session_state:
    data_cloud = load_from_cloud()
    if data_cloud:
        st.session_state.update(data_cloud)
        st.session_state.start_date = datetime.strptime(data_cloud.get("start_date"), "%Y-%m-%d").date()
    else:
        st.session_state.groups = DATOS_GRUPOS_BASE
        st.session_state.statuses, st.session_state.overrides = {}, {}
        st.session_state.role_overrides, st.session_state.swaps = {}, []
        st.session_state.data_timestamp = "00:00:00"
        st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.last_op_time = "Nunca"
    st.session_state.initialized = True

def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    processed = []
    day_st = st.session_state.statuses.get(date_key, {})
    for c in base_group['cadets']:
        c_name = c['nombre'].strip()
        cd = c.copy()
        cd['situacion'] = day_st.get(c_name, "PRESENTE")
        processed.append(cd)
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- INTERFAZ ---
if not st.session_state.get('logged_in', False):
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.image(get_logo_path(), width=150)
        st.markdown("<h2 style='text-align:center;'>CONTROL IESP 2026</h2>", unsafe_allow_html=True)
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("INGRESAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        st.image(get_logo_path(), width=100)
        st.markdown(f"### 🛡️ IESP PRO")
        st.info(f"🕒 **Sello de Datos:** `{st.session_state.get('data_timestamp')}`\n\n*(Hora en que se guardó en la PC)*")
        st.success(f"☁️ **Sincronización:** {st.session_state.last_op_time}\n\n*(Hora en que el equipo actualizó)*")
        st.divider()
        if st.button("💾 GUARDAR CAMBIOS (PC)"): sync_to_cloud()
        if st.button("🔄 ACTUALIZAR (CELULAR)"):
            data = load_from_cloud()
            if data:
                st.session_state.update(data)
                st.session_state.start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
                st.session_state.last_op_time = get_now_tucuman().strftime("%H:%M:%S")
                st.success(f"¡Baja exitosa! Sello: {data.get('data_timestamp')}"); st.rerun()
        if st.button("🚪 SALIR"): st.session_state.logged_in = False; st.rerun()

    # Cabecera
    c_logo, c_title = st.columns([1, 8])
    with c_logo: st.image(get_logo_path(), width=90)
    with c_title: st.markdown(f"<h1 style='color:#0f172a; font-weight:800;'>Diagramación IESP <span style='color:#ef4444'>PRO</span></h1>", unsafe_allow_html=True)

    # Dashboard
    sel_date = st.date_input("FECHA SELECCIONADA", get_now_tucuman().date(), key="dash_date"); date_key = str(sel_date)
    gi = get_processed_guard_for_date(sel_date)
    
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f"<div class='metric-card'><p>Guardia Hoy</p><h3>{gi['name']}</h3></div>", unsafe_allow_html=True)
    with m2: st.markdown(f"<div class='metric-card'><p>Sello Datos</p><h3>{st.session_state.get('data_timestamp')}</h3></div>", unsafe_allow_html=True)
    with m3: st.markdown(f"<div class='metric-card'><p>Novedades</p><h3>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'])}</h3></div>", unsafe_allow_html=True)
    
    st.divider()
    st.dataframe(pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] else '⚠️'} {c['nombre']}", "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])]), use_container_width=True, hide_index=True)
    
    with st.container(border=True):
        st.write("**📝 Modificar Asistencia**")
        list_names = [c['nombre'] for c in gi['cadets']]
        cad_sel = st.selectbox("Personal", list_names)
        nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"])
        if st.button("CONFIRMAR CAMBIO"):
            if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
            st.session_state.statuses[date_key][cad_sel] = nuevo_st
            sync_to_cloud(); st.rerun()

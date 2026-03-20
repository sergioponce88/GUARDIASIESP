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

# --- CONSTANTES INSTITUCIONALES ---
ESCUDO_TUCUMAN = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png/250px-Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"

# --- DISEÑO UI PREMIUM (CSS) ---
def inject_modern_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main { background-color: #f8fafc; }
        
        /* Sidebar Estilizada */
        [data-testid="stSidebar"] { 
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
        
        /* Tarjetas de Métricas */
        .metric-card {
            background: white; padding: 1.5rem; border-radius: 24px;
            border: 1px solid #e2e8f0; text-align: center;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-card p { color: #64748b; font-weight: 700; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 0.5rem; }
        .metric-card h3 { color: #0f172a; font-weight: 800; font-size: 1.3rem; margin: 0; }

        /* Botones Rojos Corporativos */
        div.stButton > button {
            background: #ef4444 !important; color: white !important; border: none !important;
            padding: 0.7rem 1.2rem !important; font-weight: 700 !important; border-radius: 16px !important;
            width: 100% !important; text-transform: uppercase; letter-spacing: 1px;
            box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2);
        }
        div.stButton > button:hover { background: #dc2626 !important; transform: scale(1.02); }
        
        /* Tablas */
        [data-testid="stDataFrame"] > div { border-radius: 20px !important; border: 1px solid #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- MOTOR DE SINCRONIZACIÓN (BLINDADO) ---
def get_cloud_params():
    try:
        conf = json.loads(st.secrets["__firebase_config"])
        # Forzamos el ID oficial del proyecto para evitar errores de ruta
        real_app_id = st.secrets.get("__app_id", "iesp-v2026-final-oficial")
        return conf.get("projectId"), real_app_id, conf.get("apiKey")
    except: return None, None, None

PROJECT_ID, APP_ID, API_KEY = get_cloud_params()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_from_cloud():
    if not BASE_URL or not API_KEY: return None
    try:
        # Forzamos bypass de caché para el celular con un token aleatorio
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
    if not BASE_URL or not API_KEY: 
        st.sidebar.error("⚠️ Configuración Cloud no detectada")
        return
    # Generamos un ID de sello basado en la hora para verificar paridad
    st.session_state.version_time = datetime.now().strftime("%H:%M:%S")
    payload = {
        "groups": st.session_state.groups,
        "overrides": st.session_state.overrides,
        "statuses": st.session_state.statuses,
        "swaps": st.session_state.swaps,
        "role_overrides": st.session_state.role_overrides,
        "start_date": str(st.session_state.start_date),
        "version_time": st.session_state.version_time
    }
    try:
        url = f"{BASE_URL}/persistence/current_state?key={API_KEY}"
        body = {"fields": {"json_data": {"stringValue": json.dumps(payload)}}}
        res = requests.patch(url, json=body, timeout=10)
        if res.status_code == 200:
            st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
            st.toast(f"✅ Sincronizado a las {st.session_state.version_time}", icon="☁️")
        else: st.error(f"Error {res.status_code}: Revisa las REGLAS de Firebase")
    except: st.error("❌ Fallo crítico de conexión")

# --- NÓMINA INSTITUCIONAL REAL ---
DATOS_GRUPOS_BASE = [
    {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete G1-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ibarra Martina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Issa Tiara", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Medina Emilse", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Coronel Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Cruz Braian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Fernández Adrián", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Figueroa Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "González Ignacio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "González Salomón Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Guevara Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Ibáñez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Jaime Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [{"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete G3-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(11)]},
    {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [{"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete G4-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
    {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Abregu Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Arganaraz Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Avila Jose", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Bazan Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Brandan Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Coronel Carlos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Diaz Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G6", "name": "GRUPO N° 2 de III° Año", "cadets": [{"n": 1, "nombre": "Carrillo Victoria", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete G6-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G7", "name": "GRUPO N° 3 de III° Año", "cadets": [{"n": 1, "nombre": "Alvarado Mauricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete G7-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G8", "name": "GRUPO N° 4 de III° Año", "cadets": [{"n": 1, "nombre": "Suarez Franco", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete G8-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G9", "name": "GRUPO N° 5 de III° Año", "cadets": [{"n": 1, "nombre": "Aybar Eduardo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete G9-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(12)]}
]

# --- INICIALIZACIÓN ---
if 'initialized' not in st.session_state:
    cloud = load_from_cloud()
    if cloud:
        st.session_state.update(cloud)
        st.session_state.start_date = datetime.strptime(cloud.get("start_date"), "%Y-%m-%d").date()
    else:
        st.session_state.groups = DATOS_GRUPOS_BASE
        st.session_state.statuses, st.session_state.overrides = {}, {}
        st.session_state.role_overrides, st.session_state.swaps = {}, []
        st.session_state.version_time, st.session_state.last_sync = "00:00:00", "Nunca"
        st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.initialized = True

def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    processed = []
    
    day_st = st.session_state.statuses.get(date_key, {})
    day_ov = st.session_state.overrides.get(date_key, {})
    swaps = st.session_state.swaps

    for c in base_group['cadets']:
        c_name = c.get('nombre', 'Sin Nombre').strip()
        # Verificar si el cadete se fue a otra guardia hoy por intercambio
        if any(s for s in swaps if s['cadet_id'].strip() == c_name and s['date'] == date_key and s['orig_group'] == base_group['name']): continue
        
        cd = c.copy()
        cd['situacion'] = day_st.get(c_name, "PRESENTE")
        if c_name in day_ov:
            cd['nombre'] = f"🔄 {day_ov[c_name]['nombre']}"
            cd['situacion'] = f"SUPLENTE"
        processed.append(cd)

    # Añadir cadetes que vienen de otras guardias
    for s in swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"INTERCAMBIO (DE {s['orig_group']})"
            processed.append(cad_swap)
            
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- INTERFAZ ---
if not st.session_state.get('logged_in', False):
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.image(ESCUDO_TUCUMAN, width=150)
        st.markdown("<h2 style='text-align:center;'>CONTROL IESP 2026</h2>", unsafe_allow_html=True)
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("INGRESAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
else:
    # --- SIDEBAR MAESTRO ---
    with st.sidebar:
        st.image(ESCUDO_TUCUMAN, width=100)
        st.markdown(f"🔹 **SELLO DATOS:** `{st.session_state.get('version_time')}`")
        if BASE_URL: st.success(f"☁️ Cloud Sinc: {st.session_state.last_sync}")
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "🔄 Intercambio", "⚙️ Ajustes"])
        st.divider()
        if st.button("💾 GUARDAR EN PC"): sync_to_cloud()
        if st.button("🔄 ACTUALIZAR CELULAR"):
            data = load_from_cloud()
            if data:
                st.session_state.update(data)
                st.session_state.start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
                st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
                st.success(f"¡Sincronizado! Sello: {data.get('version_time')}"); st.rerun()
        if st.button("🚪 SALIR"): st.session_state.logged_in = False; st.rerun()

    # Cabecera
    c_logo, c_title = st.columns([1, 8])
    with c_logo: st.image(ESCUDO_TUCUMAN, width=90)
    with c_title: st.markdown(f"<h1 style='color:#0f172a; font-weight:800;'>Diagramación IESP <span style='color:#ef4444'>PRO</span></h1>", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA SELECCIONADA", datetime.now().date(), key="dash_date"); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><p>Guardia Hoy</p><h3>{gi['name']}</h3></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><p>Efectivos</p><h3>{len(gi['cadets'])}</h3></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><p>Novedades</p><h3>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'])}</h3></div>", unsafe_allow_html=True)
        
        st.divider()
        st.dataframe(pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] else '⚠️'} {c['nombre']}", "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])]), use_container_width=True, hide_index=True, height=(len(gi['cadets'])+1)*35+10)
        
        with st.container(border=True):
            st.write("**📝 Modificar Asistencia**")
            list_pure = [c['nombre'].replace("✅ ","").replace("⚠️ ","").replace("⚡ ","").replace("🔄 ","").strip() for c in gi['cadets']]
            cad_sel = st.selectbox("Personal", list_pure, key="as_sel")
            nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key="st_sel")
            if st.button("CONFIRMAR CAMBIO"):
                if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                st.session_state.statuses[date_key][cad_sel] = nuevo_st
                sync_to_cloud(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Nóminas Completas por Grupo")
        gi_today = get_processed_guard_for_date(datetime.now().date())
        cols = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            is_on_duty = g['id'] == gi_today['id']
            with cols[i % 3]:
                header = f"🟢 {g['name']} (TURNO)" if is_on_duty else g['name']
                with st.expander(header, expanded=is_on_duty):
                    st.dataframe(pd.DataFrame(g['cadets'])[["nombre", "curso", "funcion"]], hide_index=True, use_container_width=True)

    elif menu == "🔄 Intercambio":
        st.markdown("### 🔄 Terminal de Intercambio Bidireccional")
        sw_date = st.date_input("Fecha del Servicio", datetime.now().date(), key="sw_date_final")
        col_a, col_b = st.columns(2)
        with col_a:
            g_idx_a = st.selectbox("Grupo A", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="g_a")
            c_idx_a = st.selectbox("Cadete A", range(len(st.session_state.groups[g_idx_a]['cadets'])), format_func=lambda x: st.session_state.groups[g_idx_a]['cadets'][x]['nombre'], key="c_a")
        with col_b:
            g_idx_b = st.selectbox("Grupo B", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="g_b")
            c_idx_b = st.selectbox("Cadete B", range(len(st.session_state.groups[g_idx_b]['cadets'])), format_func=lambda x: st.session_state.groups[g_idx_b]['cadets'][x]['nombre'], key="c_b")
        if st.button("EJECUTAR INTERCAMBIO"):
            if g_idx_a == g_idx_b: st.warning("Mismo grupo")
            else:
                cad_a, cad_b = st.session_state.groups[g_idx_a]['cadets'][c_idx_a], st.session_state.groups[g_idx_b]['cadets'][c_idx_b]
                st.session_state.swaps.append({"date": str(sw_date), "cadet_id": cad_a['nombre'], "cadet_obj": cad_a, "orig_group": st.session_state.groups[g_idx_a]['name'], "target_group": st.session_state.groups[g_idx_b]['name']})
                st.session_state.swaps.append({"date": str(sw_date), "cadet_id": cad_b['nombre'], "cadet_obj": cad_b, "orig_group": st.session_state.groups[g_idx_b]['name'], "target_group": st.session_state.groups[g_idx_a]['name']})
                sync_to_cloud(); st.rerun()

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Inicio de Ciclo Operativo", st.session_state.start_date)
        if st.button("GUARDAR CONFIGURACIÓN"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Ajustado")

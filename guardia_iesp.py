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
        
        /* SIDEBAR PRO */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
        
        .header-container {
            background: white; padding: 1.5rem 2.5rem; border-radius: 32px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.02); margin-bottom: 2rem;
            display: flex; justify-content: space-between; align-items: center; border: 1px solid #f1f5f9;
        }
        .header-title { color: #0f172a; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.03em; margin: 0; }

        div.stButton > button {
            background: #ef4444 !important; color: white !important; border: none !important;
            padding: 0.8rem 1.5rem !important; font-weight: 700 !important; border-radius: 18px !important;
            text-transform: uppercase; width: 100% !important; box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.2);
        }
        div.stButton > button:hover { transform: translateY(-2px); background: #dc2626 !important; }

        .metric-card {
            background: white; padding: 1.5rem; border-radius: 28px; border: 1px solid #f1f5f9;
            box-shadow: 0 4px 20px rgba(0,0,0,0.01);
        }
        .alert-banner {
            background: #fef2f2; border: 1px solid #fee2e2; padding: 1.2rem; border-radius: 20px;
            color: #991b1b; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #ef4444;
        }
        [data-testid="stDataFrame"] > div { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- CONFIGURACIÓN DE NUBE (FIRESTORE SYNC) ---
def get_cloud_config():
    try:
        config = json.loads(st.secrets["__firebase_config"])
        project_id = config.get("projectId")
        app_id = st.secrets.get("__app_id", "iesp-guardia-v4")
        return project_id, app_id
    except:
        return None, "default-app"

PROJECT_ID, APP_ID = get_cloud_config()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_from_cloud():
    if not BASE_URL: return None
    try:
        resp = requests.get(f"{BASE_URL}/persistence/current_state")
        if resp.status_code == 200:
            data = resp.json().get("fields", {})
            # Deserializar simple (solo para este ejemplo)
            return json.loads(data.get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def save_to_cloud(data):
    if not BASE_URL: return
    try:
        # Serializar fecha para JSON
        payload = data.copy()
        if isinstance(payload.get("start_date"), (datetime, datetime.date)):
            payload["start_date"] = str(payload["start_date"])
            
        body = {
            "fields": {
                "json_data": {"stringValue": json.dumps(payload)}
            }
        }
        requests.patch(f"{BASE_URL}/persistence/current_state", json=body)
    except: pass

# --- DATOS INSTITUCIONALES ---
DATOS_GRUPOS = [
    {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Abregú Francisco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Acosta Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Agüero Alexis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Albarracín Federico", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Albornoz Lautaro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Aranda Héctor", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Bazán Hernán", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Brizuela Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Bustamante Marcelo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Cantos Núñez Javier", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Castro Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Cequeira Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ibarra Martina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Issa Tiara", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Medina Emilse", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juárez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"}]}
]

# --- INICIALIZACIÓN ---
if 'initialized' not in st.session_state:
    cloud_data = load_from_cloud()
    if cloud_data:
        st.session_state.groups = cloud_data.get("groups", DATOS_GRUPOS)
        st.session_state.punishments = cloud_data.get("punishments", {})
        st.session_state.overrides = cloud_data.get("overrides", {})
        st.session_state.role_overrides = cloud_data.get("role_overrides", {})
        st.session_state.statuses = cloud_data.get("statuses", {})
        st.session_state.swaps = cloud_data.get("swaps", [])
        st.session_state.start_date = datetime.strptime(cloud_data.get("start_date"), "%Y-%m-%d").date() if cloud_data.get("start_date") else datetime(2026, 3, 19).date()
    else:
        st.session_state.groups = DATOS_GRUPOS
        st.session_state.punishments, st.session_state.overrides = {}, {}
        st.session_state.role_overrides, st.session_state.statuses = {}, {}
        st.session_state.swaps = []
        st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.initialized = True

def sync():
    save_to_cloud({
        "groups": st.session_state.groups,
        "punishments": st.session_state.punishments,
        "overrides": st.session_state.overrides,
        "role_overrides": st.session_state.role_overrides,
        "statuses": st.session_state.statuses,
        "swaps": st.session_state.swaps,
        "start_date": str(st.session_state.start_date)
    })

def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    processed = []
    
    # Filtrar cadetes base
    for i, c in enumerate(base_group['cadets']):
        cd = c.copy()
        titular_original = cd['nombre']
        
        # Verificar si salió por cambio autorizado
        if any(s for s in st.session_state.swaps if s['cadet_id'] == titular_original and s['date'] == date_key and s['orig_group'] == base_group['name']):
            continue

        # Reemplazos
        if date_key in st.session_state.overrides and str(i) in st.session_state.overrides[date_key]:
            suplente = st.session_state.overrides[date_key][str(i)]
            cd['nombre'] = f"🔄 {suplente['nombre']}"
            cd['situacion'] = f"SUPLENTE POR {titular_original.upper()}"
            cd['is_sub'] = True
        else:
            cd['situacion'] = st.session_state.statuses.get(date_key, {}).get(str(i), "PRESENTE")
            cd['is_sub'] = False
            
        if date_key in st.session_state.role_overrides and str(i) in st.session_state.role_overrides[date_key]:
            cd['funcion'] = st.session_state.role_overrides[date_key][str(i)]
        processed.append(cd)

    # Añadir los que entran por cambio autorizado
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
    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>SISTEMA DE GUARDIA</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE ACCESO", type="password")
        if st.button("ENTRAR AL SISTEMA"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Denegado")
else:
    with st.sidebar:
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Cambios Autorizados", "📂 Reportes PDF", "⚙️ Ajustes"])
        if st.button("SALIR"): st.session_state.logged_in = False; st.rerun()

    st.markdown("""<div class="header-container"><h1 class="header-title">I.E.S.P. Gestión Sincronizada 2026</h1></div>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        # ALERTA DE RESTAURACIÓN
        today_key = str(datetime.now().date())
        expired = [s for s in st.session_state.swaps if s['date'] < today_key]
        if expired:
            for ex in expired:
                st.markdown(f"""<div class="alert-banner">⚠️ RESTAURACIÓN: El cambio de <b>{ex['cadet_id']}</b> ha caducado. Favor eliminarlo de 'Cambios Autorizados' para normalizar al cadete.</div>""", unsafe_allow_html=True)

        sel_date = st.date_input("FECHA", datetime.now().date()); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Guardia Hoy</div><div class='metric-value'>{gi['name']}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Suplencias</div><div class='metric-value'>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Novedades</div><div class='metric-value'>{sum(1 for c in gi['cadets'] if 'SUPLENTE' not in c['situacion'] and c['situacion'] != 'PRESENTE' and 'CAMBIO' not in c['situacion'])}</div></div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 Nómina del Personal")
        df_display = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] or 'CAMBIO' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        with st.container(border=True):
            st.write("**📝 Actualizar Situación**")
            c_idx = st.selectbox("Personal", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'])
            nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"])
            if st.button("GUARDAR ESTADO"):
                if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                st.session_state.statuses[date_key][str(c_idx)] = nuevo_st; sync(); st.rerun()

    elif menu == "🔄 Cambios Autorizados":
        st.markdown("### 🔄 Registro de Cambios de Guardia Temporales")
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                swap_date = st.date_input("Fecha del Servicio", datetime.now().date())
                all_list = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_list.append({"label": f"{c['nombre']} (Orig: {g['name']})", "obj": c, "oname": g['name']})
                sel_c = st.selectbox("Cadete", range(len(all_list)), format_func=lambda x: all_list[x]['label'])
                target_g = st.selectbox("Guardia Destino", [g['name'] for g in st.session_state.groups])
                if st.button("REGISTRAR CAMBIO"):
                    st.session_state.swaps.append({"date": str(swap_date), "cadet_id": all_list[sel_c]['obj']['nombre'], "cadet_obj": all_list[sel_c]['obj'], "orig_group": all_list[sel_c]['oname'], "target_group": target_g})
                    sync(); st.rerun()
        with cb:
            st.write("**Permisos Activos**")
            for idx, s in enumerate(st.session_state.swaps):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📅 {s['date']} | **{s['cadet_id']}** -> {s['target_group']}")
                if c2.button("🗑️", key=f"sw_{idx}"):
                    st.session_state.swaps.pop(idx); sync(); st.rerun()

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Fecha Inicio Ciclo", st.session_state.start_date)
        if st.button("GUARDAR"):
            st.session_state.start_date = new_start; sync(); st.success("Sincronizado")

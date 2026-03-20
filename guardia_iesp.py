import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import os
import requests
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IESP - GESTIÓN DE GUARDIA PRO",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- CONSTANTES INSTITUCIONALES ---
ESCUDO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png/250px-Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"

# --- DISEÑO UI VANGUARDISTA (CSS) ---
def inject_modern_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        
        .main { background-color: #f1f5f9; }
        
        /* Sidebar Estilizada */
        [data-testid="stSidebar"] { 
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        [data-testid="stSidebar"] * { color: #f8fafc !important; }
        
        /* Cabecera Principal */
        .header-box {
            background: white;
            padding: 2rem;
            border-radius: 35px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 25px;
            border: 1px solid #ffffff;
        }
        
        .header-text h1 {
            color: #0f172a;
            font-weight: 800;
            font-size: 1.8rem;
            margin: 0;
            letter-spacing: -0.02em;
        }
        
        /* Tarjetas de Métricas */
        .metric-card {
            background: white;
            padding: 1.8rem;
            border-radius: 30px;
            border: 1px solid #e2e8f0;
            text-align: center;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04);
            transition: transform 0.3s ease;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-card p { color: #64748b; font-weight: 600; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
        .metric-card h3 { color: #0f172a; font-weight: 800; font-size: 1.5rem; margin: 0; }
        
        /* Botones de Acción */
        div.stButton > button {
            background: #ef4444 !important;
            color: white !important;
            border: none !important;
            padding: 0.8rem 1.5rem !important;
            font-weight: 700 !important;
            border-radius: 18px !important;
            width: 100% !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.2);
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            background: #dc2626 !important;
            transform: scale(1.02);
        }
        
        /* Contenedores de Formularios */
        .form-card {
            background: white;
            padding: 1.5rem;
            border-radius: 25px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        
        /* Dataframes */
        [data-testid="stDataFrame"] > div { border-radius: 25px !important; overflow: hidden !important; border: 1px solid #e2e8f0 !important; }
        
        /* Expanders */
        .stExpander { 
            border-radius: 20px !important; 
            border: 1px solid #e2e8f0 !important; 
            background: white !important;
            margin-bottom: 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- LOGO EN CABECERA ---
def show_header():
    col_l, col_r = st.columns([1, 8])
    with col_l:
        st.image(ESCUDO_URL, width=100)
    with col_r:
        st.markdown(f"""
            <div class="header-text">
                <h1>Sistema de Diagramación IESP <span style="color:#ef4444">PRO</span></h1>
                <p style="color:#64748b; font-weight:500;">Gestión Inteligente de Recursos de Guardia</p>
            </div>
        """, unsafe_allow_html=True)

# --- MOTOR DE SINCRONIZACIÓN CLOUD ---
def get_cloud_params():
    try:
        conf = json.loads(st.secrets["__firebase_config"])
        return conf.get("projectId"), st.secrets.get("__app_id", "default"), conf.get("apiKey")
    except: return None, None, None

PROJECT_ID, APP_ID, API_KEY = get_cloud_params()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_from_cloud():
    if not BASE_URL or not API_KEY: return None
    try:
        url = f"{BASE_URL}/persistence/current_state?key={API_KEY}&refresh={time.time()}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            doc_data = resp.json().get("fields", {})
            return json.loads(doc_data.get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def sync_to_cloud():
    if not BASE_URL or not API_KEY: 
        st.sidebar.error("⚠️ Error: Configure los Secrets")
        return
    payload = {
        "groups": st.session_state.groups,
        "overrides": st.session_state.overrides,
        "statuses": st.session_state.statuses,
        "swaps": st.session_state.swaps,
        "role_overrides": st.session_state.role_overrides,
        "punishments": st.session_state.punishments,
        "start_date": str(st.session_state.start_date),
        "version": time.time()
    }
    try:
        url = f"{BASE_URL}/persistence/current_state?key={API_KEY}"
        body = {"fields": {"json_data": {"stringValue": json.dumps(payload)}}}
        res = requests.patch(url, json=body, timeout=10)
        if res.status_code == 200:
            st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
            st.toast("✅ Nube Sincronizada", icon="☁️")
        else: st.error(f"Error {res.status_code}: Revisa la pestaña 'Rules' en Firebase")
    except: st.error("❌ Fallo crítico de conexión")

# --- NÓMINA INSTITUCIONAL REAL ---
DATOS_GRUPOS_BASE = [
    {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Abregú Francisco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Acosta Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Agüero Alexis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Albarracín Federico", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Albornoz Lautaro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Aranda Héctor", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Bazán Hernán", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Brizuela Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Bustamante Marcelo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Cantos Núñez Javier", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Castro Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Cequeira Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ibarra Martina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Issa Tiara", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Medina Emilse", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Coronel Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Cruz Braian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Fernández Adrián", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Figueroa Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "González Ignacio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "González Salomón Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Guevara Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Ibáñez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Jaime Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [{"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Jiménez Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Juárez Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Lagarde Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Lazarte José", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Maldonado Clemente", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Medina Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Medina Vélez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Medrano Ángel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Mena Aníbal", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Monteros Mateo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Montes Nahuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [{"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete G4-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
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
        st.session_state.role_overrides, st.session_state.punishments = {}, {}
        st.session_state.swaps = []
        st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.last_sync = "Nunca"
    st.session_state.initialized = True

def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    processed = []
    day_ov = st.session_state.overrides.get(date_key, {})
    day_st = st.session_state.statuses.get(date_key, {})
    day_ro = st.session_state.role_overrides.get(date_key, {})
    swaps = st.session_state.swaps

    for c in base_group['cadets']:
        c_name = c.get('nombre', 'Sin Nombre').strip()
        if any(s for s in swaps if s['cadet_id'].strip() == c_name and s['date'] == date_key and s['orig_group'] == base_group['name']): continue
        cd = c.copy()
        cd['situacion'] = day_st.get(c_name, "PRESENTE")
        cd['is_sub'] = False
        if c_name in day_ov:
            cd['nombre'] = f"🔄 {day_ov[c_name]['nombre']}"
            cd['situacion'] = f"SUPLENTE POR {c_name.upper()}"
            cd['is_sub'] = True
        if c_name in day_ro: cd['funcion'] = day_ro[c_name]
        processed.append(cd)

    for s in swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"CAMBIO (DE {s['orig_group']})"
            processed.append(cad_swap)
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- INTERFAZ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        st.image(ESCUDO_URL, width=150)
        st.markdown("<h2 style='text-align:center;'>CONTROL DE GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("INGRESAR AL SISTEMA"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Acceso Denegado")
else:
    # --- SIDEBAR PRO ---
    with st.sidebar:
        st.image(ESCUDO_URL, width=120)
        st.markdown(f"**SISTEMA OFICIAL 2026**")
        if BASE_URL: st.success(f"☁️ Cloud Sinc: {st.session_state.last_sync}")
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Traslados", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        st.divider()
        if st.button("💾 GUARDAR CAMBIOS (NUBE)"): sync_to_cloud()
        if st.button("🔄 ACTUALIZAR DATOS"):
            cloud = load_from_cloud()
            if cloud:
                for k, v in cloud.items(): 
                    if k == "start_date": st.session_state[k] = datetime.strptime(v, "%Y-%m-%d").date()
                    else: st.session_state[k] = v
                st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
                st.success("¡Datos actualizados!"); st.rerun()
        if st.button("🚪 SALIR"): st.session_state.logged_in = False; st.rerun()

    show_header()

    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA SELECCIONADA", datetime.now().date(), key="dash_date"); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        # Grid de Métricas Modernas
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><p>Guardia Activa</p><h3>{gi['name']}</h3></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><p>Total Efectivos</p><h3>{len(gi['cadets'])}</h3></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><p>Novedades ART/Nota</p><h3>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'])}</h3></div>", unsafe_allow_html=True)
        
        st.divider()
        
        # Tabla Principal
        st.markdown("### 📋 Nómina de Servicio")
        df_dash = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_dash, use_container_width=True, hide_index=True, height=(len(df_dash)+1)*35+10)
        
        # Formularios en Cards
        st.markdown("### 🛠️ Acciones de Control")
        col1, col2, col3 = st.columns(3)
        list_pure = [c['nombre'].replace("🔄 ","").replace("✅ ","").replace("⚠️ ","").replace("⚡ ","").strip() for c in gi['cadets']]
        
        with col1:
            st.markdown("<div class='form-card'>", unsafe_allow_html=True)
            st.write("**📝 Asistencia**")
            cad_sel = st.selectbox("Personal", list_pure, key="as_sel")
            nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key="st_sel")
            if st.button("Guardar Estado"):
                if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                st.session_state.statuses[date_key][cad_sel] = nuevo_st
                sync_to_cloud(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='form-card'>", unsafe_allow_html=True)
            st.write("**🎭 Función**")
            cad_sel_f = st.selectbox("Personal", list_pure, key="fu_sel")
            nueva_fu = st.text_input("Nueva Función", key="fu_val")
            if st.button("Asignar Función"):
                if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                st.session_state.role_overrides[date_key][cad_sel_f] = nueva_fu
                sync_to_cloud(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown("<div class='form-card'>", unsafe_allow_html=True)
            st.write("**🔄 Suplencia**")
            titular = st.selectbox("Titular", list_pure, key="su_sel")
            all_options = []
            for g in st.session_state.groups:
                for c in g['cadets']: all_options.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
            idx_sup = st.selectbox("Suplente", range(len(all_options)), format_func=lambda x: all_options[x]['label'])
            if st.button("Aplicar Reemplazo"):
                if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                st.session_state.overrides[date_key][titular] = all_options[idx_sup]['obj']
                sync_to_cloud(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Nóminas Completas del Personal")
        cols_all = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            with cols_all[i % 3]:
                with st.expander(f"#### {g['name']}"):
                    st.dataframe(pd.DataFrame(g['cadets'])[["nombre", "curso", "funcion"]], hide_index=True, use_container_width=True)

    elif menu == "⚖️ Guardia Castigo":
        pk_cast = str(st.date_input("Fecha Castigo", datetime.now().date(), key="cast_d"))
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_idx = st.selectbox("Grupo Origen", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
                c_idx = st.selectbox("Cadete", range(len(st.session_state.groups[g_idx]['cadets'])), format_func=lambda x: st.session_state.groups[g_idx]['cadets'][x]['nombre'])
                if st.button("AGREGAR REFUERZO"):
                    if pk_cast not in st.session_state.punishments: st.session_state.punishments[pk_cast] = []
                    st.session_state.punishments[pk_cast].append(st.session_state.groups[g_idx]['cadets'][c_idx]); sync_to_cloud(); st.rerun()
        with cb:
            st.write(f"**Refuerzos para {pk_cast}**")
            if pk_cast in st.session_state.punishments:
                for idx_p, p_item in enumerate(st.session_state.punishments[pk_cast]):
                    c1, c2 = st.columns([4, 1]); c1.write(f"• {p_item['nombre']}"); 
                    if c2.button("🗑️", key=f"del_p_{idx_p}"): st.session_state.punishments[pk_cast].pop(idx_p); sync_to_cloud(); st.rerun()

    elif menu == "🔄 Traslados":
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                sw_date = st.date_input("Fecha Traslado", datetime.now().date())
                all_l = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_l.append({"label": f"{c['nombre']} ({g['name']})", "obj": c, "oname": g['name']})
                sel_c = st.selectbox("Cadete", range(len(all_l)), format_func=lambda x: all_l[x]['label'])
                target_g = st.selectbox("Destino", [g['name'] for g in st.session_state.groups])
                if st.button("REGISTRAR"):
                    st.session_state.swaps.append({"date": str(sw_date), "cadet_id": all_l[sel_c]['obj']['nombre'], "cadet_obj": all_l[sel_c]['obj'], "orig_group": all_l[sel_c]['oname'], "target_group": target_g})
                    sync_to_cloud(); st.rerun()
        with cb:
            for idx, s in enumerate(st.session_state.swaps):
                st.write(f"📅 {s['date']} | {s['cadet_id']} -> {s['target_group']}")
                if st.button("🗑️", key=f"sw_{idx}"): st.session_state.swaps.pop(idx); sync_to_cloud(); st.rerun()

    elif menu == "📂 Reportes PDF":
        st.info("Generación de Planillas con Logo Institucional Oficial")
        st.button("🚀 GENERAR LOTE PDF")

    elif menu == "👥 Redistribución":
        for i_red, g_red in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g_red['name']}"):
                df_red = pd.DataFrame(g_red['cadets'])
                df_res = st.data_editor(df_red, num_rows="dynamic", key=f"ed_{i_red}", use_container_width=True)
                if st.button(f"Guardar Cambios en {g_red['id']}", key=f"btn_red_save_{i_red}"):
                    st.session_state.groups[i_red]['cadets'] = df_res.to_dict('records'); sync_to_cloud(); st.rerun()

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Inicio de Ciclo Operativo", st.session_state.start_date)
        if st.button("GUARDAR CONFIGURACIÓN"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Ajustado")

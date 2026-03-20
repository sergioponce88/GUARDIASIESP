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
    page_title="IESP - GESTIÓN DE GUARDIA",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- CONSTANTES Y LOGO ---
LOGO_FILE = "logo_iesp.png" 
# Escudo de respaldo oficial
ESCUDO_OFICIAL = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png/250px-Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"

# --- ESTILO CSS PROFESIONAL ---
def inject_modern_css():
    # Eliminamos el prefijo f para evitar el SyntaxError con las llaves de CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main { background-color: #f8fafc; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important; }
        [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
        .header-container {
            background: white; padding: 1.5rem 2rem; border-radius: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.02); margin-bottom: 2rem;
            display: flex; align-items: center; gap: 20px; border: 1px solid #f1f5f9;
        }
        .header-title { color: #0f172a; font-weight: 800; font-size: 1.4rem; margin: 0; }
        div.stButton > button {
            background: #ef4444 !important; color: white !important; border: none !important;
            padding: 0.8rem 1.5rem !important; font-weight: 700 !important; border-radius: 15px !important;
            width: 100% !important; text-transform: uppercase;
        }
        .metric-card { background: white; padding: 1.2rem; border-radius: 22px; border: 1px solid #f1f5f9; text-align: center; }
        .alert-banner {
            background: #fef2f2; border: 1px solid #fee2e2; padding: 1rem; border-radius: 20px;
            color: #991b1b; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #ef4444;
        }
        /* Estabilidad para evitar errores visuales en tablas */
        [data-testid="stDataFrame"] > div { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- LÓGICA DE SINCRONIZACIÓN CLOUD (FIRESTORE) ---
def get_cloud_params():
    try:
        conf = json.loads(st.secrets["__firebase_config"])
        return conf.get("projectId"), st.secrets.get("__app_id", "iesp-v2026-final")
    except: return None, None

PROJECT_ID, APP_ID = get_cloud_params()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_cloud_data():
    if not BASE_URL: return None
    try:
        resp = requests.get(f"{BASE_URL}/persistence/current_state", timeout=10)
        if resp.status_code == 200:
            return json.loads(resp.json().get("fields", {}).get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def sync_to_cloud():
    if not BASE_URL: 
        st.sidebar.error("⚠️ Secrets no configurados")
        return
    state = {
        "groups": st.session_state.groups,
        "overrides": st.session_state.overrides,
        "statuses": st.session_state.statuses,
        "swaps": st.session_state.swaps,
        "role_overrides": st.session_state.role_overrides,
        "punishments": st.session_state.punishments,
        "start_date": str(st.session_state.start_date)
    }
    try:
        body = {"fields": {"json_data": {"stringValue": json.dumps(state)}}}
        requests.patch(f"{BASE_URL}/persistence/current_state", json=body, timeout=10)
        st.toast("✅ Nube Sincronizada", icon="☁️")
    except: st.error("❌ Error al guardar en la nube")

# --- BASE DE DATOS MAESTRA (138 CADETES) ---
DATOS_GRUPOS_BASE = [
    {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete G1-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(14)]},
    {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete G2-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(14)]},
    {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete G3-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
    {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete G4-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(15)]},
    {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Abregu Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Arganaraz Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Avila Jose", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Bazan Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Brandan Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Coronel Carlos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Diaz Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G6", "name": "GRUPO N° 2 de III° Año", "cadets": [{"n": i+1, "nombre": f"Cadete G6-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(14)]},
    {"id": "G7", "name": "GRUPO N° 3 de III° Año", "cadets": [{"n": i+1, "nombre": f"Cadete G7-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
    {"id": "G8", "name": "GRUPO N° 4 de III° Año", "cadets": [{"n": i+1, "nombre": f"Cadete G8-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
    {"id": "G9", "name": "GRUPO N° 5 de III° Año", "cadets": [{"n": i+1, "nombre": f"Cadete G9-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(13)]}
]

# --- INICIALIZACIÓN ---
if 'initialized' not in st.session_state:
    cloud = load_cloud_data()
    if cloud:
        st.session_state.groups = cloud.get("groups", DATOS_GRUPOS_BASE)
        st.session_state.overrides = cloud.get("overrides", {})
        st.session_state.statuses = cloud.get("statuses", {})
        st.session_state.swaps = cloud.get("swaps", [])
        st.session_state.role_overrides = cloud.get("role_overrides", {})
        st.session_state.punishments = cloud.get("punishments", {})
        st.session_state.start_date = datetime.strptime(cloud.get("start_date"), "%Y-%m-%d").date()
    else:
        st.session_state.groups, st.session_state.overrides = DATOS_GRUPOS_BASE, {}
        st.session_state.statuses, st.session_state.swaps = {}, []
        st.session_state.role_overrides, st.session_state.punishments = {}, {}
        st.session_state.start_date = datetime(2026, 3, 19).date()
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

    # Miembros originales
    for i, c in enumerate(base_group['cadets']):
        if any(s for s in swaps if s['cadet_id'] == c['nombre'] and s['date'] == date_key and s['orig_group'] == base_group['name']):
            continue
        cd = c.copy()
        titular = cd['nombre']
        if str(i) in day_ov:
            cd['nombre'] = f"🔄 {day_ov[str(i)]['nombre']}"
            cd['situacion'] = f"SUPLENTE POR {titular.upper()}"
            cd['is_sub'] = True
        else:
            cd['situacion'] = day_st.get(str(i), "PRESENTE")
            cd['is_sub'] = False
        if str(i) in day_ro: cd['funcion'] = day_ro[str(i)]
        processed.append(cd)

    # Traslados hacia el grupo
    for s in swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"CAMBIO AUTORIZADO (DE {s['orig_group']})"
            processed.append(cad_swap)
            
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        # Mostrar logo o escudo oficial
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=150)
        else: st.image(ESCUDO_OFICIAL, width=150)
        st.markdown("<h2 style='text-align:center; color:#0f172a;'>CONTROL DE GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE ACCESO", type="password", key="login_pass_input")
        if st.button("INGRESAR AL SISTEMA", key="btn_login_submit"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Contraseña incorrecta")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=140)
        else: st.image(ESCUDO_OFICIAL, width=120)
        st.markdown("<h3 style='color:white; text-align:center; font-size:0.8rem;'>IESP SISTEMA 2026</h3>", unsafe_allow_html=True)
        
        # MONITOR DE NUBE
        if BASE_URL: st.success("☁️ Nube Conectada")
        else: st.warning("⚠️ Sin Configuración Nube")

        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Cambios Autorizados", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"], key="nav_radio")
        st.divider()
        if st.button("🔄 ACTUALIZAR DATOS", key="btn_sync_cloud"):
            data = load_cloud_data()
            if data: st.session_state.update(data); st.success("Sincronizado"); st.rerun()
        if st.button("🚪 SALIR", key="btn_logout"): st.session_state.logged_in = False; st.rerun()

    # --- ENCABEZADO ---
    h_col1, h_col2 = st.columns([1, 9])
    with h_col1:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=70)
        else: st.image(ESCUDO_OFICIAL, width=70)
    with h_col2:
        st.markdown(f"""<h1 style="color:#0f172a; font-weight:800; margin:0; padding-top:10px;">Diagramación de Guardia Pro</h1>""", unsafe_allow_html=True)

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        date_today = str(datetime.now().date())
        expired = [s for s in st.session_state.swaps if s['date'] < date_today]
        for ex in expired:
            st.markdown(f"<div class='alert-banner'>⚠️ ALERTA: El cambio de <b>{ex['cadet_id']}</b> ha caducado. Favor borrarlo de 'Cambios Autorizados'.</div>", unsafe_allow_html=True)

        sel_date = st.date_input("FECHA DE CONSULTA", datetime.now().date(), key="dash_date_pick"); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><b>Guardia Actual</b><br>{gi['name']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><b>Suplentes</b><br>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><b>Novedades</b><br>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'] and 'CAMBIO' not in c['situacion'])}</div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 Nómina del Personal")
        df_dash = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] or 'CAMBIO' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_dash, use_container_width=True, hide_index=True, height=(len(df_dash)+1)*35+10, key=f"tbl_dash_{date_key}")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                c_idx = st.selectbox("Personal", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key=f"sel_st_cad_{date_key}")
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key=f"sel_st_val_{date_key}")
                if st.button("GUARDAR ESTADO", key=f"btn_st_save_{date_key}"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][str(c_idx)] = nuevo_st; sync_to_cloud(); st.rerun()
        with col_m2:
            with st.container(border=True):
                st.write("**🎭 Función**")
                c_idx_f = st.selectbox("Personal", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key=f"sel_f_cad_{date_key}")
                n_f = st.text_input("Nueva Función", key=f"txt_f_val_{date_key}")
                if st.button("ASIGNAR FUNCIÓN", key=f"btn_f_save_{date_key}"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][str(c_idx_f)] = n_f; sync_to_cloud(); st.rerun()
        with col_m3:
            with st.container(border=True):
                st.write("**🔄 Suplencia**")
                target = st.selectbox("Titular", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key=f"sel_sup_tit_{date_key}")
                all_sup = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_sup.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
                suplente = st.selectbox("Buscar Suplente", range(len(all_sup)), format_func=lambda x: all_sup[x]['label'], key=f"sel_sup_val_{date_key}")
                if st.button("APLICAR REEMPLAZO", key=f"btn_sup_save_{date_key}"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][str(target)] = all_sup[suplente]['obj']; sync_to_cloud(); st.rerun()

    # --- CAMBIOS AUTORIZADOS (Traslados) ---
    elif menu == "🔄 Cambios Autorizados":
        ca_sw, cb_sw = st.columns(2)
        with ca_sw:
            with st.container(border=True):
                sw_date = st.date_input("Fecha del Servicio", datetime.now().date(), key="sw_date_pick")
                all_sw_list = []
                for g_sw in st.session_state.groups:
                    for c_sw in g_sw['cadets']: all_sw_list.append({"label": f"{c_sw['nombre']} ({g_sw['name']})", "obj": c_sw, "oname": g_sw['name']})
                sel_sw = st.selectbox("Cadete a Trasladar", range(len(all_sw_list)), format_func=lambda x: all_sw_list[x]['label'], key="sw_cad_sel")
                target_sw = st.selectbox("Guardia Destino", [g['name'] for g in st.session_state.groups], key="sw_g_dest")
                if st.button("REGISTRAR TRASLADO", key="btn_sw_reg"):
                    st.session_state.swaps.append({"date": str(sw_date), "cadet_id": all_sw_list[sel_sw]['obj']['nombre'], "cadet_obj": all_sw_list[sel_sw]['obj'], "orig_group": all_sw_list[sel_sw]['oname'], "target_group": target_sw})
                    sync_to_cloud(); st.rerun()
        with cb_sw:
            st.write("**Traslados Activos**")
            for idx_s, s_val in enumerate(st.session_state.swaps):
                c_sw1, c_sw2 = st.columns([3, 1])
                c_sw1.write(f"📅 {s_val['date']} | {s_val['cadet_id']} -> {s_val['target_group']}")
                if c_sw2.button("🗑️", key=f"btn_sw_del_{idx_s}"): st.session_state.swaps.pop(idx_s); sync_to_cloud(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        cols_all = st.columns(3)
        for i_all, g_all in enumerate(st.session_state.groups):
            with cols_all[i_all % 3]:
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:1rem; border:1px solid #f1f5f9; margin-bottom:1rem;">
                    <div style="background:#0f172a; color:white; padding:0.4rem; border-radius:10px; text-align:center; font-weight:800; font-size:0.8rem;">{g_all['name']}</div>""", unsafe_allow_html=True)
                for c_all in g_all['cadets']:
                    st.markdown(f"<div style='font-size:0.75rem; border-bottom:1px solid #f8fafc; padding:2px;'>• {c_all['nombre']}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "⚖️ Guardia Castigo":
        pk_cast = str(st.date_input("Fecha Castigo", datetime.now().date(), key="cast_date_pick"))
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_idx = st.selectbox("Grupo Origen", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="cast_g_sel")
                c_idx = st.selectbox("Cadete", range(len(st.session_state.groups[g_idx]['cadets'])), format_func=lambda x: st.session_state.groups[g_idx]['cadets'][x]['nombre'], key="cast_c_sel")
                if st.button("AGREGAR A LISTA", key="btn_cast_add"):
                    if pk_cast not in st.session_state.punishments: st.session_state.punishments[pk_cast] = []
                    st.session_state.punishments[pk_cast].append(st.session_state.groups[g_idx]['cadets'][c_idx]); sync_to_cloud(); st.rerun()
        with cb:
            st.write(f"**Refuerzos para {pk_cast}**")
            if pk_cast in st.session_state.punishments:
                for p_item in st.session_state.punishments[pk_cast]:
                    st.write(f"• {p_item['nombre']} ({p_item['curso']})")

    elif menu == "👥 Redistribución":
        st.warning("Advertencia: Los cambios aquí son permanentes en la estructura de los grupos.")
        for i_red, g_red in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g_red['name']}"):
                df_red = pd.DataFrame(g_red['cadets'])
                df_red_res = st.data_editor(df_red, num_rows="dynamic", key=f"editor_red_{i_red}", use_container_width=True)
                if st.button(f"Guardar Estructura {g_red['id']}", key=f"btn_red_save_{i_red}"):
                    st.session_state.groups[i_red]['cadets'] = df_red_res.to_dict('records'); sync_to_cloud(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        st.markdown("### Configuración de Ciclo Operativo")
        new_start = st.date_input("Fecha Inicio Grupo 1", st.session_state.start_date, key="settings_date_input")
        if st.button("SINCRONIZAR CICLO", key="btn_settings_save"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Ciclo sincronizado correctamente")

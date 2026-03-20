import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import os
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IESP - GESTIÓN DE GUARDIA",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- CONSTANTES Y LOGO ---
LOGO_FILE = "logo_iesp.png" 
ESCUDO_OFICIAL = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png/250px-Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"

# --- ESTILO CSS PRO ---
def inject_modern_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        * {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .main {{ background-color: #f8fafc; }}
        [data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important; }}
        [data-testid="stSidebar"] * {{ color: #cbd5e1 !important; }}
        .header-container {{
            background: white; padding: 1.5rem 2rem; border-radius: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.02); margin-bottom: 2rem;
            display: flex; align-items: center; gap: 20px; border: 1px solid #f1f5f9;
        }
        .header-title {{ color: #0f172a; font-weight: 800; font-size: 1.4rem; margin: 0; }}
        div.stButton > button {{
            background: #ef4444 !important; color: white !important; border: none !important;
            padding: 0.8rem 1.5rem !important; font-weight: 700 !important; border-radius: 15px !important;
            width: 100% !important;
        }
        .metric-card {{ background: white; padding: 1.2rem; border-radius: 22px; border: 1px solid #f1f5f9; text-align: center; }}
        .alert-banner {{
            background: #fef2f2; border: 1px solid #fee2e2; padding: 1rem; border-radius: 20px;
            color: #991b1b; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #ef4444;
        }
        [data-testid="stDataFrame"] > div {{ border: none !important; }}
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- CONFIGURACIÓN DE NUBE (Sincronización Firestore) ---
def get_cloud_params():
    try:
        conf = json.loads(st.secrets["__firebase_config"])
        return conf.get("projectId"), st.secrets.get("__app_id", "iesp-v2026")
    except: return None, "iesp-v2026"

PROJECT_ID, APP_ID = get_cloud_params()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_from_cloud():
    if not BASE_URL: return None
    try:
        resp = requests.get(f"{BASE_URL}/persistence/current_state", timeout=8)
        if resp.status_code == 200:
            raw = resp.json().get("fields", {}).get("json_data", {}).get("stringValue", "{}")
            return json.loads(raw)
    except: pass
    return None

def sync_to_cloud():
    if not BASE_URL: 
        st.error("Error: Configuración de base de datos no encontrada.")
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
        res = requests.patch(f"{BASE_URL}/persistence/current_state", json=body, timeout=8)
        if res.status_code == 200: st.toast("✅ Cambios guardados en la nube", icon="☁️")
        else: st.error("❌ Error al sincronizar")
    except: st.error("❌ Sin conexión")

# --- NÓMINA INSTITUCIONAL ---
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
    cloud = load_from_cloud()
    if cloud:
        st.session_state.groups = cloud.get("groups", DATOS_GRUPOS_BASE)
        st.session_state.overrides = cloud.get("overrides", {})
        st.session_state.statuses = cloud.get("statuses", {})
        st.session_state.swaps = cloud.get("swaps", [])
        st.session_state.role_overrides = cloud.get("role_overrides", {})
        st.session_state.punishments = cloud.get("punishments", {})
        st.session_state.start_date = datetime.strptime(cloud.get("start_date"), "%Y-%m-%d").date() if cloud.get("start_date") else datetime(2026, 3, 19).date()
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

    for s in swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            c_swap = s['cadet_obj'].copy()
            c_swap['nombre'] = f"⚡ {c_swap['nombre']}"
            c_swap['situacion'] = f"CAMBIO AUTORIZADO (DE {s['orig_group']})"
            processed.append(c_swap)
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        st.image(ESCUDO_OFICIAL, width=150)
        st.markdown("<h2 style='text-align:center;'>CONTROL DE GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE ACCESO", type="password")
        if st.button("ENTRAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Denegado")
else:
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=120)
        else: st.image(ESCUDO_OFICIAL, width=100)
        st.markdown("<h3 style='color:white; text-align:center; font-size:0.8rem;'>DIAGRAMACIÓN PRO 2026</h3>", unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Cambios Autorizados", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        if st.button("🔄 DESCARGAR ÚLTIMA NUBE"):
            data = load_from_cloud()
            if data: st.session_state.update(data); st.rerun()
        if st.button("CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()

    st.markdown(f"""<div class="header-container"><img src="{ESCUDO_OFICIAL}" width="50"><h1 class="header-title">I.E.S.P. Diagramación de Guardia Sincronizada</h1></div>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        today_key = str(datetime.now().date())
        expired = [s for s in st.session_state.swaps if s['date'] < today_key]
        for ex in expired:
            st.markdown(f"<div class='alert-banner'>⚠️ RESTAURACIÓN: El cambio de <b>{ex['cadet_id']}</b> caducó. Eliminar de 'Cambios Autorizados'.</div>", unsafe_allow_html=True)

        sel_date = st.date_input("FECHA", datetime.now().date()); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><b>Guardia</b><br>{gi['name']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><b>Suplentes</b><br>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><b>Novedades</b><br>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'] and 'CAMBIO' not in c['situacion'])}</div>", unsafe_allow_html=True)
        
        df = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] or 'CAMBIO' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df, use_container_width=True, hide_index=True, height=(len(df)+1)*35+10)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                c_idx = st.selectbox("Personal", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'])
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"])
                if st.button("GUARDAR ESTADO"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][str(c_idx)] = nuevo_st; sync_to_cloud(); st.rerun()
        with col2:
            with st.container(border=True):
                st.write("**🎭 Función**")
                c_idx_f = st.selectbox("Cadete", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="f")
                n_f = st.text_input("Nueva Función")
                if st.button("ASIGNAR"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][str(c_idx_f)] = n_f; sync_to_cloud(); st.rerun()
        with col3:
            with st.container(border=True):
                st.write("**🔄 Suplencia**")
                target = st.selectbox("Titular", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="t")
                all_c = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_c.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
                suplente_idx = st.selectbox("Buscar Suplente", range(len(all_c)), format_func=lambda x: all_c[x]['label'])
                if st.button("APLICAR SUPLENTE"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][str(target)] = all_c[suplente_idx]['obj']; sync_to_cloud(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        cols = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            with cols[i % 3]:
                st.markdown(f"""<div style="background:white; border-radius:20px; padding:1rem; border:1px solid #f1f5f9; margin-bottom:1rem;">
                    <div style="background:#0f172a; color:white; padding:0.4rem; border-radius:10px; text-align:center; font-weight:800; font-size:0.8rem;">{g['name']}</div>""", unsafe_allow_html=True)
                for cadet in g['cadets']:
                    st.markdown(f"<div style='font-size:0.75rem; border-bottom:1px solid #f8fafc; padding:2px;'>• {cadet['nombre']}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "⚖️ Guardia Castigo":
        pk = str(st.date_input("Fecha", datetime.now().date()))
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_p = st.selectbox("Grupo", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
                c_p = st.selectbox("Cadete", range(len(st.session_state.groups[g_p]['cadets'])), format_func=lambda x: st.session_state.groups[g_p]['cadets'][x]['nombre'])
                if st.button("AGREGAR"):
                    if pk not in st.session_state.punishments: st.session_state.punishments[pk] = []
                    st.session_state.punishments[pk].append(st.session_state.groups[g_p]['cadets'][c_p]); sync_to_cloud(); st.rerun()
        with cb:
            st.write(f"**Refuerzos para {pk}**")
            for idx, p in enumerate(st.session_state.punishments.get(pk, [])):
                st.write(f"• {p['nombre']} ({p['curso']})")

    elif menu == "🔄 Cambios Autorizados":
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                swap_date = st.date_input("Fecha Servicio", datetime.now().date())
                all_list = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_list.append({"label": f"{c['nombre']} ({g['name']})", "obj": c, "oname": g['name']})
                sel_c = st.selectbox("Cadete", range(len(all_list)), format_func=lambda x: all_list[x]['label'])
                target_g = st.selectbox("Destino", [g['name'] for g in st.session_state.groups])
                if st.button("REGISTRAR CAMBIO"):
                    st.session_state.swaps.append({"date": str(swap_date), "cadet_id": all_list[sel_c]['obj']['nombre'], "cadet_obj": all_list[sel_c]['obj'], "orig_group": all_list[sel_c]['oname'], "target_group": target_g})
                    sync_to_cloud(); st.rerun()
        with cb:
            for idx, s in enumerate(st.session_state.swaps):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📅 {s['date']} | {s['cadet_id']} -> {s['target_group']}")
                if c2.button("🗑️", key=f"sw_{idx}"): st.session_state.swaps.pop(idx); sync_to_cloud(); st.rerun()

    elif menu == "👥 Redistribución":
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g['name']}"):
                df_ed = pd.DataFrame(g['cadets'])
                df_res = st.data_editor(df_ed, num_rows="dynamic", key=f"ed_{i}", use_container_width=True, height=(len(df_ed)+1)*35+10)
                if st.button(f"Guardar Cambios {g['id']}"):
                    st.session_state.groups[i]['cadets'] = df_res.to_dict('records'); sync_to_cloud(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Fecha Inicio Ciclo", st.session_state.start_date)
        if st.button("GUARDAR CONFIGURACIÓN"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Sincronizado")

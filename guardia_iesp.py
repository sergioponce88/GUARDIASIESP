import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
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
    return datetime.now() - timedelta(hours=3)

# --- CONSTANTES INSTITUCIONALES ---
ESCUDO_URL_ESTABLE = "https://upload.wikimedia.org/wikipedia/commons/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"
LOGO_LOCAL = "logo_iesp.png"

def get_logo_path():
    if os.path.exists(LOGO_LOCAL): return LOGO_LOCAL
    return ESCUDO_URL_ESTABLE

# --- DISEÑO UI PREMIUM ---
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
        .stExpander { border-radius: 15px !important; background-color: white !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- MOTOR DE SINCRONIZACIÓN ---
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
    st.session_state.data_timestamp = get_now_tucuman().strftime("%H:%M:%S")
    payload = {
        "groups": st.session_state.groups,
        "statuses": st.session_state.statuses,
        "overrides": st.session_state.overrides,
        "swaps": st.session_state.swaps,
        "role_overrides": st.session_state.role_overrides,
        "punishments": st.session_state.punishments,
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

# --- INICIALIZACIÓN DE ESTADO ---
if 'initialized' not in st.session_state:
    st.session_state.last_op_time = "Nunca"
    st.session_state.data_timestamp = "00:00:00"
    st.session_state.groups = DATOS_GRUPOS_BASE
    st.session_state.statuses = {}
    st.session_state.overrides = {}
    st.session_state.role_overrides = {}
    st.session_state.swaps = []
    st.session_state.punishments = {}
    st.session_state.start_date = datetime(2026, 3, 19).date()
    
    data_cloud = load_from_cloud()
    if data_cloud:
        st.session_state.update(data_cloud)
        if "start_date" in data_cloud:
            st.session_state.start_date = datetime.strptime(data_cloud.get("start_date"), "%Y-%m-%d").date()
    
    st.session_state.initialized = True

def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    processed = []
    
    day_st = st.session_state.statuses.get(date_key, {})
    day_ov = st.session_state.overrides.get(date_key, {})
    day_ro = st.session_state.role_overrides.get(date_key, {})
    swaps = st.session_state.swaps
    punishments = st.session_state.punishments.get(date_key, [])

    for c in base_group['cadets']:
        c_name = c.get('nombre', 'Sin Nombre').strip()
        # Verificar Intercambio (Saliente)
        if any(s for s in swaps if s['cadet_id'].strip() == c_name and s['date'] == date_key and s['orig_group'] == base_group['name']): continue
        
        cd = c.copy()
        cd['situacion'] = day_st.get(c_name, "PRESENTE")
        cd['funcion'] = day_ro.get(c_name, c.get('funcion'))
        
        # Verificar Suplencia
        if c_name in day_ov:
            cd['nombre'] = f"🔄 {day_ov[c_name]['nombre']}"
            cd['situacion'] = f"REEMPLAZO POR {c_name.upper()}"
        processed.append(cd)

    # Añadir Intercambios (Entrantes)
    for s in swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"INTERCAMBIO (DE {s['orig_group']})"
            processed.append(cad_swap)
            
    # Añadir Guardia Castigo (Refuerzos)
    for p in punishments:
        cad_p = p.copy()
        cad_p['nombre'] = f"⚖️ {cad_p['nombre']}"
        cad_p['situacion'] = "GUARDIA CASTIGO"
        processed.append(cad_p)
            
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- REPORTES PDF ---
def generate_pdf(start_date, end_date):
    pdf = FPDF()
    curr = start_date
    while curr <= end_date:
        pdf.add_page()
        try:
            img_data = requests.get(ESCUDO_URL_ESTABLE).content
            with open("temp_logo.png", "wb") as f: f.write(img_data)
            pdf.image("temp_logo.png", 10, 8, 25)
        except: pass
        pdf.set_y(15); pdf.set_font("helvetica", 'B', 16); pdf.cell(190, 8, "INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICIA", align='C', ln=True)
        pdf.set_font("helvetica", '', 11); pdf.cell(190, 6, f"DIAGRAMACIÓN DE GUARDIA - {curr.strftime('%d/%m/%Y')}", align='C', ln=True)
        g_data = get_processed_guard_for_date(curr)
        pdf.ln(10); pdf.set_font("helvetica", 'B', 12); pdf.cell(190, 10, f"GRUPO: {g_data['name']}", ln=True)
        pdf.set_fill_color(230, 230, 230); headers = ["N", "Apellido y Nombre", "Función", "Situación", "Firma"]
        cols = [10, 60, 40, 40, 40]
        for h, w in zip(headers, cols): pdf.cell(w, 10, h, 1, align='C', fill=True)
        pdf.ln(); pdf.set_font("helvetica", '', 9)
        for i, c in enumerate(g_data['cadets']):
            pdf.cell(cols[0], 8, str(i+1), 1, align='C')
            pdf.cell(cols[1], 8, c.get('nombre', 'N/A')[:35].encode('latin-1', 'replace').decode('latin-1'), 1)
            pdf.cell(cols[2], 8, c.get('funcion', 'N/A').encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[3], 8, c.get('situacion', 'PRESENTE')[:20].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[4], 8, "", 1, ln=True)
        curr += timedelta(days=1)
    return bytes(pdf.output())

# --- LOGIN ---
if not st.session_state.get('logged_in', False):
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.image(get_logo_path(), width=150)
        st.markdown("<h2 style='text-align:center;'>CONTROL IESP 2026</h2>", unsafe_allow_html=True)
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("INGRESAR AL SISTEMA"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
else:
    # --- SIDEBAR MAESTRO ---
    with st.sidebar:
        st.image(get_logo_path(), width=100)
        st.markdown(f"### 🛡️ IESP PRO")
        st.info(f"🕒 **Sello de Datos:** `{st.session_state.get('data_timestamp', '00:00:00')}`\n\n*(PC)*")
        st.success(f"☁️ **Sinc:** `{st.session_state.get('last_op_time', 'Nunca')}`")
        st.divider()
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Intercambio", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        st.divider()
        if st.button("💾 GUARDAR EN PC"): sync_to_cloud()
        if st.button("🔄 ACTUALIZAR CELULAR"):
            data = load_from_cloud()
            if data:
                st.session_state.update(data)
                if "start_date" in data:
                    st.session_state.start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
                st.session_state.last_op_time = get_now_tucuman().strftime("%H:%M:%S")
                st.success(f"¡Sincronizado! Sello: {data.get('data_timestamp')}"); st.rerun()
        if st.button("🚪 SALIR"): st.session_state.logged_in = False; st.rerun()

    c_logo, c_title = st.columns([1, 8])
    with c_logo: st.image(get_logo_path(), width=90)
    with c_title: st.markdown(f"<h1 style='color:#0f172a; font-weight:800;'>Diagramación IESP <span style='color:#ef4444'>PRO</span></h1>", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA SELECCIONADA", get_now_tucuman().date(), key="dash_date"); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><p>Guardia Hoy</p><h3>{gi['name']}</h3></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><p>Sello Datos</p><h3>{st.session_state.get('data_timestamp')}</h3></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><p>Novedades</p><h3>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'])}</h3></div>", unsafe_allow_html=True)
        
        st.divider()
        st.dataframe(pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])]), use_container_width=True, hide_index=True, height=(len(gi['cadets'])+1)*35+10)
        
        # --- COLUMNAS DE CONTROL (RESTAURADAS) ---
        st.markdown("### 🛠️ Herramientas de Mando")
        col_as, col_fu, col_su = st.columns(3)
        list_pure = [c['nombre'].replace("✅ ","").replace("⚠️ ","").replace("⚡ ","").replace("🔄 ","").replace("⚖️ ","").strip() for c in gi['cadets']]
        
        with col_as:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                cad_sel = st.selectbox("Personal", list_pure, key="as_sel")
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key="st_sel")
                if st.button("Guardar Estado"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][cad_sel] = nuevo_st
                    sync_to_cloud(); st.rerun()

        with col_fu:
            with st.container(border=True):
                st.write("**🎭 Función**")
                cad_sel_f = st.selectbox("Personal", list_pure, key="fu_sel")
                nueva_fu = st.text_input("Nueva Función", key="fu_val")
                if st.button("Asignar Función"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][cad_sel_f] = nueva_fu
                    sync_to_cloud(); st.rerun()

        with col_su:
            with st.container(border=True):
                st.write("**🔄 Suplencia**")
                titular = st.selectbox("Titular", list_pure, key="su_sel")
                all_opts = []
                for g in st.session_state.groups:
                    for c in g.get('cadets', []): all_opts.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
                idx_sup = st.selectbox("Suplente", range(len(all_opts)), format_func=lambda x: all_opts[x]['label'])
                if st.button("Aplicar Reemplazo"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][titular] = all_opts[idx_sup]['obj']
                    sync_to_cloud(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Nóminas Completas por Grupo")
        gi_today = get_processed_guard_for_date(get_now_tucuman().date())
        cols = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            is_on_duty = g['id'] == gi_today['id']
            with cols[i % 3]:
                header = f"🟢 {g['name']} (TURNO)" if is_on_duty else g['name']
                with st.expander(header, expanded=is_on_duty):
                    st.dataframe(pd.DataFrame(g['cadets'])[["nombre", "curso", "funcion"]], hide_index=True, use_container_width=True)

    elif menu == "⚖️ Guardia Castigo":
        pk_cast = str(st.date_input("Fecha Castigo", get_now_tucuman().date(), key="cast_d"))
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_idx = st.selectbox("Grupo Origen", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
                c_idx = st.selectbox("Cadete", range(len(st.session_state.groups[g_idx]['cadets'])), format_func=lambda x: st.session_state.groups[g_idx]['cadets'][x]['nombre'])
                if st.button("AGREGAR CASTIGO"):
                    if pk_cast not in st.session_state.punishments: st.session_state.punishments[pk_cast] = []
                    st.session_state.punishments[pk_cast].append(st.session_state.groups[g_idx]['cadets'][c_idx]); sync_to_cloud(); st.rerun()
        with cb:
            st.write(f"**Refuerzos para {pk_cast}**")
            if pk_cast in st.session_state.punishments:
                for idx_p, p_item in enumerate(st.session_state.punishments[pk_cast]):
                    c1, c2 = st.columns([4, 1]); c1.write(f"• {p_item['nombre']}"); 
                    if c2.button("🗑️", key=f"del_p_{idx_p}"): st.session_state.punishments[pk_cast].pop(idx_p); sync_to_cloud(); st.rerun()

    elif menu == "🔄 Intercambio":
        st.markdown("### 🔄 Terminal de Intercambio Bidireccional")
        sw_date = st.date_input("Fecha Servicio", get_now_tucuman().date())
        col_a, col_b = st.columns(2)
        with col_a:
            g_a = st.selectbox("Grupo A", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="ga")
            c_a = st.selectbox("Cadete A", range(len(st.session_state.groups[g_a]['cadets'])), format_func=lambda x: st.session_state.groups[g_a]['cadets'][x]['nombre'], key="ca")
        with col_b:
            g_b = st.selectbox("Grupo B", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="gb")
            c_b = st.selectbox("Cadete B", range(len(st.session_state.groups[g_b]['cadets'])), format_func=lambda x: st.session_state.groups[g_b]['cadets'][x]['nombre'], key="cb")
        if st.button("EJECUTAR INTERCAMBIO"):
            cad_a, cad_b = st.session_state.groups[g_a]['cadets'][c_a], st.session_state.groups[g_b]['cadets'][c_b]
            st.session_state.swaps.append({"date": str(sw_date), "cadet_id": cad_a['nombre'], "cadet_obj": cad_a, "orig_group": st.session_state.groups[g_a]['name'], "target_group": st.session_state.groups[g_b]['name']})
            st.session_state.swaps.append({"date": str(sw_date), "cadet_id": cad_b['nombre'], "cadet_obj": cad_b, "orig_group": st.session_state.groups[g_b]['name'], "target_group": st.session_state.groups[g_a]['name']})
            sync_to_cloud(); st.rerun()

    elif menu == "📂 Reportes PDF":
        s_rep = st.date_input("Desde", get_now_tucuman().date(), key="rs")
        e_rep = st.date_input("Hasta", get_now_tucuman().date(), key="re")
        if st.button("🚀 GENERAR PDF"):
            pdf_bytes = generate_pdf(s_rep, e_rep)
            st.download_button("⬇️ DESCARGAR", pdf_bytes, f"Guardias_{s_rep}.pdf", "application/pdf")

    elif menu == "👥 Redistribución":
        for i_red, g_red in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g_red['name']}"):
                df_res = st.data_editor(pd.DataFrame(g_red['cadets']), num_rows="dynamic", key=f"ed_{i_red}", use_container_width=True)
                if st.button(f"Guardar {g_red['id']}", key=f"bs_{i_red}"):
                    st.session_state.groups[i_red]['cadets'] = df_res.to_dict('records'); sync_to_cloud(); st.rerun()

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Inicio Ciclo", st.session_state.start_date)
        if st.button("GUARDAR"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Ajustado")

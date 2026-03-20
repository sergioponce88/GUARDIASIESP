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
LOGO_LOCAL = "logo_iesp.png"

# --- DISEÑO UI PREMIUM ---
def inject_modern_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main { background-color: #f8fafc; }
        [data-testid="stSidebar"] { 
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
        .metric-card { 
            background: white; padding: 1.5rem; border-radius: 25px; 
            border: 1px solid #f1f5f9; text-align: center; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
        }
        div.stButton > button {
            background: #ef4444 !important; color: white !important; border: none !important;
            padding: 0.7rem 1rem !important; font-weight: 700 !important; border-radius: 15px !important;
            width: 100% !important; text-transform: uppercase; letter-spacing: 0.5px;
        }
        [data-testid="stDataFrame"] > div { border: none !important; border-radius: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- MOTOR DE SINCRONIZACIÓN CLOUD (PERSISTENCIA REAL) ---
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
        # Bypass de caché dinámico para sincronización instantánea
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
        else: st.error(f"Error servidor: {res.status_code}. Verifique API KEY.")
    except: st.error("❌ Fallo crítico de red")

# --- NÓMINA INSTITUCIONAL COMPLETA (138 CADETES) ---
DATOS_GRUPOS_BASE = [
    {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete G1-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ibarra Martina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Issa Tiara", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Medina Emilse", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Coronel Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Cruz Braian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Fernández Adrián", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Figueroa Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "González Ignacio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "González Salomón Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Guevara Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Ibáñez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Jaime Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [{"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete G3-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(11)]},
    {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [{"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete G4-{i+1}", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
    {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Abregu Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Arganaraz Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Avila Jose", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Bazan Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Brandan Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Coronel Carlos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Diaz Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G6", "name": "GRUPO N° 2 de III° Año", "cadets": [{"n": 1, "nombre": "Carrillo Victoria", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete G6-{i+1}", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
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
        c_name = c['nombre'].strip()
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

# --- REPORTES PDF CON LOGO ---
def generate_pdf(start_date, end_date):
    pdf = FPDF()
    curr = start_date
    while curr <= end_date:
        pdf.add_page()
        try:
            if os.path.exists(LOGO_LOCAL): pdf.image(LOGO_LOCAL, 10, 8, 25)
            else: 
                img_data = requests.get(ESCUDO_URL).content
                with open("temp.png", "wb") as f: f.write(img_data)
                pdf.image("temp.png", 10, 8, 25)
        except: pass
        pdf.set_y(15); pdf.set_font("helvetica", 'B', 16); pdf.cell(190, 8, "INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICIA", align='C', ln=True)
        pdf.set_font("helvetica", '', 11); pdf.cell(190, 6, f"DIAGRAMACIÓN DE GUARDIA - {curr.strftime('%d/%m/%Y')}", align='C', ln=True)
        g_data = get_processed_guard_for_date(curr)
        pdf.ln(10); pdf.set_font("helvetica", 'B', 12); pdf.cell(190, 10, f"GRUPO: {g_data['name']}", ln=True)
        pdf.set_fill_color(230, 230, 230); headers = ["N", "Nombre y Apellido", "Funcion", "Situacion", "Firma"]
        cols = [10, 60, 40, 40, 40]
        for h, w in zip(headers, cols): pdf.cell(w, 10, h, 1, align='C', fill=True)
        pdf.ln(); pdf.set_font("helvetica", '', 9)
        for i, c in enumerate(g_data['cadets']):
            pdf.cell(cols[0], 8, str(i+1), 1, align='C')
            pdf.cell(cols[1], 8, c['nombre'][:35].encode('latin-1', 'replace').decode('latin-1'), 1)
            pdf.cell(cols[2], 8, c['funcion'].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[3], 8, c['situacion'][:20].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[4], 8, "", 1, ln=True)
        curr += timedelta(days=1)
    return bytes(pdf.output())

# --- INTERFAZ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        st.image(ESCUDO_URL, width=150)
        st.markdown("<h2 style='text-align:center;'>ACCESO GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("INGRESAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Denegado")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        st.image(ESCUDO_URL, width=120)
        st.markdown(f"**SISTEMA OFICIAL 2026**")
        if BASE_URL: st.success(f"☁️ Cloud Sinc\n{st.session_state.last_sync}")
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
                st.success("¡Sincronizado!"); st.rerun()
        if st.button("🚪 SALIR"): st.session_state.logged_in = False; st.rerun()

    header_col1, header_col2 = st.columns([1, 8])
    with header_col1: st.image(ESCUDO_URL, width=80)
    with header_col2: st.markdown("""<h1 style="color:#0f172a; font-weight:800; margin:0; padding-top:10px;">Diagramación de Guardia Sincronizada</h1>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA", datetime.now().date(), key="dash_date"); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><b>Guardia Hoy</b><br>{gi['name']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><b>Efectivos</b><br>{len(gi['cadets'])}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><b>Novedades</b><br>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'])}</div>", unsafe_allow_html=True)
        
        df_dash = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_dash, use_container_width=True, hide_index=True, height=(len(df_dash)+1)*35+10)
        
        # --- FORMULARIOS DASHBOARD ---
        col1, col2, col3 = st.columns(3)
        list_pure = [c['nombre'].replace("🔄 ","").replace("✅ ","").replace("⚠️ ","").replace("⚡ ","").strip() for c in gi['cadets']]
        
        with col1:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                cad_sel = st.selectbox("Personal", list_pure, key="as_sel")
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key="st_sel")
                if st.button("Guardar Estado"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][cad_sel] = nuevo_st
                    sync_to_cloud(); st.rerun()
        with col2:
            with st.container(border=True):
                st.write("**🎭 Función**")
                cad_sel_f = st.selectbox("Personal", list_pure, key="fu_sel")
                nueva_fu = st.text_input("Nueva Función", key="fu_val")
                if st.button("Asignar Función"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][cad_sel_f] = nueva_fu
                    sync_to_cloud(); st.rerun()
        with col3:
            with st.container(border=True):
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

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Nóminas Completas del Personal")
        cols_all = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            with cols_all[i % 3]:
                with st.container(border=True):
                    st.markdown(f"#### {g['name']}")
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
                target_g = st.selectbox("Guardia Destino", [g['name'] for g in st.session_state.groups])
                if st.button("REGISTRAR"):
                    st.session_state.swaps.append({"date": str(sw_date), "cadet_id": all_l[sel_c]['obj']['nombre'], "cadet_obj": all_l[sel_c]['obj'], "orig_group": all_l[sel_c]['oname'], "target_group": target_g})
                    sync_to_cloud(); st.rerun()
        with cb:
            for idx, s in enumerate(st.session_state.swaps):
                st.write(f"📅 {s['date']} | {s['cadet_id']} -> {s['target_group']}")
                if st.button("🗑️", key=f"sw_{idx}"): st.session_state.swaps.pop(idx); sync_to_cloud(); st.rerun()

    elif menu == "📂 Reportes PDF":
        s_rep = st.date_input("Desde", datetime.now().date(), key="rep_s")
        e_rep = st.date_input("Hasta", datetime.now().date(), key="rep_e")
        if st.button("🚀 GENERAR PDF"):
            pdf_bytes = generate_pdf(s_rep, e_rep)
            st.download_button("⬇️ DESCARGAR PLANILLAS", pdf_bytes, f"Guardias_{s_rep}.pdf", "application/pdf")

    elif menu == "👥 Redistribución":
        for i_red, g_red in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g_red['name']}"):
                df_red = pd.DataFrame(g_red['cadets'])
                df_res = st.data_editor(df_red, num_rows="dynamic", key=f"ed_{i_red}", use_container_width=True)
                if st.button(f"Guardar Cambios permanentemente en {g_red['id']}", key=f"btn_red_save_{i_red}"):
                    st.session_state.groups[i_red]['cadets'] = df_res.to_dict('records'); sync_to_cloud(); st.rerun()

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Inicio de Ciclo Operativo", st.session_state.start_date)
        if st.button("GUARDAR CONFIGURACIÓN"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Ajustado")

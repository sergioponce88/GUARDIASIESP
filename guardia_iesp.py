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
ESCUDO_RESPALDO = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png/250px-Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"

# --- ESTILO CSS PROFESIONAL ---
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
        }}
        .header-title {{ color: #0f172a; font-weight: 800; font-size: 1.4rem; margin: 0; }}
        div.stButton > button {{
            background: #ef4444 !important; color: white !important; border: none !important;
            padding: 0.8rem 1.5rem !important; font-weight: 700 !important; border-radius: 15px !important;
            width: 100% !important; text-transform: uppercase;
        }}
        .metric-card {{ background: white; padding: 1.2rem; border-radius: 22px; border: 1px solid #f1f5f9; text-align: center; }}
        .alert-banner {{
            background: #fef2f2; border: 1px solid #fee2e2; padding: 1rem; border-radius: 20px;
            color: #991b1b; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #ef4444;
        }}
        [data-testid="stDataFrame"] > div {{ border: none !important; }}
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- LÓGICA DE SINCRONIZACIÓN CLOUD ---
def get_cloud_params():
    try:
        conf = json.loads(st.secrets["__firebase_config"])
        return conf.get("projectId"), st.secrets.get("__app_id", "iesp-v2026-v2")
    except: return None, "iesp-v2026"

PROJECT_ID, APP_ID = get_cloud_params()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_cloud_data():
    if not BASE_URL: return None
    try:
        resp = requests.get(f"{BASE_URL}/persistence/current_state", timeout=8)
        if resp.status_code == 200:
            return json.loads(resp.json().get("fields", {}).get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def sync_to_cloud():
    if not BASE_URL: return
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
        requests.patch(f"{BASE_URL}/persistence/current_state", json=body, timeout=8)
        st.toast("✅ Sincronizado con la nube", icon="☁️")
    except: st.error("❌ Error de conexión al guardar")

# --- NÓMINA INSTITUCIONAL INTEGRAL ---
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

    # 1. Procesar integrantes originales
    for i, c in enumerate(base_group['cadets']):
        # Si hoy salió por Cambio Autorizado, no se muestra
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

    # 2. Agregar integrantes que vienen de otro grupo por Cambio Autorizado
    for s in swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"CAMBIO AUTORIZADO (DE {s['orig_group']})"
            processed.append(cad_swap)
            
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- PDF ---
def generate_official_pdf(start_date, end_date):
    pdf = FPDF()
    curr = start_date
    while curr <= end_date:
        pdf.add_page()
        try: pdf.image(LOGO_FILE, 10, 8, 25)
        except: pass
        pdf.set_y(15); pdf.set_font("helvetica", 'B', 16)
        pdf.cell(190, 8, "INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICIA", align='C', ln=True)
        pdf.set_font("helvetica", '', 11)
        pdf.cell(190, 6, f"GUARDIA DE PREVENCION - FECHA: {curr.strftime('%d/%m/%Y')}", align='C', ln=True)
        g_data = get_processed_guard_for_date(curr)
        pdf.ln(10); pdf.set_font("helvetica", 'B', 12)
        pdf.cell(190, 10, f"GRUPO EN SERVICIO: {g_data['name']}", ln=True)
        pdf.set_fill_color(230, 230, 230); pdf.set_font("helvetica", 'B', 10)
        headers = ["N", "Apellido y Nombre", "Curso", "Funcion", "Situacion", "Firma"]
        cols = [10, 55, 25, 40, 30, 30]
        for h, w in zip(headers, cols): pdf.cell(w, 10, h, 1, align='C', fill=True)
        pdf.ln()
        pdf.set_font("helvetica", '', 9)
        for i, c in enumerate(g_data['cadets']):
            pdf.cell(cols[0], 8, str(i+1), 1, align='C')
            pdf.cell(cols[1], 8, c['nombre'][:35].encode('latin-1', 'replace').decode('latin-1'), 1, align='L')
            pdf.cell(cols[2], 8, c['curso'], 1, align='C')
            pdf.cell(cols[3], 8, c['funcion'].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[4], 8, c['situacion'][:20].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[5], 8, "", 1, ln=True)
        curr += timedelta(days=1)
    return bytes(pdf.output())

# --- INTERFAZ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        st.image(ESCUDO_RESPALDO, width=150)
        st.markdown("<h2 style='text-align:center;'>CONTROL DE GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE ACCESO", type="password", key="login_pwd")
        if st.button("INGRESAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Acceso Denegado")
else:
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=120)
        else: st.image(ESCUDO_RESPALDO, width=100)
        st.markdown("<h3 style='color:white; text-align:center; font-size:0.8rem;'>IESP SISTEMA 2026</h3>", unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Cambios Autorizados", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        if st.button("🔄 RECARGAR NUBE", key="sync_btn"):
            cloud = load_cloud_data()
            if cloud: st.session_state.update(cloud); st.rerun()
        if st.button("CERRAR SESIÓN", key="logout_btn"): st.session_state.logged_in = False; st.rerun()

    st.markdown(f"""<div class="header-container"><img src="{ESCUDO_RESPALDO}" width="50"><h1 class="header-title">I.E.S.P. Diagramación de Guardia Sincronizada</h1></div>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        # Alertar cambios vencidos
        today_key = str(datetime.now().date())
        expired = [s for s in st.session_state.swaps if s['date'] < today_key]
        for ex in expired:
            st.markdown(f"<div class='alert-banner'>⚠️ RESTAURACIÓN: El cambio de <b>{ex['cadet_id']}</b> caducó. Borrar de 'Cambios Autorizados' para normalizar su grupo.</div>", unsafe_allow_html=True)

        sel_date = st.date_input("FECHA", datetime.now().date(), key="dash_date"); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><b>Guardia en Turno</b><br>{gi['name']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><b>Suplentes Activos</b><br>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><b>Novedades Hoy</b><br>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'] and 'CAMBIO' not in c['situacion'])}</div>", unsafe_allow_html=True)
        
        df = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] or 'CAMBIO' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df, use_container_width=True, hide_index=True, height=(len(df)+1)*35+10, key="main_df")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                c_idx = st.selectbox("Seleccionar Cadete", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="sel_asist")
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key="sel_st")
                if st.button("GUARDAR ESTADO", key="btn_asist"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][str(c_idx)] = nuevo_st; sync_to_cloud(); st.rerun()
        with col2:
            with st.container(border=True):
                st.write("**🎭 Función**")
                c_idx_f = st.selectbox("Cadete", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="sel_func")
                n_f = st.text_input("Nueva Función", key="in_func")
                if st.button("ASIGNAR", key="btn_func"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][str(c_idx_f)] = n_f; sync_to_cloud(); st.rerun()
        with col3:
            with st.container(border=True):
                st.write("**🔄 Suplencia**")
                target = st.selectbox("Titular a Cubrir", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="sel_target")
                all_c = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_c.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
                suplente_idx = st.selectbox("Buscar Suplente", range(len(all_c)), format_func=lambda x: all_c[x]['label'], key="sel_sup")
                if st.button("APLICAR SUPLENTE", key="btn_sup"):
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
        pk = str(st.date_input("Fecha Castigo", datetime.now().date(), key="cast_date"))
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_p = st.selectbox("Grupo Origen", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="sel_g_cast")
                c_p = st.selectbox("Cadete", range(len(st.session_state.groups[g_p]['cadets'])), format_func=lambda x: st.session_state.groups[g_p]['cadets'][x]['nombre'], key="sel_c_cast")
                if st.button("AGREGAR REFUERZO", key="btn_cast"):
                    if pk not in st.session_state.punishments: st.session_state.punishments[pk] = []
                    st.session_state.punishments[pk].append(st.session_state.groups[g_p]['cadets'][c_p]); sync_to_cloud(); st.rerun()
        with cb:
            st.write(f"**Refuerzos para el {pk}**")
            if pk in st.session_state.punishments:
                for idx, p in enumerate(st.session_state.punishments[pk]):
                    st.write(f"• {p['nombre']} ({p['curso']})")

    elif menu == "🔄 Cambios Autorizados":
        st.info("Registre aquí permisos para que un cadete cumpla servicio con otro grupo en una fecha específica.")
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                swap_date = st.date_input("Fecha de Servicio", datetime.now().date(), key="swap_date")
                all_list = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_list.append({"label": f"{c['nombre']} (Orig: {g['name']})", "obj": c, "oname": g['name']})
                sel_c = st.selectbox("Cadete Autorizado", range(len(all_list)), format_func=lambda x: all_list[x]['label'], key="sel_c_swap")
                target_g = st.selectbox("Guardia de Destino", [g['name'] for g in st.session_state.groups], key="sel_g_swap")
                if st.button("REGISTRAR CAMBIO", key="btn_swap"):
                    st.session_state.swaps.append({"date": str(swap_date), "cadet_id": all_list[sel_c]['obj']['nombre'], "cadet_obj": all_list[sel_c]['obj'], "orig_group": all_list[sel_c]['oname'], "target_group": target_g})
                    sync_to_cloud(); st.rerun()
        with cb:
            st.write("**Listado de Permisos Activos**")
            for idx, s in enumerate(st.session_state.swaps):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📅 {s['date']} | {s['cadet_id']} -> {s['target_group']}")
                if c2.button("🗑️", key=f"sw_{idx}"): st.session_state.swaps.pop(idx); sync_to_cloud(); st.rerun()

    elif menu == "📂 Reportes PDF":
        s_r = st.date_input("Inicio", datetime.now().date()); e_r = st.date_input("Fin", datetime.now().date())
        if st.button("GENERAR LOTE PDF"):
            pdf_b = generate_official_pdf(s_r, e_r)
            st.download_button("⬇️ DESCARGAR", pdf_b, f"Diagramacion_{s_r}.pdf", "application/pdf")

    elif menu == "👥 Redistribución":
        st.warning("Use esta sección para corregir nombres o funciones permanentemente.")
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g['name']}"):
                df_ed = pd.DataFrame(g['cadets'])
                df_res = st.data_editor(df_ed, num_rows="dynamic", key=f"ed_{i}", use_container_width=True, height=(len(df_ed)+1)*35+10)
                if st.button(f"Guardar {g['id']}", key=f"btn_save_ed_{i}"):
                    st.session_state.groups[i]['cadets'] = df_res.to_dict('records'); sync_to_cloud(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Fecha Inicio Ciclo (Grupo 1)", st.session_state.start_date, key="aj_date")
        if st.button("RECALIBRAR SISTEMA", key="btn_aj"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Ciclo sincronizado")

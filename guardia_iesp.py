import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import os
import requests
import time
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IESP - MANDO PRO",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- AJUSTE DE HORA ARGENTINA (UTC-3) ---
def get_now_tucuman():
    try:
        return datetime.now() - timedelta(hours=3)
    except:
        return datetime.now()

# --- DISEÑO UI PREMIUM (CSS) ---
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
        [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
        
        .metric-card { 
            background: white; padding: 1.5rem; border-radius: 24px; 
            border: 1px solid #e2e8f0; text-align: center; 
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); 
            transition: all 0.3s ease;
        }
        .metric-card h3 { color: #0f172a; font-weight: 800; font-size: 1.3rem; margin: 0; }
        .metric-card p { color: #64748b; font-weight: 700; text-transform: uppercase; font-size: 0.7rem; }

        div.stButton > button { 
            background: #ef4444 !important; color: white !important; 
            font-weight: 700 !important; border-radius: 16px !important; 
            width: 100% !important; text-transform: uppercase; 
            letter-spacing: 1px; border: none !important;
            box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2);
        }
        
        .logo-box {
            background: #ef4444; color: white; padding: 15px;
            border-radius: 15px; text-align: center; font-weight: 800;
            margin-bottom: 20px; border: 2px solid rgba(255,255,255,0.2);
        }

        .guard-header {
            background-color: #0f172a; padding: 15px 25px; border-radius: 20px; 
            margin-bottom: 20px; border-left: 8px solid #ef4444;
        }
        .guard-header h3 { color: white; margin: 0; font-size: 1.1rem; font-weight: 800; text-transform: uppercase; }
        
        .whatsapp-btn {
            background-color: #25d366 !important;
            border-color: #128c7e !important;
        }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- MOTOR DE SINCRONIZACIÓN ---
def get_config():
    try:
        if "__firebase_config" in st.secrets:
            c = json.loads(st.secrets["__firebase_config"])
            return c["projectId"].strip(), "iesp-v2026-final-oficial", c["apiKey"].strip()
    except: pass
    return None, None, None

PID, AID, KEY = get_config()
URL_BASE = f"https://firestore.googleapis.com/v1/projects/{PID}/databases/(default)/documents/artifacts/{AID}/public/data/persistence/current_state?key={KEY}" if PID else None

def load_cloud_data():
    if not URL_BASE: return None
    try:
        token = str(int(time.time() * 1000))
        headers = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
        r = requests.get(f"{URL_BASE}&t={token}", headers=headers, timeout=10)
        if r.status_code == 200:
            fields = r.json().get("fields", {})
            return json.loads(fields.get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def save_cloud_data():
    if not URL_BASE: return False
    st.session_state.data_timestamp = get_now_tucuman().strftime("%H:%M:%S")
    payload = {
        "groups": st.session_state.groups,
        "statuses": st.session_state.statuses,
        "overrides": st.session_state.overrides,
        "role_overrides": st.session_state.role_overrides,
        "swaps": st.session_state.swaps,
        "punishments": st.session_state.punishments,
        "extra_cadets": st.session_state.extra_cadets,
        "removals": st.session_state.removals,
        "start_date": str(st.session_state.start_date),
        "data_timestamp": st.session_state.data_timestamp
    }
    try:
        body = {"fields": {"json_data": {"stringValue": json.dumps(payload)}}}
        r = requests.patch(URL_BASE, json=body, timeout=12)
        return r.status_code == 200
    except: pass
    return False

# --- NÓMINA OFICIAL TOTAL (DOCX) ---
def get_official_groups():
    return [
        {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Abregú Francisco", "Acosta Marcos", "Agüero Alexis", "Albarracín Federico", "Albornoz Lautaro", "Aranda Héctor", "Bazán Hernán", "Brizuela Miguel", "Bustamante Marcelo", "Cantos Núñez Javier", "Castro Miguel", "Cequeira Marcos"])]},
        {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Ibarra Martina", "Issa Tiara", "Medina Emilse", "Coronel Luis", "Cruz Braian", "Fernández Adrián", "Figueroa Franco", "González Ignacio", "González Salomón Gonzalo", "Guevara Marcos", "Ibáñez Lucas", "Jaime Christian"])]},
        {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [{"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Jiménez Gonzalo", "Juárez Santiago", "Lagarde Christian", "Lazarte José", "Maldonado Clemente", "Medina Lucas", "Medina Vélez Lucas", "Medrano Ángel", "Mena Aníbal", "Monteros Mateo", "Montes Nahuel"])]},
        {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [{"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Monteros Brenda", "Montes Eugenia", "Núñez Luciano", "Paliza Joaquín", "Ponze de León Lucas", "Quiroga López Luis", "Reyes Franco", "Reyes Alan", "Reynoso Martínez Luciano", "Roja Tomás", "Silva Axel", "Sueldo Rodrigo Gastón", "Soria José Lionel"])]},
        {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juárez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Bareiro Blanca", "Etchenique Shamira", "Abregú Franco", "Aguirre Santiago", "Arias Ramiro", "Argañaraz Lezcano Roberto", "Ávila José", "Bazán Luis", "Brandan Cristian", "Coronel Carlos", "Diaz Santiago"])]},
        {"id": "G6", "name": "GRUPO N° 2 de III° Año", "cadets": [{"n": 1, "nombre": "Carrillo Victoria", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Salas Murua", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Ocaranza Sofia", "Paz María", "Carrizo Cristian", "Chávez Máximo", "Del Lugo Franco", "Del Lugo Guillermo", "Dib Jorge", "Fernández Ariel", "Frías Ariel", "Gerez Víctor", "Girvau Mauricio", "Gómez Enrique"])]},
        {"id": "G7", "name": "GRUPO N° 3 de III° Año", "cadets": [{"n": 1, "nombre": "Alvarado Mauricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Valdez Federico", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Gómez Ramirez Marcos", "Guardia Cesar", "Iramain Guillermo", "Juárez Tomás", "Las Heras Cabocota Santiago", "Lazarte Cristian", "Luna Jorge", "Medina Nicolás", "Miro Gastón", "Nieva Juan", "Páez Fernández Manuel"])]},
        {"id": "G8", "name": "GRUPO N° 4 de III° Año", "cadets": [{"n": 1, "nombre": "Suárez Franco", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Alabarce Sergio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Salas Josefina", "Quinteros Flabia", "Palomar Esteban", "Ramos Tobías", "Rodríguez Matías", "Rojas Leonel", "Ruiz Felipe", "Ruiz Elio", "Ruiz Fabricio", "Ruiz Lozano Emanuel", "Soria Lucas"])]},
        {"id": "G9", "name": "GRUPO N° 5 de III° Año", "cadets": [{"n": 1, "nombre": "Aybar Eduardo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Quiroga Melina", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Montero Irina", "Moreno Karen", "Sotelo Leandro", "Sotelo Santiago", "Verón González", "Villagra Lucas", "Villalba David", "Vizcarra José", "Ybarra Franco", "Zamorano Sergio", "Zarate Medina Lucas"])]}
    ]

# --- INICIALIZACIÓN ---
if 'initialized' not in st.session_state:
    st.session_state.data_timestamp = "00:00:00"
    st.session_state.last_sync_status = "Iniciando..."
    st.session_state.groups = get_official_groups()
    st.session_state.statuses, st.session_state.overrides = {}, {}
    st.session_state.role_overrides, st.session_state.swaps, st.session_state.punishments = {}, [], {}
    st.session_state.extra_cadets, st.session_state.removals = {}, {}
    st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.logged_in = False
    
    data = load_cloud_data()
    if data:
        for k, v in data.items():
            if k == "start_date": st.session_state[k] = datetime.strptime(v, "%Y-%m-%d").date()
            else: st.session_state[k] = v
    st.session_state.initialized = True

def get_processed_guard_for_date(date):
    try:
        diff = (date - st.session_state.start_date).days
        idx = diff % len(st.session_state.groups)
        base_group = st.session_state.groups[idx]
        date_key = str(date)
        processed = []
        
        day_st = st.session_state.get('statuses', {}).get(date_key, {})
        day_ov = st.session_state.get('overrides', {}).get(date_key, {})
        day_ro = st.session_state.get('role_overrides', {}).get(date_key, {})
        punishments = st.session_state.get('punishments', {}).get(date_key, [])
        extras = st.session_state.get('extra_cadets', {}).get(date_key, [])
        day_removals = st.session_state.get('removals', {}).get(date_key, [])

        for c in base_group['cadets']:
            c_name = str(c.get('nombre', '')).strip()
            if c_name in day_removals: continue
            if any(s for s in st.session_state.swaps if str(s.get('cadet_id','')).strip() == c_name and s['date'] == date_key and s['orig_group'] == base_group['name']): continue
            
            cd = c.copy()
            cd['situacion'] = str(day_st.get(c_name, "PRESENTE"))
            cd['funcion'] = str(day_ro.get(c_name, c.get('funcion', '-')))
            if c_name in day_ov:
                cd['nombre'] = f"🔄 {str(day_ov[c_name].get('nombre', 'S/N'))}"
                cd['situacion'] = "REEMPLAZO"
            processed.append(cd)

        for s in st.session_state.swaps:
            if s['date'] == date_key and s['target_group'] == base_group['name']:
                cad_swap = s['cadet_obj'].copy()
                cad_swap['nombre'] = f"⚡ {str(cad_swap.get('nombre', 'S/N'))}"; cad_swap['situacion'] = f"INTERCAMBIO"; processed.append(cad_swap)
                
        for p in punishments:
            cad_p = p.copy()
            cad_p['nombre'] = f"⚖️ {str(cad_p.get('nombre', 'S/N'))}"; cad_p['situacion'] = "GUARDIA CASTIGO"; processed.append(cad_p)

        for e in extras:
            cad_e = e.copy()
            cad_e['nombre'] = f"➕ {str(cad_e.get('nombre', 'S/N'))}"; cad_e['situacion'] = "REFUERZO"; processed.append(cad_e)
                
        return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}
    except: return {"name": "Error de Datos", "cadets": [], "id": "ERR"}

# --- GENERADOR DE PDF BLINDADO ---
def generate_pdf(start_date, end_date):
    try:
        pdf = FPDF()
        curr = start_date
        while curr <= end_date:
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(190, 10, "INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICIA", 0, 1, 'C')
            pdf.set_font("Helvetica", '', 10)
            pdf.cell(190, 6, f"DIAGRAMACION OPERATIVA DE GUARDIA - FECHA: {curr.strftime('%d/%m/%Y')}", 0, 1, 'C')
            g_data = get_processed_guard_for_date(curr)
            pdf.ln(5); pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(190, 10, f"SERVICIO EN TURNO: {g_data['name']}", 0, 1, 'L')
            pdf.set_fill_color(230, 230, 230); pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(10, 8, "N", 1, 0, 'C', True); pdf.cell(85, 8, "Apellido y Nombre", 1, 0, 'C', True)
            pdf.cell(35, 8, "Funcion", 1, 0, 'C', True); pdf.cell(30, 8, "Situacion", 1, 0, 'C', True)
            pdf.cell(30, 8, "Firma", 1, 1, 'C', True); pdf.set_font("Helvetica", '', 8)
            for i, c in enumerate(g_data['cadets']):
                pdf.cell(10, 7, str(i+1), 1, 0, 'C')
                pdf.cell(85, 7, str(c.get('nombre', '-')).encode('latin-1', 'replace').decode('latin-1'), 1, 0, 'L')
                pdf.cell(35, 7, str(c.get('funcion', '-')).encode('latin-1', 'replace').decode('latin-1'), 1, 0, 'C')
                pdf.cell(30, 7, str(c.get('situacion', '-')).encode('latin-1', 'replace').decode('latin-1'), 1, 0, 'C')
                pdf.cell(30, 7, "", 1, 1)
            curr += timedelta(days=1)
        return bytes(pdf.output())
    except Exception as e: return f"Error PDF: {str(e)}".encode()

# --- INTERFAZ ---
if not st.session_state.get('logged_in', False):
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.markdown("<div style='text-align:center; font-size:80px;'>🛡️</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#0f172a;'>MANDO IESP 2026</h2>", unsafe_allow_html=True)
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("ENTRAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
else:
    all_cadets_registry = []
    for g in st.session_state.groups:
        for c in g['cadets']: all_cadets_registry.append({"nombre": str(c.get('nombre', 'S/N')), "grupo": g['name'], "curso": c.get('curso', '-'), "obj": c})

    with st.sidebar:
        st.markdown("<div class='logo-box'>CONTROL DE GUARDIA PRO</div>", unsafe_allow_html=True)
        st.info(f"🕒 **Sello Nube:**\n`{st.session_state.get('data_timestamp', '00:00:00')}`")
        st.success(f"☁️ **Estado:**\n`{st.session_state.get('last_sync_status', 'Conectado')}`")
        st.divider()
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Intercambio", "📊 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        st.divider()
        if st.button("💾 SUBIR CAMBIOS (PC)"): 
            if save_cloud_data(): st.rerun()
        if st.button("🔄 ACTUALIZAR (CELULAR)"):
            data = load_cloud_data()
            if data:
                for k, v in data.items():
                    if k == "start_date": st.session_state[k] = datetime.strptime(v, "%Y-%m-%d").date()
                    else: st.session_state[k] = v
                st.session_state.last_sync_status = f"✅ Actualizado {get_now_tucuman().strftime('%H:%M:%S')}"
                st.rerun()
        if st.button("🚪 SALIR"): st.session_state.logged_in = False; st.rerun()

    st.markdown(f"<h1 style='color:#0f172a; font-weight:800; margin-top:10px;'>Operativo IESP <span style='color:#ef4444'>PRO</span></h1>", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA", get_now_tucuman().date(), key="dash_date")
        date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><p>Turno</p><h3>{gi['name']}</h3></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><p>Total Efectivos</p><h3>{len(gi['cadets'])}</h3></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><p>Sello Nube</p><h3>{st.session_state.get('data_timestamp','00:00:00')}</h3></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='guard-header'><h3>📋 Nómina: {gi['name']}</h3></div>", unsafe_allow_html=True)
        df_v = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in str(c.get('situacion','')) else '⚠️'} {str(c.get('nombre',''))}", "Función": str(c.get('funcion','')), "Estado": str(c.get('situacion',''))} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_v, use_container_width=True, hide_index=True, height=400)
        st.markdown("### 🛠️ Mando Directo")
        ca, cf, cs, cx, cr = st.columns(5)
        list_pure = [str(c.get('nombre','')).replace("✅ ","").replace("⚠️ ","").replace("⚡ ","").replace("🔄 ","").replace("⚖️ ","").replace("➕ ","").strip() for c in gi['cadets']]
        with ca:
            with st.container(border=True):
                st.write("**Asistencia**")
                c_as = st.selectbox("Efectivo", list_pure, key="as_s")
                n_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"])
                if st.button("Fijar"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][c_as] = n_st; save_cloud_data(); st.rerun()
        with cf:
            with st.container(border=True):
                st.write("**Función**")
                c_fu = st.selectbox("Efectivo", list_pure, key="fu_s")
                n_fu = st.text_input("Rol", placeholder="Ej: Centinela")
                if st.button("Asignar"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][c_fu] = n_fu; save_cloud_data(); st.rerun()
        with cs:
            with st.container(border=True):
                st.write("**Suplencia**")
                tit = st.selectbox("Titular", list_pure, key="su_s")
                idx_sup = st.selectbox("Suplente", range(len(all_cadets_registry)), format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="su_all")
                if st.button("Cambiar"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][tit] = all_cadets_registry[idx_sup]['obj']; save_cloud_data(); st.rerun()
        with cx:
            with st.container(border=True):
                st.write("**Refuerzo**")
                idx_ex = st.selectbox("Sumar", range(len(all_cadets_registry)), format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="ex_all")
                ex_rol = st.text_input("Cargo", value="Refuerzo")
                if st.button("Añadir"):
                    if date_key not in st.session_state.extra_cadets: st.session_state.extra_cadets[date_key] = []
                    new_ex = all_cadets_registry[idx_ex]['obj'].copy(); new_ex['funcion'] = ex_rol
                    st.session_state.extra_cadets[date_key].append(new_ex); save_cloud_data(); st.rerun()
        with cr:
            with st.container(border=True):
                st.write("**Baja**")
                c_rem = st.selectbox("Quitar", list_pure, key="rem_s")
                if st.button("Remover"):
                    if date_key not in st.session_state.removals: st.session_state.removals[date_key] = []
                    st.session_state.removals[date_key].append(c_rem); save_cloud_data(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        if st.button("⚠️ RESTABLECER LISTA DEL WORD", type="secondary", use_container_width=True):
            st.session_state.groups = get_official_groups(); save_cloud_data(); st.rerun()
        cols = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            with cols[i % 3]:
                with st.expander(f"📦 {g['name']}", expanded=True): st.table(pd.DataFrame(g['cadets'])[["nombre", "curso", "funcion"]])

    elif menu == "⚖️ Guardia Castigo":
        pk_cast = str(st.date_input("FECHA CASTIGO", get_now_tucuman().date()))
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                idx_p = st.selectbox("Sancionado", range(len(all_cadets_registry)), format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})")
                r_p = st.selectbox("Rol", ["Cadete Apostado", "Jefe de Guardia", "Cabo de Cuarto"])
                if st.button("AGREGAR AL SERVICIO"):
                    if pk_cast not in st.session_state.punishments: st.session_state.punishments[pk_cast] = []
                    np = all_cadets_registry[idx_p]['obj'].copy(); np['funcion'] = r_p
                    st.session_state.punishments[pk_cast].append(np); save_cloud_data(); st.rerun()
        with c2:
            if pk_cast in st.session_state.punishments:
                for idx_d, p in enumerate(st.session_state.punishments[pk_cast]): 
                    col_p1, col_p2 = st.columns([4, 1])
                    col_p1.write(f"❌ {str(p.get('nombre',''))} - {str(p.get('funcion',''))}")
                    if col_p2.button("🗑️", key=f"dcast_{idx_d}"): st.session_state.punishments[pk_cast].pop(idx_d); save_cloud_data(); st.rerun()

    elif menu == "📊 Reportes PDF":
        st.markdown("### 📊 Generador de Diagramaciones Oficiales")
        col1, col2 = st.columns(2)
        s_rep = col1.date_input("Desde", get_now_tucuman().date())
        e_rep = col2.date_input("Hasta", get_now_tucuman().date())
        pdf_bytes = generate_pdf(s_rep, e_rep)
        
        st.download_button("⬇️ DESCARGAR REPORTE PDF (OFICIAL)", data=pdf_bytes, file_name=f"Diagramacion_IESP_{s_rep}.pdf", mime="application/pdf", use_container_width=True)
        
        st.divider()
        st.markdown("### 📱 Enviar Parte Digital por WhatsApp")
        st.info("Este botón genera un mensaje con la nómina y funciones detalladas para compartir por WhatsApp.")
        msg_date = st.date_input("Fecha para Compartir", get_now_tucuman().date(), key="wa_d")
        gi_wa = get_processed_guard_for_date(msg_date)
        
        # Construcción del reporte digital (Nómina + Función)
        roster_text = "\n".join([f"• {str(c.get('nombre',''))} - *{str(c.get('funcion',''))}*" for c in gi_wa['cadets']])
        wa_text = f"*PARTE OFICIAL DE GUARDIA IESP*\n📅 *Fecha:* {msg_date}\n🛡️ *Servicio:* {gi_wa['name']}\n👥 *Efectivos:* {len(gi_wa['cadets'])}\n\n*NÓMINA DE PERSONAL:*\n{roster_text}\n\n*Nota:* El PDF oficial se adjunta por separado."
        
        wa_encoded = urllib.parse.quote(wa_text)
        st.link_button("📤 COMPARTIR NÓMINA POR WHATSAPP", f"https://wa.me/?text={wa_encoded}", use_container_width=True)

    elif menu == "👥 Redistribución":
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"📦 {g['name']}"):
                with st.popover("➕ Alta de Efectivo"):
                    n_n = st.text_input("Nombre", key=f"nn_{i}")
                    n_c = st.selectbox("Curso", ["IIº Año", "IIIº Año"], key=f"nc_{i}")
                    n_r = st.text_input("Función", value="Cadete Apostado", key=f"nr_{i}")
                    if st.button("Confirmar Alta", key=f"nb_{i}"):
                        st.session_state.groups[i]['cadets'].append({"n": len(g['cadets'])+1, "nombre": str(n_n), "curso": str(n_c), "funcion": str(n_r)}); save_cloud_data(); st.rerun()
                df_t = pd.DataFrame(g['cadets'])
                res = st.data_editor(df_t, num_rows="dynamic", key=f"ed_{i}", use_container_width=True)
                if st.button(f"Confirmar {g['id']}", key=f"bs_{i}"):
                    ul = res.to_dict('records')
                    for idx, c in enumerate(ul): c['n'] = idx + 1
                    st.session_state.groups[i]['cadets'] = ul; save_cloud_data(); st.rerun()

    elif menu == "⚙️ Ajustes":
        st.session_state.start_date = st.date_input("Inicio de Ciclo", st.session_state.start_date)
        if st.button("GUARDAR"): save_cloud_data(); st.success("Ajustado")

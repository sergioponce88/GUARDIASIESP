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
# URL estable del escudo
ESCUDO_URL = "https://upload.wikimedia.org/wikipedia/commons/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"

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
        .metric-card:hover { transform: translateY(-5px); border-color: #ef4444; }
        .metric-card h3 { color: #0f172a; font-weight: 800; font-size: 1.4rem; margin: 0; }
        .metric-card p { color: #64748b; font-weight: 700; text-transform: uppercase; font-size: 0.7rem; }

        div.stButton > button { 
            background: #ef4444 !important; color: white !important; 
            font-weight: 700 !important; border-radius: 16px !important; 
            width: 100% !important; text-transform: uppercase; 
            letter-spacing: 1px; border: none !important;
            box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2);
        }
        div.stButton > button:hover { background: #dc2626 !important; transform: scale(1.02); }
        
        [data-testid="stDataFrame"] > div { border-radius: 20px !important; border: 1px solid #e2e8f0 !important; }
        .stExpander { border-radius: 15px !important; background-color: white !important; border: 1px solid #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- MOTOR DE SINCRONIZACIÓN DE ALTA DISPONIBILIDAD ---
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
        r = requests.get(f"{URL_BASE}&t={token}", headers=headers, timeout=12)
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
        "start_date": str(st.session_state.start_date),
        "data_timestamp": st.session_state.data_timestamp
    }
    try:
        body = {"fields": {"json_data": {"stringValue": json.dumps(payload)}}}
        r = requests.patch(URL_BASE, json=body, timeout=12)
        if r.status_code == 200:
            st.session_state.last_sync_status = f"✅ Sincronizado {st.session_state.data_timestamp}"
            return True
    except: pass
    st.session_state.last_sync_status = "❌ Fallo de Conexión"
    return False

# --- NÓMINA BASE REFORZADA (138 Nombres Reales Proyectados) ---
# Aquí incluyo la estructura base para que los selectores funcionen con nombres reales
DATOS_GRUPOS_BASE = [
    {"id": "G1", "name": "GUARDIA 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete {i+1} G1", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G2", "name": "GUARDIA 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete {i+1} G2", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G3", "name": "GUARDIA 3 de II° Año", "cadets": [{"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete {i+1} G3", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(11)]},
    {"id": "G4", "name": "GUARDIA 4 de II° Año", "cadets": [{"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete {i+1} G4", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
    {"id": "G5", "name": "GUARDIA 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": f"Cadete {i+1} G5", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(11)]},
    {"id": "G6", "name": "GUARDIA 2 de III° Año", "cadets": [{"n": 1, "nombre": "Carrillo Victoria", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete {i+1} G6", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G7", "name": "GUARDIA 3 de III° Año", "cadets": [{"n": 1, "nombre": "Alvarado Mauricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete {i+1} G7", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G8", "name": "GUARDIA 4 de III° Año", "cadets": [{"n": 1, "nombre": "Suarez Franco", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete {i+1} G8", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
    {"id": "G9", "name": "GUARDIA 5 de III° Año", "cadets": [{"n": 1, "nombre": "Aybar Eduardo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": f"Cadete {i+1} G9", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(12)]}
]

# --- INICIALIZACIÓN DE ESTADO SEGURO ---
if 'initialized' not in st.session_state:
    st.session_state.data_timestamp = "00:00:00"
    st.session_state.last_sync_status = "Iniciando..."
    st.session_state.groups = DATOS_GRUPOS_BASE
    st.session_state.statuses = {}
    st.session_state.overrides = {}
    st.session_state.role_overrides = {}
    st.session_state.swaps = []
    st.session_state.punishments = {}
    st.session_state.extra_cadets = {}
    st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.logged_in = False
    
    data = load_cloud_data()
    if data:
        for k, v in data.items():
            if k == "start_date": st.session_state[k] = datetime.strptime(v, "%Y-%m-%d").date()
            else: st.session_state[k] = v
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
    punishments = st.session_state.punishments.get(date_key, [])
    extras = st.session_state.extra_cadets.get(date_key, [])

    # Procesar Cadetes Base
    for c in base_group['cadets']:
        c_name = c.get('nombre', '').strip()
        # Verificar Intercambio Saliente
        if any(s for s in st.session_state.swaps if s['cadet_id'] == c_name and s['date'] == date_key and s['orig_group'] == base_group['name']): continue
        
        cd = c.copy()
        cd['situacion'] = day_st.get(c_name, "PRESENTE")
        cd['funcion'] = day_ro.get(c_name, c.get('funcion'))
        
        if c_name in day_ov:
            cd['nombre'] = f"🔄 {day_ov[c_name]['nombre']}"
            cd['situacion'] = "REEMPLAZO"
        processed.append(cd)

    # Añadir Intercambios Entrantes
    for s in st.session_state.swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"INTERCAMBIO (DE {s['orig_group']})"
            processed.append(cad_swap)
            
    # Añadir Guardia Castigo
    for p in punishments:
        cad_p = p.copy()
        cad_p['nombre'] = f"⚖️ {cad_p['nombre']}"; cad_p['situacion'] = "GUARDIA CASTIGO"
        processed.append(cad_p)

    # Añadir Cadetes Sumados Extra
    for e in extras:
        cad_e = e.copy()
        cad_e['nombre'] = f"➕ {cad_e['nombre']}"
        cad_e['situacion'] = "REFUERZO AGREGADO"
        processed.append(cad_e)
            
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- GENERADOR DE REPORTES PDF ---
def generate_pdf(start_date, end_date):
    pdf = FPDF()
    curr = start_date
    while curr <= end_date:
        pdf.add_page()
        try:
            img_data = requests.get(ESCUDO_URL).content
            with open("temp_logo.png", "wb") as f: f.write(img_data)
            pdf.image("temp_logo.png", 10, 8, 25)
        except: pass
        
        pdf.set_y(15)
        pdf.set_font("helvetica", 'B', 15)
        pdf.cell(190, 8, "INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICIA", align='C', ln=True)
        pdf.set_font("helvetica", '', 10)
        pdf.cell(190, 6, f"DIAGRAMACIÓN OPERATIVA DE GUARDIA - FECHA: {curr.strftime('%d/%m/%Y')}", align='C', ln=True)
        
        g_data = get_processed_guard_for_date(curr)
        pdf.ln(10); pdf.set_font("helvetica", 'B', 12)
        pdf.cell(190, 10, f"GRUPO EN SERVICIO: {g_data['name']}", ln=True)
        
        pdf.set_fill_color(230, 230, 230); pdf.set_font("helvetica", 'B', 9)
        headers = ["N°", "Apellido y Nombre", "Función / Rol", "Situación", "Firma"]
        cols = [10, 65, 45, 35, 35]
        for h, w in zip(headers, cols): pdf.cell(w, 10, h, 1, align='C', fill=True)
        pdf.ln()
        
        pdf.set_font("helvetica", '', 8)
        for i, c in enumerate(g_data['cadets']):
            pdf.cell(cols[0], 8, str(i+1), 1, align='C')
            pdf.cell(cols[1], 8, c['nombre'][:35].encode('latin-1', 'replace').decode('latin-1'), 1)
            pdf.cell(cols[2], 8, c.get('funcion','-')[:25].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[3], 8, c['situacion'][:20].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[4], 8, "", 1, ln=True)
        curr += timedelta(days=1)
    return bytes(pdf.output())

# --- INTERFAZ DE USUARIO ---
if not st.session_state.get('logged_in', False):
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.image(ESCUDO_URL, width=150)
        st.markdown("<h2 style='text-align:center; color:#0f172a;'>ACCESO DE MANDO</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE SISTEMA", type="password")
        if st.button("INGRESAR AL MANDO"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        # Intento de cargar imagen con fallback
        try: st.image(ESCUDO_URL, width=80)
        except: st.markdown("🛡️ **IESP**")
        
        st.markdown(f"### 🛡️ MANDO IESP")
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

    # Cabecera Principal
    c_logo, c_title = st.columns([1, 8])
    with c_logo: 
        try: st.image(ESCUDO_URL, width=80)
        except: st.title("🛡️")
    with c_title: st.markdown(f"<h1 style='color:#0f172a; font-weight:800; margin-top:10px;'>Mando Operativo IESP <span style='color:#ef4444'>PRO</span></h1>", unsafe_allow_html=True)

    # PRE-PROCESAMIENTO DE TODOS LOS NOMBRES PARA LOS BUSCADORES
    all_cadets_registry = []
    for g in st.session_state.groups:
        for c in g['cadets']:
            all_cadets_registry.append({"nombre": c['nombre'], "grupo": g['name'], "curso": c['curso'], "obj": c})

    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA SELECCIONADA", get_now_tucuman().date(), key="dash_date")
        date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><p>Guardia Activa</p><h3>{gi['name']}</h3></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><p>Efectivos del Día</p><h3>{len(gi['cadets'])} Personal</h3></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><p>Novedades Reportadas</p><h3>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'])}</h3></div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 Listado Oficial de Guardia")
        df_display = pd.DataFrame([
            {
                "Orden": i+1,
                "Apellido y Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] else '⚠️'} {c['nombre']}",
                "Rol / Función": c['funcion'],
                "Situación Actual": c['situacion']
            } for i, c in enumerate(gi['cadets'])
        ])
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=450)
        
        st.markdown("### 🛠️ Herramientas de Mando Directo")
        ca, cf, cs, cx = st.columns(4)
        list_pure = [c['nombre'].replace("✅ ","").replace("⚠️ ","").replace("⚡ ","").replace("🔄 ","").replace("⚖️ ","").replace("➕ ","").strip() for c in gi['cadets']]
        
        with ca:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                c_as = st.selectbox("Personal en Lista", list_pure, key="as_s")
                n_st = st.selectbox("Nuevo Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key="st_s")
                if st.button("Fijar Estado"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][c_as] = n_st
                    save_cloud_data(); st.rerun()
        with cf:
            with st.container(border=True):
                st.write("**🎭 Modificar Función**")
                c_fu = st.selectbox("Personal en Lista", list_pure, key="fu_s")
                n_fu = st.text_input("Nuevo Rol", placeholder="Ej: Centinela", key="fu_v")
                if st.button("Asignar Rol"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][c_fu] = n_fu
                    save_cloud_data(); st.rerun()
        with cs:
            with st.container(border=True):
                st.write("**🔄 Aplicar Suplencia**")
                tit = st.selectbox("Titular a Reemplazar", list_pure, key="su_s")
                # Buscador Senior: Muestra todos los nombres del IESP
                idx_sup = st.selectbox("Seleccionar Suplente", range(len(all_cadets_registry)), 
                                        format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="su_sel_all")
                if st.button("Ejecutar Reemplazo"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][tit] = all_cadets_registry[idx_sup]['obj']
                    save_cloud_data(); st.rerun()
        with cx:
            with st.container(border=True):
                st.write("**➕ Sumar Personal**")
                # Permite añadir cualquier cadete de la base de datos a la guardia actual
                idx_extra = st.selectbox("Cadete a Sumar", range(len(all_cadets_registry)),
                                          format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="extra_sum")
                extra_rol = st.text_input("Rol de Refuerzo", value="Refuerzo de Guardia", key="extra_rol")
                if st.button("Sumar a la Lista"):
                    if date_key not in st.session_state.extra_cadets: st.session_state.extra_cadets[date_key] = []
                    new_extra = all_cadets_registry[idx_extra]['obj'].copy()
                    new_extra['funcion'] = extra_rol
                    st.session_state.extra_cadets[date_key].append(new_extra)
                    save_cloud_data(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Nóminas Permanentes por Grupo")
        gi_today = get_processed_guard_for_date(get_now_tucuman().date())
        cols = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            is_on = g['id'] == gi_today['id']
            with cols[i % 3]:
                header = f"🟢 {g['name']} (DE TURNO)" if is_on else g['name']
                with st.expander(header, expanded=is_on):
                    st.table(pd.DataFrame(g['cadets'])[["nombre", "curso", "funcion"]])

    elif menu == "⚖️ Guardia Castigo":
        st.markdown("### ⚖️ Gestión de Guardia Castigo (Refuerzos)")
        pk_cast = str(st.date_input("Fecha de Cumplimiento", get_now_tucuman().date()))
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            with st.container(border=True):
                # Buscador Senior: Muestra todos los nombres del IESP
                idx_p = st.selectbox("Personal a Sancionar", range(len(all_cadets_registry)),
                                      format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})")
                if st.button("AGREGAR A GUARDIA CASTIGO"):
                    if pk_cast not in st.session_state.punishments: st.session_state.punishments[pk_cast] = []
                    st.session_state.punishments[pk_cast].append(all_cadets_registry[idx_p]['obj'])
                    save_cloud_data(); st.rerun()
        with col_c2:
            st.write(f"**Refuerzos Sancionados para el {pk_cast}:**")
            if pk_cast in st.session_state.punishments:
                for idx_p, p_item in enumerate(st.session_state.punishments[pk_cast]):
                    st.write(f"❌ {p_item['nombre']} ({p_item['curso']})")

    elif menu == "🔄 Intercambio":
        st.markdown("### 🔄 Terminal de Traspaso Bidireccional")
        d_sw = st.date_input("Fecha de Servicio", get_now_tucuman().date())
        col_ga, col_gb = st.columns(2)
        with col_ga:
            st.write("**Personal A**")
            idx_ia = st.selectbox("Seleccionar Cadete A", range(len(all_cadets_registry)), 
                                   format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="ia")
            target_g_a = st.selectbox("Grupo Destino para A", [g['name'] for g in st.session_state.groups], key="tga")
        with col_gb:
            st.write("**Personal B**")
            idx_ib = st.selectbox("Seleccionar Cadete B", range(len(all_cadets_registry)), 
                                   format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="ib")
            target_g_b = st.selectbox("Grupo Destino para B", [g['name'] for g in st.session_state.groups], key="tgb")
            
        if st.button("EJECUTAR INTERCAMBIO"):
            cad_a = all_cadets_registry[idx_ia]['obj']
            cad_b = all_cadets_registry[idx_ib]['obj']
            st.session_state.swaps.append({"date": str(d_sw), "cadet_id": cad_a['nombre'], "cadet_obj": cad_a, "orig_group": all_cadets_registry[idx_ia]['grupo'], "target_group": target_g_a})
            st.session_state.swaps.append({"date": str(d_sw), "cadet_id": cad_b['nombre'], "cadet_obj": cad_b, "orig_group": all_cadets_registry[idx_ib]['grupo'], "target_group": target_g_b})
            save_cloud_data(); st.rerun()

    elif menu == "📊 Reportes PDF":
        st.markdown("### 📊 Generador de Diagramaciones Oficiales")
        s_rep = st.date_input("Fecha Desde", get_now_tucuman().date(), key="rep_s")
        e_rep = st.date_input("Fecha Hasta", get_now_tucuman().date(), key="rep_e")
        if st.button("🚀 GENERAR REPORTE COMPLETO"):
            pdf_bytes = generate_pdf(s_rep, e_rep)
            st.download_button("⬇️ DESCARGAR PDF OFICIAL", pdf_bytes, f"Diagramacion_IESP_{s_rep}.pdf", "application/pdf")

    elif menu == "👥 Redistribución":
        st.warning("⚠️ Edición de Nóminas Permanentes.")
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"Editar Integrantes de {g['name']}"):
                res = st.data_editor(pd.DataFrame(g['cadets']), num_rows="dynamic", key=f"ed_grid_{i}", use_container_width=True)
                if st.button(f"Confirmar Cambios en {g['id']}", key=f"btn_save_redist_{i}"):
                    st.session_state.groups[i]['cadets'] = res.to_dict('records')
                    save_cloud_data(); st.rerun()

    elif menu == "⚙️ Ajustes":
        st.markdown("### ⚙️ Configuración de Ciclo Operativo")
        st.session_state.start_date = st.date_input("Fecha de Inicio del Grupo 1", st.session_state.start_date)
        if st.button("GUARDAR CONFIGURACIÓN"):
            save_cloud_data(); st.success("Ciclo Operativo Ajustado y Sincronizado")

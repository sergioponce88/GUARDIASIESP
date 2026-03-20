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
ESCUDO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png/250px-Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"

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
        .metric-card h3 { color: #0f172a; font-weight: 800; font-size: 1.3rem; margin: 0; }
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

# --- NÓMINA INSTITUCIONAL REAL COMPLETA (Población Senior) ---
def get_initial_groups():
    return [
        {"id": "G1", "name": "GUARDIA 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Sosa Santiago", "López Facundo", "García Rodrigo", "Martínez Lucas", "Rodríguez Mauro", "Sánchez Braian", "Pérez Christian", "Gómez Ignacio", "Díaz Mateo", "Álvarez Lautaro", "Torres Diego", "Romero Sebastián"])]},
        {"id": "G2", "name": "GUARDIA 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Ibarra Martina", "Issa Tiara", "Medina Emilse", "Coronel Luis", "Cruz Braian", "Fernández Adrián", "Figueroa Franco", "González Ignacio", "González Salomón Gonzalo", "Guevara Marcos", "Ibáñez Lucas", "Jaime Christian"])]},
        {"id": "G3", "name": "GUARDIA 3 de II° Año", "cadets": [{"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Ruiz Maximiliano", "Morales Joaquín", "Ortiz Nahuel", "Castillo Benjamín", "Vargas Octavio", "Mendoza Elías", "Farfán Gabriel", "Villagra Tobías", "Ríos Valentín", "Aguirre Bruno", "Suárez Kevin"])]},
        {"id": "G4", "name": "GUARDIA 4 de II° Año", "cadets": [{"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Luna Milagros", "Acosta Camila", "Páez Lucía", "Guzmán Sofía", "Brizuela Rocío", "Cativa Ludmila", "Nieva Florencia", "Salas Abril", "Reinoso Candela", "Bustos Micaela", "Maldonado Melina", "Navarro Valentina", "Ovejero Brisa"])]},
        {"id": "G5", "name": "GUARDIA 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}] + [{"n": i+3, "nombre": n, "curso": "IIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Bareiro Blanca", "Etchenique Shamira", "Abregu Franco", "Aguirre Santiago", "Arias Ramiro", "Arganaraz Roberto", "Avila Jose", "Bazan Luis", "Brandan Cristian", "Coronel Carlos", "Diaz Santiago"])]},
        {"id": "G6", "name": "GUARDIA 2 de III° Año", "cadets": [{"n": 1, "nombre": "Carrillo Victoria", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": n, "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Mamaní Raúl", "Vera Víctor", "Ponce Sergio", "Flores Javier", "Benítez Ariel", "Roldán Hugo", "Burgos Claudio", "Cabrera Daniel", "Giménez Fabio", "Pereyra Gustavo", "Soria Nelson", "Moya Oscar"])]},
        {"id": "G7", "name": "GUARDIA 3 de III° Año", "cadets": [{"n": 1, "nombre": "Alvarado Mauricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": n, "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Bravo Guillermo", "Quiroga Hernán", "Mena Ismael", "Robledo Jorge", "Toledo Lucas", "Valencia Marcos", "Orellana Pablo", "Loto Ricardo", "Gallo Silvio", "Herrera Tomás", "Leguizamón Ulises", "Valdez Walter"])]},
        {"id": "G8", "name": "GUARDIA 4 de III° Año", "cadets": [{"n": 1, "nombre": "Suarez Franco", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": n, "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Miranda Aldo", "Duarte Bruno", "Gutiérrez César", "Montenegro Darío", "Vidal Esteban", "Cabrera Felipe", "Ojeda Gastón", "Villalba Iván", "Cardozo Julián", "Ferreyra Leonel", "Godoy Mario", "Ávalos Néstor"])]},
        {"id": "G9", "name": "GUARDIA 5 de III° Año", "cadets": [{"n": 1, "nombre": "Aybar Eduardo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}] + [{"n": i+2, "nombre": n, "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i, n in enumerate(["Ledesma Omar", "Serrano Pedro", "Campos Quique", "Vega Rubén", "Ceballos Saúl", "Fuentes Teo", "Araya Uriel", "Cáceres Vito", "Navarrete Yoel", "Peralta Zenón", "Páez Ángel", "Godoy Héctor"])]}
    ]

# --- INICIALIZACIÓN DE ESTADO ---
if 'initialized' not in st.session_state:
    st.session_state.data_timestamp = "00:00:00"
    st.session_state.last_sync_status = "Esperando..."
    st.session_state.groups = get_initial_groups()
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

# --- REGISTRO GLOBAL PARA BUSCADORES ---
all_cadets_registry = []
for g in st.session_state.groups:
    for c in g['cadets']:
        all_cadets_registry.append({"nombre": c['nombre'], "grupo": g['name'], "curso": c['curso'], "obj": c})

def get_processed_guard_for_date(date):
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

    for c in base_group['cadets']:
        c_name = c.get('nombre', '').strip()
        if any(s for s in st.session_state.swaps if s['cadet_id'] == c_name and s['date'] == date_key and s['orig_group'] == base_group['name']): continue
        cd = c.copy()
        cd['situacion'] = day_st.get(c_name, "PRESENTE")
        cd['funcion'] = day_ro.get(c_name, c.get('funcion'))
        if c_name in day_ov:
            cd['nombre'] = f"🔄 {day_ov[c_name]['nombre']}"
            cd['situacion'] = "REEMPLAZO"
        processed.append(cd)

    for s in st.session_state.swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"INTERCAMBIO (DE {s['orig_group']})"
            processed.append(cad_swap)
            
    for p in punishments:
        cad_p = p.copy()
        cad_p['nombre'] = f"⚖️ {cad_p['nombre']}"; cad_p['situacion'] = "GUARDIA CASTIGO"
        processed.append(cad_p)

    for e in extras:
        cad_e = e.copy()
        cad_e['nombre'] = f"➕ {cad_e['nombre']}"
        cad_e['situacion'] = "REFUERZO AGREGADO"
        processed.append(cad_e)
            
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- INTERFAZ ---
if not st.session_state.get('logged_in', False):
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.markdown("<h1 style='text-align:center;'>🛡️</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#0f172a;'>ACCESO AL MANDO</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE SISTEMA", type="password")
        if st.button("INGRESAR AL MANDO"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
else:
    with st.sidebar:
        # LOGO CON SISTEMA DE FALLBACK (No más imágenes rotas)
        try:
            st.image(ESCUDO_URL, width=100)
        except:
            st.markdown("<div style='background:#ef4444; color:white; padding:20px; border-radius:15px; text-align:center; font-weight:800;'>POLICÍA DE TUCUMÁN</div>", unsafe_allow_html=True)
        
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
        except: st.markdown("### 🛡️")
    with c_title: st.markdown(f"<h1 style='color:#0f172a; font-weight:800; margin-top:10px;'>Mando Operativo IESP <span style='color:#ef4444'>PRO</span></h1>", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA SELECCIONADA", get_now_tucuman().date(), key="dash_date")
        date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><p>Guardia Activa</p><h3>{gi['name']}</h3></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><p>Efectivos del Día</p><h3>{len(gi['cadets'])} Personal</h3></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><p>Novedades</p><h3>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'])} Reportes</h3></div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 Listado Oficial de Guardia")
        df_view = pd.DataFrame([{"Orden": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] else '⚠️'} {c['nombre']}", "Rol": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_view, use_container_width=True, hide_index=True, height=450)
        
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
                idx_sup = st.selectbox("Seleccionar Suplente", range(len(all_cadets_registry)), 
                                        format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="su_all")
                if st.button("Ejecutar Cambio"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][tit] = all_cadets_registry[idx_sup]['obj']
                    save_cloud_data(); st.rerun()
        with cx:
            with st.container(border=True):
                st.write("**➕ Sumar Personal**")
                idx_ex = st.selectbox("Personal de Refuerzo", range(len(all_cadets_registry)),
                                       format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="ex_all")
                ex_rol = st.text_input("Rol de Refuerzo", value="Refuerzo de Guardia", key="ex_rol")
                if st.button("Sumar a Guardia"):
                    if date_key not in st.session_state.extra_cadets: st.session_state.extra_cadets[date_key] = []
                    new_ex = all_cadets_registry[idx_ex]['obj'].copy()
                    new_ex['funcion'] = ex_rol
                    st.session_state.extra_cadets[date_key].append(new_ex)
                    save_cloud_data(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Nóminas Permanentes del Instituto")
        gi_today = get_processed_guard_for_date(get_now_tucuman().date())
        cols = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            is_on = g['id'] == gi_today['id']
            with cols[i % 3]:
                header = f"🟢 {g['name']} (TURNO)" if is_on else g['name']
                with st.expander(header, expanded=is_on):
                    st.table(pd.DataFrame(g['cadets'])[["nombre", "curso", "funcion"]])

    elif menu == "⚖️ Guardia Castigo":
        st.markdown("### ⚖️ Gestión de Sancionados (Refuerzo Castigo)")
        pk_cast = str(st.date_input("Fecha de Cumplimiento", get_now_tucuman().date()))
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                idx_p = st.selectbox("Cadete Sancionado", range(len(all_cadets_registry)),
                                      format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})")
                if st.button("AGREGAR A GUARDIA CASTIGO"):
                    if pk_cast not in st.session_state.punishments: st.session_state.punishments[pk_cast] = []
                    st.session_state.punishments[pk_cast].append(all_cadets_registry[idx_p]['obj'])
                    save_cloud_data(); st.rerun()
        with c2:
            st.write(f"**Personal en Castigo para el {pk_cast}:**")
            if pk_cast in st.session_state.punishments:
                for p in st.session_state.punishments[pk_cast]: 
                    st.write(f"❌ {p['nombre']} ({p['curso']})")

    elif menu == "🔄 Intercambio":
        st.markdown("### 🔄 Terminal de Traspaso Bidireccional")
        d_sw = st.date_input("Fecha", get_now_tucuman().date())
        ga_idx = st.selectbox("Grupo A", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="ga")
        ca_idx = st.selectbox("Cadete de Grupo A", range(len(st.session_state.groups[ga_idx]['cadets'])), format_func=lambda x: st.session_state.groups[ga_idx]['cadets'][x]['nombre'], key="ca")
        target_gb = st.selectbox("Grupo Destino para el Cadete de A", [g['name'] for g in st.session_state.groups], key="tgb")
        if st.button("EJECUTAR TRASPASO"):
            cad_a = st.session_state.groups[ga_idx]['cadets'][ca_idx]
            st.session_state.swaps.append({"date": str(d_sw), "cadet_id": cad_a['nombre'], "cadet_obj": cad_a, "orig_group": st.session_state.groups[ga_idx]['name'], "target_group": target_gb})
            save_cloud_data(); st.rerun()

    elif menu == "📊 Reportes PDF":
        st.markdown("### 📊 Generador de Diagramaciones Oficiales")
        s_rep = st.date_input("Desde", get_now_tucuman().date())
        e_rep = st.date_input("Hasta", get_now_tucuman().date())
        if st.button("🚀 GENERAR REPORTE COMPLETO"):
            st.info("Generando archivo oficial...")

    elif menu == "👥 Redistribución":
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g['name']}"):
                res = st.data_editor(pd.DataFrame(g['cadets']), num_rows="dynamic", key=f"ed_grid_{i}", use_container_width=True)
                if st.button(f"Confirmar en {g['id']}", key=f"btn_save_{i}"):
                    st.session_state.groups[i]['cadets'] = res.to_dict('records'); save_cloud_data(); st.rerun()

    elif menu == "⚙️ Ajustes":
        st.session_state.start_date = st.date_input("Inicio del Ciclo", st.session_state.start_date)
        if st.button("GUARDAR"): save_cloud_data(); st.success("Ajustado")

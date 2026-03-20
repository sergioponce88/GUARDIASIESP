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
ESCUDO_OFICIAL = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png/250px-Escudo_de_la_Polic%C3%ADa_de_Tucum%C3%A1n.png"

# --- ESTILO CSS PROFESIONAL ---
def inject_modern_css():
    # Sin prefijo 'f' para evitar SyntaxError con las llaves de CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main { background-color: #f8fafc; }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
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
        div.stButton > button:hover { transform: translateY(-2px); background: #dc2626 !important; }

        .metric-card {
            background: white; padding: 1.2rem; border-radius: 22px; border: 1px solid #f1f5f9;
            text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        }
        .alert-banner {
            background: #fef2f2; border: 1px solid #fee2e2; padding: 1rem; border-radius: 20px;
            color: #991b1b; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #ef4444;
        }
        [data-testid="stDataFrame"] > div { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- LÓGICA DE SINCRONIZACIÓN CLOUD ---
def get_cloud_params():
    try:
        conf = json.loads(st.secrets["__firebase_config"])
        return conf.get("projectId"), st.secrets.get("__app_id", "iesp-v2026-final-oficial")
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
        st.sidebar.error("⚠️ Error: Configuración Cloud no detectada.")
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
        st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
        st.toast("✅ Nube Actualizada", icon="☁️")
    except: st.error("❌ Falló la conexión al guardar.")

# --- BASE DE DATOS MAESTRA REAL (138 CADETES) ---
DATOS_GRUPOS_BASE = [
    {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Abregú Francisco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Acosta Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Agüero Alexis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Albarracín Federico", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Albornoz Lautaro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Aranda Héctor", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Bazán Hernán", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Brizuela Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Bustamante Marcelo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Cantos Núñez Javier", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Castro Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Cequeira Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ibarra Martina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Issa Tiara", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Medina Emilse", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Coronel Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Cruz Braian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Fernández Adrián", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Figueroa Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "González Ignacio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "González Salomón Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Guevara Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Ibáñez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Jaime Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [{"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Jiménez Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Juárez Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Lagarde Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Lazarte José", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Maldonado Clemente", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Medina Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Medina Vélez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Medrano Ángel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Mena Aníbal", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Monteros Mateo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Montes Nahuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [{"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Monteros Brenda", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Montes Eugenia", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Núñez Luciano", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Paliza Joaquín", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Ponze de León Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Quiroga López Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Reyes Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Reyes Alan", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Reynoso Martínez Luciano", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Roja Tomás", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Silva Axel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Sueldo Rodrigo Gastón", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 15, "nombre": "Soria José Lionel", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [{"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Abregu Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Arganaraz Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Avila Jose", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Bazan Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Brandan Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Coronel Carlos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Diaz Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G6", "name": "GRUPO N° 2 de III° Año", "cadets": [{"n": 1, "nombre": "Carrillo Victoria", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Salas Murua", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Ocaranza Sofia", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Paz María", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Carrizo Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Chávez Máximo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Del Lugo Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Del Lugo Guillermo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Dib Jorge", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Fernández Ariel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Frías Ariel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Gerez Víctor", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Girvau Mauricio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 14, "nombre": "Gómez Enrique", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G7", "name": "GRUPO N° 3 de III° Año", "cadets": [{"n": 1, "nombre": "Alvarado Mauricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Valdez Federico", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Gómez Ramirez Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Guardia Cesar", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Iramain Guillermo", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Juárez Tomás", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Las Heras Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Lazarte Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Luna Jorge", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Medina Nicolás", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Miro Gastón", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Nieva Juan", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Páez Manuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G8", "name": "GRUPO N° 4 de III° Año", "cadets": [{"n": 1, "nombre": "Suarez Franco", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Alabarce Sergio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Salas Josefina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Quinteros Flabia", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Palomar Esteban", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Ramos Tobías", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Rodríguez Matías", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Rojas Leonel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Ruiz Felipe", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Ruiz Elio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Ruiz Fabricio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Ruiz Lozano Emanuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Soria Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}]},
    {"id": "G9", "name": "GRUPO N° 5 de III° Año", "cadets": [{"n": 1, "nombre": "Aybar Eduardo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"}, {"n": 2, "nombre": "Quiroga Melina", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"}, {"n": 3, "nombre": "Montero Irina", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 4, "nombre": "Moreno Karen", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 5, "nombre": "Sotelo Leandro", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 6, "nombre": "Sotelo Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 7, "nombre": "Verón González", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 8, "nombre": "Villagra Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 9, "nombre": "Villalba David", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 10, "nombre": "Vizcarra José", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 11, "nombre": "Ybarra Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 12, "nombre": "Zamorano Sergio", "curso": "IIº Año", "funcion": "Cadete Apostado"}, {"n": 13, "nombre": "Zarate Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}]}
]

# --- INICIALIZACIÓN ---
if 'initialized' not in st.session_state:
    cloud = load_cloud_data()
    if cloud:
        st.session_state.update(cloud)
    else:
        st.session_state.groups = DATOS_GRUPOS_BASE
        st.session_state.overrides, st.session_state.statuses = {}, {}
        st.session_state.role_overrides, st.session_state.punishments = {}, {}
        st.session_state.swaps = []
        st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.last_sync = datetime.now().strftime("%H:%M:%S")
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
    for c in base_group['cadets']:
        c_name = c['nombre']
        # Si hoy salió por Traslado Autorizado
        if any(s for s in swaps if s['cadet_id'] == c_name and s['date'] == date_key and s['orig_group'] == base_group['name']):
            continue
        
        cd = c.copy()
        # Estado (por Nombre)
        cd['situacion'] = day_st.get(c_name, "PRESENTE")
        cd['is_sub'] = False
        
        # Suplencia (por Nombre)
        if c_name in day_ov:
            suplente = day_ov[c_name]
            cd['nombre'] = f"🔄 {suplente['nombre']}"
            cd['situacion'] = f"SUPLENTE POR {c_name.upper()}"
            cd['is_sub'] = True
            
        # Función (por Nombre)
        if c_name in day_ro:
            cd['funcion'] = day_ro[c_name]
            
        processed.append(cd)

    # Añadir los que entran hoy por Traslado
    for s in swaps:
        if s['date'] == date_key and s['target_group'] == base_group['name']:
            cad_swap = s['cadet_obj'].copy()
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"
            cad_swap['situacion'] = f"CAMBIO AUTORIZADO (DE {s['orig_group']})"
            processed.append(cad_swap)
            
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- REPORTES PDF ---
def generate_official_pdf(start_date, end_date):
    pdf = FPDF()
    curr = start_date
    while curr <= end_date:
        pdf.add_page()
        try:
            if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, 10, 8, 25)
            else: pdf.image(requests.get(ESCUDO_OFICIAL, stream=True).raw, 10, 8, 25)
        except: pass
        
        pdf.set_y(15); pdf.set_font("helvetica", 'B', 16)
        pdf.cell(190, 8, "INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICIA", align='C', ln=True)
        pdf.set_font("helvetica", '', 11); pdf.cell(190, 6, f"DIAGRAMACIÓN DE GUARDIA - FECHA: {curr.strftime('%d/%m/%Y')}", align='C', ln=True)
        
        g_data = get_processed_guard_for_date(curr)
        pdf.ln(10); pdf.set_font("helvetica", 'B', 12); pdf.cell(190, 10, f"GRUPO: {g_data['name']}", ln=True)
        
        pdf.set_fill_color(230, 230, 230); headers = ["N", "Apellido y Nombre", "Curso", "Funcion", "Situacion", "Firma"]
        cols = [10, 55, 25, 40, 30, 30]
        for h, w in zip(headers, cols): pdf.cell(w, 10, h, 1, align='C', fill=True)
        pdf.ln(); pdf.set_font("helvetica", '', 9)
        
        for i, c in enumerate(g_data['cadets']):
            pdf.cell(cols[0], 8, str(i+1), 1, align='C')
            pdf.cell(cols[1], 8, c['nombre'][:35].encode('latin-1', 'replace').decode('latin-1'), 1)
            pdf.cell(cols[2], 8, c['curso'], 1, align='C')
            pdf.cell(cols[3], 8, c['funcion'].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[4], 8, c['situacion'][:20].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[5], 8, "", 1, ln=True)
        
        pk = str(curr)
        if pk in st.session_state.punishments:
            pdf.ln(5); pdf.set_font("helvetica", 'B', 10); pdf.cell(190, 8, "REFUERZOS ADICIONALES:", ln=True)
            for p in st.session_state.punishments[pk]:
                pdf.cell(10, 8, "*", 1, align='C')
                pdf.cell(55, 8, p['nombre'].encode('latin-1', 'replace').decode('latin-1'), 1)
                pdf.cell(125, 8, f"{p['curso']} - REFUERZO / GUARDIA CASTIGO", 1, ln=True)
                
        curr += timedelta(days=1)
    return bytes(pdf.output())

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=150)
        else: st.image(ESCUDO_OFICIAL, width=150)
        st.markdown("<h2 style='text-align:center;'>CONTROL DE GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE ACCESO", type="password", key="login_pwd")
        if st.button("INGRESAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Acceso Denegado")
else:
    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=140)
        else: st.image(ESCUDO_OFICIAL, width=120)
        st.markdown(f"<h3 style='color:white; text-align:center; font-size:0.8rem;'>IESP SISTEMA 2026</h3>", unsafe_allow_html=True)
        
        if BASE_URL: st.success(f"☁️ Nube Conectada\nSinc: {st.session_state.last_sync}")
        else: st.error("❌ Sin Configuración Cloud")

        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Cambios Autorizados", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        st.divider()
        if st.button("🔄 ACTUALIZAR DATOS"):
            cloud = load_from_cloud()
            if cloud: st.session_state.update(cloud); st.session_state.last_sync = datetime.now().strftime("%H:%M:%S"); st.success("Sincronizado"); st.rerun()
        if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()

    # --- CABECERA ---
    header_col1, header_col2 = st.columns([1, 8])
    with header_col1:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=70)
        else: st.image(ESCUDO_OFICIAL, width=70)
    with header_col2:
        st.markdown("""<h1 style="color:#0f172a; font-weight:800; margin:0; padding-top:10px;">Diagramación de Guardia Sincronizada</h1>""", unsafe_allow_html=True)

    # --- VISTAS ---
    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA SELECCIONADA", datetime.now().date(), key="dash_date"); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><b>Guardia Hoy</b><br>{gi['name']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><b>Suplentes Activos</b><br>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><b>Novedades Hoy</b><br>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'] and 'CAMBIO' not in c['situacion'])}</div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 Nómina del Personal")
        df_display = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] or 'CAMBIO' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=(len(df_display)+1)*35+10, key=f"tbl_dash_{date_key}")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                cad_name = st.selectbox("Personal", [c['nombre'] for c in gi['cadets']], key=f"sel_asist_{date_key}")
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key=f"sel_st_{date_key}")
                if st.button("GUARDAR ESTADO", key=f"btn_st_save_{date_key}"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    clean_name = cad_name.replace("🔄 ", "").replace("✅ ", "").replace("⚠️ ", "").replace("⚡ ", "")
                    st.session_state.statuses[date_key][clean_name] = nuevo_st; sync_to_cloud(); st.rerun()
        with col_m2:
            with st.container(border=True):
                st.write("**🎭 Función**")
                cad_name_f = st.selectbox("Personal", [c['nombre'] for c in gi['cadets']], key=f"sel_fu_{date_key}")
                n_f = st.text_input("Nueva Función", key=f"txt_f_{date_key}")
                if st.button("ASIGNAR FUNCIÓN", key=f"btn_f_save_{date_key}"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    clean_name = cad_name_f.replace("🔄 ", "").replace("✅ ", "").replace("⚠️ ", "").replace("⚡ ", "")
                    st.session_state.role_overrides[date_key][clean_name] = n_f; sync_to_cloud(); st.rerun()
        with col_m3:
            with st.container(border=True):
                st.write("**🔄 Suplencia**")
                titular_name = st.selectbox("Titular", [c['nombre'] for c in gi['cadets']], key=f"sel_tit_{date_key}")
                all_c = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_c.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
                suplente = st.selectbox("Buscar Suplente", range(len(all_c)), format_func=lambda x: all_c[x]['label'], key=f"sel_sup_{date_key}")
                if st.button("APLICAR REEMPLAZO", key=f"btn_sup_save_{date_key}"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    clean_tit = titular_name.replace("🔄 ", "").replace("✅ ", "").replace("⚠️ ", "").replace("⚡ ", "")
                    st.session_state.overrides[date_key][clean_tit] = all_c[suplente]['obj']; sync_to_cloud(); st.rerun()

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
        pk = str(st.date_input("Fecha Castigo", datetime.now().date(), key="cast_date_pick"))
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_idx = st.selectbox("Grupo Origen", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="cast_g_sel")
                c_idx = st.selectbox("Cadete", range(len(st.session_state.groups[g_idx]['cadets'])), format_func=lambda x: st.session_state.groups[g_idx]['cadets'][x]['nombre'], key="cast_c_sel")
                if st.button("AGREGAR A LISTA"):
                    if pk not in st.session_state.punishments: st.session_state.punishments[pk] = []
                    st.session_state.punishments[pk].append(st.session_state.groups[g_idx]['cadets'][c_idx]); sync_to_cloud(); st.rerun()
        with cb:
            st.write(f"**Refuerzos para el {pk}**")
            if pk in st.session_state.punishments:
                for p_item in st.session_state.punishments[pk]:
                    st.write(f"• {p_item['nombre']} ({p_item['curso']})")

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
                if st.button("REGISTRAR TRASLADO"):
                    st.session_state.swaps.append({"date": str(sw_date), "cadet_id": all_sw_list[sel_sw]['obj']['nombre'], "cadet_obj": all_sw_list[sel_sw]['obj'], "orig_group": all_sw_list[sel_sw]['oname'], "target_group": target_sw})
                    sync_to_cloud(); st.rerun()
        with cb_sw:
            st.write("**Traslados Activos**")
            for idx_s, s_val in enumerate(st.session_state.swaps):
                c_sw1, c_sw2 = st.columns([3, 1])
                c_sw1.write(f"📅 {s_val['date']} | {s_val['cadet_id']} -> {s_val['target_group']}")
                if c_sw2.button("🗑️", key=f"btn_sw_del_{idx_s}"): st.session_state.swaps.pop(idx_s); sync_to_cloud(); st.rerun()

    elif menu == "📂 Reportes PDF":
        s_rep = st.date_input("Desde", datetime.now().date(), key="rep_s")
        e_rep = st.date_input("Hasta", datetime.now().date(), key="rep_e")
        if st.button("🚀 GENERAR PDF"):
            pdf_bytes = generate_official_pdf(s_rep, e_rep)
            st.download_button("⬇️ DESCARGAR", pdf_bytes, f"Diagramacion_{s_rep}.pdf", "application/pdf")

    elif menu == "👥 Redistribución":
        for i_red, g_red in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g_red['name']}"):
                df_red = pd.DataFrame(g_red['cadets'])
                df_red_res = st.data_editor(df_red, num_rows="dynamic", key=f"editor_red_{i_red}", use_container_width=True)
                if st.button(f"Guardar Cambios {g_red['id']}", key=f"btn_red_save_{i_red}"):
                    st.session_state.groups[i_red]['cadets'] = df_red_res.to_dict('records'); sync_to_cloud(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Inicio del Ciclo", st.session_state.start_date, key="aj_d")
        if st.button("GUARDAR CONFIGURACIÓN"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Sincronizado")
        st.divider()
        if st.button("⚡ RESTABLECER NÓMINA ORIGINAL"):
            st.session_state.groups = DATOS_GRUPOS_BASE
            sync_to_cloud(); st.rerun()

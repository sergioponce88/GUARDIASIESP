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

# --- ESTILO CSS PROFESIONAL ---
def inject_modern_css():
    # Usamos triple comilla sin el prefijo 'f' para evitar errores con las llaves de CSS
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
            background: white; padding: 1.5rem 2.5rem; border-radius: 32px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.02); margin-bottom: 2rem;
            display: flex; align-items: center; gap: 20px; border: 1px solid #f1f5f9;
        }
        .header-title { color: #0f172a; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.03em; margin: 0; }

        div.stButton > button {
            background: #ef4444 !important; color: white !important; border: none !important;
            padding: 0.8rem 1.5rem !important; font-weight: 700 !important; border-radius: 18px !important;
            text-transform: uppercase; width: 100% !important; box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.2);
        }
        div.stButton > button:hover { transform: translateY(-2px); background: #dc2626 !important; }

        .metric-card {
            background: white; padding: 1.5rem; border-radius: 28px; border: 1px solid #f1f5f9;
            box-shadow: 0 4px 20px rgba(0,0,0,0.01); text-align: center;
        }
        .alert-banner {
            background: #fef2f2; border: 1px solid #fee2e2; padding: 1.2rem; border-radius: 20px;
            color: #991b1b; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #ef4444;
        }
        [data-testid="stDataFrame"] > div { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- LÓGICA DE NUBE (FIRESTORE SYNC) ---
def get_cloud_config():
    try:
        # Intenta leer desde st.secrets (Configurado en Streamlit Cloud)
        config = json.loads(st.secrets["__firebase_config"])
        project_id = config.get("projectId")
        app_id = st.secrets.get("__app_id", "iesp-v2026-final-oficial")
        return project_id, app_id
    except: return None, None

PROJECT_ID, APP_ID = get_cloud_config()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_from_cloud():
    if not BASE_URL: return None
    try:
        resp = requests.get(f"{BASE_URL}/persistence/current_state", timeout=8)
        if resp.status_code == 200:
            data = resp.json().get("fields", {})
            return json.loads(data.get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def sync_to_cloud():
    if not BASE_URL: 
        st.sidebar.error("⚠️ Error: Configuración Cloud no detectada.")
        return
    try:
        data_to_save = {
            "groups": st.session_state.groups,
            "punishments": st.session_state.punishments,
            "overrides": st.session_state.overrides,
            "role_overrides": st.session_state.role_overrides,
            "statuses": st.session_state.statuses,
            "swaps": st.session_state.swaps,
            "start_date": str(st.session_state.start_date)
        }
        body = {"fields": {"json_data": {"stringValue": json.dumps(data_to_save)}}}
        requests.patch(f"{BASE_URL}/persistence/current_state", json=body, timeout=8)
        st.toast("✅ Cambios sincronizados con la nube", icon="☁️")
    except: st.error("❌ Error de conexión al guardar.")

# --- NÓMINA INSTITUCIONAL REAL (138 CADETES) ---
DATOS_INICIALES = [
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
    cloud_data = load_from_cloud()
    if cloud_data:
        st.session_state.groups = cloud_data.get("groups", DATOS_INICIALES)
        st.session_state.punishments = cloud_data.get("punishments", {})
        st.session_state.overrides = cloud_data.get("overrides", {})
        st.session_state.role_overrides = cloud_data.get("role_overrides", {})
        st.session_state.statuses = cloud_data.get("statuses", {})
        st.session_state.swaps = cloud_data.get("swaps", [])
        st.session_state.start_date = datetime.strptime(cloud_data.get("start_date"), "%Y-%m-%d").date()
    else:
        st.session_state.groups = DATOS_INICIALES
        st.session_state.punishments, st.session_state.overrides = {}, {}
        st.session_state.role_overrides, st.session_state.statuses = {}, {}
        st.session_state.swaps = []
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

    # Miembros originales (Filtrar los que hoy salen por Traslado)
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

    # Miembros que entran por traslado
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
        pdf.set_font("helvetica", '', 11)
        pdf.cell(190, 6, f"GUARDIA DE PREVENCION - FECHA: {curr.strftime('%d/%m/%Y')}", align='C', ln=True)
        
        g_data = get_processed_guard_for_date(curr)
        pdf.ln(10); pdf.set_font("helvetica", 'B', 12); pdf.cell(190, 10, f"GRUPO EN SERVICIO: {g_data['name']}", ln=True)
        
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
        curr += timedelta(days=1)
    return bytes(pdf.output())

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=150)
        else: st.image(ESCUDO_OFICIAL, width=150)
        st.markdown("<h2 style='text-align:center;'>CONTROL DE GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE ACCESO", type="password", key="login_pwd")
        if st.button("INGRESAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Acceso Denegado")
else:
    # --- MENÚ LATERAL ---
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=140)
        else: st.image(ESCUDO_OFICIAL, width=120)
        st.markdown("<h3 style='color:white; text-align:center; font-size:0.8rem;'>IESP SISTEMA 2026</h3>", unsafe_allow_html=True)
        
        # MONITOR DE NUBE
        if BASE_URL: st.success("☁️ Nube Conectada")
        else: st.error("❌ Sin Configuración Cloud")

        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Cambios Autorizados", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        st.divider()
        if st.button("🔄 ACTUALIZAR DATOS"):
            cloud = load_from_cloud()
            if cloud: st.session_state.update(cloud); st.success("Sincronizado"); st.rerun()
        if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()

    # --- CABECERA ---
    header_col1, header_col2 = st.columns([1, 9])
    with header_col1:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=70)
        else: st.image(ESCUDO_OFICIAL, width=70)
    with header_col2:
        st.markdown("""<h1 style="color:#0f172a; font-weight:800; margin:0; padding-top:10px;">Diagramación de Guardia Sincronizada</h1>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        today_key = str(datetime.now().date())
        expired = [s for s in st.session_state.swaps if s['date'] < today_key]
        for ex in expired:
            st.markdown(f"<div class='alert-banner'>⚠️ AVISO: El cambio de <b>{ex['cadet_id']}</b> caducó. Borrar de 'Cambios Autorizados' para normalizar.</div>", unsafe_allow_html=True)

        sel_date = st.date_input("FECHA SELECCIONADA", datetime.now().date(), key="dash_date_pick"); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><b>Guardia en Turno</b><br>{gi['name']}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><b>Suplentes Activos</b><br>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><b>Novedades Hoy</b><br>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'] and 'CAMBIO' not in c['situacion'])}</div>", unsafe_allow_html=True)
        
        df_display = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] or 'CAMBIO' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=(len(df_display)+1)*35+10, key=f"tbl_dash_{date_key}")
        
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

    elif menu == "📂 Reportes PDF":
        st.markdown("### 📂 Generador de Planillas Oficiales")
        s_rep = st.date_input("Inicio", datetime.now().date(), key="rep_s")
        e_rep = st.date_input("Fin", datetime.now().date(), key="rep_e")
        if st.button("🚀 GENERAR PDF"):
            pdf_bytes = generate_official_pdf(s_rep, e_rep)
            st.download_button("⬇️ DESCARGAR", pdf_bytes, f"Diagramacion_{s_rep}.pdf", "application/pdf")

    elif menu == "🔄 Cambios Autorizados":
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                sw_date = st.date_input("Fecha Servicio", datetime.now().date(), key="sw_d")
                all_list = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_list.append({"label": f"{c['nombre']} ({g['name']})", "obj": c, "oname": g['name']})
                sel_c = st.selectbox("Cadete", range(len(all_list)), format_func=lambda x: all_list[x]['label'], key="sw_c")
                target_g = st.selectbox("Destino", [g['name'] for g in st.session_state.groups], key="sw_g")
                if st.button("REGISTRAR"):
                    st.session_state.swaps.append({"date": str(sw_date), "cadet_id": all_list[sel_c]['obj']['nombre'], "cadet_obj": all_list[sel_c]['obj'], "orig_group": all_list[sel_c]['oname'], "target_group": target_g})
                    sync_to_cloud(); st.rerun()
        with cb:
            for idx, s in enumerate(st.session_state.swaps):
                c1, c2 = st.columns([3, 1]); c1.write(f"📅 {s['date']} | {s['cadet_id']} -> {s['target_group']}")
                if c2.button("🗑️", key=f"sw_{idx}"): st.session_state.swaps.pop(idx); sync_to_cloud(); st.rerun()

    elif menu == "👥 Redistribución":
        for i_red, g_red in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g_red['name']}"):
                df_red = pd.DataFrame(g_red['cadets'])
                df_red_res = st.data_editor(df_red, num_rows="dynamic", key=f"editor_red_{i_red}", use_container_width=True)
                if st.button(f"Guardar Cambios {g_red['id']}", key=f"btn_red_save_{i_red}"):
                    st.session_state.groups[i_red]['cadets'] = df_red_res.to_dict('records'); sync_to_cloud(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        new_start = st.date_input("Fecha Inicio Ciclo", st.session_state.start_date, key="aj_d")
        if st.button("GUARDAR CONFIGURACIÓN"):
            st.session_state.start_date = new_start; sync_to_cloud(); st.success("Sincronizado")
        st.divider()
        if st.button("⚡ RESTABLECER NÓMINA ORIGINAL"):
            st.session_state.groups = DATOS_INICIALES
            sync_to_cloud(); st.rerun()

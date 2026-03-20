import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import os
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IESP - GESTIÓN DE DIAGRAMACIÓN DE GUARDIA",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# --- ESTILO CSS PRO 2026 ---
def inject_modern_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        .main { background-color: #f8fafc; }
        
        /* SIDEBAR PRO */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
        
        .header-container {
            background: white; padding: 1.5rem 2.5rem; border-radius: 32px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.02); margin-bottom: 2rem;
            display: flex; justify-content: space-between; align-items: center; border: 1px solid #f1f5f9;
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
            box-shadow: 0 4px 20px rgba(0,0,0,0.01);
        }
        .alert-banner {
            background: #fef2f2; border: 1px solid #fee2e2; padding: 1.2rem; border-radius: 20px;
            color: #991b1b; font-weight: 700; margin-bottom: 1.5rem; border-left: 6px solid #ef4444;
        }
        [data-testid="stDataFrame"] > div { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- CONFIGURACIÓN DE NUBE (FIRESTORE SYNC) ---
def get_cloud_config():
    try:
        config = json.loads(st.secrets["__firebase_config"])
        project_id = config.get("projectId")
        app_id = st.secrets.get("__app_id", "iesp-guardia-final")
        return project_id, app_id
    except: return None, "iesp-app"

PROJECT_ID, APP_ID = get_cloud_config()
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/artifacts/{APP_ID}/public/data" if PROJECT_ID else None

def load_from_cloud():
    if not BASE_URL: return None
    try:
        resp = requests.get(f"{BASE_URL}/persistence/current_state")
        if resp.status_code == 200:
            data = resp.json().get("fields", {})
            return json.loads(data.get("json_data", {}).get("stringValue", "{}"))
    except: pass
    return None

def save_to_cloud(data):
    if not BASE_URL: return
    try:
        payload = data.copy()
        if isinstance(payload.get("start_date"), (datetime, datetime.date)):
            payload["start_date"] = str(payload["start_date"])
        body = {"fields": {"json_data": {"stringValue": json.dumps(payload)}}}
        requests.patch(f"{BASE_URL}/persistence/current_state", json=body)
    except: pass

# --- DATOS INSTITUCIONALES INTEGRADOS (9 GRUPOS COMPLETOS) ---
DATOS_GRUPOS_BASE = [
    {
        "id": "G1",
        "name": "GRUPO N° 1 de II° Año",
        "cadets": [
            {"n": 1, "nombre": "Forales Emanuel", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Oliva Samuel", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Abregú Francisco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Acosta Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Agüero Alexis", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Albarracín Federico", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Albornoz Lautaro", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Aranda Héctor", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Bazán Hernán", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "Brizuela Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "Bustamante Marcelo", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Cantos Núñez Javier", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Castro Miguel", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 14, "nombre": "Cequeira Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    },
    {
        "id": "G2",
        "name": "GRUPO N° 2 de II° Año",
        "cadets": [
            {"n": 1, "nombre": "Mercado Marcelo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Galván Maira", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Ibarra Martina", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Issa Tiara", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Medina Emilse", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Coronel Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Cruz Braian", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Fernández Adrián", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Figueroa Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "González Ignacio", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "González Salomón Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Guevara Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Ibáñez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 14, "nombre": "Jaime Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    },
    {
        "id": "G3",
        "name": "GRUPO N° 3 de II° Año",
        "cadets": [
            {"n": 1, "nombre": "Argañaraz Patricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Centeno Luis", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Jiménez Gonzalo", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Juárez Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Lagarde Christian", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Lazarte José", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Maldonado Clemente", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Medina Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Medina Vélez Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "Medrano Ángel", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "Mena Aníbal", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Monteros Mateo", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Montes Nahuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    },
    {
        "id": "G4",
        "name": "GRUPO N° 4 de II° Año",
        "cadets": [
            {"n": 1, "nombre": "Gramajo Andrea", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Pintos Patricio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Monteros Brenda", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Montes Eugenia", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Núñez Luciano", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Paliza Joaquín", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Ponze de León Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Quiroga López Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Reyes Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "Reyes Alan", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "Reynoso Martínez Luciano", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Roja Tomás", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Silva Axel", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 14, "nombre": "Sueldo Rodrigo Gastón", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 15, "nombre": "Soria José Lionel", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    },
    {
        "id": "G5",
        "name": "GRUPO N° 1 de III° Año",
        "cadets": [
            {"n": 1, "nombre": "Juárez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Abregú Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Argañaraz Lezcano Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Ávila José", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "Bazán Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "Brandan Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Coronel Carlos", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Diaz Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    },
    {
        "id": "G6",
        "name": "GRUPO N° 2 de III° Año",
        "cadets": [
            {"n": 1, "nombre": "Carrillo Victoria", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Salas Murua", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Ocaranza Sofia", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Paz María", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Carrizo Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Chávez Máximo", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Del Lugo Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Del Lugo Guillermo", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Dib Jorge", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "Fernández Ariel", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "Frías Ariel", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Gerez Víctor", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Girvau Mauricio", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 14, "nombre": "Gómez Enrique", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    },
    {
        "id": "G7",
        "name": "GRUPO N° 3 de III° Año",
        "cadets": [
            {"n": 1, "nombre": "Alvarado Mauricio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Valdez Federico", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Gómez Ramirez Marcos", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Guardia Cesar", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Iramain Guillermo", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Juárez Tomás", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Las Heras Cabocota Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Lazarte Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Luna Jorge", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "Medina Nicolás", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "Miro Gastón", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Nieva Juan", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Páez Fernández Manuel", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    },
    {
        "id": "G8",
        "name": "GRUPO N° 4 de III° Año",
        "cadets": [
            {"n": 1, "nombre": "Suárez Franco", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Alabarce Sergio", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Salas Josefina", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Quinteros Flabia", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Palomar Esteban", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Ramos Tobías", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Rodríguez Matías", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Rojas Leonel", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Ruiz Felipe", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "Ruiz Elio", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "Ruiz Fabricio", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Ruiz Lozano Emanuel", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Soria Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    },
    {
        "id": "G9",
        "name": "GRUPO N° 5 de III° Año",
        "cadets": [
            {"n": 1, "nombre": "Aybar Eduardo", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
            {"n": 2, "nombre": "Quiroga Melina", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
            {"n": 3, "nombre": "Montero Irina", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 4, "nombre": "Moreno Karen", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 5, "nombre": "Sotelo Leandro", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 6, "nombre": "Sotelo Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 7, "nombre": "Verón González", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 8, "nombre": "Villagra Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 9, "nombre": "Villalba David", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 10, "nombre": "Vizcarra José", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 11, "nombre": "Ybarra Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 12, "nombre": "Zamorano Sergio", "curso": "IIº Año", "funcion": "Cadete Apostado"},
            {"n": 13, "nombre": "Zarate Medina Lucas", "curso": "IIº Año", "funcion": "Cadete Apostado"}
        ]
    }
]

# --- INICIALIZACIÓN ---
if 'initialized' not in st.session_state:
    cloud_data = load_from_cloud()
    if cloud_data:
        st.session_state.groups = cloud_data.get("groups", DATOS_GRUPOS_BASE)
        st.session_state.punishments = cloud_data.get("punishments", {})
        st.session_state.overrides = cloud_data.get("overrides", {})
        st.session_state.role_overrides = cloud_data.get("role_overrides", {})
        st.session_state.statuses = cloud_data.get("statuses", {})
        st.session_state.swaps = cloud_data.get("swaps", [])
        # Sincronizar fecha a hoy 19/03/2026 para iniciar el ciclo
        st.session_state.start_date = datetime(2026, 3, 19).date()
    else:
        st.session_state.groups = DATOS_GRUPOS_BASE
        st.session_state.punishments, st.session_state.overrides = {}, {}
        st.session_state.role_overrides, st.session_state.statuses = {}, {}
        st.session_state.swaps = []
        st.session_state.start_date = datetime(2026, 3, 19).date()
    st.session_state.initialized = True

def sync():
    save_to_cloud({
        "groups": st.session_state.groups,
        "punishments": st.session_state.punishments,
        "overrides": st.session_state.overrides,
        "role_overrides": st.session_state.role_overrides,
        "statuses": st.session_state.statuses,
        "swaps": st.session_state.swaps,
        "start_date": str(st.session_state.start_date)
    })

def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    processed = []
    
    day_overrides = st.session_state.overrides.get(date_key, {})
    day_statuses = st.session_state.statuses.get(date_key, {})
    day_role_overrides = st.session_state.role_overrides.get(date_key, {})
    swaps = st.session_state.get('swaps', [])

    # 1. Cadetes originales (Filtrando los que hoy tienen "Cambio Autorizado" a otro grupo)
    for i, c in enumerate(base_group['cadets']):
        cd = c.copy()
        titular_nombre = cd['nombre']
        
        # Verificar si hoy salió de este grupo por cambio autorizado
        if any(s for s in swaps if s['cadet_id'] == titular_original and s['date'] == date_key and s['orig_group'] == base_group['name']):
            continue

        # Aplicar Suplencias
        if str(i) in day_overrides:
            suplente = day_overrides[str(i)]
            cd['nombre'] = f"🔄 {suplente['nombre']}"
            cd['situacion'] = f"SUPLENTE POR {titular_nombre.upper()}"
            cd['is_sub'] = True
        else:
            cd['situacion'] = day_statuses.get(str(i), "PRESENTE")
            cd['is_sub'] = False
            
        # Aplicar Funciones
        if str(i) in day_role_overrides:
            cd['funcion'] = day_role_overrides[str(i)]
            
        processed.append(cd)

    # 2. Agregar Cadetes que entran por "Cambio Autorizado"
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

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>SISTEMA DE GUARDIA IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE ACCESO", type="password")
        if st.button("ENTRAR AL SISTEMA"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Acceso Denegado")
else:
    with st.sidebar:
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Cambios Autorizados", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        if st.button("SALIR"): st.session_state.logged_in = False; st.rerun()

    st.markdown("""<div class="header-container"><h1 class="header-title">I.E.S.P. Gestión Sincronizada 2026</h1></div>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        # ALERTA DE RESTAURACIÓN (CAMBIOS VENCIDOS)
        today_key = str(datetime.now().date())
        expired_swaps = [s for s in st.session_state.swaps if s['date'] < today_key]
        if expired_swaps:
            for ex in expired_swaps:
                st.markdown(f"""<div class="alert-banner">⚠️ RESTAURACIÓN: El cambio de <b>{ex['cadet_id']}</b> ha caducado. Favor eliminarlo de 'Cambios Autorizados' para normalizar su guardia original.</div>""", unsafe_allow_html=True)

        sel_date = st.date_input("FECHA SELECCIONADA", datetime.now().date()); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Guardia Hoy</div><div class='metric-value'>{gi['name']}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Suplencias</div><div class='metric-value'>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Novedades</div><div class='metric-value'>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'] and 'CAMBIO' not in c['situacion'])}</div></div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 Nómina del Personal")
        df_display = pd.DataFrame([{"N°": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] or 'SUPLENTE' in c['situacion'] or 'CAMBIO' in c['situacion'] else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                c_idx = st.selectbox("Personal", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'])
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"])
                if st.button("ACTUALIZAR ESTADO"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][str(c_idx)] = nuevo_st; sync(); st.rerun()
        with col_m2:
            with st.container(border=True):
                st.write("**🎭 Función**")
                c_idx_f = st.selectbox("Cadete", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="f_sel")
                n_f = st.text_input("Nueva Función")
                if st.button("ASIGNAR FUNCIÓN"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][str(c_idx_f)] = n_f; sync(); st.rerun()
        with col_m3:
            with st.container(border=True):
                st.write("**🔄 Suplente**")
                target = st.selectbox("Titular", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="t_sel")
                all_c = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_c.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
                suplente = st.selectbox("Buscar Suplente", range(len(all_c)), format_func=lambda x: all_c[x]['label'])
                if st.button("APLICAR REEMPLAZO"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][str(target)] = all_c[suplente]['obj']; sync(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        cols = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            with cols[i % 3]:
                st.markdown(f"""<div style="background:white; border-radius:24px; padding:1.2rem; border:1px solid #f1f5f9; margin-bottom:1rem;">
                    <div style="background:#0f172a; color:white; padding:0.5rem; border-radius:10px; text-align:center; font-weight:800; font-size:0.8rem;">{g['name']}</div>""", unsafe_allow_html=True)
                for cadet in g['cadets']:
                    st.markdown(f"<div style='font-size:0.75rem; border-bottom:1px solid #f8fafc; padding:3px;'><b>• {cadet['nombre']}</b></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🔄 Cambios Autorizados":
        st.markdown("### 🔄 Registro de Cambios Temporales")
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                swap_date = st.date_input("Fecha del Cambio", datetime.now().date())
                all_list = []
                for g in st.session_state.groups:
                    for c in g['cadets']: all_list.append({"label": f"{c['nombre']} (Orig: {g['name']})", "obj": c, "oname": g['name']})
                sel_c = st.selectbox("Cadete a Trasladar", range(len(all_list)), format_func=lambda x: all_list[x]['label'])
                target_g = st.selectbox("Guardia de Destino", [g['name'] for g in st.session_state.groups])
                if st.button("REGISTRAR TRASLADO"):
                    st.session_state.swaps.append({"date": str(swap_date), "cadet_id": all_list[sel_c]['obj']['nombre'], "cadet_obj": all_list[sel_c]['obj'], "orig_group": all_list[sel_c]['oname'], "target_group": target_g})
                    sync(); st.rerun()
        with cb:
            st.write("**Lista de Traslados Activos**")
            for idx, s in enumerate(st.session_state.swaps):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📅 {s['date']} | **{s['cadet_id']}** -> {s['target_group']}")
                if c2.button("🗑️", key=f"sw_{idx}"): st.session_state.swaps.pop(idx); sync(); st.rerun()

    elif menu == "⚖️ Guardia Castigo":
        pk = str(st.date_input("Fecha", datetime.now().date()))
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_p = st.selectbox("Grupo", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
                c_p = st.selectbox("Cadete", range(len(st.session_state.groups[g_p]['cadets'])), format_func=lambda x: st.session_state.groups[g_p]['cadets'][x]['nombre'])
                if st.button("AGREGAR REFUERZO"):
                    if pk not in st.session_state.punishments: st.session_state.punishments[pk] = []
                    st.session_state.punishments[pk].append(st.session_state.groups[g_p]['cadets'][c_p]); sync(); st.rerun()
        with cb:
            st.write("**Lista de Refuerzos**")
            for idx, p in enumerate(st.session_state.punishments.get(pk, [])):
                st.write(f"• {p['nombre']} ({p['curso']})")

    elif menu == "📂 Reportes PDF":
        s_rep = st.date_input("Inicio", datetime.now().date()); e_rep = st.date_input("Fin", datetime.now().date())
        if st.button("🚀 GENERAR PLANILLAS"):
            pdf_bytes = generate_official_pdf(s_rep, e_rep)
            st.download_button("⬇️ DESCARGAR PDF", pdf_bytes, f"Planillas_{s_rep}.pdf", "application/pdf")

    elif menu == "👥 Redistribución":
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"📝 Editar {g['name']}"):
                df_ed = st.data_editor(pd.DataFrame(g['cadets']), num_rows="dynamic", key=f"ed_{i}", use_container_width=True)
                if st.button(f"Guardar Cambios {g['id']}"):
                    st.session_state.groups[i]['cadets'] = df_ed.to_dict('records'); sync(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        st.markdown("### ⚙️ Configuración del Ciclo")
        new_start = st.date_input("Fecha Inicio Ciclo (Actualmente 19/03)", st.session_state.start_date)
        if st.button("GUARDAR CONFIGURACIÓN"):
            st.session_state.start_date = new_start; sync(); st.success("Sincronizado")

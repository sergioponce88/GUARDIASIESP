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

# --- AJUSTE DE HORA ARGENTINA (UTC-3) ---
def get_now_tucuman():
    return datetime.now() - timedelta(hours=3)

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
        
        [data-testid="stDataFrame"] > div { border-radius: 20px !important; border: 1px solid #e2e8f0 !important; }
        
        .logo-box {
            background: #ef4444; color: white; padding: 15px;
            border-radius: 15px; text-align: center; font-weight: 800;
            margin-bottom: 20px; border: 2px solid rgba(255,255,255,0.2);
        }

        .guard-header {
            background-color: #0f172a; 
            padding: 15px 25px; 
            border-radius: 20px; 
            margin-bottom: 20px;
            border-left: 8px solid #ef4444;
        }
        .guard-header h3 { color: white; margin: 0; font-size: 1.1rem; font-weight: 800; text-transform: uppercase; }
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

# --- NÓMINA OFICIAL TOTAL ---
def get_official_groups():
    return [
        {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [
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
        ]},
        {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [
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
        ]},
        {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [
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
        ]},
        {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [
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
        ]},
        {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [
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
        ]},
        {"id": "G6", "name": "GRUPO N° 2 de III° Año", "cadets": [
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
        ]},
        {"id": "G7", "name": "GRUPO N° 3 de III° Año", "cadets": [
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
        ]},
        {"id": "G8", "name": "GRUPO N° 4 de III° Año", "cadets": [
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
        ]},
        {"id": "G9", "name": "GRUPO N° 5 de III° Año", "cadets": [
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
        ]}
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
        cloud_groups = data.get("groups", [])
        if len(cloud_groups) > 0 and len(cloud_groups[0].get("cadets", [])) < 10:
            st.session_state.groups = get_official_groups()
        else:
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
    
    day_st = st.session_state.get('statuses', {}).get(date_key, {})
    day_ov = st.session_state.get('overrides', {}).get(date_key, {})
    day_ro = st.session_state.get('role_overrides', {}).get(date_key, {})
    punishments = st.session_state.get('punishments', {}).get(date_key, [])
    extras = st.session_state.get('extra_cadets', {}).get(date_key, [])
    day_removals = st.session_state.get('removals', {}).get(date_key, [])

    for c in base_group['cadets']:
        c_name = c.get('nombre', '').strip()
        if c_name in day_removals: continue
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
            cad_swap['nombre'] = f"⚡ {cad_swap['nombre']}"; cad_swap['situacion'] = f"INTERCAMBIO"; processed.append(cad_swap)
            
    for p in punishments:
        cad_p = p.copy()
        cad_p['nombre'] = f"⚖️ {cad_p['nombre']}"; cad_p['situacion'] = "GUARDIA CASTIGO"; processed.append(cad_p)

    for e in extras:
        cad_e = e.copy()
        cad_e['nombre'] = f"➕ {cad_e['nombre']}"; cad_e['situacion'] = "REFUERZO"; processed.append(cad_e)
            
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- GENERADOR DE PDF OPERATIVO ---
def generate_pdf(start_date, end_date):
    pdf = FPDF()
    curr = start_date
    while curr <= end_date:
        pdf.add_page()
        # Encabezado
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(190, 8, "INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICIA", 0, 1, 'C')
        pdf.set_font("Helvetica", '', 10)
        pdf.cell(190, 6, f"DIAGRAMACION OPERATIVA DE GUARDIA - FECHA: {curr.strftime('%d/%m/%Y')}", 0, 1, 'C')
        
        g_data = get_processed_guard_for_date(curr)
        pdf.ln(5)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(190, 10, f"SERVICIO EN TURNO: {g_data['name']}", 0, 1, 'L')
        
        # Tabla
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Helvetica", 'B', 9)
        pdf.cell(10, 8, "N", 1, 0, 'C', True)
        pdf.cell(80, 8, "Apellido y Nombre", 1, 0, 'C', True)
        pdf.cell(40, 8, "Funcion", 1, 0, 'C', True)
        pdf.cell(30, 8, "Situacion", 1, 0, 'C', True)
        pdf.cell(30, 8, "Firma", 1, 1, 'C', True)
        
        pdf.set_font("Helvetica", '', 8)
        for i, c in enumerate(g_data['cadets']):
            pdf.cell(10, 7, str(i+1), 1, 0, 'C')
            # Sanitizar nombres para PDF
            nombre_pdf = c['nombre'].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(80, 7, nombre_pdf, 1, 0, 'L')
            funcion_pdf = c['funcion'].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(40, 7, funcion_pdf, 1, 0, 'C')
            situacion_pdf = c['situacion'].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(30, 7, situacion_pdf, 1, 0, 'C')
            pdf.cell(30, 7, "", 1, 1)
        
        curr += timedelta(days=1)
    return pdf.output()

# --- INTERFAZ ---
if not st.session_state.get('logged_in', False):
    _, col_log, _ = st.columns([1, 1.4, 1])
    with col_log:
        st.markdown("<div style='text-align:center; font-size:80px;'>🛡️</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#0f172a;'>MANDO IESP</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE", type="password")
        if st.button("INGRESAR"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
else:
    all_cadets_registry = []
    for g in st.session_state.groups:
        for c in g['cadets']:
            all_cadets_registry.append({"nombre": c['nombre'], "grupo": g['name'], "curso": c['curso'], "obj": c})

    with st.sidebar:
        st.markdown("<div class='logo-box'>CONTROL DE GUARDIA PRO<br><span style='font-size:0.7rem; font-weight:400;'>I.E.S.P. TUCUMÁN</span></div>", unsafe_allow_html=True)
        st.info(f"🕒 **Sello Nube:**\n`{st.session_state.get('data_timestamp', '00:00:00')}`")
        st.success(f"☁️ **Estado:**\n`{st.session_state.get('last_sync_status', 'Conectado')}`")
        st.divider()
        menu = st.radio("MENÚ", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "🔄 Intercambio", "📊 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
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

    st.markdown(f"<h1 style='color:#0f172a; font-weight:800; margin-top:10px;'>Mando Operativo IESP <span style='color:#ef4444'>PRO</span></h1>", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        sel_date = st.date_input("FECHA SELECCIONADA", get_now_tucuman().date(), key="dash_date")
        date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-card'><p>Guardia Hoy</p><h3>{gi['name']}</h3></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-card'><p>Efectivos</p><h3>{len(gi['cadets'])} Personal</h3></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-card'><p>Novedades</p><h3>{sum(1 for c in gi['cadets'] if 'PRESENTE' not in c['situacion'])} Reportes</h3></div>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='guard-header'><h3>📋 Listado de Guardia: {gi['name']}</h3></div>", unsafe_allow_html=True)
        
        df_view = pd.DataFrame([{"Orden": i+1, "Nombre": f"{'✅' if 'PRESENTE' in c['situacion'] else '⚠️'} {c['nombre']}", "Rol": c['funcion'], "Situación": c['situacion']} for i, c in enumerate(gi['cadets'])])
        st.dataframe(df_view, use_container_width=True, hide_index=True, height=400)
        
        st.markdown("### 🛠️ Herramientas de Mando Directo")
        ca, cf, cs, cx, cr = st.columns(5)
        list_pure = [c['nombre'].replace("✅ ","").replace("⚠️ ","").replace("⚡ ","").replace("🔄 ","").replace("⚖️ ","").replace("➕ ","").strip() for c in gi['cadets']]
        
        with ca:
            with st.container(border=True):
                st.write("**📝 Asistencia**")
                c_as = st.selectbox("Efectivo", list_pure, key="as_s")
                n_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"], key="st_s")
                if st.button("Fijar"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][c_as] = n_st
                    save_cloud_data(); st.rerun()
        with cf:
            with st.container(border=True):
                st.write("**🎭 Función**")
                c_fu = st.selectbox("Efectivo", list_pure, key="fu_s")
                n_fu = st.text_input("Rol", placeholder="Centinela", key="fu_v")
                if st.button("Asignar"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][c_fu] = n_fu
                    save_cloud_data(); st.rerun()
        with cs:
            with st.container(border=True):
                st.write("**🔄 Suplencia**")
                tit = st.selectbox("Titular", list_pure, key="su_s")
                idx_sup = st.selectbox("Suplente", range(len(all_cadets_registry)), format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="su_all")
                if st.button("Reemplazar"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][tit] = all_cadets_registry[idx_sup]['obj']
                    save_cloud_data(); st.rerun()
        with cx:
            with st.container(border=True):
                st.write("**➕ Refuerzo**")
                idx_ex = st.selectbox("Sumar", range(len(all_cadets_registry)), format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})", key="ex_all")
                ex_rol = st.text_input("Cargo", value="Refuerzo", key="ex_rol")
                if st.button("Sumar"):
                    if date_key not in st.session_state.extra_cadets: st.session_state.extra_cadets[date_key] = []
                    new_ex = all_cadets_registry[idx_ex]['obj'].copy()
                    new_ex['funcion'] = ex_rol
                    st.session_state.extra_cadets[date_key].append(new_ex)
                    save_cloud_data(); st.rerun()
        with cr:
            with st.container(border=True):
                st.write("**❌ Quitar**")
                c_rem = st.selectbox("Baja de Lista", list_pure, key="rem_s")
                if st.button("Quitar"):
                    if date_key not in st.session_state.removals: st.session_state.removals[date_key] = []
                    st.session_state.removals[date_key].append(c_rem)
                    save_cloud_data(); st.rerun()

        if date_key in st.session_state.removals and st.session_state.removals[date_key]:
            with st.expander("🗑️ Ver Personal Quitado de esta Guardia"):
                for idx_r, name_r in enumerate(st.session_state.removals[date_key]):
                    c1, c2 = st.columns([4,1])
                    c1.write(f"• {name_r}")
                    if c2.button("Restablecer", key=f"re_btn_{idx_r}"):
                        st.session_state.removals[date_key].pop(idx_r); save_cloud_data(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Nóminas Permanentes (Word Oficial)")
        if st.button("⚠️ RESTABLECER TODA LA NÓMINA OFICIAL (WORD)", type="secondary", use_container_width=True):
            st.session_state.groups = get_official_groups()
            save_cloud_data(); st.success("Lista oficial del Word cargada con éxito."); st.rerun()
        st.divider()
        cols = st.columns(3)
        for i, g in enumerate(st.session_state.groups):
            with cols[i % 3]:
                with st.expander(f"Nómina: {g['name']}", expanded=True):
                    st.table(pd.DataFrame(g['cadets'])[["nombre", "curso", "funcion"]])

    elif menu == "⚖️ Guardia Castigo":
        pk_cast = str(st.date_input("Fecha Cumplimiento", get_now_tucuman().date()))
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                idx_p = st.selectbox("Sancionado", range(len(all_cadets_registry)), format_func=lambda x: f"{all_cadets_registry[x]['nombre']} ({all_cadets_registry[x]['grupo']})")
                if st.button("AGREGAR CASTIGO"):
                    if pk_cast not in st.session_state.punishments: st.session_state.punishments[pk_cast] = []
                    st.session_state.punishments[pk_cast].append(all_cadets_registry[idx_p]['obj'])
                    save_cloud_data(); st.rerun()
        with c2:
            st.write(f"**Personal en Castigo para {pk_cast}:**")
            if pk_cast in st.session_state.punishments:
                for p in st.session_state.punishments[pk_cast]: st.write(f"❌ {p['nombre']} ({p['curso']})")

    elif menu == "🔄 Intercambio":
        d_sw = st.date_input("Fecha Servicio", get_now_tucuman().date())
        ga_idx = st.selectbox("Grupo A", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'], key="ga")
        ca_idx = st.selectbox("Cadete de A", range(len(st.session_state.groups[ga_idx]['cadets'])), format_func=lambda x: st.session_state.groups[ga_idx]['cadets'][x]['nombre'], key="ca")
        target_gb = st.selectbox("Grupo Destino", [g['name'] for g in st.session_state.groups], key="tgb")
        if st.button("EJECUTAR TRASPASO"):
            cad_a = st.session_state.groups[ga_idx]['cadets'][ca_idx]
            st.session_state.swaps.append({"date": str(d_sw), "cadet_id": cad_a['nombre'], "cadet_obj": cad_a, "orig_group": st.session_state.groups[ga_idx]['name'], "target_group": target_gb})
            save_cloud_data(); st.rerun()

    elif menu == "📊 Reportes PDF":
        st.markdown("### 📊 Generador de Diagramaciones Oficiales")
        col1, col2 = st.columns(2)
        s_rep = col1.date_input("Desde", get_now_tucuman().date())
        e_rep = col2.date_input("Hasta", get_now_tucuman().date())
        
        if st.button("🚀 GENERAR PLANILLA PDF"):
            with st.spinner("Generando reporte..."):
                pdf_bytes = generate_pdf(s_rep, e_rep)
                st.download_button(
                    label="⬇️ DESCARGAR ARCHIVO PDF",
                    data=pdf_bytes,
                    file_name=f"Diagramacion_IESP_{s_rep}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("Reporte generado con éxito.")

    elif menu == "👥 Redistribución":
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g['name']}"):
                res = st.data_editor(pd.DataFrame(g['cadets']), num_rows="dynamic", key=f"ed_grid_{i}", use_container_width=True)
                if st.button(f"Confirmar en {g['id']}", key=f"btn_save_{i}"):
                    st.session_state.groups[i]['cadets'] = res.to_dict('records'); save_cloud_data(); st.rerun()

    elif menu == "⚙️ Ajustes":
        st.session_state.start_date = st.date_input("Inicio del Ciclo", st.session_state.start_date)
        if st.button("GUARDAR"): save_cloud_data(); st.success("Ajustado")

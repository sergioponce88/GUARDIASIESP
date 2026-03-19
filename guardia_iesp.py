import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import os

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
        .main { background-color: #fcfdfe; }
        
        /* SIDEBAR PRO */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e3a8a 0%, #0f172a 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        [data-testid="stSidebar"] * { color: #f8fafc !important; }

        /* HEADER BAR */
        .header-container {
            background: white;
            padding: 1.5rem 2rem;
            border-radius: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #f1f5f9;
        }
        .header-title {
            color: #1e3a8a;
            font-weight: 800;
            font-size: 1.4rem;
            letter-spacing: -0.02em;
            margin: 0;
        }

        /* BOTONES PRO */
        div.stButton > button {
            background: #ef4444 !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 700 !important;
            border-radius: 16px !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase;
            width: 100% !important;
            box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.2);
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            background: #dc2626 !important;
            box-shadow: 0 20px 25px -5px rgba(239, 68, 68, 0.3);
        }

        /* TARJETAS MÉTRICAS */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 24px;
            border: 1px solid #f1f5f9;
            box-shadow: 0 10px 30px rgba(0,0,0,0.02);
        }
        .metric-label { color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
        .metric-value { color: #0f172a; font-size: 1.4rem; font-weight: 800; margin-top: 0.5rem; }

        /* GRUPOS CARD */
        .group-card {
            background: white;
            border-radius: 28px;
            overflow: hidden;
            border: 1px solid #f1f5f9;
            box-shadow: 0 10px 25px rgba(0,0,0,0.03);
            margin-bottom: 2rem;
        }
        .group-header {
            background: #0f172a;
            padding: 1rem;
            color: white;
            text-align: center;
            font-weight: 800;
            font-size: 0.85rem;
        }
        .cadet-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.7rem 1.2rem;
            border-bottom: 1px solid #f8fafc;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 10px;
            display: inline-block;
        }
        .dot-blue { background-color: #2563eb; }
        .dot-green { background-color: #10b981; }

        /* LOGIN BOX */
        .login-box {
            background: white;
            padding: 3rem;
            border-radius: 32px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
            text-align: center;
            border: 1px solid #f1f5f9;
        }
        
        /* ELIMINAR SCROLL EN DATAFRAME */
        [data-testid="stDataFrame"] > div { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- PERSISTENCIA DE DATOS ---
DB_FILE = "datos_guardia.json"
LOGO_FILE = "logo_iesp.png"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "start_date" in data:
                    data["start_date"] = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
                return data
        except: return None
    return None

def save_data():
    data_to_save = {
        "groups": st.session_state.groups,
        "punishments": st.session_state.punishments,
        "overrides": st.session_state.overrides,
        "role_overrides": st.session_state.role_overrides,
        "statuses": st.session_state.statuses,
        "start_date": st.session_state.start_date.strftime("%Y-%m-%d")
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# --- INICIALIZACIÓN ---
if 'groups' not in st.session_state:
    saved = load_data()
    if saved:
        st.session_state.groups = saved["groups"]
        st.session_state.punishments = saved["punishments"]
        st.session_state.overrides = saved["overrides"]
        st.session_state.role_overrides = saved.get("role_overrides", {})
        st.session_state.statuses = saved.get("statuses", {})
        st.session_state.start_date = saved["start_date"]
    else:
        st.session_state.groups = [
            {"id": "G1", "name": "GUARDIA 1 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G1", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(14)]},
            {"id": "G5", "name": "GUARDIA 1 de III° Año", "cadets": [
                {"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
                {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
                {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 5, "nombre": "Abregu Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 8, "nombre": "Arganaraz Lezcano Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"}
            ]},
            {"id": "G2", "name": "GUARDIA 2 de II° Año", "cadets": []},
            {"id": "G3", "name": "GUARDIA 3 de II° Año", "cadets": []},
            {"id": "G4", "name": "GUARDIA 4 de II° Año", "cadets": []},
            {"id": "G6", "name": "GUARDIA 2 de III° Año", "cadets": []},
            {"id": "G7", "name": "GUARDIA 3 de III° Año", "cadets": []},
            {"id": "G8", "name": "GUARDIA 4 de III° Año", "cadets": []},
            {"id": "G9", "name": "GUARDIA 5 de III° Año", "cadets": []}
        ]
        st.session_state.punishments = {}
        st.session_state.overrides = {}
        st.session_state.role_overrides = {}
        st.session_state.statuses = {}
        st.session_state.start_date = datetime(2026, 3, 15).date()

# --- LÓGICA DE PROCESAMIENTO CENTRALIZADA ---
def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    
    processed_cadets = []
    for i, c in enumerate(base_group['cadets']):
        cadet_data = c.copy()
        
        # 1. Aplicar Reemplazo por Suplente
        if date_key in st.session_state.overrides and str(i) in st.session_state.overrides[date_key]:
            suplente = st.session_state.overrides[date_key][str(i)]
            cadet_data['nombre'] = f"🔄 {suplente['nombre']} (SUPL)"
            cadet_data['is_sub'] = True
        else:
            cadet_data['is_sub'] = False
            
        # 2. Aplicar Función Temporal
        if date_key in st.session_state.role_overrides and str(i) in st.session_state.role_overrides[date_key]:
            cadet_data['funcion'] = st.session_state.role_overrides[date_key][str(i)]
            
        # 3. Aplicar Situación (Estado)
        cadet_data['situacion'] = st.session_state.statuses.get(date_key, {}).get(str(i), "PRESENTE")
        
        processed_cadets.append(cadet_data)
        
    return {"name": base_group['name'], "cadets": processed_cadets, "id": base_group['id']}

# --- LÓGICA PDF ---
def generate_official_pdf(start_date, end_date):
    pdf = FPDF()
    current_date = start_date
    while current_date <= end_date:
        pdf.add_page()
        if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, 10, 8, 25)
        pdf.set_y(15); pdf.set_font("helvetica", 'B', 16)
        pdf.cell(190, 8, "INSTITUTO DE ENSEÑANZA SUPERIOR DE POLICIA", align='C', ln=True)
        pdf.set_font("helvetica", '', 11)
        pdf.cell(190, 6, f"GUARDIA DE PREVENCION - FECHA: {current_date.strftime('%d/%m/%Y')}", align='C', ln=True)
        
        guard_data = get_processed_guard_for_date(current_date)
        pdf.ln(10); pdf.set_font("helvetica", 'B', 12)
        pdf.cell(190, 10, f"GRUPO EN SERVICIO: {guard_data['name']}", ln=True)
        
        pdf.set_fill_color(230, 230, 230); pdf.set_font("helvetica", 'B', 10)
        headers = ["N", "Apellido y Nombre", "Curso", "Función", "Situación", "Firma"]
        cols = [10, 55, 25, 40, 30, 30]
        for h, w in zip(headers, cols): pdf.cell(w, 10, h, 1, align='C', fill=True)
        pdf.ln()
        
        pdf.set_font("helvetica", '', 9)
        for c in guard_data['cadets']:
            clean_nom = c['nombre'].encode('latin-1', 'replace').decode('latin-1')
            clean_func = c['funcion'].encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(cols[0], 8, str(c['n']), 1, align='C')
            pdf.cell(cols[1], 8, clean_nom[:35], 1, align='L')
            pdf.cell(cols[2], 8, c['curso'], 1, align='C')
            pdf.cell(cols[3], 8, clean_func, 1, align='C')
            pdf.cell(cols[4], 8, c['situacion'], 1, align='C')
            pdf.cell(cols[5], 8, "", 1, ln=True)
        current_date += timedelta(days=1)
    return bytes(pdf.output())

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=120)
        st.markdown("### GESTIÓN DE GUARDIA")
        pwd = st.text_input("CONTRASEÑA", type="password", placeholder="••••", label_visibility="collapsed")
        if st.button("ENTRAR AL SISTEMA"):
            if pwd == "iesp2026":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Clave Incorrecta")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=100)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        menu = st.radio("NAVEGACIÓN", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        if st.button("SALIR"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown(f"""<div class="header-container"><h1 class="header-title">I.E.S.P. GESTIÓN DE DIAGRAMACIÓN DE GUARDIA</h1><div style="color: #1e3a8a; font-weight: 800; font-size: 0.7rem;">🟢 MODO ONLINE</div></div>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        if st.button("🔄 CORREGIR CICLO DE ROTACIÓN"):
            st.session_state.start_date = datetime(2026, 3, 15).date()
            save_data(); st.rerun()
        
        sel_date = st.date_input("FECHA SELECCIONADA", datetime.now().date())
        date_key = str(sel_date)
        guard_info = get_processed_guard_for_date(sel_date)

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Grupo Actual</div><div class='metric-value'>{guard_info['name']}</div></div>", unsafe_allow_html=True)
        with c2: 
            supl = sum(1 for c in guard_info['cadets'] if c.get('is_sub'))
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Suplentes</div><div class='metric-value'>{supl}</div></div>", unsafe_allow_html=True)
        with c3:
            nov = sum(1 for c in guard_info['cadets'] if c['situacion'] != "PRESENTE")
            st.markdown(f"<div class='metric-card'><div class='metric-label'>Novedades</div><div class='metric-value'>{nov}</div></div>", unsafe_allow_html=True)

        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown("### 📋 Nómina del Personal")
            df_display = pd.DataFrame([
                {
                    "N°": c['n'], 
                    "Nombre": f"{'✅' if c['situacion'] == 'PRESENTE' else '⚠️'} {c['nombre']}", 
                    "Función": c['funcion'],
                    "Situación": c['situacion']
                } for c in guard_info['cadets']
            ])
            h = (len(df_display) + 1) * 35 + 5
            st.dataframe(df_display, use_container_width=True, hide_index=True, height=h)

        with col_r:
            st.markdown("### ⚙️ Gestión Diaria")
            with st.container(border=True):
                st.write("**📝 Situación de Revista**")
                c_idx = st.selectbox("Personal", range(len(guard_info['cadets'])), format_func=lambda x: guard_info['cadets'][x]['nombre'])
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "NOTA MÉDICA", "A.R.T.", "AUSENTE"])
                if st.button("ACTUALIZAR ESTADO"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][str(c_idx)] = nuevo_st
                    save_data(); st.rerun()

            with st.container(border=True):
                st.write("**🎭 Modificar Función**")
                c_idx_role = st.selectbox("Elegir Cadete", range(len(guard_info['cadets'])), format_func=lambda x: guard_info['cadets'][x]['nombre'], key="role_sel")
                nueva_func = st.text_input("Nueva Función", placeholder="Ej: Centinela...")
                if st.button("ASIGNAR FUNCIÓN"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][str(c_idx_role)] = nueva_func
                    save_data(); st.rerun()
            
            with st.container(border=True):
                st.write("**🔄 Reemplazo Suplente**")
                target = st.selectbox("Titular", range(len(guard_info['cadets'])), format_func=lambda x: guard_info['cadets'][x]['nombre'], key="re")
                g_sel = st.selectbox("Grupo Suplente", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
                c_sel = st.selectbox("Elegir Suplente", range(len(st.session_state.groups[g_sel]['cadets'])), format_func=lambda x: st.session_state.groups[g_sel]['cadets'][x]['nombre'])
                if st.button("APLICAR"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][str(target)] = st.session_state.groups[g_sel]['cadets'][c_sel]
                    save_data(); st.rerun()

            if date_key in st.session_state.overrides or date_key in st.session_state.role_overrides:
                if st.button("♻️ RESTABLECER ORIGINALES"):
                    st.session_state.overrides[date_key] = {}
                    st.session_state.role_overrides[date_key] = {}
                    save_data(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Estado Actual de Todos los Grupos")
        st.info("Esta vista muestra la nómina de cada grupo con los cambios aplicados para el día de HOY.")
        today = datetime.now().date()
        today_group_data = get_processed_guard_for_date(today)
        
        cols = st.columns(3)
        for i in range(len(st.session_state.groups)):
            # Calculamos la guardia de cada grupo para hoy (para ver si tiene cambios activos)
            diff = (today - st.session_state.start_date).days
            today_idx = diff % len(st.session_state.groups)
            
            # Si el grupo es el que está de guardia hoy, cargamos sus datos procesados
            if i == today_idx:
                current_g_data = today_group_data
                is_active = True
            else:
                # Si no está de guardia, mostramos su base (o podrías procesarlo también si quisieras)
                current_g_data = {"name": st.session_state.groups[i]['name'], "cadets": st.session_state.groups[i]['cadets'], "id": st.session_state.groups[i]['id']}
                is_active = False

            with cols[i % 3]:
                st.markdown(f"""<div class="group-card"><div class="group-header">{current_g_data['name']}</div><div style="padding:1rem;">""", unsafe_allow_html=True)
                if is_active: st.markdown('<p style="color:#2563eb; font-weight:900; text-align:center; font-size:0.7rem;">⚡ DE SERVICIO HOY (ACTUALIZADO)</p>', unsafe_allow_html=True)
                for cadet in current_g_data['cadets']:
                    dot = "dot-blue" if cadet['n'] <= 2 else "dot-green"
                    nom_f = cadet['nombre']
                    func_f = cadet.get('funcion', 'Cadete')
                    st.markdown(f"""<div class="cadet-row"><span><span class="status-dot {dot}"></span>{nom_f}</span><span style="color:#cbd5e1; font-size:0.6rem; font-weight:800;">{func_f}</span></div>""", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

    elif menu == "⚖️ Guardia Castigo":
        st.markdown("### ⚖️ Gestión de Cadetes de Guardia Castigo")
        p_date = st.date_input("Fecha", datetime.now().date()); pk = str(p_date)
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_p = st.selectbox("Grupo Origen", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
                c_p = st.selectbox("Cadete", range(len(st.session_state.groups[g_p]['cadets'])), format_func=lambda x: st.session_state.groups[g_p]['cadets'][x]['nombre'])
                if st.button("AGREGAR"):
                    if pk not in st.session_state.punishments: st.session_state.punishments[pk] = []
                    st.session_state.punishments[pk].append(st.session_state.groups[g_p]['cadets'][c_p])
                    save_data(); st.rerun()
        with cb:
            for idx, p in enumerate(st.session_state.punishments.get(pk, [])):
                c1, c2 = st.columns([3, 1])
                c1.write(f"• {p['nombre']}")
                if c2.button("🗑️", key=f"d_{idx}"):
                    st.session_state.punishments[pk].pop(idx); save_data(); st.rerun()

    elif menu == "📂 Reportes PDF":
        st.markdown("### 📂 Generación de Documentación")
        c_r1, c_r2 = st.columns(2)
        s_rep = c_r1.date_input("Inicio", datetime.now().date())
        e_rep = c_r2.date_input("Fin", datetime.now().date())
        if st.button("🚀 GENERAR PDF"):
            try:
                pdf_bytes = generate_official_pdf(s_rep, e_rep)
                st.download_button("⬇️ DESCARGAR", pdf_bytes, f"Planilla_{s_rep}.pdf", "application/pdf")
            except Exception as e: st.error(f"Error: {e}")

    elif menu == "👥 Redistribución":
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"📝 Editar {g['name']}"):
                df_editor = st.data_editor(pd.DataFrame(g['cadets']), num_rows="dynamic", key=f"ed_{i}", use_container_width=True)
                if st.button(f"Guardar {g['id']}", key=f"s_{i}"):
                    st.session_state.groups[i]['cadets'] = df_editor.to_dict('records'); save_data(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        n_s = st.date_input("Inicio Ciclo", st.session_state.start_date)
        if st.button("GUARDAR"):
            st.session_state.start_date = n_s; save_data(); st.success("Sincronizado")
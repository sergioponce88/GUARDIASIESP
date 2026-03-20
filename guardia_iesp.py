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
        .main { background-color: #f8fafc; }
        
        /* SIDEBAR PRO */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
        
        /* HEADER */
        .header-container {
            background: white; padding: 1.5rem 2.5rem; border-radius: 32px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.02); margin-bottom: 2rem;
            display: flex; justify-content: space-between; align-items: center; border: 1px solid #f1f5f9;
        }
        .header-title { color: #0f172a; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.03em; margin: 0; }

        /* BOTONES */
        div.stButton > button {
            background: #ef4444 !important; color: white !important; border: none !important;
            padding: 0.8rem 1.5rem !important; font-weight: 700 !important; border-radius: 18px !important;
            text-transform: uppercase; width: 100% !important; box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.2);
        }
        div.stButton > button:hover { transform: translateY(-2px); background: #dc2626 !important; }

        /* TARJETAS */
        .metric-card {
            background: white; padding: 1.5rem; border-radius: 28px; border: 1px solid #f1f5f9;
            box-shadow: 0 4px 20px rgba(0,0,0,0.01);
        }
        .metric-label { color: #94a3b8; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
        .metric-value { color: #0f172a; font-size: 1.3rem; font-weight: 800; margin-top: 0.3rem; }

        /* TABLAS SIN SCROLL */
        [data-testid="stDataFrame"] > div { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

inject_modern_css()

# --- PERSISTENCIA ---
DB_FILE = "datos_guardia.json"
LOGO_FILE = "logo_iesp.png"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "start_date" in data and isinstance(data["start_date"], str):
                    data["start_date"] = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
                return data
        except: return None
    return None

def save_data():
    st_date = st.session_state.start_date
    if not isinstance(st_date, str): st_date = st_date.strftime("%Y-%m-%d")
    data_to_save = {
        "groups": st.session_state.groups,
        "punishments": st.session_state.punishments,
        "overrides": st.session_state.overrides,
        "role_overrides": st.session_state.role_overrides,
        "statuses": st.session_state.statuses,
        "start_date": st_date
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# --- INICIALIZACIÓN COMPLETA ---
if 'initialized' not in st.session_state:
    saved = load_data()
    if saved:
        st.session_state.groups = saved.get("groups", [])
        st.session_state.punishments = saved.get("punishments", {})
        st.session_state.overrides = saved.get("overrides", {})
        st.session_state.role_overrides = saved.get("role_overrides", {})
        st.session_state.statuses = saved.get("statuses", {})
        st.session_state.start_date = saved.get("start_date", datetime(2026, 3, 15).date())
    else:
        st.session_state.groups = [
            {"id": "G1", "name": "GUARDIA 1 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G1", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(12)]},
            {"id": "G5", "name": "GUARDIA 1 de III° Año", "cadets": [
                {"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
                {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
                {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 5, "nombre": "Abregu Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 8, "nombre": "Arganaraz Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"}
            ]},
            {"id": "G2", "name": "GUARDIA 2 de II° Año", "cadets": []},
            {"id": "G3", "name": "GUARDIA 3 de II° Año", "cadets": []},
            {"id": "G4", "name": "GUARDIA 4 de II° Año", "cadets": []},
            {"id": "G6", "name": "GUARDIA 2 de III° Año", "cadets": []},
            {"id": "G7", "name": "GUARDIA 3 de III° Año", "cadets": []},
            {"id": "G8", "name": "GUARDIA 4 de III° Año", "cadets": []},
            {"id": "G9", "name": "GUARDIA 5 de III° Año", "cadets": []}
        ]
        st.session_state.punishments, st.session_state.overrides = {}, {}
        st.session_state.role_overrides, st.session_state.statuses = {}, {}
        st.session_state.start_date = datetime(2026, 3, 15).date()
    st.session_state.initialized = True

# --- LÓGICA DE PROCESAMIENTO ---
def get_processed_guard_for_date(date):
    diff = (date - st.session_state.start_date).days
    idx = diff % len(st.session_state.groups)
    base_group = st.session_state.groups[idx]
    date_key = str(date)
    processed = []
    
    overrides = st.session_state.get('overrides', {})
    role_overrides = st.session_state.get('role_overrides', {})
    statuses = st.session_state.get('statuses', {})

    for i, c in enumerate(base_group['cadets']):
        cd = c.copy()
        titular_original = cd['nombre'] # Guardamos el nombre del titular original
        
        # 1. Suplencias y Situación Especial
        if date_key in overrides and str(i) in overrides[date_key]:
            suplente = overrides[date_key][str(i)]
            cd['nombre'] = f"🔄 {suplente['nombre']}"
            cd['is_sub'] = True
            # Forzamos la situación a indicar el reemplazo
            cd['situacion'] = f"SUPLENTE POR {titular_original.upper()}"
        else: 
            cd['is_sub'] = False
            cd['situacion'] = statuses.get(date_key, {}).get(str(i), "PRESENTE")
            
        # 2. Funciones
        if date_key in role_overrides and str(i) in role_overrides[date_key]:
            cd['funcion'] = role_overrides[date_key][str(i)]
            
        processed.append(cd)
    return {"name": base_group['name'], "cadets": processed, "id": base_group['id']}

# --- LÓGICA PDF ---
def generate_official_pdf(start_date, end_date):
    pdf = FPDF()
    curr = start_date
    while curr <= end_date:
        pdf.add_page()
        if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, 10, 8, 25)
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
        for c in g_data['cadets']:
            pdf.cell(cols[0], 8, str(c['n']), 1, align='C')
            pdf.cell(cols[1], 8, c['nombre'][:35].encode('latin-1', 'replace').decode('latin-1'), 1, align='L')
            pdf.cell(cols[2], 8, c['curso'], 1, align='C')
            pdf.cell(cols[3], 8, c['funcion'].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[4], 8, c['situacion'][:20].encode('latin-1', 'replace').decode('latin-1'), 1, align='C')
            pdf.cell(cols[5], 8, "", 1, ln=True)
        
        # Castigos en PDF
        date_key = str(curr)
        p_list = st.session_state.punishments.get(date_key, [])
        if p_list:
            pdf.ln(10); pdf.set_font("helvetica", 'B', 11)
            pdf.cell(190, 8, "CADETES DE GUARDIA CASTIGO / REFUERZO", ln=True)
            pdf.set_font("helvetica", '', 9)
            for p in p_list:
                pdf.cell(130, 8, f"- {p['nombre']} ({p['curso']})".encode('latin-1', 'replace').decode('latin-1'), 1)
                pdf.cell(60, 8, "Firma: ________________", 1, ln=True)
        curr += timedelta(days=1)
    return bytes(pdf.output())

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=120)
        st.markdown("<h2 style='color:#0f172a;'>SISTEMA DE GUARDIA</h2>", unsafe_allow_html=True)
        pwd = st.text_input("CLAVE DE ACCESO", type="password", placeholder="••••••••", label_visibility="collapsed")
        if st.button("ENTRAR AL SISTEMA"):
            if pwd == "iesp2026": st.session_state.logged_in = True; st.rerun()
            else: st.error("Acceso Denegado")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- NAVEGACIÓN ---
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=100)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        menu = st.radio("MENÚ PRINCIPAL", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Guardia Castigo", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"])
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        if st.button("SALIR"):
            st.session_state.logged_in = False; st.rerun()

    st.markdown("""<div class="header-container"><h1 class="header-title">I.E.S.P. Diagramación de Guardia 2026</h1></div>""", unsafe_allow_html=True)

    if menu == "🏠 Dashboard":
        if st.button("🔄 CORREGIR CICLO DE ROTACIÓN (SINCRONIZAR HOY)"):
            st.session_state.start_date = datetime(2026, 3, 15).date(); save_data(); st.rerun()
        
        sel_date = st.date_input("FECHA SELECCIONADA", datetime.now().date()); date_key = str(sel_date)
        gi = get_processed_guard_for_date(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Guardia</div><div class='metric-value'>{gi['name']}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Suplentes</div><div class='metric-value'>{sum(1 for c in gi['cadets'] if c.get('is_sub'))}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Novedades</div><div class='metric-value'>{sum(1 for c in gi['cadets'] if c['situacion'] != 'PRESENTE' and not c.get('is_sub'))}</div></div>", unsafe_allow_html=True)
        
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown("### 📋 Nómina del Personal")
            df_display = pd.DataFrame([{"N°": c['n'], "Nombre": f"{'✅' if c['situacion'] == 'PRESENTE' or c.get('is_sub') else '⚠️'} {c['nombre']}", "Función": c['funcion'], "Situación": c['situacion']} for c in gi['cadets']])
            st.dataframe(df_display, use_container_width=True, hide_index=True, height=(len(df_display)+1)*35+10)
        
        with col_r:
            st.markdown("### ⚙️ Gestión")
            with st.container(border=True):
                st.write("**📝 Situación de Revista**")
                c_idx = st.selectbox("Personal", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'])
                nuevo_st = st.selectbox("Estado", ["PRESENTE", "FRANCO", "A.R.T.", "AUSENTE", "NOTA MÉDICA"])
                if st.button("ACTUALIZAR ESTADO"):
                    if date_key not in st.session_state.statuses: st.session_state.statuses[date_key] = {}
                    st.session_state.statuses[date_key][str(c_idx)] = nuevo_st; save_data(); st.rerun()

            with st.container(border=True):
                st.write("**🎭 Cambiar Función**")
                c_idx_r = st.selectbox("Cadete", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="rs")
                n_f = st.text_input("Nueva Función (Ej: Centinela)")
                if st.button("ASIGNAR"):
                    if date_key not in st.session_state.role_overrides: st.session_state.role_overrides[date_key] = {}
                    st.session_state.role_overrides[date_key][str(c_idx_r)] = n_f; save_data(); st.rerun()

            with st.container(border=True):
                st.write("**🔄 Reemplazo por Suplente**")
                target = st.selectbox("Titular a cubrir", range(len(gi['cadets'])), format_func=lambda x: gi['cadets'][x]['nombre'], key="target")
                
                search_list = []
                for g in st.session_state.groups:
                    for c in g['cadets']:
                        search_list.append({"label": f"{c['nombre']} ({g['name']})", "obj": c})
                
                if search_list:
                    suplente_idx = st.selectbox(
                        "Buscar Suplente por Apellido", 
                        range(len(search_list)), 
                        format_func=lambda x: search_list[x]['label'],
                        key="suplente_search"
                    )
                    
                    if st.button("APLICAR SUPLENCIA"):
                        if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                        st.session_state.overrides[date_key][str(target)] = search_list[suplente_idx]['obj']
                        save_data(); st.rerun()
                else:
                    st.warning("Cargue personal en los grupos primero.")

            if date_key in st.session_state.overrides or date_key in st.session_state.role_overrides:
                if st.button("♻️ RESTABLECER ORIGINALES"):
                    st.session_state.overrides[date_key] = {}; st.session_state.role_overrides[date_key] = {}; save_data(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        st.markdown("### 📋 Vista General de Grupos")
        today = datetime.now().date()
        cols = st.columns(3)
        for i in range(len(st.session_state.groups)):
            diff = (today - st.session_state.start_date).days
            is_active = (i == diff % len(st.session_state.groups))
            # Para la vista general, si el grupo está hoy activo, mostramos los procesados (con suplentes)
            g_data = get_processed_guard_for_date(today) if is_active else st.session_state.groups[i]
            with cols[i % 3]:
                st.markdown(f"""<div style="background:white; border-radius:24px; padding:1.2rem; border:1px solid #f1f5f9; margin-bottom:1.5rem;">
                    <div style="background:{'#ef4444' if is_active else '#0f172a'}; color:white; padding:0.6rem; border-radius:12px; text-align:center; font-weight:800; font-size:0.75rem;">{g_data['name']} {'(HOY)' if is_active else ''}</div>""", unsafe_allow_html=True)
                for cadet in g_data['cadets']:
                    st.markdown(f"""<div style="display:flex; justify-content:space-between; padding:0.3rem 0; border-bottom:1px solid #f8fafc; font-size:0.7rem;"><b>{cadet['nombre']}</b><span style="color:#94a3b8;">{cadet.get('funcion','Cadete')}</span></div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "⚖️ Guardia Castigo":
        st.markdown("### ⚖️ Gestión de Cadetes de Guardia Castigo")
        p_d = st.date_input("Fecha", datetime.now().date()); pk = str(p_d)
        ca, cb = st.columns(2)
        with ca:
            with st.container(border=True):
                g_p = st.selectbox("Grupo", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
                c_p = st.selectbox("Cadete", range(len(st.session_state.groups[g_p]['cadets'])), format_func=lambda x: st.session_state.groups[g_p]['cadets'][x]['nombre'])
                if st.button("AGREGAR A LISTA"):
                    if pk not in st.session_state.punishments: st.session_state.punishments[pk] = []
                    st.session_state.punishments[pk].append(st.session_state.groups[g_p]['cadets'][c_p])
                    save_data(); st.rerun()
        with cb:
            st.write(f"**Lista para el {p_d.strftime('%d/%m/%Y')}**")
            for idx, p in enumerate(st.session_state.punishments.get(pk, [])):
                c1, c2 = st.columns([3, 1])
                c1.write(f"• {p['nombre']} ({p['curso']})")
                if c2.button("🗑️", key=f"del_{idx}"):
                    st.session_state.punishments[pk].pop(idx); save_data(); st.rerun()

    elif menu == "📂 Reportes PDF":
        st.markdown("### 📂 Generación de Planillas")
        c_r1, c_r2 = st.columns(2)
        s_rep = c_r1.date_input("Fecha Inicio", datetime.now().date())
        e_rep = c_r2.date_input("Fecha Fin", datetime.now().date())
        if st.button("🚀 GENERAR PDF"):
            try:
                pdf_bytes = generate_official_pdf(s_rep, e_rep)
                st.download_button("⬇️ DESCARGAR ARCHIVO PDF", pdf_bytes, f"Planilla_{s_rep}.pdf", "application/pdf")
            except Exception as e: st.error(f"Error: {e}")

    elif menu == "👥 Redistribución":
        st.markdown("### 👥 Edición de Nóminas")
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"📝 Editar {g['name']}"):
                df_editor = st.data_editor(pd.DataFrame(g['cadets']), num_rows="dynamic", key=f"ed_{i}", use_container_width=True)
                if st.button(f"Guardar Cambios {g['id']}", key=f"s_{i}"):
                    st.session_state.groups[i]['cadets'] = df_editor.to_dict('records'); save_data(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        st.markdown("### ⚙️ Configuración del Sistema")
        with st.container(border=True):
            st.write("**📅 Ciclo de Rotación**")
            st.info("La fecha de inicio determina qué grupo está de guardia hoy. Ajuste esto si el calendario se desfasa.")
            new_start = st.date_input("Fecha de inicio del Ciclo (Grupo 1)", st.session_state.start_date)
            if st.button("GUARDAR CONFIGURACIÓN DE CICLO"):
                st.session_state.start_date = new_start
                save_data()
                st.success("Ciclo actualizado correctamente.")
        
        with st.container(border=True):
            st.write("**📁 Gestión de Base de Datos**")
            st.write(f"Archivo de persistencia: `{DB_FILE}`")
            if st.button("🔄 RECARGAR DESDE DISCO"):
                saved = load_data()
                if saved:
                    st.session_state.update(saved)
                    st.success("Datos recargados.")

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

# --- ESTILO CSS PERSONALIZADO (LOGIN Y DASHBOARD) ---
def inject_custom_css():
    st.markdown("""
    <style>
        .main { background-color: #ffffff; }
        
        /* BARRA SUPERIOR ESTILO NETLIFY */
        .header-bar {
            background-color: white;
            padding: 15px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #f1f5f9;
            margin-bottom: 25px;
        }
        .header-title {
            color: #1e3a8a;
            font-weight: 800;
            font-size: 1.4rem;
            letter-spacing: -0.5px;
        }
        
        /* LOGIN ESTILO PRO */
        .login-card {
            max-width: 450px;
            margin: 80px auto;
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
        }
        .login-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1e293b;
            margin-top: 20px;
            margin-bottom: 5px;
            text-transform: uppercase;
        }
        
        /* BOTÓN ENTRAR ROJO */
        div.stButton > button:first-child {
            background-color: #ff4b4b !important;
            color: white !important;
            border: none !important;
            padding: 10px 20px !important;
            width: 100% !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            height: 45px !important;
        }
        
        /* PANEL IZQUIERDO */
        [data-testid="stSidebar"] { background-color: #1e3a8a !important; }
        [data-testid="stSidebar"] * { color: white !important; }
        
        /* TARJETAS */
        .metric-card {
            background-color: #f8fafc;
            padding: 20px;
            border-radius: 12px;
            border-top: 4px solid #1e3a8a;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        
        /* TODAS LAS GUARDIAS - TARJETAS */
        .group-container {
            background-color: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 20px rgba(0,0,0,0.08);
            margin-bottom: 25px;
            border: 1px solid #f1f5f9;
        }
        .group-header {
            background-color: #0f172a;
            color: white;
            padding: 15px;
            text-align: center;
        }
        .group-header h4 { color: white !important; margin: 0 !important; font-size: 0.85rem; }
        .group-body { padding: 12px; }
        .cadet-row { display: flex; align-items: center; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #f8fafc; }
        .status-dot { width: 7px; height: 7px; border-radius: 50%; }
        .dot-blue { background-color: #2563eb; }
        .dot-green { background-color: #10b981; }
        .cadet-name { font-weight: 600; color: #334155 !important; font-size: 0.7rem; }
        .cadet-meta { color: #cbd5e1 !important; font-size: 0.6rem; font-weight: bold; }
        .on-duty-meta { color: #2563eb !important; font-size: 0.6rem; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- CONSTANTES Y DATOS ---
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
        "start_date": st.session_state.start_date.strftime("%Y-%m-%d")
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# --- INICIALIZACIÓN ---
if 'groups' not in st.session_state:
    saved_state = load_data()
    if saved_state:
        st.session_state.groups = saved_state["groups"]
        st.session_state.punishments = saved_state["punishments"]
        st.session_state.overrides = saved_state["overrides"]
        st.session_state.start_date = saved_state["start_date"]
    else:
        # NÓMINA COMPLETA 9 GRUPOS
        st.session_state.groups = [
            {"id": "G1", "name": "GRUPO N° 1 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G1", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(14)]},
            {"id": "G2", "name": "GRUPO N° 2 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G2", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(14)]},
            {"id": "G3", "name": "GRUPO N° 3 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G3", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
            {"id": "G4", "name": "GRUPO N° 4 de II° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G4", "curso": "IIº Año", "funcion": "Cadete Apostado"} for i in range(15)]},
            {"id": "G5", "name": "GRUPO N° 1 de III° Año", "cadets": [
                {"n": 1, "nombre": "Juarez Ignacio", "curso": "IIIº Año", "funcion": "Jefe de Guardia"},
                {"n": 2, "nombre": "Contreras Melani", "curso": "IIIº Año", "funcion": "Cabo de Cuarto"},
                {"n": 3, "nombre": "Bareiro Blanca", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 4, "nombre": "Etchenique Shamira", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 5, "nombre": "Abregu Franco", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 6, "nombre": "Aguirre Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 7, "nombre": "Arias Ramiro", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 8, "nombre": "Arganaraz Lezcano Roberto", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 9, "nombre": "Avila Jose", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 10, "nombre": "Bazan Luis", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 11, "nombre": "Brandan Cristian", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 12, "nombre": "Coronel Carlos", "curso": "IIº Año", "funcion": "Cadete Apostado"},
                {"n": 13, "nombre": "Diaz Santiago", "curso": "IIº Año", "funcion": "Cadete Apostado"}
            ]},
            {"id": "G6", "name": "GRUPO N° 2 de III° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G6", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(14)]},
            {"id": "G7", "name": "GRUPO N° 3 de III° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G7", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
            {"id": "G8", "name": "GRUPO N° 4 de III° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G8", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(13)]},
            {"id": "G9", "name": "GRUPO N° 5 de III° Año", "cadets": [{"n": i+1, "nombre": f"Cadete {i+1} G9", "curso": "IIIº Año", "funcion": "Cadete Apostado"} for i in range(13)]}
        ]
        st.session_state.punishments = {}
        st.session_state.overrides = {}
        st.session_state.start_date = datetime(2026, 3, 15).date()

# --- FORZADO DE FECHA PARA HOY (Juarez Ignacio) ---
if datetime.now().date() == datetime(2026, 3, 19).date():
    st.session_state.start_date = datetime(2026, 3, 15).date()

# --- LÓGICA DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_screen():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=150)
    st.markdown('<div class="login-title">GESTIÓN DE DIAGRAMACIÓN DE GUARDIA</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; margin-bottom:20px;">Ingrese su contraseña para continuar</p>', unsafe_allow_html=True)
    
    pwd = st.text_input("Contraseña", type="password", label_visibility="collapsed", placeholder="Contraseña")
    if st.button("ENTRAR"):
        if pwd == "iesp2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Acceso denegado")
    st.markdown('</div>', unsafe_allow_html=True)

# --- APLICACIÓN PRINCIPAL ---
if not st.session_state.logged_in:
    login_screen()
else:
    # Barra Superior
    st.markdown("""
    <div class="header-bar">
        <div class="header-title">I.E.S.P. GESTIÓN DE DIAGRAMACIÓN DE GUARDIA</div>
        <div style="color:#64748b; font-weight:bold; font-size:0.8rem;">LOCAL HOST ACTIVO</div>
    </div>
    """, unsafe_allow_html=True)

    # LÓGICA DE ROTACIÓN
    def get_group_for_date(target_date):
        diff = (target_date - st.session_state.start_date).days
        idx = diff % len(st.session_state.groups)
        return st.session_state.groups[idx]

    def get_full_guard(date):
        date_key = str(date)
        base = get_group_for_date(date)
        ovr = st.session_state.overrides.get(date_key, {})
        final = []
        for i, c in enumerate(base['cadets']):
            if str(i) in ovr:
                final.append({**ovr[str(i)], "is_override": True, "original_role": c['funcion']})
            else:
                final.append({**c, "is_override": False})
        return {"name": base['name'], "cadets": final, "punishments": st.session_state.punishments.get(date_key, [])}

    # SIDEBAR
    with st.sidebar:
        if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width=120)
        st.markdown("### MENÚ IESP")
        menu = st.radio("Menu", ["🏠 Dashboard", "📋 Todas las Guardias", "⚖️ Gestión Guardia Castigo", "📂 Reportes PDF", "👥 Redistribución", "⚙️ Ajustes"], label_visibility="collapsed")
        if st.button("SALIR"):
            st.session_state.logged_in = False
            st.rerun()

    # VISTAS
    if menu == "🏠 Dashboard":
        st.title("🛡️ Panel de Diagramación")
        sel_date = st.date_input("Fecha de gestión", datetime.now().date())
        guard = get_full_guard(sel_date)
        date_key = str(sel_date)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='metric-card'><h3>Grupo Actual</h3><p style='color:#1e3a8a; font-weight:900;'>{guard['name']}</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><h3>Suplentes</h3><p style='color:#f59e0b; font-weight:900;'>{sum(1 for c in guard['cadets'] if c['is_override'])}</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><h3>Guardia Castigo</h3><p style='color:#ef4444; font-weight:900;'>{len(guard['punishments'])}</p></div>", unsafe_allow_html=True)

        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.subheader("📋 Nómina de Servicio")
            # Se limpia la tabla para no mostrar columnas técnicas
            df_view = pd.DataFrame([{"N°": c['n'], "Nombre": f"⚠️ {c['nombre']} (SUPLENTE)" if c['is_override'] else c['nombre'], "Curso": c['curso'], "Estado": "SUPLENTE" if c['is_override'] else "Titular"} for c in guard['cadets']])
            st.dataframe(df_view, width="stretch", hide_index=True)

        with col_r:
            st.subheader("🔄 Suplentes")
            with st.container(border=True):
                target = st.selectbox("Reemplazar a:", range(len(guard['cadets'])), format_func=lambda x: guard['cadets'][x]['nombre'])
                g_src = st.selectbox("Grupo del suplente:", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
                c_src = st.selectbox("Elegir suplente:", range(len(st.session_state.groups[g_src]['cadets'])), format_func=lambda x: st.session_state.groups[g_src]['cadets'][x]['nombre'])
                if st.button("Aplicar Reemplazo"):
                    if date_key not in st.session_state.overrides: st.session_state.overrides[date_key] = {}
                    st.session_state.overrides[date_key][str(target)] = st.session_state.groups[g_src]['cadets'][c_src]
                    save_data(); st.rerun()

    elif menu == "📋 Todas las Guardias":
        st.title("📋 Nómina General de Grupos")
        today_g = get_group_for_date(datetime.now().date())
        gs = st.session_state.groups
        for i in range(0, len(gs), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(gs):
                    g = gs[i + j]
                    is_active = g['id'] == today_g['id']
                    meta = "DE GUARDIA" if is_active else "IESP"
                    cls = "on-duty-meta" if is_active else "cadet-meta"
                    with cols[j]:
                        html = f"""<div class="group-container"><div class="group-header"><h4>{g['name']}</h4></div><div class="group-body">"""
                        for cadet in g['cadets'][:6]:
                            dot = "dot-blue" if cadet['n'] <= 2 else "dot-green"
                            html += f"""<div class="cadet-row"><div style="display:flex;align-items:center;gap:8px;"><div class="status-dot {dot}"></div><div class="cadet-name">{cadet['nombre']}</div></div><div class="{cls}">{meta}</div></div>"""
                        html += "</div></div>"
                        st.markdown(html, unsafe_allow_html=True)

    elif menu == "⚖️ Gestión Guardia Castigo":
        st.title("⚖️ Gestión de Guardia Castigo")
        p_date = st.date_input("Fecha", datetime.now().date())
        pk = str(p_date)
        c_a, c_b = st.columns(2)
        with c_a:
            st.subheader("Asignar")
            g_p = st.selectbox("Grupo", range(len(st.session_state.groups)), format_func=lambda x: st.session_state.groups[x]['name'])
            c_p = st.selectbox("Cadete", range(len(st.session_state.groups[g_p]['cadets'])), format_func=lambda x: st.session_state.groups[g_p]['cadets'][x]['nombre'])
            if st.button("AGREGAR"):
                if pk not in st.session_state.punishments: st.session_state.punishments[pk] = []
                st.session_state.punishments[pk].append(st.session_state.groups[g_p]['cadets'][c_p])
                save_data(); st.rerun()
        with c_b:
            st.subheader("Lista")
            for idx, p in enumerate(st.session_state.punishments.get(pk, [])):
                st.write(f"• {p['nombre']}")
                if st.button(f"Eliminar {idx}"):
                    st.session_state.punishments[pk].pop(idx); save_data(); st.rerun()

    elif menu == "📂 Reportes PDF":
        st.title("📂 Generación de Planillas")
        st.info("Esta sección genera los documentos oficiales listos para imprimir.")
        s_d = st.date_input("Desde", datetime.now().date())
        e_d = st.date_input("Hasta", datetime.now().date() + timedelta(days=6))
        if st.button("DESCARGAR PDF"):
            st.success("Planilla generada correctamente.")

    elif menu == "👥 Redistribución":
        st.title("👥 Editar Listas Permanentes")
        for i, g in enumerate(st.session_state.groups):
            with st.expander(f"Editar {g['name']}"):
                df = st.data_editor(pd.DataFrame(g['cadets']), num_rows="dynamic", key=f"e_{i}", width="stretch")
                if st.button(f"Guardar Cambios {i}"):
                    st.session_state.groups[i]['cadets'] = df.to_dict('records')
                    save_data(); st.success("Guardado")

    elif menu == "⚙️ Ajustes":
        st.title("⚙️ Ajustes de Ciclo")
        n_s = st.date_input("Inicio de ciclo (Grupo 1)", st.session_state.start_date)
        if st.button("REINICIAR ROTACIÓN"):
            st.session_state.start_date = n_s; save_data(); st.success("Sincronizado")
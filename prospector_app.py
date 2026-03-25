import streamlit as st
import datetime
import sqlite3
import pandas as pd
import urllib.parse
import json
import os
from gemini_engine import analizar_perfil_linkedin, generar_seguimiento
from search_engine import find_linkedin_profiles

st.set_page_config(page_title="ELEVARE SMART LEADS - Expert Prospector", page_icon="💎", layout="wide")

# --- CONFIGURACIÓN DE BASE DE DATOS (SQLite) ---
def init_db():
    conn = sqlite3.connect('prospector_master.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leads 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, linea TEXT, cargo TEXT, 
                  contexto TEXT, mensaje TEXT, estado TEXT, texto_original TEXT,
                  score INTEGER, analisis_detalle TEXT,
                  sequence_id INTEGER, current_step INTEGER, next_action_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sequences 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, pasos TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, accion TEXT, detalle TEXT)''')
    
    # Migraciones Seguras
    try: c.execute("ALTER TABLE leads ADD COLUMN score INTEGER")
    except: pass
    try: c.execute("ALTER TABLE leads ADD COLUMN analisis_detalle TEXT")
    except: pass
    try: c.execute("ALTER TABLE leads ADD COLUMN sequence_id INTEGER")
    except: pass
    try: c.execute("ALTER TABLE leads ADD COLUMN current_step INTEGER DEFAULT 0")
    except: pass
    try: c.execute("ALTER TABLE leads ADD COLUMN next_action_date TEXT")
    except: pass
    try: c.execute("ALTER TABLE leads ADD COLUMN linkedin_url TEXT")
    except: pass
        
    conn.commit()
    conn.close()

def update_lead_status(lead_id, nuevo_estado):
    conn = sqlite3.connect('prospector_master.db')
    c = conn.cursor()
    c.execute("UPDATE leads SET estado = ? WHERE id = ?", (nuevo_estado, lead_id))
    conn.commit()
    conn.close()

def get_sequences():
    conn = sqlite3.connect('prospector_master.db')
    df = pd.read_sql_query("SELECT * FROM sequences", conn)
    conn.close()
    return df

def save_sequence(nombre, pasos):
    conn = sqlite3.connect('prospector_master.db')
    c = conn.cursor()
    c.execute("INSERT INTO sequences (nombre, pasos) VALUES (?,?)", (nombre, json.dumps(pasos)))
    conn.commit()
    conn.close()

def log_activity(accion, detalle):
    conn = sqlite3.connect('prospector_master.db')
    c = conn.cursor()
    fecha = datetime.datetime.now().strftime("%H:%M:%S")
    c.execute("INSERT INTO activity (fecha, accion, detalle) VALUES (?,?,?)", (fecha, accion, detalle))
    conn.commit()
    conn.close()

def get_activity():
    conn = sqlite3.connect('prospector_master.db')
    df = pd.read_sql_query("SELECT * FROM activity ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    return df

init_db()

# --- ESTILOS CSS (ELEVARE Premium Glassmorphism) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    :root {
        --glass-bg: rgba(15, 23, 42, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
        --accent-blue: #3B82F6;
        --accent-emerald: #10B981;
    }
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #020617;
    }
    .metric-card, .history-card, .pain-point { 
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .history-card:hover {
        transform: translateY(-4px);
        border-color: var(--accent-blue);
        box-shadow: 0 12px 40px 0 rgba(59, 130, 246, 0.2);
    }
    .score-badge {
        font-size: 28px;
        font-weight: 800;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
        text-shadow: 0 0 15px currentColor;
    }
    .score-high { color: #34D399; border: 2px solid #059669; box-shadow: inset 0 0 20px rgba(52, 211, 153, 0.2); }
    .score-mid { color: #FBBF24; border: 2px solid #D97706; box-shadow: inset 0 0 20px rgba(251, 191, 36, 0.2); }
    .score-low { color: #F87171; border: 2px solid #DC2626; box-shadow: inset 0 0 20px rgba(248, 113, 113, 0.2); }
    .icp-match { 
        color: #ffffff; font-weight: 700; padding: 6px 12px; 
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        border-radius: 8px; display: inline-block; font-size: 11px; letter-spacing: 0.5px;
    }
    .pain-point { 
        border-left: 5px solid var(--accent-blue); 
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.05) 0%, transparent 100%);
    }
    .stButton>button {
        border-radius: 12px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02); box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
    }
    [data-testid="stMetricValue"] {
        font-size: 32px !important; font-weight: 800 !important; color: var(--accent-blue) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL DE NAVEGACIÓN ---
with st.sidebar:
    st.markdown("<h1 style='color: #3B82F6; font-size: 24px;'>ELEVARE SMART LEADS</h1>", unsafe_allow_html=True)
    menu = st.radio("Navegación", ["📊 TABLERO", "🧬 SECUENCIAS", "🎯 DESCUBRIMIENTO", "🔍 ANALIZAR", "📜 HISTORIA", "⚙️ AJUSTES"])
    
    st.markdown("---")
    st.header("⚙️ Configuración de Campaña")
    linea_negocio = st.selectbox("Línea de Negocio", ["Venta de CRM B2B", "Gestoría Proyectos CORFO", "Campaña Personalizada"])
    
    cargo_objetivo = st.text_input("Cargo Target (Libre)", value="Gerente Comercial, CEO, Director")
    dolor_objetivo = st.text_area("Dolor/Oportunidad (Libre)", value="Desorden comercial, planillas Excel, problemas para escalar ventas.")

# --- LÓGICA DE PESTAÑAS ---

if menu == "📊 TABLERO":
    st.title("Comando de Inteligencia ELEVARE")
    
    conn = sqlite3.connect('prospector_master.db')
    try:
        df = pd.read_sql_query("SELECT * FROM leads", conn)
    except Exception:
        df = pd.DataFrame()
        
    if df.empty:
        st.info("Tu embudo está vacío. Ve a la pestaña '🎯 DESCUBRIMIENTO' para escanear y calificar tus primeros prospectos.")
    else:
        st.subheader("Funnel de Prospección")
        total_leads = len(df)
        calificados = len(df[df['score'] >= 60]) if 'score' in df.columns else 0
        contactados = len(df[df['estado'] == 'Contactado'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("1. Leads Descubiertos", total_leads)
        
        tasa_calificacion = f"{(calificados/total_leads*100):.1f}%" if total_leads > 0 else "0%"
        col2.metric("2. Calificados por IA (>60 pts)", calificados, tasa_calificacion)
        
        tasa_contacto = f"{(contactados/calificados*100):.1f}%" if calificados > 0 else "0%"
        col3.metric("3. Contactados (Éxito)", contactados, tasa_contacto)
        
        st.markdown("---")
        
        st.subheader("🔥 Top Leads para Atacar Hoy")
        st.markdown("Los perfiles con mayor encaje (ICP) que aún no has contactado.")
        
        if 'score' in df.columns and 'estado' in df.columns:
            df_pendientes = df[(df['estado'] == 'Pendiente') & (df['score'] >= 60)].sort_values(by='score', ascending=False).head(5)
            
            if df_pendientes.empty:
                st.success("¡Excelente trabajo! Inbox Zero. No tienes leads calificados pendientes de contacto hoy.")
            else:
                for index, row in df_pendientes.iterrows():
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    c_info, c_action = st.columns([3, 1])
                    
                    with c_info:
                        color = "🟢" if row['score'] >= 80 else "🟡"
                        st.markdown(f"### {color} {row['cargo']} | Score: {row['score']}")
                        st.caption(f"Campaña: {row['linea']} | Evaluado el: {row['fecha']}")
                        dolor = row.get('analisis_detalle', 'Sin detalle estratégico')
                        if dolor:
                            st.markdown(f"**Estrategia:** {dolor[:100]}...")
                        
                    with c_action:
                        url_destino = row.get('linkedin_url') if row.get('linkedin_url') else "https://www.linkedin.com/messaging/"
                        st.link_button("🔗 Abrir & Conectar", url_destino, use_container_width=True)
                        
                        if st.button("✅ Contactado", key=f"dash_btn_{row['id']}", use_container_width=True):
                            update_lead_status(row['id'], "Contactado")
                            log_activity("Comando Rápido", f"Lead #{row['id']} marcado como contactado desde Tablero.")
                            st.rerun()
                            
                    st.markdown('</div>', unsafe_allow_html=True)
                    
    conn.close()

elif menu == "🧬 SECUENCIAS":
    st.title("Comando de Inteligencia ELEVARE")
    st.markdown("---")
    st.info("🕒 Módulo en desarrollo para ejecución automática de secuencias multicanal.")
    st.markdown("""
    Esta sección permitirá orquestar las cadencias de contacto (LinkedIn + Email) de forma 100% autónoma. 
    Actualmente puedes usar el **Tablero** para envíos manuales asistidos por IA.
    """)
                
    st.markdown("---")
    
    # 2. Visualizador de Secuencias Activas
    st.subheader("📋 Secuencias Activas")
    df_seq = get_sequences()
    
    if not df_seq.empty:
        df_show = df_seq.copy()
        
        # Función para formatear el JSON de pasos
        def format_pasos(pasos_json):
            try:
                pasos_list = json.loads(pasos_json)
                return " ➔ ".join([f"{p['canal']} (+{p['delay']}d)" for p in pasos_list])
            except:
                return "Error de formato"
                
        df_show['Flujo de Contacto'] = df_show['pasos'].apply(format_pasos)
        df_show = df_show.rename(columns={'nombre': 'Nombre de Secuencia', 'id': 'ID'})
        
        st.dataframe(df_show[['ID', 'Nombre de Secuencia', 'Flujo de Contacto']], use_container_width=True, hide_index=True)
    else:
        st.info("💡 Aún no tienes secuencias. Crea la primera en el panel superior para estructurar tu seguimiento.")

elif menu == "🎯 DESCUBRIMIENTO":
    st.title("Smart Discovery by ELEVARE")
    st.markdown("Identifica prospectos de alto valor con búsqueda semántica y evalúalos en 1 clic.")
    
    col1, col2 = st.columns(2)
    with col1:
        cargo_search = st.text_input("Buscar Cargos", placeholder="ej: Gerente Comercial")
    with col2:
        industria_search = st.text_input("Industria / Nicho", placeholder="ej: SaaS, Minería, Fintech")
        
    c_loc, c_num = st.columns(2)
    ubicacion_search = c_loc.text_input("Ubicación", value="Chile")
    cantidad_search = c_num.slider("N° Resultados", 5, 50, 10)
        
    if st.button("🔍 Iniciar Escaneo Inteligente", type="primary"):
        if not cargo_search or not industria_search:
            st.warning("Por favor ingresa cargo e industria.")
        else:
            with st.spinner("ELEVARE escaneando LinkedIn..."):
                results = find_linkedin_profiles(cargo_search, industria_search, ubicacion_search, cantidad_search)
                
                if isinstance(results, dict) and "error" in results:
                    st.error(results["error"])
                elif not results:
                    st.info("No se encontraron resultados.")
                else:
                    st.session_state['search_results'] = results
                    log_activity("Búsqueda Ejecutada", f"{cargo_search} en {industria_search}")
                    st.success(f"Se encontraron {len(results)} perfiles calificados.")

    if 'search_results' in st.session_state:
        st.subheader("Resultados de Búsqueda")
        for i, res in enumerate(st.session_state['search_results']):
            with st.container():
                st.markdown(f"**{res['title']}**")
                st.caption(res['link'])
                st.write(res['snippet'])
                
                if st.button(f"⚡ Evaluar Automáticamente", key=f"search_{i}", type="primary"):
                    with st.spinner("Analizando encaje con tu campaña..."):
                        texto_perfil = res['snippet']
                        url_perfil = res['link']
                        
                        resultado = analizar_perfil_linkedin(texto_perfil, linea_negocio, cargo_objetivo, dolor_objetivo)
                        
                        if "error" in resultado:
                            st.error(resultado["error"])
                        else:
                            conn = sqlite3.connect('prospector_master.db')
                            cur = conn.cursor()
                            cur.execute("""INSERT INTO leads 
                                        (fecha, linea, cargo, contexto, mensaje, estado, texto_original, score, analisis_detalle, linkedin_url) 
                                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                                        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), linea_negocio, cargo_objetivo, 
                                         resultado.get('resumen_contexto', ''), resultado.get('mensaje_sugerido', ''), 'Pendiente', 
                                         texto_perfil, resultado.get('score', 0), resultado.get('analisis_detalle', ''), url_perfil))
                            conn.commit()
                            conn.close()
                            
                            score = resultado.get('score', 0)
                            log_activity("Análisis Directo", f"Lead evaluado con {score} pts")
                            
                            if score >= 60:
                                st.success(f"✅ ¡Lead calificado ({score} pts)! Se ha guardado en tu HISTORIA listo para contactar.")
                            else:
                                st.warning(f"⚠️ Lead analizado pero el Score es bajo ({score} pts).")
                st.markdown("---")

elif menu == "🔍 ANALIZAR":
    st.title("Análisis Inteligente ELEVARE")
    modo = st.radio("Modo de Prospección", ["Individual", "Lote Autónomo (Subir CSV/Excel)"], horizontal=True)
    
    if modo == "Individual":
        url_perfil = st.text_input("URL de LinkedIn (Opcional):", placeholder="https://linkedin.com/in/...")
        texto_perfil = st.text_area("LinkedIn Profile Data:", height=150, placeholder="Pega el extracto del perfil aquí...")
        
        if st.button("🚀 Analizar y Redactar", type="primary"):
            if texto_perfil.strip():
                with st.spinner("Gemini analizando señales (Anti-alucinación)..."):
                    resultado = analizar_perfil_linkedin(texto_perfil, linea_negocio, cargo_objetivo, dolor_objetivo)
                    
                    if "error" in resultado:
                        st.error(resultado["error"])
                    else:
                        conn = sqlite3.connect('prospector_master.db')
                        cur = conn.cursor()
                        cur.execute("""INSERT INTO leads 
                                    (fecha, linea, cargo, contexto, mensaje, estado, texto_original, score, analisis_detalle, linkedin_url) 
                                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                                    (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), linea_negocio, cargo_objetivo, 
                                     resultado.get('resumen_contexto', ''), resultado.get('mensaje_sugerido', ''), 'Pendiente', 
                                     texto_perfil, resultado.get('score', 0), resultado.get('analisis_detalle', ''), url_perfil))
                        conn.commit()
                        conn.close()
                        
                        st.success("¡Análisis completado y guardado!")
                        st.code(resultado.get("mensaje_sugerido", ""), language="markdown")
            else:
                st.warning("⚠️ Ingresa el texto del perfil.")
                
    else:
        st.info("💡 Sube un archivo CSV o Excel.")
        archivo = st.file_uploader("Sube tu base de datos de LinkedIn", type=["csv", "xlsx"])
        
        if archivo and st.button("🚀 Procesar Lote con IA", type="primary"):
            df_leads = pd.read_csv(archivo) if archivo.name.endswith('.csv') else pd.read_excel(archivo)
            
            col_texto = next((col for col in df_leads.columns if col.lower() in ['perfil', 'resumen', 'about', 'summary']), None)
            col_url = next((col for col in df_leads.columns if col.lower() in ['url', 'enlace', 'linkedin', 'link']), None)
            
            if not col_texto:
                st.error("❌ No se encontró una columna de texto válida.")
            else:
                bar = st.progress(0)
                for i, row in df_leads.iterrows():
                    texto = str(row[col_texto])
                    url = str(row[col_url]) if col_url else ""
                    if len(texto) > 20: 
                        res = analizar_perfil_linkedin(texto, linea_negocio, cargo_objetivo, dolor_objetivo)
                        if "error" not in res and res.get("score", 0) >= 60:
                            conn = sqlite3.connect('prospector_master.db')
                            cur = conn.cursor()
                            cur.execute("""INSERT INTO leads 
                                        (fecha, linea, cargo, contexto, mensaje, estado, texto_original, score, analisis_detalle, linkedin_url) 
                                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                                        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), linea_negocio, cargo_objetivo, 
                                         res.get('resumen_contexto', ''), res.get('mensaje_sugerido', ''), 'Pendiente', 
                                         texto, res.get('score', 0), res.get('analisis_detalle', ''), url))
                            conn.commit()
                            conn.close()
                    bar.progress((i + 1) / len(df_leads))
                st.success("✅ ¡Procesamiento masivo completado!")

elif menu == "📜 HISTORIA":
    st.title("Gestión de Envíos Multicanal")
    
    conn = sqlite3.connect('prospector_master.db')
    df = pd.read_sql_query("SELECT * FROM leads ORDER BY id DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("No hay prospectos en la base de datos.")
    else:
        for index, row in df.iterrows():
            st.markdown('<div class="history-card">', unsafe_allow_html=True)
            col_score, col_main, col_actions = st.columns([0.8, 3.5, 1.2])
            
            with col_score:
                score = row.get('score', 0) if row.get('score') is not None else 0
                color_class = "score-high" if score >= 80 else "score-mid" if score >= 60 else "score-low"
                st.markdown(f'<div class="score-badge {color_class}">{score}</div>', unsafe_allow_html=True)

            with col_main:
                st.markdown(f"### {row['cargo']}")
                st.markdown(f"**Contexto:** {row['contexto']}")
                estrategia = row.get("analisis_detalle", "")
                if estrategia:
                    st.markdown(f'<div class="pain-point"><strong>Estrategia:</strong> {estrategia}</div>', unsafe_allow_html=True)
                
                st.code(row['mensaje'], language="markdown")
            
            with col_actions:
                estado_full = "🟢 Contactado" if row['estado'] == 'Contactado' else "🟠 Pendiente"
                st.info(estado_full)
                
                url_destino = row.get('linkedin_url') if row.get('linkedin_url') else "https://www.linkedin.com/messaging/"
                st.link_button("🔗 Abrir Perfil & Conectar", url_destino, use_container_width=True)
                
                if row['estado'] != 'Contactado':
                    if st.button("Marcar Éxito", key=f"btn_{row['id']}", use_container_width=True, type="primary"):
                        update_lead_status(row['id'], "Contactado")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⚙️ AJUSTES":
    st.title("Configuración de Sistema")
    st.info("Panel de ajustes técnicos.")
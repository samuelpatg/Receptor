import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
 
# ---------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
    layout="centered",
)
 
# ---------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
 
    :root {
        --ink: #12263A;
        --ink-soft: #5B6B7B;
        --paper: #F3F6F9;
        --card: #FFFFFF;
        --line: #DCE4EC;
        --signal: #0E9F8E;
        --signal-soft: #E1F5F2;
        --alert: #D64545;
    }
 
    html, body, [class*="css"], .stApp {
        font-family: 'Manrope', system-ui, sans-serif;
    }
 
    .stApp { background: var(--paper); }
    .block-container { padding-top: 2rem; max-width: 760px; }
 
    /* Encabezado */
    .hero {
        background: var(--ink);
        color: #fff;
        border-radius: 20px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        color: #fff;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 0.3rem 0;
        padding: 0;
    }
    .hero p { color: #B9C7D5; margin: 0 0 1rem 0; font-size: 0.95rem; }
    .chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .chip {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.18);
        color: #E6EEF5;
        border-radius: 999px;
        padding: 0.25rem 0.8rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
 
    /* Tarjetas de medición */
    .reading {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .reading .icon { font-size: 1.4rem; }
    .reading .label {
        color: var(--ink-soft);
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    .reading .value {
        color: var(--ink);
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        font-variant-numeric: tabular-nums;
        line-height: 1.15;
        word-break: break-word;
    }
 
    /* Estado */
    .status {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background: var(--signal-soft);
        color: #0A6B5F;
        border-radius: 12px;
        padding: 0.7rem 1rem;
        font-weight: 600;
        font-size: 0.92rem;
        margin-bottom: 1rem;
    }
    .status.error { background: #FBE9E9; color: #9B2C2C; }
    .dot {
        width: 10px; height: 10px; border-radius: 50%;
        background: var(--signal);
        flex-shrink: 0;
    }
    .status.error .dot { background: var(--alert); }
    .status .time { margin-left: auto; font-weight: 500; opacity: 0.8; }
 
    .section-title {
        color: var(--ink);
        font-weight: 800;
        font-size: 1.15rem;
        margin: 1.4rem 0 0.7rem 0;
    }
 
    /* Botón principal */
    .stButton > button {
        background: var(--signal);
        color: #fff;
        border: none;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        font-weight: 700;
        font-size: 1rem;
        transition: background 0.15s ease;
    }
    .stButton > button:hover { background: #0B857A; color: #fff; border: none; }
    .stButton > button:focus-visible { outline: 3px solid #0E9F8E55; }
 
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid var(--line);
    }
 
    /* Expanders */
    div[data-testid="stExpander"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
    }
 
    /* ---- Colores explícitos (funcionan aunque el tema de Streamlit sea oscuro) ---- */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: var(--paper) !important;
        color: var(--ink) !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        color: var(--ink) !important;
    }
    header[data-testid="stHeader"] * { color: var(--ink) !important; fill: var(--ink) !important; }
 
    /* Texto general */
    .stApp p, .stApp label, .stApp li, .stApp h2, .stApp h3,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: var(--ink) !important;
    }
 
    /* Sidebar */
    section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {
        background: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span {
        color: var(--ink) !important;
    }
    section[data-testid="stSidebar"] button svg { fill: var(--ink-soft) !important; color: var(--ink-soft) !important; }
 
    /* Campos de entrada */
    div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="input"] > div {
        background: #F3F6F9 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"] { border: 1px solid var(--line) !important; }
    div[data-baseweb="input"]:focus-within { border-color: var(--signal) !important; }
    div[data-baseweb="input"] input {
        background: transparent !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
        font-weight: 600;
    }
    [data-testid="stNumberInput"] button { background: transparent !important; color: var(--ink) !important; }
    [data-testid="stNumberInput"] button svg { fill: var(--ink) !important; }
 
    /* Expander */
    div[data-testid="stExpander"] details, div[data-testid="stExpander"] summary {
        background: var(--card) !important;
        border-radius: 14px;
    }
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary svg {
        color: var(--ink) !important;
        fill: var(--ink) !important;
        font-weight: 700;
    }
    div[data-testid="stExpander"] code {
        background: var(--signal-soft) !important;
        color: #0A6B5F !important;
    }
 
    /* Botón: texto siempre blanco */
    .stButton > button, .stButton > button p, .stButton > button span { color: #FFFFFF !important; }
 
    /* Spinner */
    [data-testid="stSpinner"] p, [data-testid="stSpinner"] { color: var(--ink) !important; }
 
    /* Bloque JSON / código */
    [data-testid="stJson"], pre, code { background: #F3F6F9 !important; }
 
    /* Encabezado oscuro: texto claro (va al final para ganar a las reglas generales) */
    .stApp .hero h1 { color: #FFFFFF !important; }
    .stApp .hero p { color: #B9C7D5 !important; }
    .stApp .hero .chip { color: #E6EEF5 !important; }
 
    /* Estados y tarjetas */
    .stApp .status { color: #0A6B5F !important; }
    .stApp .status.error { color: #9B2C2C !important; }
    .stApp .reading .label { color: var(--ink-soft) !important; }
    .stApp .reading .value { color: var(--ink) !important; }
    .stApp .section-title { color: var(--ink) !important; }
 
    /* Estado vacío */
    .empty {
        background: var(--card);
        border: 1px dashed #B7C4D1;
        border-radius: 16px;
        padding: 1.6rem;
        text-align: center;
        color: var(--ink-soft);
        font-weight: 600;
    }
    .stApp .empty { color: var(--ink-soft) !important; }
 
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ---------------------------------------------------------------
# Variables de estado
# ---------------------------------------------------------------
if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = None
if "last_update" not in st.session_state:
    st.session_state.last_update = None
 
 
# ---------------------------------------------------------------
# Lógica MQTT
# ---------------------------------------------------------------
def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
    message_received = {"received": False, "payload": None}
 
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            # Si no es JSON, guardar como texto
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
 
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
 
        # Esperar máximo 5 segundos
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
 
        client.loop_stop()
        client.disconnect()
 
        return message_received["payload"]
 
    except Exception as e:
        return {"error": str(e)}
 
 
# ---------------------------------------------------------------
# Utilidades visuales
# ---------------------------------------------------------------
def icon_for(key):
    k = str(key).lower()
    if "temp" in k:
        return "🌡️"
    if "hum" in k:
        return "💧"
    if "pres" in k or "press" in k:
        return "🧭"
    if "alt" in k:
        return "⛰️"
    if "light" in k or "luz" in k or "lux" in k:
        return "💡"
    return "📈"
 
 
def format_value(value):
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)
 
 
def reading_card(key, value):
    st.markdown(
        f"""
        <div class="reading">
            <div class="icon">{icon_for(key)}</div>
            <div class="label">{key}</div>
            <div class="value">{format_value(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
 
 
# ---------------------------------------------------------------
# Sidebar - Configuración
# ---------------------------------------------------------------
with st.sidebar:
    st.subheader("⚙️ Configuración de Conexión")
 
    broker = st.text_input(
        "Broker MQTT",
        value="broker.mqttdashboard.com",
        help="Dirección del broker MQTT",
    )
 
    port = st.number_input(
        "Puerto",
        value=1883,
        min_value=1,
        max_value=65535,
        help="Puerto del broker (generalmente 1883)",
    )
 
    topic = st.text_input(
        "Tópico",
        value="Sensor/THP2",
        help="Tópico MQTT a suscribirse",
    )
 
    client_id = st.text_input(
        "ID del Cliente",
        value="streamlit_client",
        help="Identificador único para este cliente",
    )
 
# ---------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <h1>📡 Lector de Sensor MQTT</h1>
        <p>Consulta el último mensaje publicado por tu sensor en tiempo real.</p>
        <div class="chips">
            <span class="chip">Broker: {broker}</span>
            <span class="chip">Puerto: {int(port)}</span>
            <span class="chip">Tópico: {topic}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
 
# Información
with st.expander("ℹ️ Cómo usar esta aplicación", expanded=False):
    st.markdown(
        """
        1. **Broker MQTT**: ingresa la dirección del servidor MQTT en la barra lateral.
        2. **Puerto**: generalmente es 1883 para conexiones no seguras.
        3. **Tópico**: el canal al que deseas suscribirte.
        4. **ID del Cliente**: un identificador único para esta conexión.
        5. Haz clic en **Obtener datos del sensor** para recibir el mensaje más reciente.
 
        **Brokers públicos para pruebas:** `broker.mqttdashboard.com`, `test.mosquitto.org`, `broker.hivemq.com`
        """
    )
 
# ---------------------------------------------------------------
# Botón para obtener datos
# ---------------------------------------------------------------
if st.button("🔄 Obtener datos del sensor", use_container_width=True):
    with st.spinner("Conectando al broker y esperando datos..."):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
 
# ---------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------
data = st.session_state.sensor_data
 
if data:
    st.markdown('<div class="section-title">📊 Datos recibidos</div>', unsafe_allow_html=True)
 
    stamp = st.session_state.last_update or ""
 
    if isinstance(data, dict) and "error" in data:
        st.markdown(
            f"""
            <div class="status error">
                <span class="dot"></span>
                <span>Error de conexión: {data['error']}</span>
                <span class="time">{stamp}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="status">
                <span class="dot"></span>
                <span>Datos recibidos correctamente</span>
                <span class="time">{stamp}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
 
        if isinstance(data, dict):
            # Tarjetas en filas de máximo 3 columnas
            items = list(data.items())
            per_row = 3
            for start in range(0, len(items), per_row):
                row = items[start:start + per_row]
                cols = st.columns(per_row)
                for col, (key, value) in zip(cols, row):
                    with col:
                        reading_card(key, value)
 
            with st.expander("Ver JSON completo"):
                st.json(data)
        else:
            # Si no es diccionario, mostrar como texto
            st.code(data)
else:
    st.markdown(
        '<div class="empty">📡 Aún no hay lecturas.<br>Pulsa «Obtener datos del sensor» para empezar.</div>',
        unsafe_allow_html=True,
    )

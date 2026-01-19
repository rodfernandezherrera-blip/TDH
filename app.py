import streamlit as st
import math
import urllib.parse

# 1. Configuración de la pestaña e Icono
st.set_page_config(page_title="TDH Pro", page_icon="b.PNG", layout="centered")

# 2. Inyección de Icono para iPhone y Estilos Pro
st.markdown(f'''
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/rodfernandezherrera-blip/TDH/main/b.PNG">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; background-color: #1565C0; color: white; font-weight: bold; border: none; }}
        .result-card {{ background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; border-left: 5px solid #1565C0; }}
    </style>
''', unsafe_allow_html=True)

st.title("💧Calculadora Hidráulica Sistema de Impulsión")
st.markdown("---")

# --- BLOQUE ÚNICO DE ENTRADA ---
st.subheader("📝 Datos de Entrada")
col_f1, col_f2 = st.columns(2)

with col_f1:
    tipo_fluido = st.selectbox("Fluido", ["Agua", "Pulpa Mineral"])
    L = st.number_input("Largo tubería (m)", value=100.0)
    D_mm = st.number_input("Diámetro Int. (mm)", value=100.0)

with col_f2:
    if tipo_fluido == "Agua":
        rho, tau_y, mu_p = 1000.0, 0.0, 0.001
        st.info("💧 Agua: 1000kg/m³ | 0 Pa | 0.001cP")
    else:
        rho = st.number_input("Densidad (kg/m³)", value=1250.0)
        tau_y = st.number_input("Yield Stress (Pa)", value=5.0)
        mu_p = st.number_input("Viscosidad (Pa·s)", value=0.010, format="%.3f")
    
    epsilon_mm = st.number_input("Rugosidad (mm)", value=0.045, format="%.3f")

col_op1, col_op2 = st.columns(2)
with col_op1:
    Q_h = st.number_input("Caudal (m³/h)", value=50.0)
with col_op2:
    dz = st.number_input("Δ Cota (m)", value=10.0)

st.markdown(" ") # Espaciador

# --- EJECUCIÓN ---
if st.button("🚀 CALCULAR TDH"):
    # Lógica de cálculos
    D = D_mm / 1000
    epsilon = epsilon_mm / 1000
    Q = Q_h / 3600
    g = 9.81
    V = Q / ((math.pi * D**2) / 4)

    He = (rho * tau_y * (D**2)) / (mu_p**2)
    Re_ct = 2100 * (1 + math.sqrt(He / 32000))
    Vt = (Re_ct * mu_p) / (rho * D)
    Re_b = (rho * V * D) / mu_p
    
    if V < Vt:
        f = (64 / Re_b) * (1 + (He / (6.22 * Re_b))**0.958)
        regimen = "LAMINAR (Bingham)"
        color_reg = "#FB8C00" # Naranja
    else:
        f_n = 0.25 / (math.log10((epsilon / (3.7 * D)) + (5.74 / (Re_b**0.9))))**2
        tau_w = (f_n * rho * V**2) / 2
        alpha = tau_y / tau_w if tau_w > 0 else 0
        f = f_n / ((1 + alpha/6)**2)
        regimen = "TURBULENTO"
        color_reg = "#2E7D32" # Verde

    J = f * (1 / D) * (V**2 / (2 * g))
    hf = J * L
    tdh = dz + hf + (1.5 * (V**2 / (2 * g)))
    presion = (tdh * rho * g) / 100000

    # --- PANEL DE RESULTADOS ---
    st.markdown("---")
    st.subheader("📊 Resultados del Sistema")
    
    st.markdown(f"""
    <div class="result-card">
        <p style="margin:0; color:#666;">Estado del Flujo</p>
        <h2 style="margin:0; color:{color_reg};">{regimen}</h2>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.metric("Gradiente (J)", f"{J:.6f} m/m")
    c1.metric("Pérdida (hf)", f"{hf:.2f} m")
    
    c2.metric("Velocidad (V)", f"{V:.2f} m/s")
    c2.metric("Presión", f"{presion:.2f} bar")

    st.divider()
    st.balloons()
    st.markdown(f"### 🎯 TDH TOTAL: {tdh:.2f} mcp")

    # --- FUNCIÓN WHATSAPP ---
    mensaje = (
        f"🚀 *Reporte Hidráulico TDH*\n"
        f"---------------------------\n"
        f"🔹 Fluido: {tipo_fluido}\n"
        f"🔹 Caudal: {Q_h} m3/h\n"
        f"🔹 Régimen: {regimen}\n"
        f"🔸 *J*: {J:.6f} m/m\n"
        f"🔸 *hf*: {hf:.2f} m\n"
        f"✅ *TDH TOTAL*: {tdh:.2f} m\n"
        f"✅ *Presión*: {presion:.2f} bar"
    )
    
    # Botón de WhatsApp
    msg_encoded = urllib.parse.quote(mensaje)
    whatsapp_url = f"https://wa.me/?text={msg_encoded}"
    
    st.markdown(f'''
        <a href="{whatsapp_url}" target="_blank">
            <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:12px; font-weight:bold; cursor:pointer;">
                📲 Compartir por WhatsApp
            </button>
        </a>
    ''', unsafe_allow_html=True)

else:
    st.info("Ingrese los datos arriba y presione el botón para calcular.")

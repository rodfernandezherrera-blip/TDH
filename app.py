import streamlit as st
import math

# 1. Configuración de la pestaña e Icono para navegadores
st.set_page_config(page_title="Calculadora Hidráulica", page_icon="b.PNG", layout="centered")

# 2. TRUCO MAESTRO PARA EL ICONO EN IPHONE (Safari)
# Esto fuerza a iOS a usar tu imagen b.PNG como icono de aplicación
st.markdown(f'''
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/rodfernandezherrera-blip/TDH/main/b.PNG">
    <link rel="apple-touch-icon-precomposed" href="https://raw.githubusercontent.com/rodfernandezherrera-blip/TDH/main/b.PNG">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; background-color: #1565C0; color: white; font-weight: bold; border: none; }}
        .result-card {{ background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; border-left: 5px solid #1565C0; }}
    </style>
''', unsafe_allow_html=True)

# --- CONTINUACIÓN DEL CÓDIGO ---
st.title("⚒️ Suite Hidráulica")
opcion_menu = st.radio("Seleccione el módulo de cálculo:", ["Calculadora TDH", "Balance de Masa"], horizontal=True)
st.markdown("---")

# [El resto del código de TDH y Balance de Masa se mantiene igual abajo...]



import streamlit as st
import math

# 1. Configuración de la pestaña e Icono
st.set_page_config(page_title="Hidráulica Pro", page_icon="b.PNG", layout="centered")

# 2. Estilos y configuración para iPhone
st.markdown(f'''
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/rodfernandezherrera-blip/TDH/main/b.PNG">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; background-color: #1565C0; color: white; font-weight: bold; border: none; }}
        .result-card {{ background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; border-left: 5px solid #1565C0; }}
        .nota-informativa {{ font-size: 0.85em; color: #555; font-style: italic; margin-top: 5px; }}
    </style>
''', unsafe_allow_html=True)

# --- MENÚ DE NAVEGACIÓN PRINCIPAL ---
st.title("⚒️ Suite Hidráulica")
opcion_menu = st.radio("Seleccione el módulo de cálculo:", ["Calculadora TDH", "Balance de Masa"], horizontal=True)
st.markdown("---")

# ==========================================
# MÓDULO 1: CALCULADORA TDH
# ==========================================
if opcion_menu == "Calculadora TDH":
    st.subheader("💧 Cálculo de TDH")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tipo_fluido = st.selectbox("Fluido", ["Agua", "Pulpa Mineral"])
        L = st.number_input("Largo tubería (m)", value=100.0)
        D_mm = st.number_input("Diámetro Int. (mm)", value=100.0)
    
    with col_f2:
        if tipo_fluido == "Agua":
            rho, tau_y, mu_p = 1000.0, 0.0, 0.001
            st.info("💧 Agua: 1000kg/m³ | 0.001 Pa*s")
        else:
            rho = st.number_input("Densidad (kg/m³)", value=1250.0)
            tau_y = st.number_input("Yield Stress (Pa)", value=5.0)
            mu_p = st.number_input("Viscosidad (Pa·s)", value=0.010, format="%.3f")
        
        material = st.selectbox("Material de Tubería", ["Acero", "HDPE", "Manual"])
        if material == "Acero": 
            epsilon_mm = 0.200
        elif material == "HDPE": 
            epsilon_mm = 0.05
        else: 
            epsilon_mm = st.number_input("Rugosidad (mm)", value=0.045, format="%.3f")

    col_op1, col_op2 = st.columns(2)
    with col_op1: Q_h = st.number_input("Caudal (m³/h)", value=50.0)
    with col_op2: dz = st.number_input("Δ Cota (m)", value=10.0)

    if st.button("🚀 CALCULAR TDH"):
        D, epsilon, Q, g = D_mm/1000, epsilon_mm/1000, Q_h/3600, 9.81
        V = Q / ((math.pi * D**2) / 4)
        He = (rho * tau_y * (D**2)) / (mu_p**2)
        Re_ct = 2100 * (1 + math.sqrt(He / 32000))
        Vt = (Re_ct * mu_p) / (rho * D)
        Re_b = (rho * V * D) / mu_p
        
        if V < Vt:
            f = (64 / Re_b) * (1 + (He / (6.22 * Re_b))**0.958)
            regimen, color_reg = "LAMINAR (Bingham)", "#FB8C00"
        else:
            f_n = 0.25 / (math.log10((epsilon / (3.7 * D)) + (5.74 / (Re_b**0.9))))**2
            tau_w = (f_n * rho * V**2) / 2
            alpha = tau_y / tau_w if tau_w > 0 else 0
            f = f_n / ((1 + alpha/6)**2)
            regimen, color_reg = "TURBULENTO", "#2E7D32"

        J = f * (1 / D) * (V**2 / (2 * g))
        hf = J * L
        tdh_final = (dz + hf + (1.5 * (V**2 / (2 * g)))) * 1.10 # Cambiado a 1.10 según tu instrucción previa
        presion = (tdh_final * rho * g) / 100000
        eficiencia = 0.90
        p_kw = (Q * rho * g * tdh_final) / (1000 * eficiencia)
        p_hp = p_kw * 1.341

        # --- RESULTADOS (Dentro del IF) ---
        st.markdown(f"""
        <div class="result-card">
            <p style="margin:0; color:#666;">Estado del Flujo</p>
            <h2 style="margin:0; color:{color_reg};">{regimen}</h2>
        </div>
        """, unsafe_allow_html=True)

        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Gradiente (J)", f"{J:.6f} m/m")
            st.metric("Pérdida Fricción (hf)", f"{hf:.2f} m")
            
        
        with col_res2:
            st.metric("Velocidad (V)", f"{V:.2f} m/s")
            st.metric("Presión Final", f"{presion:.2f} bar")
            st.metric("Potencia al Eje (HP)", f"{p_hp:.2f} HP")
            st.metric("Potencia al Eje (kW)", f"{p_kw:.2f} kW")
        
        st.divider()
        st.markdown(f"### 🎯 TDH TOTAL: {tdh_final:.2f} mcp")
        st.markdown('<p class="nota-informativa">Nota: Incluye factor 1.10 por singulares y η=90%.</p>', unsafe_allow_html=True)
    else:
        st.info("Configure los datos y presione Calcular.")

# ==========================================
# MÓDULO 2: BALANCE DE MASA
# ==========================================
elif opcion_menu == "Balance de Masa":
    st.subheader("⚖️ Balance de Masa (Sólidos/Líquidos)")
    
    tipo_calc = st.radio("Tipo de cálculo:", ["Directo (TMS a Flujo)", "Inverso (Flujo a TMS)"])
    st.markdown("---")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        ge = st.number_input("Gravedad Específica (GE)", value=2.70, format="%.2f")
    with col_b2:
        cp = st.number_input("% Conc. Sólidos (%Cp)", value=30.0, format="%.1f")

    if tipo_calc == "Directo (TMS a Flujo)":
        tms_in = st.number_input("Tonelaje Seco (TMS t/h)", value=100.0)
        if st.button("CALCULAR FLUJO"):
            f_agua = tms_in * (1 - cp/100) / (cp/100)
            vol_sol = tms_in / ge
            q_pulpa = vol_sol + f_agua
            rho_pulpa = (tms_in + f_agua) / q_pulpa
            
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.metric("Flujo de Pulpa", f"{q_pulpa:.2f} m³/h")
            st.metric("Flujo de Agua", f"{f_agua:.2f} m³/h")
            st.metric("Densidad Pulpa", f"{rho_pulpa:.3f} t/m³")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        qp_in = st.number_input("Flujo de Pulpa (m³/h)", value=150.0)
        if st.button("CALCULAR TMS"):
            tms_out = qp_in / ((1/ge) + ((100 - cp) / cp))
            f_agua = qp_in - (tms_out / ge)
            rho_pulpa = (tms_out + f_agua) / qp_in
            
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.metric("Tonelaje Seco (TMS)", f"{tms_out:.2f} t/h")
            st.metric("Flujo de Agua", f"{f_agua:.2f} m³/h")
            st.metric("Densidad Pulpa", f"{rho_pulpa:.3f} t/m³")
            st.markdown('</div>', unsafe_allow_html=True)

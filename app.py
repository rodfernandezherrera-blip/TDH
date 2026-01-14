import streamlit as st
import math

# Configuración de la página
st.set_page_config(page_title="Calculadora Hidráulica", page_icon="💧")

st.title("🚀 Diseño Hidráulico Slatter & Wasp")

# --- BARRA LATERAL (ENTRADAS) ---
st.sidebar.header("Configuración de Entrada")
tipo_fluido = st.sidebar.selectbox("Tipo de Fluido", ["Agua", "Pulpa Mineral"])

if tipo_fluido == "Agua":
    rho = 1000.0
    tau_y = 0.0
    mu_p = 0.001
    st.sidebar.info("Valores de Agua cargados por defecto.")
else:
    rho = st.sidebar.number_input("Densidad (kg/m3)", value=1250.0)
    tau_y = st.sidebar.number_input("Yield Stress (Pa)", value=5.0)
    mu_p = st.sidebar.number_input("Viscosidad Plástica (Pa·s)", value=0.010)

# Datos de tubería
st.sidebar.markdown("---")
L = st.sidebar.number_input("Largo tubería (m)", value=100.0)
D_mm = st.sidebar.number_input("Diámetro Int. (mm)", value=100.0)
epsilon_mm = st.sidebar.number_input("Rugosidad (mm)", value=0.045)
Q_h = st.sidebar.number_input("Caudal (m3/h)", value=50.0)
dz = st.sidebar.number_input("Diferencia de Cota (m)", value=10.0)

# --- CÁLCULOS ---
if st.sidebar.button("CALCULAR"):
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
        estado_color = "orange"
    else:
        f_n = 0.25 / (math.log10((epsilon / (3.7 * D)) + (5.74 / (Re_b**0.9))))**2
        tau_w = (f_n * rho * V**2) / 2
        alpha = tau_y / tau_w if tau_w > 0 else 0
        f = f_n / ((1 + alpha/6)**2)
        regimen = "TURBULENTO"
        estado_color = "green"

    J = f * (1 / D) * (V**2 / (2 * g))
    hf = J * L
    tdh = dz + hf + (1.5 * (V**2 / (2 * g)))
    presion = (tdh * rho * g) / 100000

    # --- RESULTADOS AMIGABLES ---
    st.subheader("Reporte de Resultados")
    
    col1, col2 = st.columns(2)
    col1.metric("Velocidad V", f"{V:.3f} m/s")
    col2.metric("Velocidad Vt", f"{Vt:.3f} m/s")
    
    st.write(f"Estado de flujo: :{estado_color}[**{regimen}**]")
    
    st.divider()
    
    st.success(f"**Gradiente Hidráulico (J):** {J:.6f} mcp/m")
    
    c1, c2, c3 = st.columns(3)
    c1.write("**Pérdida hf:**")
    c1.write(f"{hf:.2f} m")
    c2.write("**TDH Total:**")
    c2.write(f"{tdh:.2f} m")
    c3.write("**Presión:**")
    c3.write(f"{presion:.2f} bar")

else:
    st.info("Configura los datos en la barra lateral y presiona Calcular.")

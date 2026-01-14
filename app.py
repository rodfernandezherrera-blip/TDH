import math
import tkinter as tk
from tkinter import messagebox, ttk

def actualizar_tipo_fluido(*args):
    tipo = combo_fluido.get()
    if tipo == "Agua":
        # Insertar valores por defecto y deshabilitar edición
        entries["rho"].delete(0, tk.END)
        entries["rho"].insert(0, "1000")
        entries["mu"].delete(0, tk.END)
        entries["mu"].insert(0, "0.001")
        entries["tau"].delete(0, tk.END)
        entries["tau"].insert(0, "0")
        
        entries["rho"].config(state='disabled')
        entries["mu"].config(state='disabled')
        entries["tau"].config(state='disabled')
    else:
        # Habilitar campos para ingreso manual
        entries["rho"].config(state='normal')
        entries["mu"].config(state='normal')
        entries["tau"].config(state='normal')

def calcular():
    try:
        # 1. OBTENCIÓN DE DATOS (Habilitamos temporalmente para leer valores deshabilitados)
        for key in ["rho", "mu", "tau"]: entries[key].config(state='normal')
        
        L = float(entries["L"].get())
        D_mm = float(entries["D_mm"].get())
        z_succion = float(entries["z_s"].get())
        z_descarga = float(entries["z_d"].get())
        epsilon_mm = float(entries["eps"].get())
        Q_h = float(entries["Q"].get())
        rho = float(entries["rho"].get())
        tau_y = float(entries["tau"].get())
        mu_p = float(entries["mu"].get())
        
        actualizar_tipo_fluido() # Re-bloquear si es necesario

        # 2. LÓGICA DE CÁLCULO
        D = D_mm / 1000
        epsilon = epsilon_mm / 1000
        dz = z_descarga - z_succion
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
            color_reg = "#e67e22"
        else:
            f_n = 0.25 / (math.log10((epsilon / (3.7 * D)) + (5.74 / (Re_b**0.9))))**2
            tau_w = (f_n * rho * V**2) / 2
            alpha = tau_y / tau_w if tau_w > 0 else 0
            f = f_n / ((1 + alpha/6)**2)
            regimen = "TURBULENTO"
            color_reg = "#27ae60"

        J = f * (1 / D) * (V**2 / (2 * g))
        hf = J * L
        tdh_total = dz + hf + (1.5 * (V**2 / (2 * g)))
        presion_bar = (tdh_total * rho * g) / 100000

        # 3. ACTUALIZAR INTERFAZ
        res_vars["V"].set(f"{V:.3f} m/s")
        res_vars["Vt"].set(f"{Vt:.3f} m/s")
        res_vars["Reg"].set(regimen)
        lbl_regimen.config(fg=color_reg)
        res_vars["J"].set(f"{J:.6f} mcp/m")
        res_vars["hf"].set(f"{hf:.2f} m")
        res_vars["TDH"].set(f"{tdh_total:.2f} m")
        res_vars["Presion"].set(f"{presion_bar:.2f} bar")

    except Exception as e:
        messagebox.showerror("Error", "Verifique que todos los campos tengan números válidos.")

# --- CONFIGURACIÓN DE LA VENTANA ---
root = tk.Tk()
root.title("Calculadora Hidráulica Slatter & Wasp")
root.geometry("480x700")

# SELECTOR DE TIPO DE FLUIDO
frame_top = tk.Frame(root, pady=10)
frame_top.pack()
tk.Label(frame_top, text="Tipo de Fluido:", font=("Arial", 10, "bold")).pack(side="left")
combo_fluido = ttk.Combobox(frame_top, values=["Agua", "Pulpa Mineral"], state="readonly")
combo_fluido.set("Pulpa Mineral")
combo_fluido.pack(side="left", padx=10)
combo_fluido.bind("<<ComboboxSelected>>", actualizar_tipo_fluido)

# SECCIÓN DE ENTRADAS
frame_in = tk.LabelFrame(root, text=" Datos de Entrada ", padx=10, pady=10)
frame_in.pack(padx=20, fill="x")

labels_text = [
    ("Largo tubería (m):", "L"), ("Diámetro Int. (mm):", "D_mm"),
    ("Cota inicial (m):", "z_s"), ("Cota final (m):", "z_d"),
    ("Rugosidad (mm):", "eps"), ("Caudal (m3/h):", "Q"),
    ("Densidad (kg/m3):", "rho"), ("Yield Stress (Pa):", "tau"),
    ("Viscosidad (Pa·s):", "mu")
]

entries = {}
for i, (txt, key) in enumerate(labels_text):
    tk.Label(frame_in, text=txt).grid(row=i, column=0, sticky="w", pady=2)
    ent = tk.Entry(frame_in, justify="center")
    ent.grid(row=i, column=1, padx=10, sticky="e")
    entries[key] = ent

btn_calc = tk.Button(root, text="CALCULAR", command=calcular, bg="#2c3e50", fg="white", font=("Arial", 11, "bold"))
btn_calc.pack(pady=15, fill="x", padx=20)

# SECCIÓN DE RESULTADOS
frame_out = tk.LabelFrame(root, text=" Reporte de Resultados ", padx=10, pady=10)
frame_out.pack(padx=20, fill="both", expand=True)

res_vars = {k: tk.StringVar(value="--") for k in ["V", "Vt", "Reg", "J", "hf", "TDH", "Presion"]}

def crear_fila_res(row, label, var_key, color="black"):
    tk.Label(frame_out, text=label).grid(row=row, column=0, sticky="w", pady=2)
    lbl = tk.Label(frame_out, textvariable=res_vars[var_key], font=("Arial", 10, "bold"), fg=color)
    lbl.grid(row=row, column=1, sticky="e", padx=20)
    return lbl

crear_fila_res(0, "Velocidad de Flujo:", "V")
crear_fila_res(1, "Velocidad de Transición:", "Vt")
lbl_regimen = crear_fila_res(2, "Régimen de Flujo:", "Reg")
tk.Label(frame_out, text="-"*40, fg="grey").grid(row=3, columnspan=2)
crear_fila_res(4, "Gradiente Hidráulico (J):", "J", "#c0392b")
crear_fila_res(5, "Pérdida por Fricción (hf):", "hf")
crear_fila_res(6, "TDH Total Requerido:", "TDH")
crear_fila_res(7, "Presión Bomba:", "Presion", "#2980b9")

root.mainloop()

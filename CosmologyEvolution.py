import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button  
from scipy.integrate import solve_ivp
from scipy.fft import rfft, rfftfreq
import sys

# Gestione del suono nativa cross-platform
if sys.platform.startswith('win'):
    import winsound
    def riproduci_suono(frequenza):
        winsound.Beep(frequenza, 300)  
else:
    import os
    def riproduci_suono(frequenza):
        print('\a')
        os.system('echo -e "\a"')

# --- 1. CONFIGURAZIONE GEOMETRICA E COERENZA MODALE ---
N_u = 6
u = np.linspace(0, 2 * np.pi, N_u)
risoluzione_base = 2400  

# --- 2. SOLUTORE INTRINSECAMENTE IPERBOLICO (GEOMETRODINAMICA COVARIANTE PURA) ---
def equazione_stato_einstein_cartan(tau, stato_metrico, scatolamento):
    chi = stato_metrico[0] 
    velocita_chi = stato_metrico[1]
    
    # Sostituzione del clamping con transizione asintotica continua nativa (tanh)
    chi_sat = 150.0 * np.tanh(chi / 150.0)
    log_r_dx = chi_sat
    
    # Coefficienti di scala strutturalmente speculari ed equivalenti
    fattore_dx = np.exp(log_r_dx * 0.1)  
    fattore_sx = np.exp(-log_r_dx * 0.1)
    
    arg_dx = (4 * np.pi / risoluzione_base) * fattore_dx / (1.0 + log_r_dx**2)
    arg_sx = (4 * np.pi / risoluzione_base) * fattore_sx
    
    chiralita = np.where(np.arange(risoluzione_base) % 2 == 0, 1.0, -1.0)
    tor_dx = np.sinh(chiralita * arg_dx)
    tor_sx = np.sinh(chiralita * arg_sx)
    
    mu_dx = np.mean(np.abs(tor_dx))
    mu_sx = np.mean(np.abs(tor_sx))
    
    tensione_taglio = np.mean(tor_dx * tor_sx)
    energia_torsionale = np.mean((np.abs(tor_dx) - np.abs(tor_sx))**2)
    
    r_conforme = 5.0 * np.exp(log_r_dx * 0.05)
    accoppiamento_topologico = 1.0 / (r_conforme**2 + 1e-6)
    
    densita_materia = (mu_sx - mu_dx) * scatolamento
    tensione_newtoniana = tensione_taglio * accoppiamento_topologico
    densita_torsione_quadratica = (tensione_taglio**2 + energia_torsionale**2) * accoppiamento_topologico
    
    # La pressione emerge unicamente dal bilancio delle densità energetiche torsionali
    pressione_vuoto = densita_materia - tensione_newtoniana - densita_torsione_quadratica
    
    # Sostituzione dell'if/else con Jacobiano analitico unificato continuo
    jacobiano_metrico = 1.0 + 4.0 * (1.0 + np.tanh(np.abs(chi_sat) - 13.5)) / (np.abs(chi_sat) + 1e-9)
        
    # Accelerazione pura spogliata da qualsiasi toppa di smorzamento o attrito viscoso indotto a mano
    accelerazione_conforme = pressione_vuoto * (jacobiano_metrico + 1e-9)
        
    return [velocita_chi, accelerazione_conforme]

# --- 3. DEFINIZIONE STILI GRAFICI ---
def set_style_3d(ax, title, color):
    ax.set_title(title, color=color, fontsize=9, weight='bold', pad=15)
    ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))
    ax.xaxis._axinfo["grid"].update({'color': '#22c55e', 'linewidth': 0.1, 'alpha': 0.15})
    ax.yaxis._axinfo["grid"].update({'color': '#22c55e', 'linewidth': 0.1, 'alpha': 0.15})
    ax.zaxis._axinfo["grid"].update({'color': '#22c55e', 'linewidth': 0.1, 'alpha': 0.15})
    ax.tick_params(colors='#64748b', labelsize=7)

def set_style_2d(ax, title, color):
    ax.set_title(title, color=color, fontsize=9, weight='bold', pad=10)
    ax.spines['bottom'].set_color('#1e293b'); ax.spines['left'].set_color('#1e293b')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#64748b', labelsize=7)
    ax.grid(color='#22c55e', linestyle='--', linewidth=0.1, alpha=0.2)

# --- 4. INIZIALIZZAZIONE INTERFACCIA E SUBPLOTS ---
fig = plt.figure(figsize=(18, 10), facecolor='#020617')
gs = fig.add_gridspec(2, 3, height_ratios=[1.2, 0.8], hspace=0.35, wspace=0.25)
plt.subplots_adjust(bottom=0.15, top=0.88, left=0.06, right=0.90)

ax_mat = fig.add_subplot(gs[0, 0], projection='3d', facecolor='#020617')
ax_main = fig.add_subplot(gs[0, 1], projection='3d', facecolor='#020617')
ax_spa = fig.add_subplot(gs[0, 2], projection='3d', facecolor='#020617')

set_style_3d(ax_mat, "SPETTRO MATERIA 3D (CHIRALITÀ SX)", '#ff007f')
set_style_3d(ax_main, "TOPOLOGIA GLOBALE INTRINSECA REALE", '#deff9a')
set_style_3d(ax_spa, "SPETTRO SPAZIO 3D (CHIRALITÀ DX)", '#00d2ff')

ax_fft = fig.add_subplot(gs[1, 0:2], facecolor='#020617') 
ax_fractal = fig.add_subplot(gs[1, 2], facecolor='#020617') 

set_style_2d(ax_fft, "TELEMETRIA GEOMETRICA PURA: FFT, IMPEDENZA Z & GRAVITÀ G", '#deff9a')
set_style_2d(ax_fractal, "COMPLESSITÀ FRATTALE ORIGINARIA (HAUSDORFF PROXY)", '#ffb100')

ax_z_axis = ax_fft.twinx()
ax_z_axis.spines['top'].set_visible(False); ax_z_axis.spines['left'].set_visible(False)
ax_z_axis.spines['right'].set_color('#ff007f'); ax_z_axis.tick_params(colors='#ff007f', labelsize=7)

ax_g_axis = ax_fft.twinx()
ax_g_axis.spines['top'].set_visible(False); ax_g_axis.spines['left'].set_visible(False)
ax_g_axis.spines['right'].set_position(('outward', 45))
ax_g_axis.spines['right'].set_color('#38bdf8'); ax_g_axis.tick_params(colors='#38bdf8', labelsize=7)

linea_mat, = ax_mat.plot([], [], [], color='#ff007f', lw=1.2, alpha=0.8)
linea_spa, = ax_spa.plot([], [], [], color='#00d2ff', lw=1.2, alpha=0.8)
scat_dx = ax_main.scatter([], [], [], color='#00d2ff', s=0.5, alpha=0.1)
scat_sx = ax_main.scatter([], [], [], color='#ff007f', s=2.2, alpha=0.7)

linea_fft, = ax_fft.plot([], [], color='#deff9a', lw=1.5, label='FFT Modale (SX)')
linea_z, = ax_z_axis.plot([], [], color='#ff007f', lw=1.2, linestyle='--', label='Z Vuoto')
linea_g, = ax_g_axis.plot([], [], color='#38bdf8', lw=1.5, linestyle='-', label='G Emergente')
linea_fractal, = ax_fractal.plot([], [], color='#ffb100', lw=1.5)

punti_complessita = []
punti_G = []
punti_Z = []

text_info = fig.text(0.06, 0.96, "", color='#deff9a', fontname='monospace', fontsize=8, weight='bold', verticalalignment='top')

linee = [linea_fft, linea_z, linea_g]
etichette = [l.get_label() for l in linee]
legenda = ax_fft.legend(linee, etichette, loc='upper right', facecolor='#0f172a', edgecolor='#1e293b', fontsize=8)
for testo in legenda.get_texts(): testo.set_color('#64748b')

# --- 5. ENGINE DI PROIEZIONE GEOMETRICA UNIFICATO ---
stato_attuale = [-4.50, 0.1] 
tau_corrente = 0.0
complessita_precedente = None
tempo_relazionale_cumulativo = 0.0  
animazione_in_esecuzione = False

velocita_precedente = stato_attuale[1]
suono_inversione_fatto = False
suono_tempo_fatto = False

def genera_mappatura(log_r, frame):
    log_r_clamped = 150.0 * np.tanh(log_r / 150.0)
    
    # Rettifica dell'asimmetria empirica: fattori speculari specchiati coerenti
    f_dx = np.exp(log_r_clamped * 0.02)
    f_sx = np.exp(-log_r_clamped * 0.02)
    
    theta = np.linspace(0, 4 * np.pi, risoluzione_base)
    freq = 12.0 + (np.floor(np.abs(log_r_clamped * 0.2)) * 2.0)
    r_m = 5.0 * np.exp(log_r_clamped * 0.05)
    
    # Sincronizzazione ed eliminazione dell'ortogonalità artificiale (Seno vs Coseno)
    distorsione_topologica = (f_dx - f_sx) * 0.002
    theta_spazio = theta + distorsione_topologica * np.sin(3.0 * theta)
    theta_materia = theta - distorsione_topologica * np.sin(3.0 * theta)
    
    # Ripristino dell'inviluppo lineare continuo puro (Rimossa la radice quadra 0.15)
    env_dx = 1.5 * np.sin(freq * theta_spazio)
    env_sx = 1.5 * np.sin(freq * theta_materia)
    
    p_dx = env_dx * f_dx
    p_sx = env_sx * f_sx
    
    # Costruzione dello spazio conforme tridimensionale tramite triedro di Frenet-Serret
    xb = r_m * np.cos(theta); yb = r_m * np.sin(theta); zb = np.zeros_like(theta)
    T = np.vstack(np.gradient([xb,yb,zb], axis=1)); T /= (np.linalg.norm(T, axis=0) + 1e-12)
    N = np.vstack(np.gradient(T, axis=1)); N /= (np.linalg.norm(N, axis=0) + 1e-12)
    B = np.cross(T.T, N.T).T
    
    A_DX = u[:, None] + (theta/2)[None, :] + frame*0.05
    A_SX = u[:, None] - (theta/2)[None, :] - frame*0.05
    
    foc_dx = 0.8 * f_dx * (1 + 0.3 * np.sin(freq*theta_spazio))
    foc_sx = 0.8 * f_sx * (1 + 0.3 * np.sin(freq*theta_materia))
    
    x_s = (r_m + (p_dx + p_sx)*0.5) * np.cos(theta)
    y_s = (r_m + (p_dx + p_sx)*0.5) * np.sin(theta)
    z_s = (r_m * 0.4) * np.cos(freq * theta)
    
    X_dx = x_s + foc_dx * (np.cos(A_DX)*N[0] + np.sin(A_DX)*B[0])
    Y_dx = y_s + foc_dx * (np.cos(A_DX)*N[1] + np.sin(A_DX)*B[1])
    Z_dx = z_s + foc_dx * (np.cos(A_DX)*N[2] + np.sin(A_DX)*B[2])
    
    X_sx = x_s + foc_sx * (np.cos(A_SX)*N[0] + np.sin(A_SX)*B[0])
    Y_sx = y_s + foc_sx * (np.cos(A_SX)*N[1] + np.sin(A_SX)*B[1])
    Z_sx = z_s + foc_sx * (np.cos(A_SX)*N[2] + np.sin(A_SX)*B[2])
    
    return X_dx.flatten(), Y_dx.flatten(), Z_dx.flatten(), X_sx.flatten(), Y_sx.flatten(), Z_sx.flatten(), r_m, freq, theta, p_dx, p_sx

# --- 6. LOOP DI COERENZA DINAMICA INTEGRALE ---
def update(frame):
    global stato_attuale, tau_corrente, complessita_precedente, tempo_relazionale_cumulativo 
    global punti_complessita, punti_G, punti_Z, animazione_in_esecuzione, velocita_precedente
    global suono_inversione_fatto, suono_tempo_fatto
    
    d_tau = 0.06
    if animazione_in_esecuzione:
        sol = solve_ivp(equazione_stato_einstein_cartan, [tau_corrente, tau_corrente+d_tau], stato_attuale, args=(2.0,), method='Radau')
        stato_attuale = sol.y[:, -1]
        tau_corrente += d_tau

    chi = stato_attuale[0]
    velocita_chi = stato_attuale[1]
    
    Xdx, Ydx, Zdx, Xsx, Ysx, Zsx, rm, fr, th, pdx, psx = genera_mappatura(chi, frame)
    
    scat_dx._offsets3d = (Xdx, Ydx, Zdx)
    scat_sx._offsets3d = (Xsx, Ysx, Zsx)
    lim = max(0.1, rm * 1.8)  
    for ax in [ax_main, ax_mat, ax_spa]: 
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
        ax.set_box_aspect((1,1,1))
    
    zs = np.sin(th*2) * rm * 0.2
    linea_mat.set_data_3d((rm+psx)*np.cos(th), (rm+psx)*np.sin(th), zs)
    linea_spa.set_data_3d((rm+pdx)*np.cos(th), (rm+pdx)*np.sin(th), zs)

    yf = rfft(psx)
    xf = rfftfreq(risoluzione_base, d=(th[1]-th[0]))
    linea_fft.set_data(xf[:120], np.abs(yf[:120]))
    ax_fft.set_xlim(0, 25); ax_fft.set_ylim(0, np.max(np.abs(yf[:120]))*1.1 if np.max(np.abs(yf[:120])) > 0 else 1.0)
    
    mu_dx_ist = np.mean(np.abs(pdx))
    mu_sx_ist = np.mean(np.abs(psx))
    tensione_taglio_ist = np.mean(pdx * psx)
    energia_torsionale = np.mean((np.abs(pdx) - np.abs(psx))**2)
    
    G_topologica = np.abs(tensione_taglio_ist) / ((mu_dx_ist * mu_sx_ist) + 1e-12)
    alpha_G = 6.74088e-11 
    G_fisica = G_topologica * alpha_G
    Z_vuoto = np.abs(energia_torsionale) / (np.abs(tensione_taglio_ist) + 1e-12)
    
    punti_G.append(G_fisica)
    punti_Z.append(Z_vuoto)
    if len(punti_G) > 100: punti_G.pop(0)
    if len(punti_Z) > 100: punti_Z.pop(0)
    
    asse_x_dinamico = np.linspace(0, 25, len(punti_G))
    linea_g.set_data(asse_x_dinamico, punti_G)
    linea_z.set_data(asse_x_dinamico, punti_Z)
    
    z_min, z_max = min(punti_Z), max(punti_Z)
    if np.abs(z_max - z_min) < 1e-16:
        ax_z_axis.set_ylim(z_min * 0.9, z_min * 1.1 if z_min > 0 else 1.0)
    else:
        ax_z_axis.set_ylim(z_min - (z_max-z_min)*0.1, z_max + (z_max-z_min)*0.1)
        
    g_min, g_max = min(punti_G), max(punti_G)
    if np.abs(g_max - g_min) < 1e-16:
        ax_g_axis.set_ylim(g_min * 0.999, g_min * 1.001)
    else:
        ax_g_axis.set_ylim(g_min - (g_max-g_min)*0.1, g_max + (g_max-g_min)*0.1)
    
    chi_sat_ev = 150.0 * np.tanh(chi / 150.0)
    if np.abs(chi_sat_ev) < 15.0:
        esponente_reale = chi_sat_ev - 4.5
    else:
        esponente_reale = np.sign(chi_sat_ev) * (15.0 + np.log(np.abs(chi_sat_ev) - 13.5) * 5.0) - 4.5
        
    Massa_simulata = np.sum(np.abs(psx)) * (th[1] - th[0])
    volume_conforme = rm**3
    rho_materia = Massa_simulata / (volume_conforme + 1e-12)
    rho_torsione = energia_torsionale / (volume_conforme + 1e-12)
    rho_totale = np.abs(rho_materia - rho_torsione)
    
    H_quadrato = (8.0 * np.pi * G_fisica / 3.0) * rho_totale
    
    # Rigenerazione del parametro di Hubble tramite il Jacobiano analitico unificato
    jac_ev = 1.0 + 4.0 * (1.0 + np.tanh(np.abs(chi_sat_ev) - 13.5)) / (np.abs(chi_sat_ev) + 1e-9)
    hubble_metrico_puro = velocita_chi * jac_ev * np.log(10)
    H_fisica = np.sign(hubble_metrico_puro) * np.sqrt(H_quadrato + 2.197e-36)
    
    comp = np.sum(np.abs(np.diff(psx))) / (rm + 1e-9)
    punti_complessita.append(comp)
    if len(punti_complessita) > 100: punti_complessita.pop(0)
    linea_fractal.set_data(range(len(punti_complessita)), punti_complessita)
    ax_fractal.set_xlim(0, 100); ax_fractal.set_ylim(0, max(punti_complessita)*1.2 if punti_complessita else 1.0)

    if animazione_in_esecuzione:
        if complessita_precedente is not None:
            # Eliminazione radicale del pavimento artificiale: scorrimento relazionale puro
            tempo_relazionale_cumulativo += np.abs(comp - complessita_precedente) * 0.1
        complessita_precedente = comp

    # --- INTEGRAZIONE E SCALATURA TEMPORALE MULTISCALA ---
    frequenza_orologio = np.sqrt(H_fisica**2 + 1e-36)
    tempo_assoluto_secondi = tempo_relazionale_cumulativo / (frequenza_orologio + 1e-43)
    
    if tempo_assoluto_secondi < 1e-9:
        valore_scalato = tempo_assoluto_secondi * 1e12
        unita_misura = "ps (picosecondi)"
    elif tempo_assoluto_secondi < 1e-6:
        valore_scalato = tempo_assoluto_secondi * 1e9
        unita_misura = "ns (nanosecondi)"
    elif tempo_assoluto_secondi < 1e-3:
        valore_scalato = tempo_assoluto_secondi * 1e6
        unita_misura = "µs (microsecondi)"
    elif tempo_assoluto_secondi < 1.0:
        valore_scalato = tempo_assoluto_secondi * 1e3
        unita_misura = "ms (millisecondi)"
    elif tempo_assoluto_secondi < 60.0:
        valore_scalato = tempo_assoluto_secondi
        unita_misura = "s (secondi)"
    elif tempo_assoluto_secondi < 3600.0:
        valore_scalato = tempo_assoluto_secondi / 60.0
        unita_misura = "min (minuti)"
    elif tempo_assoluto_secondi < 86400.0:
        valore_scalato = tempo_assoluto_secondi / 3600.0
        unita_misura = "hour (ore)"
    elif tempo_assoluto_secondi < 3.1536e16:
        valore_scalato = tempo_assoluto_secondi / 86400.0
        unita_misura = "days (giorni)"
    else:
        valore_scalato = tempo_assoluto_secondi / 3.1536e16
        unita_misura = "Gyr (miliardi di anni)"
    
    fase_moto = "BIG CRUNCH (CONTRAZIONE INVERSA)" if velocita_chi < 0 else "ESPANSIONE CONFORME"
    
    text_info.set_text(
        f"METRICA: 10^({esponente_reale:.2f})m | DINAMICA: {fase_moto} \n"
        f"OROLOGIO RELAZIONALE: {valore_scalato:.6f} {unita_misura} | H_REALE: {H_fisica:.6e} s^-1 | \n"
        f"G_FISICA: {G_fisica:.6e} m^3 kg^-1 s^-2 | Z_VUOTO: {Z_vuoto:.4e}"
    )
    
    # --- SEGNALAZIONI ACUSTICHE CONTINUATIVE (SENZA INTERRUZIONE DEL MOTORE) ---
    if animazione_in_esecuzione:
        # Nota acuta (1200 Hz) per segnalare il passaggio del punto critico (Bounce geometrico)
        if np.sign(velocita_chi) != np.sign(velocita_precedente) and frame > 2:
            if not suono_inversione_fatto:
                suono_inversione_fatto = True
                print(f"[AUDIO] Punto di inversione (Bounce) intercettato alla metrica: 10^{esponente_reale:.2f}m")
                riproduci_suono(1200)
            
        # Nota grave (500 Hz) per l'ingresso stabile nell'era macroscopica
        elif esponente_reale >= 0 and tempo_assoluto_secondi > 1e-3 and not suono_tempo_fatto:
            suono_tempo_fatto = True
            print(f"[AUDIO] Ingresso stabile nel macrocosmo. Unità orologio: {unita_misura}")
            riproduci_suono(500)

    velocita_precedente = velocita_chi
    return scat_dx, scat_sx, linea_mat, linea_spa, linea_fft, linea_z, linea_g, linea_fractal

# --- 7. CONTROLLI UTENTE INTERATTIVI ---
ax_btn = fig.add_axes([0.45, 0.04, 0.1, 0.04])
btn = Button(ax_btn, 'PLAY', color='#16a34a', hovercolor='#15803d')
btn.label.set_color('white'); btn.label.set_weight('bold')

def toggle(e):
    global animazione_in_esecuzione
    animazione_in_esecuzione = not animazione_in_esecuzione
    btn.label.set_text("PAUSE" if animazione_in_esecuzione else "PLAY")
    btn.ax.set_facecolor('#dc2626' if animazione_in_esecuzione else '#16a34a')

btn.on_clicked(toggle)
ax_main.mouse_init(); ax_mat.mouse_init(); ax_spa.mouse_init()

ani = FuncAnimation(fig, update, frames=200, interval=50, blit=False)
plt.show()

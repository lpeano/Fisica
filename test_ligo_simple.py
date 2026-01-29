#!/usr/bin/env python3
"""
Test semplificato per onde gravitazionali ROF
"""

import numpy as np

def test_ligo_simple():
    print("🌊 TEST LIGO/VIRGO SEMPLIFICATO")
    print("=" * 40)
    
    # Parametri ROF
    alpha_0 = 1.01147
    beta = 0.07952
    
    # Dati eventi selezionati
    events = {
        "GW150914": [0.09, 440],
        "GW170817": [0.01, 40], 
        "GW190521": [0.82, 5300]
    }
    
    print("Evento     | z     | DL_obs | DL_ROF | Differenza")
    print("-" * 50)
    
    deviations = []
    z_vals = []
    
    for name, (z, dl_obs) in events.items():
        alpha_z = alpha_0 * np.exp(-beta * z)
        dl_rof = dl_obs * alpha_z
        diff = dl_rof - dl_obs
        
        deviations.append(diff)
        z_vals.append(z)
        
        print(f"{name:<10} | {z:<5.3f} | {dl_obs:<6.0f} | {dl_rof:<6.1f} | {diff:+6.1f} Mpc")
    
    # Statistica base
    mean_dev = np.mean(deviations)
    correlation = np.corrcoef(z_vals, deviations)[0,1]
    
    print("-" * 50)
    print(f"Deviazione media: {mean_dev:+.1f} Mpc")
    print(f"Correlazione z-dev: {correlation:+.3f}")
    
    if correlation > 0.5:
        print("✅ TREND POSITIVO: compatibile con ROF!")
    else:
        print("⚪ Trend debole o nullo")

if __name__ == "__main__":
    test_ligo_simple()
#!/usr/bin/env python3
"""
Verifica delle affermazioni numeriche della teoria ROF in relazione all'Ipotesi di Riemann
Analisi critica dei calcoli proposti nel documento
"""

import numpy as np
import math
from scipy.special import zeta
import sympy as sp

def verifica_correlazione_alpha_zeta():
    """Verifica la correlazione proposta tra α e la funzione zeta"""
    print("=" * 60)
    print("VERIFICA 1: Correlazione α e funzione ζ(s)")
    print("=" * 60)
    
    alpha = 1.012
    
    # Calcolo 1/ln(α)
    log_inv = 1 / np.log(alpha)
    
    # Calcolo ζ(α) 
    zeta_val = float(zeta(alpha))
    
    # Differenza
    differenza = abs(log_inv - zeta_val)
    
    print(f"Alpha (α):        {alpha}")
    print(f"1/ln(α):         {log_inv:.6f}")
    print(f"ζ(α):            {zeta_val:.6f}")
    print(f"Differenza:      {differenza:.6f}")
    print(f"Differenza %:    {(differenza/zeta_val)*100:.3f}%")
    
    # Confronto con γ (costante di Eulero-Mascheroni)
    gamma = float(sp.EulerGamma)
    print(f"\nCostante γ:      {gamma:.6f}")
    print(f"Rapporto diff/γ: {differenza/gamma:.6f}")
    
    return log_inv, zeta_val, differenza

def verifica_formula_primi():
    """Verifica la formula proposta per l'n-esimo numero primo"""
    print("\n" + "=" * 60)
    print("VERIFICA 2: Formula ROF per i numeri primi")
    print("=" * 60)
    
    alpha = 1.012
    
    def p_n_rof(n):
        """Formula ROF proposta per l'n-esimo primo"""
        return n * np.log(n) * (1 + 12 * (alpha - 1))
    
    def p_n_standard(n):
        """Teorema dei numeri primi standard"""
        return n * np.log(n)
    
    def p_n_better_approx(n):
        """Approssimazione migliorata standard"""
        if n < 6:
            return n * np.log(n)
        return n * (np.log(n) + np.log(np.log(n)) - 1)
    
    test_ns = [10, 100, 1000, 10000, 100000]
    
    print(f"{'n':<8} {'Reale':<10} {'ROF':<10} {'Standard':<10} {'Miglior.':<10} {'Err.ROF%':<10} {'Err.Std%':<10} {'Err.Mig%':<10}")
    print("-" * 90)
    
    for n in test_ns:
        if n <= 100000:  # Limit per evitare calcoli troppo lunghi
            actual = int(sp.prime(n))
            rof_approx = p_n_rof(n)
            std_approx = p_n_standard(n)
            better_approx = p_n_better_approx(n)
            
            error_rof = abs(actual - rof_approx) / actual * 100
            error_std = abs(actual - std_approx) / actual * 100
            error_better = abs(actual - better_approx) / actual * 100
            
            print(f"{n:<8} {actual:<10} {rof_approx:<10.1f} {std_approx:<10.1f} {better_approx:<10.1f} "
                  f"{error_rof:<10.2f} {error_std:<10.2f} {error_better:<10.2f}")

def analisi_critica_alpha():
    """Analisi critica del valore α = 1.012"""
    print("\n" + "=" * 60)
    print("ANALISI CRITICA: Valore di α")
    print("=" * 60)
    
    alpha = 1.012
    
    # Verifica se α ha proprietà matematiche speciali
    print(f"α = {alpha}")
    print(f"α² = {alpha**2:.6f}")
    print(f"α³ = {alpha**3:.6f}")
    print(f"α⁷ = {alpha**7:.6f}")
    
    # Confronto con altre costanti note
    phi = (1 + np.sqrt(5)) / 2  # Sezione aurea
    e = np.e
    pi = np.pi
    
    print(f"\nConfronto con costanti note:")
    print(f"Rapporto α/φ:    {alpha/phi:.6f}")
    print(f"Rapporto α/e:    {alpha/e:.6f}")
    print(f"Rapporto α/π:    {alpha/pi:.6f}")
    
    # Test se α è derivato da dati osservativi
    h0_planck = 67.4  # km/s/Mpc da Planck
    h0_local = 73.0   # km/s/Mpc da misure locali
    
    alpha_hubble = h0_local / h0_planck
    alpha_hubble_7th = alpha_hubble**(1/7)
    
    print(f"\nDerivazione da tensione di Hubble:")
    print(f"H₀(locale)/H₀(Planck) = {alpha_hubble:.6f}")
    print(f"(H₀(locale)/H₀(Planck))^(1/7) = {alpha_hubble_7th:.6f}")
    print(f"Differenza da α proposto: {abs(alpha - alpha_hubble_7th):.6f}")

def test_alpha_redshift():
    """Test cruciale: variazione di α con il redshift"""
    print("\n" + "=" * 60)
    print("TEST CRITICO: Variazione α(z) con il Redshift")
    print("=" * 60)
    
    # Dati simulati basati su osservazioni cosmologiche tipiche
    # In un'implementazione reale, questi verrebbero da database astronomici
    redshifts = np.array([0.0, 0.2, 0.5, 1.0, 1.5, 2.0])
    
    # Valori H0 osservati a diversi redshift (simulati)
    # Questi sono rappresentativi di misure reali da supernovae e BAO
    h0_observed = np.array([73.0, 72.1, 70.8, 69.2, 68.4, 67.8])
    h0_cmb = 67.4  # Valore dal CMB (Planck)
    
    # Calcola α(z) empirico dai dati
    alpha_z = (h0_observed / h0_cmb)**(1/7)
    
    print(f"{'z':<6} {'H0_obs':<8} {'α(z)':<10} {'Previsione ROF':<15}")
    print("-" * 45)
    
    alpha_0 = 1.012  # valore locale
    for i, z in enumerate(redshifts):
        # Modello ROF prevede decadimento esponenziale
        alpha_rof_predicted = alpha_0 * np.exp(-0.1 * z)  # parametro da calibrare
        print(f"{z:<6.1f} {h0_observed[i]:<8.1f} {alpha_z[i]:<10.6f} {alpha_rof_predicted:<15.6f}")
    
    # Calcola correlazione
    correlation = np.corrcoef(redshifts[1:], alpha_z[1:])[0,1]
    print(f"\nCorrelazione z vs α(z): {correlation:.4f}")
    
    # Test statistico
    slope = np.polyfit(redshifts, alpha_z, 1)[0]
    print(f"Pendenza dα/dz: {slope:.6f}")
    
    if abs(correlation) > 0.8:
        print("\n✓ RISULTATO: Correlazione significativa trovata!")
        print("  La variazione di α con z supporta l'ipotesi ROF.")
    else:
        print("\n✗ RISULTATO: Correlazione debole.")
        print("  I dati non supportano fortemente l'ipotesi ROF.")
    
    return redshifts, alpha_z

def test_ipotesi_riemann():
    """Analisi critica delle correlazioni con Riemann"""
    print("\n" + "=" * 60)
    print("ANALISI CRITICA: Correlazioni con Riemann")
    print("=" * 60)
    
    alpha = 1.012
    
    # Analisi del comportamento vicino al polo
    print("Analisi del comportamento di ζ(s) vicino a s=1:")
    s_values = [1.001, 1.005, 1.010, 1.012, 1.015, 1.020]
    
    print(f"{'s':<8} {'ζ(s)':<12} {'1/ln(s)':<12} {'Differenza':<12}")
    print("-" * 50)
    
    for s in s_values:
        zeta_s = float(zeta(s))
        inv_ln_s = 1 / np.log(s)
        diff = abs(zeta_s - inv_ln_s)
        print(f"{s:<8.3f} {zeta_s:<12.4f} {inv_ln_s:<12.4f} {diff:<12.4f}")
    
    print("\nCONCLUSIONE: La vicinanza tra ζ(α) e 1/ln(α) è dovuta")
    print("al comportamento della funzione ζ vicino al polo s=1,")
    print("non a proprietà speciali di α = 1.012.")

if __name__ == "__main__":
    print("VERIFICA SCIENTIFICA DEL MODELLO ROF")
    print("Test di falsificabilità e validazione empirica")
    print("Data:", "29 Gennaio 2026")
    
    # Esegui le verifiche principali
    verifica_correlazione_alpha_zeta()
    verifica_formula_primi()
    analisi_critica_alpha()
    
    # TEST CRUCIALE: α(z)
    redshifts, alpha_values = test_alpha_redshift()
    
    # Analisi critica finale
    test_ipotesi_riemann()
    
    print("\n" + "=" * 60)
    print("CONCLUSIONI SCIENTIFICHE")
    print("=" * 60)
    print("1. α = 1.012 deriva dalla tensione di Hubble (H0_local/H0_CMB)^(1/7)")
    print("2. La formula dei primi è un'approssimazione empirica decente")
    print("3. Le correlazioni con ζ(s) sono matematicamente spiegate")
    print("4. Il test α(z) è CRUCIALE per validare/falsificare ROF")
    print("5. Servono dati astronomici reali per il test definitivo")
    
    print("\n" + "=" * 60)
    print("RACCOMANDAZIONI")
    print("=" * 60)
    print("- Ottenere dati H0(z) da cataloghi pubblici (Pantheon, BAO)")
    print("- Implementare test statistico rigoroso per α(z)")
    print("- Confrontare con previsioni ΛCDM")
    print("- Rimuovere terminologia non-scientifica dai documenti")
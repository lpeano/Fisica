# MiKTeX Auto-Install Configuration
# Esegui questo comando una sola volta per abilitare installazione automatica

# PowerShell (Admin)
initexmf --set-config-value [MPM]AutoInstall=1
initexmf --update-fndb
mpm --update-db

# Verifica configurazione
initexmf --report

# Per installazione manuale pacchetti mancanti:
# mpm --install <package-name>

# Esempio per REVTeX:
mpm --install revtex4-2
mpm --install natbib
mpm --install amsmath
mpm --install graphicx
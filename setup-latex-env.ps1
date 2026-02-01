#!/usr/bin/env pwsh
# ROF LaTeX Environment Setup Script
# Configura ambiente completo per manoscritto Physical Review D

Write-Host "🚀 Configurazione Ambiente LaTeX per Modello ROF" -ForegroundColor Green

# Verifica e installa MiKTeX
if (!(Get-Command "pdflatex" -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Installazione MiKTeX..." -ForegroundColor Yellow
    winget install MiKTeX.MiKTeX
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host "✅ MiKTeX installato: $(pdflatex --version | Select-Object -First 1)" -ForegroundColor Green

# Configura MiKTeX per auto-install pacchetti
Write-Host "⚙️ Configurazione MiKTeX auto-install..." -ForegroundColor Yellow
& "initexmf" "--set-config-value" "[MPM]AutoInstall=1"
& "initexmf" "--update-fndb"

# Installa pacchetti REVTeX essenziali
Write-Host "📚 Pre-installazione pacchetti REVTeX..." -ForegroundColor Yellow
$packages = @(
    "revtex4-2", "revtex", "natbib", "graphicx", 
    "amsmath", "amssymb", "amsfonts", "bm",
    "hyperref", "url", "booktabs", "dcolumn",
    "braket", "multirow", "color", "xcolor"
)

foreach ($pkg in $packages) {
    Write-Host "  Installing $pkg..." -ForegroundColor Cyan
    & "mpm" "--install" $pkg
}

# Verifica VS Code e installa estensioni
if (Get-Command "code" -ErrorAction SilentlyContinue) {
    Write-Host "📝 Installazione estensioni VS Code..." -ForegroundColor Yellow
    & "code" "--install-extension" "James-Yu.latex-workshop"
    & "code" "--install-extension" "valentjn.vscode-ltex"  # Spell check
    & "code" "--install-extension" "tecosaur.latex-utilities"
} else {
    Write-Host "⚠️ VS Code non trovato. Installa da: https://code.visualstudio.com/" -ForegroundColor Red
}

# Test compilazione
Write-Host "🧪 Test compilazione LaTeX..." -ForegroundColor Yellow
$testFile = @"
\documentclass[twocolumn,showpacs,preprintnumbers,amsmath,amssymb,prd]{revtex4-2}
\usepackage{graphicx}
\usepackage{dcolumn}
\usepackage{bm}

\begin{document}
\title{Test ROF LaTeX Environment}
\author{Test Author}
\affiliation{Test Institution}

\begin{abstract}
Environment test successful.
\end{abstract}

\maketitle

\section{Test}
Environment configured correctly for ROF manuscript compilation.
The metric resolution parameter is $\alpha(z) = \alpha_0 e^{-\beta z}$.

\end{document}
"@

$testFile | Out-File -FilePath "rof_test.tex" -Encoding UTF8
& "pdflatex" "rof_test.tex"

if (Test-Path "rof_test.pdf") {
    Write-Host "🎉 SUCCESS! Ambiente LaTeX configurato correttamente." -ForegroundColor Green
    Remove-Item "rof_test.*"
} else {
    Write-Host "❌ ERRORE nella compilazione di test." -ForegroundColor Red
    Write-Host "Check log file: rof_test.log" -ForegroundColor Yellow
}

Write-Host @"

🏆 SETUP COMPLETATO!

Prossimi passi:
1. Apri VS Code: code ROF_Physical_Review_D_LaTeX.tex
2. Salva file (Ctrl+S) → Compilazione automatica
3. View PDF: Ctrl+Alt+V

Shortcuts utili:
- Ctrl+Alt+B: Build
- Ctrl+Alt+C: Clean
- Ctrl+Alt+J: View log
- Ctrl+Alt+V: View PDF

Repository: https://github.com/lpeano/Fisica
"@ -ForegroundColor Cyan
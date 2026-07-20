# Complete Windows setup for Retrieval-based-Voice-Conversion (official library + WebUI)
# Must match the video Slide 4 success lines:
#   [pin] library @7b284a634667
#   [pin] WebUI @c1e005f0e226 (hard fail if clone/pip/models fail)
#   [ok]  library · WebUI deps · download_models
#
# Usage (from rvc-voice-cloning\, venv active):
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\setup_rvc.ps1
#
# https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
# WebUI lives next to the companion:
#   <parent>\Retrieval-based-Voice-Conversion-WebUI

$ErrorActionPreference = "Stop"

function Die {
    param([string]$Message)
    Write-Host "FAIL: $Message" -ForegroundColor Red
    exit 1
}

function Test-Cmd {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Ensure-WingetPackage {
    param(
        [string]$Id,
        [string]$CheckCmd,
        [string]$Label
    )
    if (Test-Cmd $CheckCmd) { return }
    if (-not (Test-Cmd "winget")) {
        Die "$Label is missing and winget is not available. Install $Label, then re-run."
    }
    Write-Host "[0/6] Installing $Label via winget ($Id)…"
    winget install --id $Id -e --accept-package-agreements --accept-source-agreements
    if (-not (Test-Cmd $CheckCmd)) {
        Die "$Label still not on PATH after winget install. Close PowerShell, reopen, activate .venv, re-run .\setup_rvc.ps1"
    }
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Parent = Split-Path -Parent $Root
$WebUI = Join-Path $Parent "Retrieval-based-Voice-Conversion-WebUI"

# Tested pins (do not float on develop / HEAD)
$RvcLibPin = "7b284a634667c34103eaaeed972b48ccdb4b893e"
$RvcLibShort = "7b284a634667"
$WebUIPin = "c1e005f0e226a3c2a10adfc8a9be03a6944506d0"
$WebUIShort = "c1e005f0e226"

Write-Host "════════════════════════════════════════════════════"
Write-Host " COMPLETE RVC SETUP (library + WebUI train deps)"
Write-Host " Library pin: $RvcLibPin"
Write-Host " WebUI pin:   $WebUIPin"
Write-Host " WebUI path:  $WebUI"
Write-Host "════════════════════════════════════════════════════"
Write-Host ""

# --- Clean Windows gates ---
if (-not $env:VIRTUAL_ENV) {
    Die @"
Activate the companion venv first:
  cd `"$Root`"
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  Set-ExecutionPolicy -Scope Process Bypass
  .\setup_rvc.ps1
"@
}

if ($PSVersionTable.PSVersion.Major -lt 5) {
    Die "Need Windows PowerShell 5.1+ or PowerShell 7+. You have $($PSVersionTable.PSVersion)"
}

Ensure-WingetPackage -Id "Git.Git" -CheckCmd "git" -Label "Git"
Ensure-WingetPackage -Id "Gyan.FFmpeg" -CheckCmd "ffmpeg" -Label "FFmpeg"

$ff = & ffmpeg -version 2>$null | Select-Object -First 1
if ($ff) { Write-Host $ff }

$pyOk = & python -c @"
import sys
v = sys.version_info
ok = (v.major, v.minor) >= (3, 10) and (v.major, v.minor) < (3, 12)
print('1' if ok else '0')
"@
if ($LASTEXITCODE -ne 0) { Die "python check failed" }
if ($pyOk.Trim() -ne "1") {
    $ver = (& python --version 2>&1 | Out-String).Trim()
    Die @"
Need Python 3.10–3.11 for the pinned RVC library (you have $ver).
  Install Python 3.11 from https://www.python.org/downloads/windows/
  (check 'Add python.exe to PATH'), then:
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    .\setup_rvc.ps1
"@
}
$pyVer = (& python --version 2>&1 | Out-String).Trim()
Write-Host "[ok] $pyVer · venv=$env:VIRTUAL_ENV"

Write-Host ""
Write-Host "[1/6] pip install companion requirements…"
python -m pip install -U pip wheel
if ($LASTEXITCODE -ne 0) { Die "pip upgrade failed" }
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Die "companion requirements.txt failed" }

Write-Host ""
Write-Host "[2/6] Install official RVC library (pinned — not develop)…"
# Prefetch a modern av binary wheel (FFmpeg 8), install RVC with --no-deps, then runtime deps.
python -m pip install -U poetry-core
if ($LASTEXITCODE -ne 0) { Die "poetry-core install failed (needed to build pinned RVC)" }
python -m pip install "av==18.0.0"
if ($LASTEXITCODE -ne 0) { Die "av binary wheel install failed (needed with FFmpeg 8)" }
python -m pip install --no-deps `
    "git+https://github.com/RVC-Project/Retrieval-based-Voice-Conversion.git@$RvcLibPin"
if ($LASTEXITCODE -ne 0) { Die "pinned RVC library install failed (@$RvcLibPin)" }

python -m pip install `
    "torch>=2.1.0" `
    "soundfile>=0.12.1,<0.13" `
    "librosa>=0.10.1,<0.11" `
    "praat-parselmouth>=0.4.3" `
    "pyworld>=0.3.4" `
    "torchcrepe>=0.0.22,<0.0.23" `
    "faiss-cpu>=1.7.4" `
    "python-dotenv>=1.0.0" `
    "pydub>=0.25.1" `
    "click>=8.1.7" `
    "tensorboardx>=2.6.2.2" `
    "poethepoet>=0.24.4,<0.25" `
    "python-multipart>=0.0.6,<0.0.7" `
    "numba==0.58.1" `
    "git+https://github.com/Tps-F/fairseq.git@main"
if ($LASTEXITCODE -ne 0) { Die "RVC runtime dependencies failed" }

python -c @"
import importlib.util
import sys
if importlib.util.find_spec('rvc') is None:
    sys.exit('import rvc failed')
print('  import rvc: OK')
"@
if ($LASTEXITCODE -ne 0) { Die "RVC library import failed after pip install" }
Write-Host "[pin] library @$RvcLibShort"

Write-Host ""
Write-Host "[3/6] Initialize companion RVC assets (rvc init / dlmodel)…"
if (-not (Test-Cmd "rvc")) {
    Die "rvc CLI not on PATH after library install — confirm .venv is active and re-run"
}
if (-not (Test-Path (Join-Path $Root "assets"))) {
    & rvc init
    if ($LASTEXITCODE -ne 0) {
        & rvc env create
        if ($LASTEXITCODE -ne 0) { Die "rvc init / env create failed" }
    }
}
& rvc dlmodel
if ($LASTEXITCODE -ne 0) { Die "rvc dlmodel failed — network or assets download error" }

Write-Host ""
Write-Host "[4/6] Clone / pin WebUI…"
if (-not (Test-Path (Join-Path $WebUI ".git"))) {
    git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git $WebUI
    if ($LASTEXITCODE -ne 0) { Die "git clone WebUI failed" }
}

Push-Location $WebUI
try {
    git fetch --depth 1 origin $WebUIPin
    if ($LASTEXITCODE -ne 0) {
        git fetch origin $WebUIPin
        if ($LASTEXITCODE -ne 0) { Die "git fetch WebUI pin $WebUIPin failed" }
    }
    git checkout --detach $WebUIPin
    if ($LASTEXITCODE -ne 0) { Die "WebUI checkout $WebUIPin failed" }
    $Head = (git rev-parse HEAD).Trim()
    if ($Head -ne $WebUIPin) {
        Die "WebUI HEAD is $Head — expected $WebUIPin"
    }
    $Short = (git rev-parse --short HEAD).Trim()
    Write-Host "  WebUI at $Short"
}
finally {
    Pop-Location
}
Write-Host "[pin] WebUI @$WebUIShort (hard fail if clone/pip/models fail)"

Write-Host ""
Write-Host "[5/6] Install WebUI dependencies + download train assets…"
if (-not (Test-Path $WebUI)) { Die "WebUI folder missing: $WebUI" }
Push-Location $WebUI
try {
    if (-not (Test-Path "requirements.txt")) { Die "WebUI requirements.txt missing" }
    Write-Host "  pip install -r requirements.txt (WebUI)"
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { Die "WebUI pip install failed — see docs/TROUBLESHOOT.md" }
    if (-not (Test-Path "tools\download_models.py")) {
        Die "tools\download_models.py missing on pinned WebUI — wrong revision?"
    }
    Write-Host "  python tools\download_models.py"
    python tools\download_models.py
    if ($LASTEXITCODE -ne 0) { Die "tools\download_models.py failed — retry inside WebUI folder" }
}
finally {
    Pop-Location
}
Write-Host "[ok]  library · WebUI deps · download_models"

Write-Host ""
Write-Host "[6/6] Wire companion config.yaml (Windows paths)…"
python configure_rvc.py --prefer-library --webui $WebUI
if ($LASTEXITCODE -ne 0) { Die "configure_rvc.py failed" }

Write-Host ""
Write-Host "DONE (hard checks passed)."
Write-Host "  WebUI: $WebUI"
Write-Host ""
Write-Host "Next:"
Write-Host "  python configure_rvc.py --check"
Write-Host "  python open_recorder.py          # 10+ min YOUR voice → data\raw\"
Write-Host "  python prepare.py --input data\raw --speaker myvoice"
Write-Host "  python next_step.py"
Write-Host ""
Write-Host "Train:"
Write-Host "  cd `"$WebUI`""
Write-Host "  python infer-web.py"
Write-Host "  # open http://localhost:7865 → Train tab"
Write-Host "  # fields: docs\TRAIN_WEBUI.md"
Write-Host "  # Copy-Item assets\weights\*.pth + logs\*\*.index → models\rvc\"
Write-Host "  # THEN regenerate YOUR clone (do not reuse old WAV):"
Write-Host "  cd `"$Root`""
Write-Host "  python infer.py --text-file scripts\clone_prove.txt --out output\clone_prove.wav"
Write-Host "  python play_clone.py --wav output\clone_prove.wav"
Write-Host ""
Write-Host "Docs: BEGINNER.md · docs\TRAIN_WEBUI.md · docs\TROUBLESHOOT.md"

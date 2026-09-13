<#
  Netune installer  -  https://dataash.de/netune-free-beta.html

  Run from PowerShell:
      irm https://dataash.de/install.ps1 | iex

  (from a Command Prompt, type  powershell  first, then the line above)

  What it does, in order, and nothing else:
    1. Reads https://dataash.de/netune-latest.json to learn the current
       version, where Netune's installer is, and its SHA-256. (The website
       hands out a plain zip instead; this takes the installer, so that what
       lands is a proper install with an entry under Settings > Apps.)
    2. Downloads Netune's Setup.exe (about 25 MB) from the GitHub release.
    3. Checks the SHA-256. A file that does not match is deleted, and this
       stops - it never runs something it cannot vouch for.
    4. Runs that installer without asking any questions: Netune goes into
       %LOCALAPPDATA%\Programs\Netune (your own user folder; no
       administrator rights, nothing under Program Files), with a Desktop
       and Start-menu shortcut and an entry under Settings > Apps.
    5. Starts Netune, which opens in your browser.

  Your saved projects live in %LOCALAPPDATA%\Netune and are never touched,
  so running this again simply updates the program.

  To remove Netune later: Settings > Apps > Netune > Uninstall.

  It sends nothing anywhere. The only two addresses it talks to are
  dataash.de and github.com, both to download.

  Knobs, as environment variables set before running:
    NETUNE_INSTALL_DIR   somewhere other than %LOCALAPPDATA%\Programs\Netune
    NETUNE_NO_SHORTCUT   =1  make no shortcuts
    NETUNE_NO_START      =1  install, but do not start it afterwards
#>

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Manifest = "https://dataash.de/netune-latest.json"
$Work = Join-Path ([IO.Path]::GetTempPath()) ("netune-install-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))

function Say([string]$text)  { Write-Host ("  " + $text) }
function Step([string]$text) { Write-Host ""; Write-Host $text -ForegroundColor Cyan }
function Fail([string]$text) {
    Write-Host ""; Write-Host ("  " + $text) -ForegroundColor Red
    Write-Host "  Nothing was installed. Netune can also be downloaded by hand from https://dataash.de/netune-free-beta.html"
    if (Test-Path $Work) { Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue }
    exit 1
}

Write-Host ""
Write-Host "Netune installer" -ForegroundColor White

# ---------------------------------------------------------------- 0. this machine
if (-not [Environment]::Is64BitOperatingSystem) { Fail "Netune needs 64-bit Windows." }
if ($PSVersionTable.PSVersion.Major -lt 5) { Fail "Netune's installer needs PowerShell 5 or newer (Windows 10 and 11 have it)." }

# ---------------------------------------------------------------- 1. what is current
Step "Asking dataash.de which version is current"
try {
    $latest = Invoke-RestMethod -Uri $Manifest -UseBasicParsing -TimeoutSec 30
} catch {
    Fail "Could not read $Manifest ($($_.Exception.Message))."
}
if (-not $latest.version) { Fail "The version file at dataash.de names no version; please try again later." }
# The page hands out the zip; this script runs Netune's installer, which the
# version file names separately. Older files named it as the main download.
$url  = if ($latest.setup_url)    { $latest.setup_url }    else { $latest.url }
$sha  = if ($latest.setup_sha256) { $latest.setup_sha256 } else { $latest.sha256 }
$file = if ($latest.setup_file)   { $latest.setup_file }   else { $latest.file }
$size = if ($latest.setup_bytes)  { $latest.setup_bytes }  else { $latest.bytes }
if ($file -notmatch '\.exe$') { Fail "The version file names no installer to run; please download Netune by hand from https://dataash.de/netune-free-beta.html" }
if ($sha -notmatch '^[0-9a-fA-F]{64}$') { Fail "The version file carries no usable checksum; refusing to continue." }
if ($url -notmatch '^https://(github\.com/ashonque/dataash/|dataash\.de/)') { Fail "The version file points somewhere unexpected ($url); refusing to download from there." }
Say ("Netune " + $latest.version + "  -  " + $file)

# ---------------------------------------------------------------- 2. download
Step ("Downloading (about " + $(if ($size) { [math]::Round($size / 1MB) } else { 25 }) + " MB)")
New-Item -ItemType Directory -Path $Work -Force | Out-Null
$setup = Join-Path $Work $file
try {
    $old = $ProgressPreference; $ProgressPreference = "SilentlyContinue"   # the progress bar makes 5.1 downloads ten times slower
    Invoke-WebRequest -Uri $url -OutFile $setup -UseBasicParsing -TimeoutSec 600
    $ProgressPreference = $old
} catch {
    Fail "The download failed ($($_.Exception.Message))."
}
Say ("received " + [math]::Round((Get-Item $setup).Length / 1MB, 1) + " MB")

# ---------------------------------------------------------------- 3. check it
Step "Checking the file against its published SHA-256"
$got = (Get-FileHash -Algorithm SHA256 -Path $setup).Hash.ToLower()
if ($got -ne $sha.ToLower()) {
    Remove-Item $setup -Force -ErrorAction SilentlyContinue
    Fail ("The download does not match its checksum (got " + $got.Substring(0, 12) + "..., expected " + $sha.Substring(0, 12) + "...). It was deleted. Please try again; if it happens twice, write to dataash@proton.me.")
}
Say "matches"
Unblock-File -Path $setup -ErrorAction SilentlyContinue     # verified; the mark-of-the-web has done its job

# ---------------------------------------------------------------- 4. install
# Netune's own installer, run with its questions answered, rather than a
# second installer written here: the uninstaller, the shortcuts and the
# Settings > Apps entry are then the real ones, made by the tool that knows
# how to take them away again.
Step "Installing"
$opts = @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/NOCANCEL")
if ($env:NETUNE_INSTALL_DIR) { $opts += "/DIR=`"$($env:NETUNE_INSTALL_DIR)`"" }
if ($env:NETUNE_NO_SHORTCUT -eq "1") { $opts += @("/NOICONS", "/MERGETASKS=!desktopicon") }
$run = Start-Process -FilePath $setup -ArgumentList $opts -Wait -PassThru
if ($run.ExitCode -ne 0) { Fail "The installer stopped with code $($run.ExitCode)." }
Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue

$dest = if ($env:NETUNE_INSTALL_DIR) { $env:NETUNE_INSTALL_DIR } else { Join-Path $env:LOCALAPPDATA "Programs\Netune" }
$launcher = Join-Path $dest "Netune.exe"
if (-not (Test-Path $launcher)) { Fail "The installer finished but $launcher is not there." }
Say ("installed in " + $dest)

# ---------------------------------------------------------------- 5. go
Write-Host ""
Write-Host "Netune $($latest.version) is installed." -ForegroundColor Green
if ($env:NETUNE_NO_SHORTCUT -eq "1") {
    Say "Start it any time from:  $launcher"
} else {
    Say "Start it any time from the Desktop or Start-menu shortcut."
}
Say "To remove it later: Settings > Apps > Netune."
if ($env:NETUNE_NO_START -ne "1") {
    # the wizard's own start-afterwards tick is skipped in silent mode, by design
    Step "Starting Netune - it opens in your browser; leave its window open while you use it"
    Start-Process -FilePath $launcher -WorkingDirectory $dest
}
Write-Host ""

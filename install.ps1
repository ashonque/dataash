<#
  Netune installer  -  https://dataash.de/netune-free-beta.html

  Run from PowerShell:
      irm https://dataash.de/install.ps1 | iex

  (from a Command Prompt, type  powershell  first, then the line above)

  What it does, in order, and nothing else:
    1. Reads https://dataash.de/netune-latest.json to learn the current
       version, where its zip is, and the zip's SHA-256.
    2. Downloads the portable zip (about 37 MB) from the GitHub release -
       the same program the Setup.exe installs, without the wizard.
    3. Checks the SHA-256. A file that does not match is deleted, and the
       installer stops - it never unpacks something it cannot vouch for.
    4. Unpacks into  %LOCALAPPDATA%\Programs\Netune  (your own user folder;
       no administrator rights, nothing under Program Files, nothing in the
       system). An earlier Netune there is replaced; your saved projects
       live in %LOCALAPPDATA%\Netune and are not touched.
    5. Puts a Netune shortcut on the Desktop and in the Start menu, lists
       Netune under Settings > Apps so it can be uninstalled from there, and
       writes an "Uninstall Netune.ps1" beside the program.
    6. Starts Netune, which opens in your browser.

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
$Dest = if ($env:NETUNE_INSTALL_DIR) { $env:NETUNE_INSTALL_DIR } else { Join-Path $env:LOCALAPPDATA "Programs\Netune" }
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
Write-Host "  installs into $Dest"

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
foreach ($k in "version", "url", "sha256", "file") {
    if (-not $latest.$k) { Fail "The version file at dataash.de is missing '$k'; please try again later." }
}
# the version file names the Setup.exe first; this script wants the zip beside it
$zipUrl = if ($latest.zip_url) { $latest.zip_url } else { $latest.url }
$zipSha = if ($latest.zip_sha256) { $latest.zip_sha256 } else { $latest.sha256 }
$zipFile = if ($latest.zip_file) { $latest.zip_file } else { $latest.file }
$zipBytes = if ($latest.zip_bytes) { $latest.zip_bytes } else { $latest.bytes }
if ($zipFile -notmatch '\.zip$') { Fail "The version file names no zip to install from; use the Setup.exe on https://dataash.de/netune-free-beta.html instead." }
if ($zipSha -notmatch '^[0-9a-fA-F]{64}$') { Fail "The version file carries no usable checksum; refusing to continue." }
if ($zipUrl -notmatch '^https://(github\.com/ashonque/dataash/|dataash\.de/)') { Fail "The version file points somewhere unexpected ($zipUrl); refusing to download from there." }
Say ("Netune " + $latest.version + "  -  " + $zipFile)

$installed = Join-Path $Dest "app\edition.txt"
$verFile = Join-Path $Dest "installed-version.txt"
if (Test-Path $verFile) {
    $have = (Get-Content $verFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($have -eq $latest.version) { Say ("This version is already installed in " + $Dest + "; it will be refreshed.") }
    else { Say ("Replacing Netune " + $have + " with " + $latest.version + ". Your projects are kept.") }
}

# ---------------------------------------------------------------- 2. download
Step "Downloading (about $([math]::Round($zipBytes / 1MB)) MB)"
New-Item -ItemType Directory -Path $Work -Force | Out-Null
$zip = Join-Path $Work $zipFile
try {
    $old = $ProgressPreference; $ProgressPreference = "SilentlyContinue"   # the progress bar makes 5.1 downloads ten times slower
    Invoke-WebRequest -Uri $zipUrl -OutFile $zip -UseBasicParsing -TimeoutSec 600
    $ProgressPreference = $old
} catch {
    Fail "The download failed ($($_.Exception.Message))."
}
Say ("received " + [math]::Round((Get-Item $zip).Length / 1MB, 1) + " MB")

# ---------------------------------------------------------------- 3. check it
Step "Checking the file against its published SHA-256"
$got = (Get-FileHash -Algorithm SHA256 -Path $zip).Hash.ToLower()
if ($got -ne $zipSha.ToLower()) {
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    Fail ("The download does not match its checksum (got " + $got.Substring(0, 12) + "..., expected " + $zipSha.Substring(0, 12) + "...). It was deleted. Please try again; if it happens twice, write to dataash@proton.me.")
}
Say "matches"
Unblock-File -Path $zip -ErrorAction SilentlyContinue      # the file is verified; the mark-of-the-web is no longer needed

# ---------------------------------------------------------------- 4. unpack
Step "Unpacking"
$stage = Join-Path $Work "unpacked"
Expand-Archive -Path $zip -DestinationPath $stage -Force
$inner = Get-ChildItem $stage -Directory | Select-Object -First 1
if (-not $inner -or -not (Test-Path (Join-Path $inner.FullName "Netune.exe"))) { Fail "The zip did not hold a Netune folder." }

# a Netune already running from the destination would hold its files open
$running = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
           Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($Dest, [StringComparison]::OrdinalIgnoreCase) }
if ($running) {
    Say "Netune is running from that folder; stopping it first."
    $running | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}

if (Test-Path $Dest) {
    # replace the program, never the user's data (which is not in here)
    Get-ChildItem $Dest -Force | Where-Object { $_.Name -ne "installed-version.txt" } |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
} else {
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
}
Get-ChildItem $inner.FullName -Force | Move-Item -Destination $Dest -Force
Set-Content -Path $verFile -Value $latest.version -Encoding ASCII
Remove-Item -Recurse -Force $Work -ErrorAction SilentlyContinue
Say ("installed in " + $Dest)

# ---------------------------------------------------------------- 5. shortcuts, and a way out
$launcher = Join-Path $Dest "Netune.exe"
$icon = Join-Path $Dest "app\netune.ico"
$uninstall = Join-Path $Dest "Uninstall Netune.ps1"

function Shortcut([string]$path) {
    $s = (New-Object -ComObject WScript.Shell).CreateShortcut($path)
    $s.TargetPath = $launcher
    $s.WorkingDirectory = $Dest
    $s.IconLocation = "$icon,0"
    $s.Description = "Start Netune"
    $s.Save()
}

if ($env:NETUNE_NO_SHORTCUT -ne "1") {
    Step "Shortcuts"
    $desktopLnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "Netune.lnk"
    $startDir = Join-Path ([Environment]::GetFolderPath("StartMenu")) "Programs"
    $startLnk = Join-Path $startDir "Netune.lnk"
    Shortcut $desktopLnk; Say "on the Desktop"
    if (Test-Path $startDir) { Shortcut $startLnk; Say "in the Start menu" }
    # Explorer remembers an icon by its path; a replaced icon would otherwise keep its old face
    Start-Process -FilePath "ie4uinit.exe" -ArgumentList "-show" -WindowStyle Hidden -ErrorAction SilentlyContinue
}

@"
# Removes Netune from this computer. Your saved projects and settings, in
# %LOCALAPPDATA%\Netune, are deliberately left where they are.
`$dest = "$Dest"
`$answer = Read-Host "Remove Netune from `$dest? (y/n)"
if (`$answer -notmatch '^[Yy]') { exit }
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { `$_.ExecutablePath -and `$_.ExecutablePath.StartsWith(`$dest, [StringComparison]::OrdinalIgnoreCase) } |
    ForEach-Object { Stop-Process -Id `$_.ProcessId -Force -ErrorAction SilentlyContinue }
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path ([Environment]::GetFolderPath("Desktop")) "Netune.lnk")
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path ([Environment]::GetFolderPath("StartMenu")) "Programs\Netune.lnk")
Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Netune" -Recurse -Force -ErrorAction SilentlyContinue
Set-Location `$env:TEMP
Remove-Item -Recurse -Force `$dest
Write-Host "Netune was removed. Your projects in `$env:LOCALAPPDATA\Netune were kept."
"@ | Set-Content -Path $uninstall -Encoding UTF8

# Settings > Apps, for this user only: no administrator rights, nothing machine-wide
try {
    $key = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Netune"
    New-Item -Path $key -Force | Out-Null
    Set-ItemProperty $key "DisplayName" "Netune (free edition)"
    Set-ItemProperty $key "DisplayVersion" ([string]$latest.version)
    Set-ItemProperty $key "Publisher" "DataAsh"
    Set-ItemProperty $key "URLInfoAbout" "https://dataash.de/"
    Set-ItemProperty $key "DisplayIcon" $launcher
    Set-ItemProperty $key "InstallLocation" $Dest
    Set-ItemProperty $key "UninstallString" ("powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"" + $uninstall + "`"")
    Set-ItemProperty $key "NoModify" 1 -Type DWord
    Set-ItemProperty $key "NoRepair" 1 -Type DWord
    Set-ItemProperty $key "EstimatedSize" ([int]((Get-ChildItem $Dest -Recurse -File | Measure-Object Length -Sum).Sum / 1KB)) -Type DWord
} catch { Say "Could not list Netune under Settings > Apps ($($_.Exception.Message)); the uninstaller is still beside the program." }

# ---------------------------------------------------------------- 6. go
Write-Host ""
Write-Host "Netune $($latest.version) is installed." -ForegroundColor Green
Say "Start it any time from the Desktop or Start-menu shortcut, or:  $launcher"
Say "To remove it later: Settings > Apps > Netune, or run `"$uninstall`"."
if ($env:NETUNE_NO_START -ne "1") {
    Step "Starting Netune - it opens in your browser; leave its window open while you use it"
    Start-Process -FilePath $launcher -WorkingDirectory $Dest
}
Write-Host ""

$ErrorActionPreference = 'SilentlyContinue';

$stop_application = if (Get-Process -Name Nyrna -ErrorAction SilentlyContinue) {$false} else {$true}

if ($stop_application -and (Get-Process -Name Nyrna -ErrorAction SilentlyContinue)) {
    Stop-Process -processname Nyrna
}
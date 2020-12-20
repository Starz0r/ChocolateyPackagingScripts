$InstallDir = Join-Path $env:ChocolateyToolsLocation "flutter";

Remove-Item -Path $InstallDir -Force -Recurse;
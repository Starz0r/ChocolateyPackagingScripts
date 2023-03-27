$InstallDir = Join-Path Get-ToolsLocation "flutter";

Remove-Item -Path $InstallDir -Force -Recurse;
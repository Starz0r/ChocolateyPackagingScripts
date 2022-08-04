$PackageName = 'flyingcarpet.install';
$ToolsPath = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$OldInstallDir = Join-Path $(Get-ToolsLocation) "flyingcarpet";
$Desktop = [System.Environment]::GetFolderPath("Desktop");

if (Test-Path -Path $OldInstallDir -PathType Container) {
	Write-Warning "This package no longer installs Flying Carpet at $OldInstallDir. Please delete that directory at your nearest convenience.";
	Remove-Item -Force "$Desktop\Flying Carpet.lnk" -EA 0;
};

Install-ChocolateyShortcut -ShortcutFilePath "$Desktop\Flying Carpet.lnk" -TargetPath "$ToolsPath\x64\flyingcarpetw.exe" -WorkingDirectory "$InstallDir" -WindowStyle 1;
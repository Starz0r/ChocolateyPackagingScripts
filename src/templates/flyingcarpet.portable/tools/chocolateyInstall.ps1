$PackageName = 'flyingcarpet.portable';
$ToolsPath = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$OldInstallDir = Join-Path $(Get-ToolsLocation) "flyingcarpet.portable";

if (Test-Path -Path $OldInstallDir -PathType Container) {
	Write-Warning "This package no longer installs Flying Carpet (Portable) at $OldInstallDir. Please delete that directory at your nearest convenience.";
	Uninstall-BinFile flyingcarpet -path "$OldInstallDir\flyingcarpet.exe";
};
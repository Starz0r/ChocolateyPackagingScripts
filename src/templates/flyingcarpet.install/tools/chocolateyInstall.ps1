$ErrorActionPreference = 'Stop';
$PackageName = 'flyingcarpet.install';
$ToolsPath = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$OldInstallDirX64 = Join-Path $ToolsPath "x64";
$OldInstallDirX86 = Join-Path $ToolsPath "x86";
$OlderInstallDir = Join-Path $(Get-ToolsLocation) "flyingcarpet";
$Desktop = [System.Environment]::GetFolderPath("Desktop");

if (Test-Path -Path $OldInstallDirX64 -PathType Container) {
	Write-Warning "This package no longer installs Flying Carpet at $OldInstallDirX64. Please delete that directory at your nearest convenience.";
};

if (Test-Path -Path $OldInstallDirX86 -PathType Container) {
	Write-Warning "This package no longer installs Flying Carpet at $OldInstallDirX86. Please delete that directory at your nearest convenience.";
};

if (Test-Path -Path $OlderInstallDir -PathType Container) {
	Write-Warning "This package no longer installs Flying Carpet at $OlderInstallDir either. Please delete that directory at your nearest convenience.";
	Remove-Item -Force "$Desktop\Flying Carpet.lnk" -EA 0;
};

Remove-Item "$Desktop\Flying Carpet.lnk" -ErrorAction SilentlyContinue -Force | Out-Null
 
$PackageArgs = @{
    PackageName    = $PackageName
    FileType       = "msi"
    SoftwareName   = "flyingcarpet"
    File64         = $(Get-Item $(Join-Path $ToolsPath "$fname"))
    SilentArgs     = "/qn /norestart /quiet"
    ValidExitCodes = @(0, 1605, 1614, 1641, 3010)
};
Install-ChocolateyInstallPackage @packageArgs;

Remove-Item -Force $(Get-Item $(Join-Path $ToolsPath "$fname")) -EA 0 | Out-Null;
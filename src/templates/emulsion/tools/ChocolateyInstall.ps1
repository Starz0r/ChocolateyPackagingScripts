$ErrorActionPreference = 'Stop';
$PackageName           = $env:ChocolateyPackageName;
$ToolsDir              = Split-Path -parent $MyInvocation.MyCommand.Definition;
$PkgParams             = Get-PackageParameters;
$Desktop               = [System.Environment]::GetFolderPath("Desktop");
$PrgmFiles             = [System.Environment]::GetFolderPath("ProgramFiles");

$PackageArgs = @{
  PackageName     = $PackageName
  
  FileType        = 'exe'
  File64          = Get-Item $(Join-Path $ToolsDir "$fname")

  SoftwareName    = 'emulsion*'
  
  SilentArgs      = "/S"
  ValidExitCodes  = @(0,3010)
};

Install-ChocolateyInstallPackage @PackageArgs;

if ($PkgParams.DesktopShortcut)
{
	Install-ChocolateyShortcut -ShortcutFilePath "$Desktop\Emulsion.lnk" -TargetPath "$PrgmFiles\Emulsion\Emulsion.exe" -WorkingDirectory "$PrgmFiles\Emulsion" -WindowStyle 1
}

if ($PkgParams.AddToPath)
{
	Install-ChocolateyPath -PathToInstall "$PrgmFiles\Emulsion" -PathType 'Machine'
}

Remove-Item $(Get-Item $(Join-Path $ToolsDir "$fname"));
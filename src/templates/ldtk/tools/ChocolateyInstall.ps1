$ErrorActionPreference = 'Stop';
$PackageName           = $env:ChocolateyPackageName;
$ToolsDir              = Split-Path -parent $MyInvocation.MyCommand.Definition;

$PackageArgs = @{
  PackageName     = $PackageName
  
  FileType        = 'exe'
  File64          = Get-Item $(Join-Path $ToolsDir "$fname")

  SoftwareName    = 'ldtk*'
  
  SilentArgs      = "/S"
  ValidExitCodes  = @(0,3010)
};

Install-ChocolateyInstallPackage @PackageArgs;
Remove-Item $(Get-Item $(Join-Path $ToolsDir "$fname"));
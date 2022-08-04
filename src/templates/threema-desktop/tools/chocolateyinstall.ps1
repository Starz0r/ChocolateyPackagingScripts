$ErrorActionPreference = 'Stop';
$ToolsDir               = Split-Path $MyInvocation.MyCommand.Definition;

$PackageArgs = @{
  file64         = Join-Path $ToolsDir '$fname'
  packageName    = $env:ChocolateyPackageName
  installerType  = 'exe'
  silentArgs     = '--silent'
  validExitCodes = @(0)
  softwareName   = 'Threema' 
};

Install-ChocolateyInstallPackage @PackageArgs;

Remove-Item -ea 0 -Force -Path $ToolsDir\*.exe;
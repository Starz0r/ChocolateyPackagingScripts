$PackageName = "neovide.install";
$ErrorActionPreference = 'Stop';
$ToolsDir = Split-Path $MyInvocation.MyCommand.Definition;
 
$PackageArgs = @{
    PackageName    = $PackageName
    FileType       = "msi"
    SoftwareName   = "Neovide"
    File64         = Get-Item $(Join-Path $ToolsDir "$fname")
    SilentArgs     = "/qn /norestart /quiet"
    ValidExitCodes = @(0, 3010, 1641)
};
Install-ChocolateyInstallPackage @packageArgs;

Remove-Item -Force "$fname" -EA 0;
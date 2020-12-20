$ErrorActionPreference = 'Stop';
$ToolsDir = Split-Path $MyInvocation.MyCommand.Definition;

$PackageArgs = @{
    PackageName    = 'imageglass'
    FileType       = "msi"
    SoftwareName   = "imageglass"
    File64         = Get-Item $(Join-Path $ToolsDir "$fname")
    SilentArgs     = "/qn /norestart /quiet"
    ValidExitCodes = @(0, 3010, 1641)
};

Install-ChocolateyPackage @PackageArgs;

$PackageName = $PackageArgs.PackageName;
$InstallLocation = Get-AppInstallLocation $PackageName;
if (!$InstallLocation)  { Write-Warning "Can't find $PackageName install location"; return; };
Write-Host "$PackageName installed to '$InstallLocation'";

Remove-Item $(Get-Item $(Join-Path $ToolsDir "$fname")) -ErrorAction SilentlyContinue -Force | Out-Null;
$ErrorActionPreference = 'Stop';

$PackageName  = $env:ChocolateyPackageName;
$InstallDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)";

$PackageArgs = @{
  PackageName    = $PackageName
  FileType       = 'exe'
  File           = Get-Item $(Join-Path $InstallDir "$fname")
  File64         = Get-Item $(Join-Path $InstallDir "$fname64")

  SoftwareName   = 'sagelinks*'
  
  SilentArgs     = '/S /SILENT /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  ValidExitCodes = @(0, 1223)
};

Install-ChocolateyPackage @PackageArgs;

Remove-Item $(Get-Item $(Join-Path $InstallDir "$fname")) -EA 0 | Out-Null;
Remove-Item $(Get-Item $(Join-Path $InstallDir "$fname64")) -EA 0 | Out-Null;

$InstallLocation = Get-AppInstallLocation "$PackageName*";
if ($InstallLocation)  {
    Write-Host "$PackageName installed to '$InstallLocation'.";
    Register-Application "$InstallLocation\$PackageName.exe";
    Write-Host "$PackageName registered as $PackageName.";
} else {
	Write-Warning "Can't find $PackageName install location.";
};
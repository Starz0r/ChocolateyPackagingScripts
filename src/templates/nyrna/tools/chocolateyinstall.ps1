$ErrorActionPreference = 'Stop';

$PackageName  = $env:ChocolateyPackageName
$App = $PackageName.Split(".")[0]
$InstallDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$ToolsDir = Split-Path -parent $MyInvocation.MyCommand.Definition

$PackageArgs = @{
  PackageName   = $PackageName
  FileType      = 'exe'
  File64        = Get-Item $(Join-Path $ToolsDir "$fname")

  SoftwareName  = 'nyrna*'

  Checksum      = "$checksum"
  ChecksumType  = 'sha512'
  
  SilentArgs   = '/SILENT /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  ValidExitCodes= @(0, 1223)
}

Install-ChocolateyPackage @PackageArgs
$InstallLocation = Get-AppInstallLocation "$PackageName*"

Remove-Item $(Get-Item $(Join-Path $ToolsDir "$fname"))

Write-Host "$PackageName registered as $App"
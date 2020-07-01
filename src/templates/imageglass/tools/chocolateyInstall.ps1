$ErrorActionPreference = 'Stop'

$PackageArgs = @{
  PackageName    = 'imageglass'
  FileType       = 'msi'
  Url            = '$url'
  Checksum       = '$checksum'
  ChecksumType   = 'sha512'
  Url64          = '$url64'
  Checksum64     = '$checksum64'
  ChecksumType64 = 'sha512'
  SilentArgs     = '/quiet /qn /norestart'
  ValidExitCodes = @(0)
}
Install-ChocolateyPackage @PackageArgs

$PackageName = $PackageArgs.PackageName
$InstallLocation = Get-AppInstallLocation $PackageName
if (!$InstallLocation)  { Write-Warning "Can't find $PackageName install location"; return }
Write-Host "$PackageName installed to '$InstallLocation'"
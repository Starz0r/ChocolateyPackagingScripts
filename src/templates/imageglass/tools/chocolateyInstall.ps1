$ErrorActionPreference = 'Stop'

$packageArgs = @{
  packageName    = 'imageglass'
  fileType       = 'msi'
  url            = '$url'
  checksum       = '$checksum'
  checksumType   = 'sha512'
  url64          = '$url64'
  checksum64     = '$checksum64'
  checksumType64 = 'sha512'
  silentArgs     = '/quiet /qn /norestart'
  validExitCodes = @(0)
}
Install-ChocolateyPackage @packageArgs

$packageName = $packageArgs.packageName
$installLocation = Get-AppInstallLocation $packageName
if (!$installLocation)  { Write-Warning "Can't find $packageName install location"; return }
Write-Host "$packageName installed to '$installLocation'"
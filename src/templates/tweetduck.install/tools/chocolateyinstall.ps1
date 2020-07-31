$ErrorActionPreference = 'Stop';

$PackageName  = $env:ChocolateyPackageName
$App = $PackageName.Split(".")[0]
$InstallDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

$PackageArgs = @{
  PackageName   = $PackageName
  UnzipLocation = $InstallDir
  FileType      = 'exe'
  Url           = "$url"

  SoftwareName  = 'tweetduck*'

  Checksum      = "$checksum"
  ChecksumType  = 'sha512'
  
  SilentArgs   = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  ValidExitCodes= @(0)
}

Install-ChocolateyPackage @PackageArgs
$InstallLocation = Get-AppInstallLocation "$PackageName*"

Write-Host "$PackageName registered as $App"
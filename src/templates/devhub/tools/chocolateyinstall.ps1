$ErrorActionPreference = 'Stop';

$PackageName  = $env:ChocolateyPackageName
$App = $PackageName.Split(".")[0]
$InstallDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

$PackageArgs = @{
  PackageName    = $PackageName
  UnzipLocation  = $InstallDir
  FileType       = 'exe'
  Url64          = "$url"

  SoftwareName   = 'devhub*'

  Checksum64     = "$checksum"
  ChecksumType64 = 'sha512'
  
  SilentArgs     = '/S /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  ValidExitCodes = @(0)
}

Install-ChocolateyPackage @PackageArgs
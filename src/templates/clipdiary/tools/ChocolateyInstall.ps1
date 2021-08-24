$ErrorActionPreference = 'Stop';

$packageName = $env:ChocolateyPackageName
$toolsDir    = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url         = 'http://clipdiary.com/download/clipdiary_5.51.exe'

$packageArgs = @{
  packageName    = $packageName
  unzipLocation  = $toolsDir
  fileType       = 'exe'
  url            = $url

  softwareName   = 'clipdiary*'

  checksum       = '5507A5C6C1C980EBE1C4DBCD143C70CCE0410A0440F4658FDD2A65EC27FF28C0C86D59A4EF8853DF6CB5035710046D587B722E1D35F581D5E163D89CDF30B68E'
  checksumType   = 'sha512'
  
  silentArgs     = '/S'
  validExitCodes = @(0)
}

Install-ChocolateyPackage @packageArgs
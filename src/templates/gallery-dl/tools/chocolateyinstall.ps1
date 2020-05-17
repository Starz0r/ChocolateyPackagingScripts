$ErrorActionPreference = "Stop";
$installDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

Get-ChocolateyWebFile -PackageName "gallery-dl" -FileFullPath "$installDir\gallery-dl.exe" -Url "$url" -Checksum "$checksum" -ChecksumType "SHA512"
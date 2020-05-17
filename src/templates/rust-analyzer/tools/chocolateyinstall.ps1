$ErrorActionPreference = "Stop";
$installDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

Get-ChocolateyWebFile -PackageName "rust-analyzer" -FileFullPath "$installDir\rust-analyzer.exe" -Url64bit "$url" -Checksum64 "$checksum" -ChecksumType64 "SHA512"
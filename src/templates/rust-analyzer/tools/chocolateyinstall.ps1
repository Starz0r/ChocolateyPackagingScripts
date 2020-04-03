$ErrorActionPreference = "Stop";
$installDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

if (Get-OSArchitectureWidth 32) {
	Write-Host -ForegroundColor red "Unsupported 32-Bit System."
	exit 1
}

Get-ChocolateyWebFile -PackageName "rust-analyzer" -FileFullPath "$installDir\rust-analyzer.exe" -Url "$url"
Get-ChecksumValid -File "$installDir\rust-analyzer.exe" -Checksum "$checksum" -ChecksumType "SHA512" -OriginalUrl "$url"
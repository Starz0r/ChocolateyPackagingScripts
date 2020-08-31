$PackageName = 'terraform-lsp'
$ToolsPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallDir = Join-Path $(Get-ToolsLocation) $PackageName

$PackageArgs = @{
	PackageName = $PackageName
	Url64 = '$url'
	Checksum64 = '$checksum'
	ChecksumType64 = 'sha512'
	UnzipLocation = $InstallDir
}
Install-ChocolateyZipPackage @PackageArgs
$TarFile = $(Join-Path $InstallDir "$fname").TrimEnd(".gz")
Get-ChocolateyUnzip -FileFullPath $TarFile -Destination $InstallDir
Remove-Item $TarFile

Install-BinFile 'terraform-lsp' -Path "$InstallDir\terraform-lsp.exe" -UseStart
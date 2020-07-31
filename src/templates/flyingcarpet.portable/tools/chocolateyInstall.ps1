$PackageName = 'flyingcarpet.portable'
$ToolsPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallDir = Join-Path $(Get-ToolsLocation) $PackageName

$desktop = [System.Environment]::GetFolderPath("Desktop")

$PackageArgs = @{
	PackageName = $PackageName
	Url64 = '$url'
	Checksum64 = '$checksum'
	ChecksumType64 = 'sha512'
	UnzipLocation = $InstallDir
}
Install-ChocolateyZipPackage @PackageArgs

Install-BinFile flyingcarpet -path "$InstallDir\flyingcarpet.exe" -UseStart
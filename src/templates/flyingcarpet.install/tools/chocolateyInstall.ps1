$PackageName = 'flyingcarpet.install'
$ToolsPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InstallDir = Join-Path $(Get-ToolsLocation) "flyingcarpet"

$desktop = [System.Environment]::GetFolderPath("Desktop")

$PackageArgs = @{
	PackageName = $PackageName
	Url64 = '$url'
	Checksum64 = '$checksum'
	ChecksumType64 = 'sha512'
	UnzipLocation = $InstallDir
}
Install-ChocolateyZipPackage @PackageArgs

Install-ChocolateyShortcut -ShortcutFilePath "$desktop\Flying Carpet.lnk" -TargetPath "$InstallDir\flyingcarpet.exe" -WorkingDirectory "$InstallDir" -WindowStyle 1
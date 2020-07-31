$PackageName = 'flyingcarpet.portable'
$InstallDir = Join-Path $(Get-ToolsLocation) $PackageName
$desktop = [System.Environment]::GetFolderPath("Desktop")

Uninstall-BinFile flyingcarpet -path "$InstallDir\flyingcarpet.exe"
Uninstall-ChocolateyZipPackage -PackageName $PackageName -ZipFileName '$filename'

Remove-Item $InstallDir
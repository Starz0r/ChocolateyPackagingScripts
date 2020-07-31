$PackageName = 'flyingcarpet.install'
$InstallDir = Join-Path $(Get-ToolsLocation) "flyingcarpet"
$desktop = [System.Environment]::GetFolderPath("Desktop")

Uninstall-ChocolateyZipPackage -PackageName $PackageName -ZipFileName '$filename'

Remove-Item $InstallDir
Remove-Item "$desktop\Flying Carpet.lnk" -ErrorAction SilentlyContinue -Force | Out-Null
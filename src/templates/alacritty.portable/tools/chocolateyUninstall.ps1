$PackageName = 'alacritty.portable'
$InstallDir = Join-Path $(Get-ToolsLocation) "alacritty"
$desktop = [System.Environment]::GetFolderPath("Desktop")

Uninstall-BinFile alacritty -path "$InstallDir\alacritty.exe"
Uninstall-ChocolateyZipPackage -PackageName 'alacritty.portable' -ZipFileName '$filename'

Remove-Item $InstallDir
Remove-Item "$desktop\Alacritty.lnk" -ErrorAction SilentlyContinue -Force | Out-Null
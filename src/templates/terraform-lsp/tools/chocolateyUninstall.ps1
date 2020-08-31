$PackageName = 'terraform-lsp'
$InstallDir = Join-Path $(Get-ToolsLocation) $PackageName

Uninstall-BinFile "terraform-lsp" -Path "$InstallDir\terraform-lsp.exe"
Uninstall-ChocolateyZipPackage -PackageName $PackageName -ZipFileName '$fname'

Remove-Item $InstallDir
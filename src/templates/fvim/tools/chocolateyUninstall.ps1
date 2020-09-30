$PackageName = 'fvim';
$InstallDir  = Join-Path $(Get-ToolsLocation) $PackageName;
$Desktop = [System.Environment]::GetFolderPath("Desktop");

Uninstall-BinFile "fvim" -Path "$InstallDir\FVim.exe";

if ($WindowsVersion.Major -eq "10") {
	Uninstall-ChocolateyZipPackage -PackageName $PackageName -ZipFileName '$fname64';
} else {
	Uninstall-ChocolateyZipPackage -PackageName $PackageName -ZipFileName '$fname';
};

Remove-Item $InstallDir -ErrorAction SilentlyContinue;
Remove-Item "$Desktop\FVim.lnk" -ErrorAction SilentlyContinue -Force | Out-Null;
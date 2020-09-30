$PackageName    = 'fvim';
$ToolsPath      = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$InstallDir     = Join-Path $(Get-ToolsLocation) $PackageName;
$Desktop        = [System.Environment]::GetFolderPath("Desktop");
$WindowsVersion = [Environment]::OSVersion.Version;

if ($WindowsVersion.Major -eq "10") {
	$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath64 = Get-Item $(Join-Path $ToolsPath '$fname64')
		Checksum64     = '$checksum64'
		ChecksumType64 = 'sha512'
		Destination    = $InstallDir
	};
} else {
	$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath64 = Get-Item $(Join-Path $ToolsPath '$fname')
		Checksum64     = '$checksum'
		ChecksumType64 = 'sha512'
		Destination    = $InstallDir
	};
};

Install-ChocolateyZipPackage @PackageArgs;
Remove-Item ($ToolsPath + '\*.' + 'zip');

Install-BinFile 'fvim' -Path "$InstallDir\FVim.exe" -UseStart;
Install-ChocolateyShortcut -ShortcutFilePath "$Desktop\FVim.lnk" -TargetPath "$InstallDir\fvim.exe" -WorkingDirectory "$InstallDir" -WindowStyle 1
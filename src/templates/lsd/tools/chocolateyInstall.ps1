$PackageName = 'lsd';
$ToolsPath   = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$PkgParams   = Get-PackageParameters;

# Remove Previous Installations
Get-ChildItem $ToolsPath\* | Where-Object { $_.PSISContainer } | ForEach-Object {
	IF (($_.BaseName -ne "x86") -and ($_.BaseName -ne "x64")) {
		Write-Warning "Deleting $_ from previous deprecated installation process. Chocolatey may continue to refer to this path until you uninstall and reinstall this package. No further action is required.";
		Remove-Item $_ -Recurse -Force -EA 0 | Out-Null;
	}
}
Remove-Item ($ToolsPath + '\*.' + 'zip');
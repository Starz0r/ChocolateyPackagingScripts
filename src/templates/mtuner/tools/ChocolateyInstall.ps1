$ErrorActionPreference = 'Stop';
$PackageName = "MTuner";
$ToolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)";
$UserDesktop = [Environment]::GetFolderPath("Desktop");

if (Get-OSArchitectureWidth -Compare 32) {
	Write-Warning "32-bit system architecture detected, installation may not finish properly.";
};

Get-ChocolateyUnzip -PackageName $PackageName -FileFullPath64 "$ToolsDir\MTuner.zip" -Destination $ToolsDir;

$AppLocation = $(Get-ChildItem $ToolsDir -Recurse -Filter "MTuner.exe")[0].FullName;

Get-ChildItem $ToolsDir -Recurse -Filter *.exe | Where-Object {$_.Name -ne "MTuner.exe"} | ForEach-Object {
	New-Item -ItemType file "$($_.FullName)$('.ignore')" -EA 0 | Out-Null;
};

$ShortcutFile = Join-Path $UserDesktop "$PackageName.lnk";
Install-ChocolateyShortcut -ShortcutFilePath $ShortcutFile -TargetPath $AppLocation;

Remove-Item "$ToolsDir\MTuner.zip" -EA 0 | Out-Null;
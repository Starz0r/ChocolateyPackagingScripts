$ErrorActionPreference = 'Stop';

$ToolsDir        = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)";
$FileName        = $(Join-Path $ToolsDir $fname);
$PackageName     = "NeoChat";
$Version         = "$version";
$WindowsVersion  = [Environment]::OSVersion.Version;
$UserDesktop     = [Environment]::GetFolderPath("Desktop");
$AppFileName     = "neochat.exe"

if (Get-OSArchitectureWidth -Compare 32) {
	Write-Warning "32-bit system architecture detected, application may not run at all on this device.";
};

if ($WindowsVersion.Major -lt "10") {
  Throw "This package requires at least Windows 10 or higher.";
};

Get-ChocolateyUnzip -PackageName $PackageName -FileFullPath64 "$ToolsDir\$fname" -Destination $ToolsDir;
$AppLocation = $(Get-ChildItem $ToolsDir -Recurse -Filter $AppFileName)[0].FullName;

Get-ChildItem $ToolsDir -Recurse -Filter *.exe | Where-Object {$_.Name -ne $AppFileName} | ForEach-Object {
	New-Item -ItemType file "$($_.FullName)$('.ignore')" -EA 0 | Out-Null;
};

$ShortcutFile = Join-Path $UserDesktop "$PackageName.lnk";
Install-ChocolateyShortcut -ShortcutFilePath $ShortcutFile -TargetPath $AppLocation;

Remove-Item "$ToolsDir\$fname" -EA 0 | Out-Null;
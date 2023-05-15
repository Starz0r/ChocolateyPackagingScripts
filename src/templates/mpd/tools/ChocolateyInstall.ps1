$ErrorActionPreference = 'Stop';
$ToolsPath   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)";

If (Test-Path -Path $ToolsPath\"mpd.exe" -PathType Leaf) {
	Remove-Item -Path $ToolsPath\"mpd.exe" | Out-Null;
	Write-Warning "mpd from previous version detected, deleting...";
};
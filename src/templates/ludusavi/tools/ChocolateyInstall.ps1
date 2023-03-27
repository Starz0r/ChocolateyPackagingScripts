$PackageName = 'ludusavi';
$ToolsPath   = Split-Path -Parent $MyInvocation.MyCommand.Definition;

If (Test-Path -Path $ToolsPath\"ludusavi.exe" -PathType Leaf) {
	Remove-Item -Path $ToolsPath\"ludusavi.exe" | Out-Null;
	Write-Warning "Ludusavi from previous version detected, deleting...";
};
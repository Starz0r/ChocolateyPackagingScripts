$ErrorActionPreference = 'Stop';

$PackageName = 'hyperfine';
$ToolsPath   = Split-Path -Parent $MyInvocation.MyCommand.Definition;

If (Test-Path -Path $ToolsPath\"hyperfine.exe" -PathType Leaf) {
	Remove-Item -Path $ToolsPath\"hyperfine.exe" | Out-Null;
	Write-Warning "hyperfine from previous version detected, deleting...";
};

$items = Get-ChildItem -Path $ToolsPath;
ForEach ($item in $items) {
	If (Test-Path -Path $item -Include "hyperfine-*" -PathType Container) {
		Remove-Item -Path $item -Recurse -Force | Out-Null;
		Write-Warning "Extra junk found from previous version detected, deleting...";
		Continue;
	};
	
	If (Test-Path -Path $item -Include "*hyperfine.ps1" -PathType Leaf) {
		Remove-Item -Path $item -Recurse -Force | Out-Null;
		Write-Warning "Extra junk found from previous version detected, deleting...";
		Continue;
	};
	
	If (Test-Path -Path $item -Include "LICENSE-APACHE" -PathType Leaf) {
		Remove-Item -Path $item -Force | Out-Null;
		Write-Warning "Extra junk found from previous version detected, deleting...";
		Continue;
	};
	
	If (Test-Path -Path $item -Include "LICENSE-MIT" -PathType Leaf) {
		Remove-Item -Path $item -Force | Out-Null;
		Write-Warning "Extra junk found from previous version detected, deleting...";
		Continue;
	};
	
	If (Test-Path -Path $item -Include "README.md" -PathType Leaf) {
		Remove-Item -Path $item -Force | Out-Null;
		Write-Warning "Extra junk found from previous version detected, deleting...";
		Continue;
	};
};
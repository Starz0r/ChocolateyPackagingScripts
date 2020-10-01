$ToolsPath = Split-Path -Parent $MyInvocation.MyCommand.Definition;

Remove-Item $(Get-Item $(Join-Path $ToolsPath 'tokei.exe')) -EA 0;

# Only One Can Survive
if (Get-OSArchitectureWidth -Compare 32)
{
	Remove-Item $(Get-Item $(Join-Path $ToolsPath '$fname64'));
	Rename-Item -Path $(Get-Item $(Join-Path $ToolsPath '$fname')) -NewName "tokei.exe";
}
elseif (Get-OSArchitectureWidth -Compare 64)
{
	Remove-Item $(Get-Item $(Join-Path $ToolsPath '$fname'));
	Rename-Item -Path $(Get-Item $(Join-Path $ToolsPath '$fname64')) -NewName "tokei.exe";
};
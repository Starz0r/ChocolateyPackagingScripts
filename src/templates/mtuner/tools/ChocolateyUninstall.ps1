$ErrorActionPreference = 'Stop';

$UserDesktop = [Environment]::GetFolderPath("Desktop");
$ShortcutFile = Join-Path $UserDesktop "MTuner.lnk";
if (Test-Path $ShortcutFile) {
	Remove-Item $ShortcutFile;
};
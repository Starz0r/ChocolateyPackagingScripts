$ErrorActionPreference = 'Stop';

$UserDesktop = [Environment]::GetFolderPath("Desktop");
$ShortcutFile = Join-Path $UserDesktop "NeoChat.lnk";
If (Test-Path $ShortcutFile) {
	Remove-Item $ShortcutFile;
};
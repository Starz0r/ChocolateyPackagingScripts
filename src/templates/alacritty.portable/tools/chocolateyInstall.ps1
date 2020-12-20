$PackageName = 'alacritty.portable'
$ToolsPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$OldInstallDir = Join-Path $(Get-ToolsLocation) "alacritty"
$Desktop = [System.Environment]::GetFolderPath("Desktop")
$ChocoBin = "C:\ProgramData\chocolatey\bin"

$Preexisting = Test-Path -Path $OldInstallDir -PathType Container
if ($Preexisting) {
	Write-Host -ForegroundColor yellow "WARNING: Old Alacritty Portable detected."
	Write-Host -ForegroundColor yellow "If you installed a previous version of this package the semantics have changed."
	Write-Host -ForegroundColor yellow "The previous install folder located at: $OldInstallDir ..."
	Write-Host -ForegroundColor yellow "is no longer in use, and is recommended that you delete or move that folder ..."
	Write-Host -ForegroundColor yellow "to prevent conflicts in the future."
}

Install-ChocolateyShortcut -ShortcutFilePath "$Desktop\Alacritty.lnk" -TargetPath "$ChocoBin\alacritty.exe" -WindowStyle 1

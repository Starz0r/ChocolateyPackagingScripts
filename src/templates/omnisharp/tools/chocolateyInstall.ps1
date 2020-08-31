$ToolsPath = Split-Path $MyInvocation.MyCommand.Definition
$InstallDir = Join-Path $(Get-ToolsLocation) "omnisharp"

$PackageArgs = @{
	PackageName = "omnisharp"
	FileFullPath = Get-Item $ToolsPath\*-win-x86*.zip
	FileFullPath64 = Get-Item $ToolsPath\*-win-x64*.zip
	Destination = $InstallDir
}
Get-ChildItem $ToolsPath\* | Where-Object { $_.PSISContainer } | Remove-Item -Recurse -Force #remove older package dirs
Get-ChocolateyUnzip @PackageArgs
Remove-Item $ToolsPath\*.zip -ea 0
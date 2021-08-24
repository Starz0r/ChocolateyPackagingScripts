$PackageName = 'ludusavi';
$ToolsPath   = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$PkgParams   = Get-PackageParameters;

$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath   = Get-Item $(Join-Path $ToolsPath '$fname')
		FileFullPath64 = Get-Item $(Join-Path $ToolsPath '$fname64')
		Destination    = $ToolsPath
};

Get-ChocolateyUnzip @PackageArgs;
Remove-Item ($ToolsPath + '\*.' + 'zip');
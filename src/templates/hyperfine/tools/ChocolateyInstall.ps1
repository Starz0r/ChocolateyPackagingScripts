$PackageName = 'hyperfine';
$ToolsPath   = Split-Path -Parent $MyInvocation.MyCommand.Definition;

$PackageArgs = @{
	PackageName    = $PackageName
	FileFullPath64 = Get-Item $(Join-Path $ToolsPath '$fname')
	Destination    = $ToolsPath
};

Get-ChocolateyUnzip @PackageArgs;
Remove-Item ($ToolsPath + '\*.' + 'zip');
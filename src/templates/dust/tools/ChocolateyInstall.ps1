$PackageName = 'dust';
$ToolsPath   = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$PkgParams   = Get-PackageParameters;

if ($PkgParams.GNU) {
	$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath   = Get-Item $(Join-Path $ToolsPath '$altfname')
		FileFullPath64 = Get-Item $(Join-Path $ToolsPath '$altfname64')
		Destination    = $ToolsPath
	};
} else {
	$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath   = Get-Item $(Join-Path $ToolsPath '$fname')
		FileFullPath64 = Get-Item $(Join-Path $ToolsPath '$fname64')
		Destination    = $ToolsPath
	};
};

Get-ChocolateyUnzip @PackageArgs;
Remove-Item ($ToolsPath + '\*.' + 'zip');
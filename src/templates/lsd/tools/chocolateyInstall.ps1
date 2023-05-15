$PackageName = 'lsd';
$ToolsPath   = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$PkgParams   = Get-PackageParameters;

If ($PkgParams.GNU) {
	$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath   = Get-Item $(Join-Path $ToolsPath '$altfname')
		FileFullPath64 = Get-Item $(Join-Path $ToolsPath '$altfname64')
		Destination    = $ToolsPath
	};
} Else {
	$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath   = Get-Item $(Join-Path $ToolsPath '$fname')
		FileFullPath64 = Get-Item $(Join-Path $ToolsPath '$fname64')
		Destination    = $ToolsPath
	};
};

# Remove Previous Installations
Get-ChildItem $ToolsPath\* | Where-Object { $_.PSISContainer } | ForEach-Object {
	Remove-Item $_ -Recurse -Force -EA 0 | Out-Null;
};
Get-ChocolateyUnzip @PackageArgs;
Remove-Item ($ToolsPath + '\*.' + 'zip');
$PackageName = 'dust';
$ToolsPath   = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$PkgParams   = Get-PackageParameters;

$PrevInstallations = Get-ChildItem $ToolsPath;

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

# cleanup
ForEach ($Installation in $PrevInstallations) {
	if (Test-Path -Path $Installation.FullName -PathType Container) {
		Remove-Item -Recurse -Force $Installation.FullName -EA 0;
	};
};
Remove-Item ($ToolsPath + '\*.' + 'zip');
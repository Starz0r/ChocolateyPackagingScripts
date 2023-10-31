$PackageName    = "lua-language-server";
$ToolsPath      = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$ArchWidth      = Get-OSArchitectureWidth;

if ($ArchWidth -eq 64) {
	$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath64 = Get-Item $(Join-Path $(Join-Path $ToolsPath "x64") "$fname64")
		Destination    = Join-Path $ToolsPath "x64"
	};
	mkdir $(Join-Path $(Join-Path $ToolsPath "x64") "log");
} else {
	$PackageArgs = @{
		PackageName    = $PackageName
		FileFullPath   = Get-Item $(Join-Path $(Join-Path $ToolsPath "x86") "$fname")
		Destination    = Join-Path $ToolsPath "x86"
	};
	mkdir $(Join-Path $(Join-Path $ToolsPath "x86") "log");
};

Get-ChocolateyUnzip @PackageArgs;
Remove-Item ($ToolsPath + '\*.' + 'zip');
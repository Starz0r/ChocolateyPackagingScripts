$ErrorActionPreference = 'Stop';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$installDir = Join-Path $(Get-ToolsLocation) $PackageName

Uninstall-BinFile -Name "vcpkg" -Path "$installDir\vcpkg.exe"
Remove-Item -Recurse -Force $installDir
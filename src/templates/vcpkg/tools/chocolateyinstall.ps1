$ErrorActionPreference = 'Stop';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$installDir = Join-Path $(Get-ToolsLocation) $PackageName

git clone --single-branch --branch $tag https://github.com/Microsoft/vcpkg.git $installDir
Invoke-BatchFile "$installDir\bootstrap-vcpkg.bat"
Install-BinFile -Name "vcpkg" -Path "$installDir\vcpkg.exe"
& "$installDir\vcpkg.exe" integrate install
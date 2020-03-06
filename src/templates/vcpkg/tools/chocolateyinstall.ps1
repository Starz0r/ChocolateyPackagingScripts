$ErrorActionPreference = 'SilentlyContinue';
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$installDir = Join-Path $(Get-ToolsLocation) $PackageName

$preinstalled = Test-Path -Path $installDir -PathType Container
$precompiled = Test-Path -Path "$installDir\vcpkg.exe" -PathType Leaf

if ($preinstalled) {
	Write-Host -ForegroundColor green "Vcpkg repository already exists, pulling new changes instead."
	git -C $installDir pull
	git -C $installDir checkout $tag
} else {
	Write-Host -ForegroundColor green "Cloning GitHub Repository"
	git clone --single-branch --branch $tag https://github.com/Microsoft/vcpkg.git $installDir
}

if ($precompiled) {
	Write-Host -ForegroundColor green "Vcpkg already compiled, deleting executable."
	Remove-Item -Path "$installDir\vcpkg.exe"
}

$ErrorActionPreference = 'Stop';
Write-Host -ForegroundColor green "Bootstraping vcpkg"
Invoke-Expression "$installDir\bootstrap-vcpkg.bat"

Write-Host -ForegroundColor green "Adding Shim to PATH"
Install-BinFile -Name "vcpkg" -Path "$installDir\vcpkg.exe"

Write-Host -ForegroundColor green "Setting vcpkg root"
Invoke-Expression "$installDir\vcpkg.exe integrate install"
$packageName = "alacritty.install"
$oldInstallDir = Join-Path $(Get-ToolsLocation) "alacritty"

$preexisting = Test-Path -Path $oldInstallDir -PathType Container
if ($preexisting) {
	Write-Host -ForegroundColor yellow "WARNING: Alacritty Portable detected."
	Write-Host -ForegroundColor yellow "If you installed a previous version of this package the semantics have changed."
	Write-Host -ForegroundColor yellow "This is now a install package, and will install the MSI version of this software instead."
	Write-Host -ForegroundColor yellow "If you are OK with this, or installed portable through your own means, ignore this message."
	Write-Host -ForegroundColor yellow "Otherwise you should delete the files at $oldInstallDir to prevent conflicts in the future."
}

$ErrorActionPreference = 'Stop'
$toolsPath = Split-Path $MyInvocation.MyCommand.Definition
 
$packageArgs = @{
    PackageName    = $packageName
    FileType       = "msi"
    SoftwareName   = "Alacritty"
    Url64bit       = "$url"
	Checksum64     = "$checksum"
	ChecksumType64 = "sha512"
    SilentArgs     = "/qn /norestart"
    ValidExitCodes = @(0, 3010, 1641)
}
Install-ChocolateyPackage @packageArgs
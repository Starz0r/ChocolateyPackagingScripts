$PackageName = "alacritty.install";
$OldInstallDir = Join-Path $(Get-ToolsLocation) "alacritty";

$Preexisting = Test-Path -Path $OldInstallDir -PathType Container;
if ($Preexisting) {
	Write-Host -ForegroundColor yellow "WARNING: Alacritty Portable detected.";
	Write-Host -ForegroundColor yellow "If you installed a previous version of this package the semantics have changed.";
	Write-Host -ForegroundColor yellow "This is now a install package, and will install the MSI version of this software instead.";
	Write-Host -ForegroundColor yellow "If you are OK with this, or installed portable through your own means, ignore this message.";
	Write-Host -ForegroundColor yellow "Otherwise you should delete the files at $OldInstallDir to prevent conflicts in the future.";
};

$ErrorActionPreference = 'Stop';
$ToolsDir = Split-Path $MyInvocation.MyCommand.Definition;
 
$PackageArgs = @{
    PackageName    = $PackageName
    FileType       = "msi"
    SoftwareName   = "Alacritty"
    File64         = Get-Item $(Join-Path $ToolsDir "$fname")
    SilentArgs     = "/qn /norestart /quiet"
    ValidExitCodes = @(0, 3010, 1641)
};
Install-ChocolateyInstallPackage @packageArgs;

Remove-Item -Force "$fname" -EA 0;
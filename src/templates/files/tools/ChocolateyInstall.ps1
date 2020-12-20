$ErrorActionPreference = 'Stop';

$ToolsDir       = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)";
$FileName       = $(Join-Path $ToolsDir $fname);
$Version        = "$version";

$WindowsVersion=[Environment]::OSVersion.Version;
if ($WindowsVersion.Major -ne "10") {
  throw "This package requires Windows 10.";
};
#The .msixbundle format is not supported on Windows 10 version 1709 and 1803. https://docs.microsoft.com/en-us/windows/msix/msix-1709-and-1803-support
$IsCorrectBuild=[Environment]::OSVersion.Version.Build;
if ($IsCorrectBuild -lt "18362") {
  throw "This package requires at least Windows 10 version 1903/OS build 18362.x.";
};

$AppxPackageName = "49306atecsolution.FilesUWP";

if ((Get-AppxPackage -name $AppxPackageName).Version -Match $Version) {
  if($env:ChocolateyForce) {
    # you can't install the same version of an appx package, you need to remove it first
    Write-Host Removing already installed version first. ;
    Get-AppxPackage -Name $AppxPackageName | Remove-AppxPackage;
  } else {
    Write-Host The $Version version of Files is already installed. If you want to reinstall use --force ;
    return;
  };
};

Add-AppxPackage -Path $FileName;
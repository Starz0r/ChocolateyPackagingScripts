$ErrorActionPreference = 'Stop';
$ToolsPath             = Split-Path -Parent $MyInvocation.MyCommand.Definition;
$InstallDir            = Get-ToolsLocation; # Dangerous but appending -SpecificFolder to Install-ChocolateyZipPackage doesn't work

Install-ChocolateyZipPackage $env:ChocolateyPackageName "$url" $InstallDir -checksum '$checksum' -checksumType 'sha256';
Install-ChocolateyPath "$InstallDir\bin";
$ErrorActionPreference = 'Stop';
$PackageName           = $env:ChocolateyPackageName;
$App                   = $PackageName.Split(".")[0];
$InstallDir            = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)";
$ToolsDir              = Split-Path -parent $MyInvocation.MyCommand.Definition;

$PackageArgs = @{
  PackageName     = $PackageName
  UnzipLocation   = $InstallDir
  FileType        = 'exe'
  File64          = Get-Item $(Join-Path $ToolsDir "$fname")

  SoftwareName    = 'devhub*'

  Checksum64      = "$checksum"
  ChecksumType64  = 'sha512'
  
  SilentArgs      = "/S", "/SILENT", "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", "/LOG"
  ValidExitCodes  = @(0)
}

Install-ChocolateyPackage @PackageArgs
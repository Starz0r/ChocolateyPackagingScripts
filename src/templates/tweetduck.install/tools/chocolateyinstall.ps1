$ErrorActionPreference = 'Stop';

$PackageName  = $env:ChocolateyPackageName
$App = $PackageName.Split(".")[0]
$InstallDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

$stop_application = if (Get-Process -Name TweetDuck -ErrorAction SilentlyContinue) {$false} else {$true}

$PackageArgs = @{
  PackageName   = $PackageName
  UnzipLocation = $InstallDir
  FileType      = 'exe'
  Url           = "$url"

  SoftwareName  = 'tweetduck*'

  Checksum      = "$checksum"
  ChecksumType  = 'sha512'
  
  SilentArgs   = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  ValidExitCodes= @(0)
}


if ($stop_application -and (Get-Process -Name TweetDuck -ErrorAction SilentlyContinue)) {
    Stop-Process -processname TweetDuck
}

Install-ChocolateyPackage @PackageArgs
$InstallLocation = Get-AppInstallLocation "$PackageName*"

Write-Host "$PackageName registered as $App"
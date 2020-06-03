$ErrorActionPreference = 'Stop';

$packageName  = $env:ChocolateyPackageName
$installDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url32        = "$url"

$stop_application = if (Get-Process -Name TweetDuck -ErrorAction SilentlyContinue) {$false} else {$true}

$packageArgs = @{
  packageName   = $packageName
  unzipLocation = $installDir
  fileType      = 'exe'
  url           = $url32

  softwareName  = 'tweetduck*'

  checksum      = "$checksum"
  checksumType  = 'sha512'
  
  silentArgs   = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  validExitCodes= @(0)
}


if ($stop_application -and (Get-Process -Name TweetDuck -ErrorAction SilentlyContinue)) {
    Stop-Process -processname TweetDuck
}

Install-ChocolateyPackage @packageArgs
$installLocation = Get-AppInstallLocation "$packageName*"

Install-BinFile $packageName "$installLocation\$packageName.exe"
Register-Application "$installLocation\$packageName.exe"
Write-Host "$packageName registered as $packageName"






    
$installDir = Join-Path $env:ChocolateyToolsLocation "flutter"

Remove-Item -Path $installDir -Force -Recurse

$oldpath = (Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH).path
$updatedPath = $oldpath.Replace(";$installDir", '')
Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $updatedPath

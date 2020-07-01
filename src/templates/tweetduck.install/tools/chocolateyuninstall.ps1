$ErrorActionPreference = 'Stop'

$PackageName = $env:ChocolateyPackageName.Split(".")[0]

[array] $key = Get-UninstallRegistryKey "PackageName*"
if ($key.Count -eq 1) {
    $key | ForEach-Object {
        $PackageArgs = @{
            PackageName            = $PackageName
            SilentArgs             = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
            FileType               = 'EXE'
            ValidExitCodes         = @(0)
            File                   = "$($_.UninstallString.Replace(' /x86=0', ''))"
        }
        Uninstall-ChocolateyPackage @PackageArgs
    }
}
elseif ($key.Count -eq 0) {
    Write-Warning "$PackageName has already been uninstalled by other means."
}
elseif ($key.Count -gt 1) {
    Write-Warning "$($key.Count) matches found!"
    Write-Warning "To prevent accidental data loss, no programs will be uninstalled."
    Write-Warning "Please alert package maintainer the following keys were matched:"
    $key | ForEach-Object {Write-Warning "- $($_.DisplayName)"}
}
$PackageName = 'flyingcarpet.install'
$Desktop = [System.Environment]::GetFolderPath("Desktop")

Remove-Item "$Desktop\Flying Carpet.lnk" -ErrorAction SilentlyContinue -Force | Out-Null
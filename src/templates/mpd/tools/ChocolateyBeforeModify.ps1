$ErrorActionPreference = 'SilentlyContinue';

$Procs = Get-Process -Name mpd -ErrorAction SilentlyContinue;

ForEach ($Proc in $Procs) {
	Write-Warning "mpd is open, stopping the process to allow for update..." ;
    Stop-Process $Proc;
};
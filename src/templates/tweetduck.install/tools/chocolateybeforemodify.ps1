$ErrorActionPreference = 'SilentlyContinue';

$stop_application = if (Get-Process -Name TweetDuck -ErrorAction SilentlyContinue) {$false} else {$true}

if ($stop_application -and (Get-Process -Name TweetDuck -ErrorAction SilentlyContinue)) {
    Stop-Process -processname TweetDuck
}
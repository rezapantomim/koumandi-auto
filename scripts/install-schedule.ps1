# Registers the long-video writer in Windows Task Scheduler: Sundays and Wednesdays 10:00 (each run fills the next 7 days,
# so one missed run - PC off - is covered by the other). If the PC was off at that time, it runs as soon as possible afterwards.
$root = Split-Path -Parent $PSScriptRoot
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$root\scripts\writer.ps1`"" -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday,Wednesday -At 10:00
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 4) -WakeToRun
Register-ScheduledTask -TaskName 'KOUMANDI Writer' -Action $action -Trigger $trigger -Settings $settings -Force
Write-Host "Registered 'KOUMANDI Writer' (Sun + Wed 10:00)."

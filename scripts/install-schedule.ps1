# Registers the long-video writer in Windows Task Scheduler: every day 09:00 (each run fills the long slots of the next
# schedule.plan_days_ahead days - Sat/Mon/Wed/Fri - and stops quickly when the queue is full). If the PC was off at that
# time, it runs as soon as possible afterwards.
$root = Split-Path -Parent $PSScriptRoot
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$root\scripts\writer.ps1`"" -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Daily -At 09:00
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 4) -WakeToRun
Register-ScheduledTask -TaskName 'KOUMANDI Writer' -Action $action -Trigger $trigger -Settings $settings -Force
Write-Host "Registered 'KOUMANDI Writer' (daily 09:00)."

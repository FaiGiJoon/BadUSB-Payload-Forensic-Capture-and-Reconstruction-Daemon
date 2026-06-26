# setup_service.ps1
# This script configures the Forensic Ducky Monitor to run as a Scheduled Task
# with highest privileges under the NT AUTHORITY\SYSTEM account.
# This ensures hook persistence across Secure Desktop (UAC) transitions.

$TaskName = "ForensicDuckyMonitor"
$PythonPath = (Get-Command python.exe).Source
$ScriptPath = Join-Path (Get-Location) "main.py"
$WorkingDirectory = (Get-Location).Path

# Define the action: Run python main.py
$Action = New-ScheduledTaskAction -Execute "$PythonPath" -Argument "$ScriptPath" -WorkingDirectory "$WorkingDirectory"

# Define the trigger: At startup
$Trigger = New-ScheduledTaskTrigger -AtStartup

# Define the settings: Allow start on batteries, no stop on idle
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 365)

# Register the task to run as SYSTEM with Highest Privileges
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -User "NT AUTHORITY\SYSTEM" -RunLevel Highest -Force

Write-Host "Forensic Ducky Monitor has been configured as a Scheduled Task."
Write-Host "It will run under the SYSTEM account to maintain hook persistence."
Write-Host "You can start it manually now using: Start-ScheduledTask -TaskName $TaskName"

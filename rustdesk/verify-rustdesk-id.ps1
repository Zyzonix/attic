#
# written by Zyzonix
# published by xerberosDevelopments
# 
# Copyright (c) 2024 xerberosDevelopments
# 
# date created  | 17-08-2024 10:42:26 
# file          | rustdesk/verify-rustdesk-id.ps1
# project       | attic
#

# script to verify the rustdesk ID equals hostname

# sleep to verify correct start of all RustDesk services
Start-Sleep -Seconds 10

# save start path
$STARTPATH = $pwd

# path to config file RustDesk.toml (in ServiceProfile)
$RustDesk = "C:\Windows\ServiceProfiles\LocalService\AppData\Roaming\RustDesk\config\RustDesk.toml"

# check if paths exist
$RustDeskExists = Test-Path -Path C:\Windows\ServiceProfiles\LocalService\AppData\Roaming\RustDesk\config\RustDesk.toml
$RustDesk2Exists = Test-Path -Path C:\Windows\ServiceProfiles\LocalService\AppData\Roaming\RustDesk\config\RustDesk2.toml
Write-Host "Found RustDesk.toml: "$RustDeskExists
Write-Host "Found RustDesk2.toml: "$RustDesk2Exists

if ($RustDeskExists -and $RustDesk2Exists){
    Write-Host "Both files found - RustDesk installed"
    # change path to allow access to EXE
    Set-Location -Path "C:\"

    $RDID = @(& '.\Program Files\RustDesk\rustdesk.exe' --get-id | Out-String)
    $HOSTNAME = $env:COMPUTERNAME

    #Write-Host $RDID
    #Write-Host $HOSTNAME

    Write-Host "Comparing variables..."
    $HOSTNAMECORRECT = $RDID.toUpper().Contains($HOSTNAME)

    if (-Not $HOSTNAMECORRECT) { 
        Write-Host "RustDesk ID doesn't equal Hostname..."
        Write-Host "Setting correct ID"

        Write-Host "Stopping RustDesk services"
        Stop-Service -Name "RustDesk"

        Start-Sleep -Seconds 15s

        Write-Host "Stopping all running RustDesk tasks"
        Stop-Process -Name "RustDesk" -Force

        $RustDeskContent = "id = '$HOSTNAME'"

        # get content from config; leave line password --> will automatically pasted later
        # check for empty 'enc_id = '''; to prevent double entries
        $RustDeskFileContent = Get-Content -Path $RustDesk | Where-Object { -not $_.Contains('password') -and -not $_.Contains('enc_id = ''')}

        # get line with 'enc_id', will be replaced with new settings
        $enc_id = $RustDeskFileContent | Select -First 1

        # replace content and write to file RustDesk.toml
        $RustDeskFileContent.Replace($enc_id,$RustDeskContent) | Set-Content -Path $RustDesk

        # finally restart the service
        Write-Host "Starting RustDesk services"
        Start-Sleep -Seconds 30
        sc.exe start "RustDesk"
    }

    Write-Host "Set correct ID."
    # finally reset to the origin path
    Set-Location -Path $STARTPATH
}

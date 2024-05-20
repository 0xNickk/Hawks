def generate_cmdlet(cmdlet):
    ascii_values = [ord(c) for c in cmdlet]
    new_value = "& ([string]::join('', ( (" + ','.join(map(str, ascii_values)) + ") |%{ ( [char][int] $_)})))"
    return new_value

cmdlet = 'Hidden'
print(generate_cmdlet(cmdlet))
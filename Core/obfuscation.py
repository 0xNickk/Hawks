import base64
import re
from uuid import uuid4


def variable_rename(payload):

    used_var_names = []

    find_variable = re.findall('\$[a-zA-Z0-9_]*[\ ]{0,}=', payload)
    find_variable.sort(key=len)
    find_variable.reverse()

    for var in find_variable:
        var = var.strip("\n \r\t=")

        while True:

            new_var_name = uuid4().hex

            if (new_var_name in used_var_names) or (re.search(new_var_name, payload)):
                continue

            else:
                used_var_names.append(new_var_name)
                break

        payload = payload.replace(var, f'${new_var_name}')

    return payload


def find_cmdlets(payload):

    find_cmdlets = r'[A-Z][a-zA-Z]*-[A-Za-z]*'
    cmdlets = re.findall(find_cmdlets, payload)

    return cmdlets


def cmdlet_to_ascii(payload):

    cmdlets = find_cmdlets(payload)

    for token in cmdlets:
        ascii_token_value = [ord(c) for c in token]
        obfuscated_token = "&([string]::join('',((" + ','.join(map(str, ascii_token_value)) + ")|%{([char][int]$_)})))"
        payload = payload.replace(token, obfuscated_token)

    return payload


def cmdlet_concatenation(payload):

    cmdlets = find_cmdlets(payload)

    for token in cmdlets:
        parts = [f"'{token[i:i + len(token) // 4]}'" for i in range(0, len(token), len(token) // 4)]
        obfuscated_token = ".(" + " + ".join(parts) + ")"
        payload = payload.replace(token, obfuscated_token)

    return payload


def find_methods(payload):

    find_method = r'\.[A-Z][a-zA-Z0-9_]*'
    methods = re.findall(find_method, payload)
    methods = [method[1:] for method in methods]

    return methods


def method_concatenation(payload):

    invalid_methods = []
    valid_methods = []

    find_namespace = r'(?<=\s|\()[A-Z][a-zA-Z0-9_.]*'
    namespaces = re.findall(find_namespace, payload)

    namespaces = [word.split('.') for word in namespaces if word.count('.') >= 2]

    for namespace in namespaces:
        invalid_methods.extend(namespace)

    methods = find_methods(payload)

    for method in methods:
        if method not in invalid_methods:
            valid_methods.append(method)

    for method in valid_methods:
        step = len(method) // 4 if len(method) >= 4 else 1
        parts = [f"'{method[i:i + step]}'" for i in range(0, len(method), step)]
        obfuscated_method = "(" + "+".join(parts) + ")"
        payload = payload.replace(method, obfuscated_method)

    return payload


def find_strings(payload):

    find_string = r"'(.*?)'"
    strings = re.findall(find_string, payload)

    return strings


def string_concatenation(payload):

    strings = find_strings(payload)

    for string in strings:
        step = len(string) // 4 if len(string) >= 4 else 1
        parts = [f"'{string[i:i + step]}'" for i in range(0, len(string), step)]
        concatenated_string = "(" + "+".join(parts) + ")"
        payload = payload.replace(f"'{string}'", concatenated_string)

    return payload


def string_to_ascii(payload):

    string_chars = []

    strings = find_strings(payload)

    for string in strings:
        string = ''.join(string)
        string_chars = []

        for orig_char in string:
            string_chars.append(f"$([char]{ord(orig_char)})")

        ascii_string = '+'.join(string_chars).strip()
        payload = payload.replace(f"'{string}'", f"({ascii_string})")

    return payload


def base64_encode(payload):

    payload_encoded = base64.b64encode(payload.encode("utf-16le")).decode()
    return payload_encoded


def ascii_encode(payload):

    encoded_payload = ', '.join(str(ord(c)) for c in payload)
    encoded_payload = "[cHAr[]](" + encoded_payload + ")" + "-JOiN '' |INvOkE-EXPreSSIoN"
    return encoded_payload


def binary_encode(payload):

    encoded_payload = [str(bin(ord(c)))[2:] for c in payload]
    encoded_payload = "[STRInG]::jOIn('' , ('" + ','.join(
        encoded_payload) + "'-spLIT '@'-SpLIt ','-spLIt'Y'-sPliT 'W' -SPLIT '~' -spLiT'R'-SPliT 'N'-sPLIT 'E' -spLIt 'p'-SPLIt 'l'| forEaCH-OBjEcT{( [CONVert]::toInt16(($_.tOsTrinG() ),2 )-as [chaR])} )) | . ( $verbOSePReFeReNCE.tOSTRIng()[1,3]+'x'-joiN'')"
    return encoded_payload


def octal_encode(payload):

    encoded_payload = [str(oct(ord(c)))[2:] for c in payload]
    encoded_payload = "&( $enV:comSPeC[4,24,25]-join'') ( [strInG]::joiN( '',( ( " + ' ,'.join(
        encoded_payload) + " ) | FOReach-oBjEcT{ ( [CONVeRT]::TOinT16( ($_.ToSTRIng() ), 8)-AS [ChAR])})))"
    return encoded_payload

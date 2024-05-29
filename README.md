# Hawks 
![python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![powershell](https://img.shields.io/badge/powershell-5391FE?style=for-the-badge&logo=powershell&logoColor=white)
![kaliLinux](https://img.shields.io/badge/Kali_Linux-557C94?style=for-the-badge&logo=kali-linux&logoColor=white)


## Description
Hawks is a simple C2 framework based on python which can handle multiple powershell agents through TCP and executed additional features. It support obfuscated payload generation capable of bypassing Windows Defender and almost every AV. 

Hawks is designed to be simple and easy to use, providing a solid and customizable usage configuration. 

> [!WARNING]
> This tool is created for educational purposes only. Using it for attacking targets without prior explicit consent is illegal. The author is not responsible for any misuse or damage caused by this tool.


## Features 

Hawks framework main features include:

- Download and upload files (via **HTTP**)
- Support **SSL** encryption 
- Accept external **TCP** connections (via **ngrok**)
- Auto-completion of commands
- Multiple agents control
- Command history
- Payload generation (only PowerShell for now)
- Modules customization
- Various and customizable payload obfuscation techniques (**AMSI** bypass)


## Requirements

Hawks framework has been tested on the following operating systems:

- Kali Linux (2024.1)
- Parrot Security (6.0)


## Installation 

Clone the repository:
```bash
git clone  https://github.com/0xNickk/Hawks.git
```

Install python dependencies:
```bash
cd ./Hawks
pip install -r requirements.txt
```

## Preview
![preview](https://github.com/0xNickk/Hawks/assets/96845504/e3e6c604-3c0f-4e32-abef-9a37ac6a8c93)

## Programmed features

- [ ] Add new listeners 
- [ ] Add new payloads 
- [ ] Persistent agent 
- [ ] Add more Windows evasion techniques

> [!IMPORTANT]
> This project is still under development and I am a beginner. So feel free to give me any type of feedback and advice. 






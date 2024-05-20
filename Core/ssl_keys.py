from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from .settings import SSLSettings
import datetime

def generate_keys():

    key_file = SSLSettings.ssl_dir + SSLSettings.key_file
    cert_file = SSLSettings.ssl_dir + SSLSettings.cert_file

    private_key = rsa.generate_private_key(
        
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
        
    )

    public_key = private_key.public_key()

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([
        
        x509.NameAttribute(NameOID.COMMON_NAME, u'localhost')
        
    ]))

    builder = builder.issuer_name(x509.Name([
        
        x509.NameAttribute(NameOID.COMMON_NAME, u'localhost')
        
    ]))

    builder = builder.not_valid_before(datetime.datetime.today() - datetime.timedelta(days=1))
    builder = builder.not_valid_after(datetime.datetime.today() + datetime.timedelta(days=365))
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)

    builder = builder.add_extension(
        
        x509.SubjectAlternativeName([x509.DNSName(u'localhost')]),
        critical=False
        
    )

    certificate = builder.sign(
        
        private_key=private_key, 
        algorithm=hashes.SHA256(),
        backend=default_backend()
        
    )

    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
            
        ))
        
    with open(cert_file, "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

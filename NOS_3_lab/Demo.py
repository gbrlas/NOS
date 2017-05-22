import os
import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import MD5

# AES

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))

# generate a random secret key
secret = os.urandom(16)
print ("Secret key:", str(secret))
# generate the initialization vector
IV = os.urandom(16)

# create a cipher object using the random secret
cipher = AES.new(secret, AES.MODE_CFB, IV)

# encode a string
encoded = EncodeAES(cipher, 'password')
print ('Encrypted string:', encoded)

# create a cipher object using the random secret
cipher = AES.new(secret, AES.MODE_CFB, IV)

# decode the encoded string
decoded = DecodeAES(cipher, encoded)
print ('Decrypted string:', decoded)



# RSA

# Use a larger key length in practice...
KEY_LENGTH = 1024  # Key size (in bits)
random_gen = Random.new().read

keypair = RSA.generate(KEY_LENGTH, random_gen)

# Public key export for exchange between parties...
publicKey = keypair.publickey()

# Plain text messages...
print("AES key:", secret)
message = secret

# Generate digital signatures using private keys...
messageHash = MD5.new(message).digest()

signature = keypair.sign(messageHash, '')

# Encrypt messages using the other party's public key...
encryptedMessage = publicKey.encrypt(message, 32)
print("Encrypted AES key: ", encryptedMessage)

# Decrypt messages using own private keys...
decryptedMessage = keypair.decrypt(encryptedMessage)

# Signature validation and console output...
hashDecrypted = MD5.new(decryptedMessage).digest()
if publicKey.verify(hashDecrypted, signature):
    print("Decrypted AES key:", decryptedMessage)



# DIGITALNA OMOTNICA

# KRIPTIRANJE
P = "Ovo je moja poruka"
print("Pocetna poruka: ", P, "\n")

secret = os.urandom(16)
IV = os.urandom(16)

cipher = AES.new(secret, AES.MODE_CFB, IV)

C1 = EncodeAES(cipher, P)

keypair = RSA.generate(KEY_LENGTH, random_gen)
publicKey = keypair.publickey()

C2 = publicKey.encrypt(secret, 32)

M = (C1, C2)

print("Sadrzaj omotnice M:\n", M, "\n")

# DEKRIPTIRANJE

key = keypair.decrypt(C2)

cipher = AES.new(key, AES.MODE_CFB, IV)

P = DecodeAES(cipher, C1)
print ('Dekriptirana poruka:', P.decode('ascii'))


# DIGITALNI POTPIS
import hashlib
m = hashlib.md5()

m.update(str(C1).encode('utf-8'))
m.update(str(C2).encode('utf-8'))

H = m.digest()

print(H)

# DIGITALNI PECAT

keypair1 = RSA.generate(KEY_LENGTH, random_gen)
publicKey = keypair.publickey()

C3 =  publicKey.encrypt(H, 32)

H = keypair.decrypt(C3)

print (H)
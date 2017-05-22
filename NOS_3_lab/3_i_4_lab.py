import os
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import MD5

# WRITING TO FILES
def savePrivateKey(private, size):
    with open("privateKey.txt", "w") as f:
        f.write("---BEGIN OS2 CRYPTO DATA---\n")
        f.write("\nDescription:\n")
        f.write("\tPrivate key\n\n")
        f.write("Method:\n")
        f.write("\tRSA\n\n")
        f.write("Key length:\n")
        f.write("\t0{0:x}".format(size)+"\n")
        f.write("\nPrivate key: \n")
        f.write(str(private.exportKey())[2:-1])
        f.write("\n")
        f.write("\n---END OS2 CRYPTO DATA---")


def savePublicKey(public, size):
    with open("publicKey.txt", "w") as f:
        f.write("---BEGIN OS2 CRYPTO DATA---\n")
        f.write("\nDescription:\n")
        f.write("\tPublic key\n\n")
        f.write("Method:\n")
        f.write("\tRSA\n\n")
        f.write("Key length:\n")
        f.write("\t0{0:x}".format(size)+"\n")
        f.write("\nPublic key: \n")
        f.write(str(public.exportKey())[2:-1])
        f.write("\n")
        f.write("\n---END OS2 CRYPTO DATA---")


def saveAESKey(key):
    with open("aesKey.txt", "w") as f:
        f.write("---BEGIN OS2 CRYPTO DATA---\n")
        f.write("\nDescription:\n")
        f.write("\tSecret key\n\n")
        f.write("Method:\n")
        f.write("\tAES\n")
        f.write("\nSecret key: \n")
        f.write(str(key))
        f.write("\n")
        f.write("\n---END OS2 CRYPTO DATA---")

def printEnvelope(data, encryptedKey, aes_size, rsa_size):
    with open("envelope.txt", "w") as f:
        f.write("---BEGIN OS2 CRYPTO DATA---\n")
        f.write("\nDescription:\n")
        f.write("\tEnvelope\n\n")
        f.write("Method:\n")
        f.write("\tAES\n")
        f.write("\tRSA\n")
        f.write("Key length:\n")
        f.write("\t0{0:x}".format(aes_size) + "\n")
        f.write("\t0{0:x}".format(rsa_size) + "\n")
        f.write("\nEnvelope data: \n")
        f.write(str(data))
        f.write("\n")
        f.write("\nEnvelope crypt key: \n")
        f.write(str(encryptedKey)[2:-2])
        f.write("\n")
        f.write("\n---END OS2 CRYPTO DATA---")


def printSignature(digest, sha_size, rsa_size):
    with open("signature.txt", "w") as f:
        f.write("---BEGIN OS2 CRYPTO DATA---\n")
        f.write("\nDescription:\n")
        f.write("\tSignature\n\n")
        f.write("Method:\n")
        f.write("\tSHA-1\n")
        f.write("\tRSA\n")
        f.write("\nKey length:\n")
        f.write("\t0{0:x}".format(sha_size) + "\n")
        f.write("\t0{0:x}".format(rsa_size) + "\n")
        f.write("\nSignature: \n")
        f.write(str(digest))
        f.write("\n")
        f.write("\n---END OS2 CRYPTO DATA---")

# AES
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))

# generate a random secret key and initialization vector
secret = os.urandom(16)
IV = os.urandom(16)
print ("Secret key:", str(secret)[2:-1])
saveAESKey(secret)

cipher = AES.new(secret, AES.MODE_CFB, IV)

encoded = EncodeAES(cipher, 'test string')
print ('Encrypted string:', str(encoded)[2:-1])

cipher = AES.new(secret, AES.MODE_CFB, IV)

decoded = DecodeAES(cipher, encoded)
print ('Decrypted string:', str(decoded)[2:-1])


# RSA

KEY_LENGTH = 1024
random_gen = Random.new().read

keypair = RSA.generate(KEY_LENGTH, random_gen)

publicKey = keypair.publickey()
savePublicKey(publicKey, 1024)
savePrivateKey(keypair, 1024)

print("AES key:", str(secret)[2:-1], "\n")
message = secret

messageHash = MD5.new(message).digest()

signature = keypair.sign(messageHash, '')

encryptedMessage = publicKey.encrypt(message, 32)
print ("Encrypted AES key: ", str(encryptedMessage)[3:-3], "\n")

decryptedMessage = keypair.decrypt(encryptedMessage)

# Signature validation
decryptedHash = MD5.new(decryptedMessage).digest()

if publicKey.verify(decryptedHash, signature):
    print ("Decrypted AES key:", str(decryptedMessage)[2:-1], "\n")


# DIGITALNA OMOTNICA

# KRIPTIRANJE
P = "Ovo je moja poruka"
print("Pocetna poruka: ", P, "\n")

AES_BLOCK_SIZE = 16

secret = os.urandom(AES_BLOCK_SIZE)
IV = os.urandom(AES_BLOCK_SIZE)

cipher = AES.new(secret, AES.MODE_CFB, IV)

C1 = EncodeAES(cipher, P)

keypair = RSA.generate(KEY_LENGTH, random_gen)
publicKey = keypair.publickey()

C2 = publicKey.encrypt(secret, 32)

M = (C1, C2)

print("Sadrzaj omotnice M:\n", M, "\n")

printEnvelope(C1, C2, 128, 1024)

# DEKRIPTIRANJE

key = keypair.decrypt(C2)

cipher = AES.new(key, AES.MODE_CFB, IV)

P = DecodeAES(cipher, C1)
print ('Dekriptirana poruka:', P.decode('ascii'))


# DIGITALNI POTPIS

m = hashlib.md5()

m.update(str(C1).encode('utf-8'))
m.update(str(C2).encode('utf-8'))

H = m.digest()
hexdigest = m.hexdigest()

printSignature(hexdigest, 160, 1024)

print("Digest:", str(H)[2:-1])
print("Hex digest:", hexdigest)


# DIGITALNI PECAT

keypair = RSA.generate(KEY_LENGTH, random_gen)
publicKey = keypair.publickey()
secret = os.urandom(AES_BLOCK_SIZE)
IV = os.urandom(16)

cipher = AES.new(secret, AES.MODE_CFB, IV)

C1 = EncodeAES(cipher, P)
C3 =  publicKey.encrypt(H, 32)
C2 = publicKey.encrypt(secret, 32)

M = (C1, C2, C3)

print("M(C1, C2, C3):", M, "\n")

K = keypair.decrypt(C2)
cipher = AES.new(K, AES.MODE_CFB, IV)
P = DecodeAES(cipher, C1)
S = keypair.decrypt(C3)

print ("K=", str(K)[2:-1])
print ("P=", str(P)[2:-1])
print ("S=", str(S)[2:-1])


# SHA-1 IMPLEMENTATION

"""
    Razbija poruke u komade od n bitova.
    """
def chunks(array, n):
    return [array[i:i+n] for i in range(0, len(array), n)]

"""
    Rotacija dobivenog niza u lijevo za n bitova.
    """
def rotate_left(word, n):
    return ((word << n) | (word >> (32 - n))) & 0xffffffff

def sha1(data):
    bytes = ""
    
    # INICIJALIZACIJA VARIJABLE
    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0
    
    # PRED-OBRADA
    
    # pretvaranje ulaznog stringa u 8-bitni zapis
    for n in range(len(data)):
        bytes += '{0:08b}'.format(ord(data[n]))
    
    # dodavanje 1 na kraj poruke
    bits = bytes + "1"

    paddedBits = bits
    
    # dodavanje k 0 sve dok rezultirajuca poruke bude kongruent 448 (mod 512)
    while len(paddedBits) % 512 != 448:
        paddedBits += "0"

    # dodaj duljinu pocetnog niza kao 64-bitni big-endidan cijeli broj
    paddedBits += '{0:064b}'.format(len(bits) - 1)
    
    # PODJELA NA DIJELOVE I OBRADA
    for c in chunks(paddedBits, 512):
        words = chunks(c, 32)
        w = [0]*80
        
        for n in range(0, 16):
            w[n] = int(words[n], 2)
        
        for i in range(16, 80):
            w[i] = rotate_left((w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16]), 1)
        
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        
        for i in range(0, 80):
            if 0 <= i <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= i <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= i <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            elif 60 <= i <= 79:
                f = b ^ c ^ d
                k = 0xCA62C1D6
            
            temp = rotate_left(a, 5) + f + e + k + w[i] & 0xffffffff
            
            e = d
            d = c
            c = rotate_left(b, 30)
            b = a
            a = temp

        h0 = h0 + a & 0xffffffff
        h1 = h1 + b & 0xffffffff
        h2 = h2 + c & 0xffffffff
        h3 = h3 + d & 0xffffffff
        h4 = h4 + e & 0xffffffff

    return '%08x%08x%08x%08x%08x' % (h0, h1, h2, h3, h4)


m = hashlib.sha1()
m.update("ovo je test string".encode('utf-8'))
print(m.hexdigest())
print(sha1("ovo je test string"))

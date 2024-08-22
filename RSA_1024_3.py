#NOT FOR COMMERCIAL USE - IF YOU BOUGHT THIS YOU GOT RIPPED OFF
# RSA_1024_3.py
# V 1.0.0 2024-08-21 by MIBonk

from Crypto.PublicKey import RSA

# Generiere ein RSA-1024-Schlüsselpaar mit einem öffentlichen Exponenten von 3
key = RSA.generate(1024, e=3)

# Extrahiere den Modulus und den öffentlichen Exponenten
n = key.n
e = key.e

# Zeige den Modulus und den öffentlichen Exponenten in Hexadezimalform an
modulus_hex = hex(n)[2:]  # Entferne das '0x' Präfix
exponent_hex = hex(e)[2:]

# Modulus (in Hex, 128 Bytes oder 256 Zeichen)
print(f"\nModulus (Hex): {modulus_hex.upper()}")

# Öffentlicher Exponent (in Hex)
print(f"\nÖffentlicher Exponent (Hex): {exponent_hex.upper()}")

# Extrahiere den privaten Schlüssel (d) und zeige ihn in Hexadezimalform an
d = key.d
private_exponent_hex = hex(d)[2:]

print(f"\nPrivater Exponent (Hex): {private_exponent_hex.upper()}")

# Speichere die Daten in einer Binärdatei
with open("rsa_key.bin", "wb") as bin_file:
    # Konvertiere die Hexadezimal-Darstellung in Bytes und schreibe sie in die Datei
    bin_file.write(bytes.fromhex(private_exponent_hex.upper()))
    bin_file.write(bytes.fromhex(modulus_hex.upper()))

print("\nDer RSA-Schlüssel wurde in 'rsa_key.bin' gespeichert.")

input("\nPress Enter to continue...")


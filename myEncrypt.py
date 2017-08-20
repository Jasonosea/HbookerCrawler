from Cryptodome.PublicKey import RSA

def encrypt(chapter_content, encryt_keys, chapter_access_key):
    k = []
    k.append(encryt_keys[chapter_access_key[0]])
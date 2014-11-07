import base64
import urllib
from Crypto.Cipher import AES
from taskstopipeline.settings import BLOCK_SIZE, CRYPTO_SALT, PADDING


def truncate(string, length):
    return string[:length] + '...' if len(string) > length else string


def user_id_encoder(decoded_uid):
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    cipher = AES.new(CRYPTO_SALT)
    encode_aes = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    return urllib.quote_plus(encode_aes(cipher, decoded_uid))


def user_id_decoder(encoded_uid):
    cipher = AES.new(CRYPTO_SALT)
    decode_aes = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    return decode_aes(cipher, urllib.unquote_plus(encoded_uid))



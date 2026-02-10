import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# 1. Load Environment Variables HERE
load_dotenv()

# 2. Get the Key (Logic moves here)
key_string = os.getenv("SECRET_KEY")

if key_string:
    SECRET_KEY = key_string.encode()
else:
    # Your Dev Fallback
    SECRET_KEY = b'hRNA6q5E4YLKXBTptX1w_iLTQeStPI7ilkFYJmUmddk='

# 3. Create the Cipher HERE
cipher = Fernet(SECRET_KEY)

# 4. The Functions
def encrypt_text(text):
    if not text: return "None"
    try:
        return cipher.encrypt(text.encode()).decode()
    except Exception as e:
        return "None"

def decrypt_text(encrypted_text):
    if not encrypted_text or encrypted_text == "None": return "None"
    try:
        return cipher.decrypt(encrypted_text.encode()).decode()
    except:
        return encrypted_text

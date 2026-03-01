import socket
import json
import base64
import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

# --- CONFIGURATION ---
HOST = '127.0.0.1'  # Server's IP address
PORT = 65432
KEM_ALG = "Kyber512 (Simulated PQC)"

print(f"[*] Starting PQC Secure Chat Client to {HOST}:{PORT}")

def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("[*] Connecting to Server...")
            s.connect((HOST, PORT))
            print("[+] Connected!")
            
            # --- 1. RECEIVE PUBLIC KEY FROM SERVER ---
            server_public_key_pem = s.recv(4096)
            server_public_key = RSA.import_key(server_public_key_pem)
            print(f"[+] Received {KEM_ALG} Public Key ({len(server_public_key_pem)} bytes)")
            
            # --- 2. ENCAPSULATE SHARED SECRET ---
            print(f"[*] Encapsulating shared AES key against Server's Public Key...")
            
            # Simulated KEM: Generate 256-bit AES key and encrypt it with the Server's Public Key
            aes_key = get_random_bytes(32) # 256-bit AES Key
            cipher_rsa = PKCS1_OAEP.new(server_public_key)
            ciphertext = cipher_rsa.encrypt(aes_key)
            
            print(f"[+] Encapsulated Secret AES-256 Key: {aes_key[:8].hex()}... (256-bit)")
            
            # --- 3. SEND CIPHERTEXT TO SERVER ---
            print("[*] Sending Ciphertext to Server...")
            s.sendall(ciphertext)
            print("-" * 50)
            print(f"      SECURE {KEM_ALG} CHANNEL ESTABLISHED      ")
            print("-" * 50)
            print("Type a message and press Enter (or type 'exit' to quit):")
            
            # --- 4. SEND ENCRYPTED MESSAGES ---
            while True:
                msg = input("\nYou: ")
                if msg.lower() == 'exit':
                    break
                    
                # Encrypt message with AES-GCM
                cipher = AES.new(aes_key, AES.MODE_GCM)
                ciphertext_msg, tag = cipher.encrypt_and_digest(msg.encode('utf-8'))
                
                # Bundle the ciphertext, MAC tag, and the initialization vector (nonce)
                payload = {
                    "nonce": base64.b64encode(cipher.nonce).decode('utf-8'),
                    "tag": base64.b64encode(tag).decode('utf-8'),
                    "ciphertext": base64.b64encode(ciphertext_msg).decode('utf-8')
                }
                
                s.sendall(json.dumps(payload).encode('utf-8'))
                print("[*] Encrypted & Sent.")

    except Exception as e:
        print(f"[-] Connection Error: {e}")

if __name__ == "__main__":
    main()

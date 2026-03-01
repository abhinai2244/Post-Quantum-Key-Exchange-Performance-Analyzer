import socket
import threading
import json
import base64
import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA

# --- CONFIGURATION ---
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 65432
KEM_ALG = "Kyber512 (Simulated PQC)"

print(f"[*] Starting PQC Secure Chat Server on {HOST}:{PORT}")

# --- 1. GENERATE KEYPAIR (Simulating Kyber KEM) ---
print(f"[*] Generating {KEM_ALG} Keypair...")
server_keypair = RSA.generate(2048)  # Used mathematically as the public/private KEM pair
server_public_key = server_keypair.publickey().export_key()
print(f"[+] Public Key generated ({len(server_public_key)} bytes)")


def handle_client(conn, addr):
    print(f"\n[+] Accepted connection from {addr}")
    
    # --- 2. SEND PUBLIC KEY TO CLIENT ---
    print(f"[*] Sending {KEM_ALG} Public Key to client...")
    conn.sendall(server_public_key)
    
    # --- 3. RECEIVE ENCAPSULATED SECRET FROM CLIENT ---
    print("[*] Waiting for encapsulated AES key from client...")
    ciphertext = conn.recv(1024) 
    print(f"[+] Received Encapsulated ciphertext ({len(ciphertext)} bytes)")
    
    # --- 4. DECAPSULATE TO GET AES KEY ---
    # The client encrypted a random 256-bit AES key with our public key
    cipher_rsa = PKCS1_OAEP.new(server_keypair)
    aes_key = cipher_rsa.decrypt(ciphertext)
    
    print(f"[+] Decapsulated Shared AES-256 Key: {aes_key[:8].hex()}... (256-bit)")
    print("-" * 50)
    print(f"      SECURE {KEM_ALG} CHANNEL ESTABLISHED      ")
    print("-" * 50)
    
    # --- 5. RECEIVE AND DECRYPT MESSAGES ---
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
                
            # Parse the incoming JSON payload (nonce + tag + ciphertext)
            payload = json.loads(data.decode('utf-8'))
            nonce = base64.b64decode(payload['nonce'])
            tag = base64.b64decode(payload['tag'])
            enc_msg = base64.b64decode(payload['ciphertext'])
            
            # Decrypt using AES-GCM
            cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
            decrypted_msg = cipher.decrypt_and_verify(enc_msg, tag)
            
            print(f"\n[Encrypted Traffic Received: {len(data)} bytes]")
            print(f"Client: {decrypted_msg.decode('utf-8')}")
            
        except Exception as e:
            print(f"[-] Connection error: {e}")
            break
            
    print(f"[-] Connection closed by {addr}")
    conn.close()


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print("[*] Listening for incoming connections...")
            
            while True:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
    except KeyboardInterrupt:
        print("\n[*] Server shutting down.")

if __name__ == "__main__":
    main()

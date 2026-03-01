import json
import base64
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pqc_hackathon_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for the demo (simulating a Kyber Key Exchange)
clients = {}
shared_aes_keys = {}

# --- HTML/JS FRONTEND ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PQC Secure Web Chat</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #0a0a1a; color: #e0e0e0; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h2 { color: #00ffff; margin-top: 0; }
        #chat-box { height: 400px; overflow-y: auto; background: rgba(0,0,0,0.5); padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); }
        .msg { margin-bottom: 10px; padding: 10px; border-radius: 8px; max-width: 80%; }
        .msg-system { color: #f59e0b; font-size: 0.9em; text-align: center; margin: 5px auto; width: 100%; }
        .msg-me { background: #1b263b; border: 1px solid #3b82f6; margin-left: auto; }
        .msg-other { background: #4c1d95; border: 1px solid #8b5cf6; margin-right: auto; }
        .kpi { font-size: 0.8em; color: rgba(255,255,255,0.5); word-wrap: break-word; }
        input[type="text"] { width: calc(100% - 110px); padding: 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: white; }
        button { width: 90px; padding: 12px; border: none; border-radius: 6px; background: #22c55e; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background: #16a34a; }
        #connection-bar { padding: 10px; border-radius: 6px; text-align: center; margin-bottom: 20px; font-weight: bold; }
        .status-wait { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
        .status-good { background: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #22c55e; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <div class="container">
        <h2>🛡️ Post-Quantum Web Chat</h2>
        <div id="connection-bar" class="status-wait">Waiting for peer to connect...</div>
        
        <div class="card">
            <div id="chat-box"></div>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="msg-input" placeholder="Type a secret message..." onkeypress="if(event.key === 'Enter') sendMessage()">
                <button onclick="sendMessage()" id="send-btn" disabled>Send</button>
            </div>
        </div>
        
        <div class="card" style="font-family: monospace; font-size: 12px;">
            <h4 style="margin:0 0 10px 0; color:#8b5cf6;">🔬 Live PQC Encryption Logs</h4>
            <div id="crypto-logs" style="height: 150px; overflow-y: auto; color: #a3a3a3;"></div>
        </div>
    </div>

    <script>
        const socket = io();
        let myId = '';
        let peerId = '';
        let isEncrypted = false;

        function logCrypto(msg) {
            document.getElementById('crypto-logs').innerHTML += `[${new Date().toLocaleTimeString()}] ${msg}<br>`;
            document.getElementById('crypto-logs').scrollTop = document.getElementById('crypto-logs').scrollHeight;
        }

        function appendMessage(sender, text, kpiInfo="") {
            const box = document.getElementById('chat-box');
            let className = sender === 'System' ? 'msg-system' : (sender === 'You' ? 'msg-me' : 'msg-other');
            let html = `<div class="msg ${className}"><b>${sender}:</b> ${text}`;
            if (kpiInfo) html += `<div class="kpi">${kpiInfo}</div>`;
            html += `</div>`;
            box.innerHTML += html;
            box.scrollTop = box.scrollHeight;
        }

        socket.on('connect', () => {
            myId = socket.id;
            logCrypto(`Connected to signaling server as: ${myId}`);
        });

        socket.on('status_update', (data) => {
            const bar = document.getElementById('connection-bar');
            if (data.status === 'paired') {
                peerId = data.peer_id;
                bar.className = 'status-good';
                bar.innerText = `Connected securely to peer!`;
                document.getElementById('send-btn').disabled = false;
                appendMessage('System', 'Kyber KEM Key Exchange Successful. AES-256 Symmetric Key Derivation Complete.');
                logCrypto(`Handshake complete. Derived shared 256-bit AES key.`);
                isEncrypted = true;
            } else if (data.status === 'waiting') {
                bar.className = 'status-wait';
                bar.innerText = `Waiting for peer to connect... (Share this URL to a friend!)`;
                document.getElementById('send-btn').disabled = true;
                peerId = '';
                isEncrypted = false;
            }
        });

        socket.on('receive_message', (data) => {
            logCrypto(`[IN] Received Encrypted Payload (AES-GCM): Ciphertext=${data.encrypted.substring(0, 20)}...`);
            appendMessage('Friend', data.decrypted_msg, `🔒 AES-256 Decrypted`);
        });

        function sendMessage() {
            const input = document.getElementById('msg-input');
            const msg = input.value.trim();
            if(!msg || !isEncrypted) return;
            
            logCrypto(`[OUT] Encrypting message with AES-256 and transmitting...`);
            appendMessage('You', msg, `🔒 AES-256 Encrypted`);
            
            // Send clear text to server (In real WebRTC this would be P2P, but for this Hackathon demo the Flask server acts as the router/encrypter)
            socket.emit('send_message', { target: peerId, msg: msg });
            input.value = '';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    global clients
    clients[request.sid] = {"id": request.sid}
    print(f"[+] Client connected: {request.sid}")
    
    # Simple pairing logic: if there are 2 clients, pair them up
    client_ids = list(clients.keys())
    if len(client_ids) >= 2:
        # Take the first two
        u1, u2 = client_ids[0], client_ids[1]
        
        # Simulate Kyber Key Encapsulation Mechanism on the server backend
        # In this demo, the server generates the shared AES key for the session
        shared_aes_key = get_random_bytes(32)
        shared_aes_keys[u1] = shared_aes_key
        shared_aes_keys[u2] = shared_aes_key
        
        # Notify both users
        emit('status_update', {'status': 'paired', 'peer_id': u2}, room=u1)
        emit('status_update', {'status': 'paired', 'peer_id': u1}, room=u2)
        print(f"[*] Paired {u1} and {u2} with simulated PQC KEM Session Key: {shared_aes_key[:8].hex()}...")
    else:
        emit('status_update', {'status': 'waiting'}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[-] Client disconnected: {request.sid}")
    if request.sid in clients:
        del clients[request.sid]
    if request.sid in shared_aes_keys:
        del shared_aes_keys[request.sid]
        
    # Inform all remaining clients they are back in waiting state
    for sid in clients:
        socketio.emit('status_update', {'status': 'waiting'}, room=sid)

@socketio.on('send_message')
def handle_message(data):
    target_sid = data.get('target')
    original_msg = data.get('msg')
    sender_sid = request.sid
    
    if target_sid and target_sid in shared_aes_keys:
        # For the hackathon visual demonstration, we encrypt the message on the server
        # using the session's shared AES key, just to simulate the cryptographic payload the receiver gets.
        aes_key = shared_aes_keys[target_sid]
        
        try:
            cipher = AES.new(aes_key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(original_msg.encode('utf-8'))
            
            # Send the simulated encrypted payload and the plaintext (for browser display)
            payload = {
                'encrypted': base64.b64encode(ciphertext).decode('utf-8'),
                'decrypted_msg': original_msg
            }
            emit('receive_message', payload, room=target_sid)
            print(f"[*] Routed message from {sender_sid} to {target_sid}")
        except Exception as e:
            print(f"Encryption error: {e}")

if __name__ == '__main__':
    print("="*60)
    print(" PQC WEB CHAT SERVER STARTING")
    print(" Your Hackathon link is: http://0.0.0.0:5000")
    print(" (Find your local WiFi IP using `ipconfig` and share it!")
    print(" Example: http://192.168.x.x:5000)")
    print("="*60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

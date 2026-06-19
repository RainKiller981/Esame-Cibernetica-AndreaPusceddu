import socket
import json
import sys

def run():
    # Read the save script
    script_path = r"C:\Users\andre\Intranet\non-existent-or-just-read-it-directly" # Wait, the correct path is:
    script_path = r"C:\Users\andre\.gemini\antigravity-cli\brain\016b5a10-8f21-4ca2-9b5d-0630d3f05179\scratch\save_blend.py"
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()
        
    host = 'localhost'
    port = 9876
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(20.0)
    
    try:
        sock.connect((host, port))
        command = {
            "type": "execute_code",
            "params": {
                "code": code
            }
        }
        sock.sendall(json.dumps(command).encode('utf-8'))
        
        # Receive response
        chunks = []
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                data = b''.join(chunks)
                res = json.loads(data.decode('utf-8'))
                return res
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Error connecting/communicating with Blender: {str(e)}")
        return None
    finally:
        sock.close()

if __name__ == '__main__':
    res = run()
    if res:
        print(json.dumps(res, indent=2))

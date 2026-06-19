import socket
import json

def send_command(command_type, params=None):
    if params is None:
        params = {}
    host = '127.0.0.1'
    port = 9876
    
    payload = {
        "type": command_type,
        "params": params
    }
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        # Send JSON command
        message = json.dumps(payload)
        s.sendall(message.encode('utf-8'))
        
        # Receive response
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        
        s.close()
        return json.loads(response.decode('utf-8'))
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Getting scene info...")
    res = send_command("get_scene_info")
    print(json.dumps(res, indent=2))

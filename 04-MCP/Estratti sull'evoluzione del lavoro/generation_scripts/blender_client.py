import socket
import json
import sys

def send_command(command_type, params=None):
    host = 'localhost'
    port = 9876
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10.0)
    try:
        sock.connect((host, port))
        command = {
            "type": command_type,
            "params": params or {}
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
        print(f"Error: {str(e)}", file=sys.stderr)
        return None
    finally:
        sock.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python blender_client.py <command_type> [params_json]")
        sys.exit(1)
        
    cmd_type = sys.argv[1]
    params = {}
    if len(sys.argv) > 2:
        params = json.loads(sys.argv[2])
        
    result = send_command(cmd_type, params)
    print(json.dumps(result, indent=2))

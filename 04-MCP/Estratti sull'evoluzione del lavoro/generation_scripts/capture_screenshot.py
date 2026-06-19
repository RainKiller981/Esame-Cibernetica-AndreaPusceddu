import socket
import json

def send_command(command_type, params=None):
    if params is None:
        params = {}
    host = '127.0.0.1'
    port = 9876
    payload = {"type": command_type, "params": params}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(json.dumps(payload).encode('utf-8'))
    response = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        response += chunk
    s.close()
    return json.loads(response.decode('utf-8'))

if __name__ == "__main__":
    filepath = r"C:\Users\andre\Desktop\xenomorph_and_egg.png"
    print(f"Capturing viewport screenshot and saving to {filepath}...")
    res = send_command("get_viewport_screenshot", {
        "max_size": 1200,
        "filepath": filepath,
        "format": "png"
    })
    print(json.dumps(res, indent=2))

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

code = """
import bpy
mat = bpy.data.materials.get("XenomorphSkin")
mat_info = {}
if mat:
    mat_info["use_nodes"] = mat.use_nodes
    if mat.use_nodes:
        nodes = []
        for n in mat.node_tree.nodes:
            nodes.append({
                "name": n.name,
                "type": n.type,
                "label": n.label
            })
        mat_info["nodes"] = nodes
else:
    mat_info["status"] = "not found"
import json
print("MAT_START")
print(json.dumps(mat_info, indent=2))
print("MAT_END")
"""

res = send_command("execute_code", {"code": code})
print(res.get("result", {}).get("stdout", ""))

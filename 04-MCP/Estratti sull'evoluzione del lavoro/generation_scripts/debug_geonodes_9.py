import socket
import json
import sys

def receive_full_response(sock, buffer_size=8192):
    chunks = []
    sock.settimeout(180.0)
    while True:
        try:
            chunk = sock.recv(buffer_size)
            if not chunk:
                if not chunks:
                    raise Exception("Connection closed before receiving any data")
                break
            chunks.append(chunk)
            try:
                data = b''.join(chunks)
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            print("Socket timeout during receive")
            break
        except Exception as e:
            print(f"Error during receive: {e}")
            raise
    if chunks:
        data = b''.join(chunks)
        try:
            json.loads(data.decode('utf-8'))
            return data
        except json.JSONDecodeError:
            raise Exception("Incomplete JSON response received")
    else:
        raise Exception("No data received")

def send_command(sock, command_type, params=None):
    command = {
        "type": command_type,
        "params": params or {}
    }
    sock.sendall(json.dumps(command).encode('utf-8'))
    response_data = receive_full_response(sock)
    response = json.loads(response_data.decode('utf-8'))
    if response.get("status") == "error":
        raise Exception(response.get("message", "Unknown error from Blender"))
    return response.get("result", {})

def main():
    host = "localhost"
    port = 9876
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)

    try:
        debug_code = """import bpy
# Let's inspect the actual execution in generate_nostromo_props
try:
    # 1. Base
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=3, size=15)
    base = bpy.context.active_object
    base.name = "Base_Corridor"
    
    # 2. Prop
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.4, depth=1.5, location=(0, 0, 5))
    prop = bpy.context.active_object
    prop.name = "Prop_Terminal"
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 3. Create nodes
    modifier = base.modifiers.new(name="Geo_Instancer", type='NODES')
    node_tree = bpy.data.node_groups.new(name="Instancer_Tree_9", type='GeometryNodeTree')
    modifier.node_group = node_tree
    
    # Sockets
    sock_in = node_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    sock_out = node_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    nodes = node_tree.nodes
    links = node_tree.links
    
    node_in = nodes.new('NodeGroupInput')
    node_out = nodes.new('NodeGroupOutput')
    node_inst = nodes.new('GeometryNodeInstanceOnPoints')
    node_info = nodes.new('GeometryNodeObjectInfo')
    
    node_info.inputs[0].default_value = prop
    node_info.transform_space = 'RELATIVE'
    
    print("Testing connection logic:")
    
    # Try connecting node_in to node_inst Points
    print("Connecting Points...")
    links.new(node_in.outputs[0], node_inst.inputs['Points'])
    
    # Try connecting node_info to node_inst Instance
    print("Connecting Instance...")
    links.new(node_info.outputs['Geometry'], node_inst.inputs['Instance'])
    
    # Try connecting node_inst to node_out
    print("Connecting Output...")
    links.new(node_inst.outputs['Geometry'], node_out.inputs[0])
    
    print("All links succeeded!")
except Exception as e:
    print("Exception in node construction:", e)
"""
        res = send_command(sock, "execute_code", {"code": debug_code})
        print(res.get('result'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()

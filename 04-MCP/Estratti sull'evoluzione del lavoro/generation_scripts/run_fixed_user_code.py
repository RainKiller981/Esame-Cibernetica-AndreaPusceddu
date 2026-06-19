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
    print(f"Connecting to Blender...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        print("Connected!")
    except Exception as e:
        print(f"Failed to connect to Blender: {e}")
        sys.exit(1)

    try:
        print("Running fixed Geometry Nodes script...")
        
        fixed_code = """import bpy
import math
import mathutils

def clean_scene():
    \"\"\"Pulizia sicura per l'esecuzione headless.\"\"\"
    for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes): bpy.data.meshes.remove(mesh, do_unlink=True)
    for mat in list(bpy.data.materials): bpy.data.materials.remove(mat, do_unlink=True)
    for node_group in list(bpy.data.node_groups): bpy.data.node_groups.remove(node_group, do_unlink=True)

def create_geometry_nodes_instancer(base_obj, instance_obj):
    \"\"\"Costruisce un albero di Geometry Nodes per distribuire istanze.\"\"\"
    modifier = base_obj.modifiers.new(name="Geo_Instancer", type='NODES')
    
    # Inizializza il Node Group
    node_tree = bpy.data.node_groups.new(name="Instancer_Tree", type='GeometryNodeTree')
    modifier.node_group = node_tree
    
    # Compatibilità API: Blender 4.0+ usa 'interface', Blender 3.x usa 'inputs/outputs'
    if hasattr(node_tree, "interface"): 
        sock_in = node_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        sock_out = node_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        in_id = sock_in.identifier
        out_id = sock_out.identifier
    else:
        node_tree.inputs.new('NodeSocketGeometry', "Geometry")
        node_tree.outputs.new('NodeSocketGeometry', "Geometry")
        in_id = "Geometry"
        out_id = "Geometry"
        
    nodes = node_tree.nodes
    links = node_tree.links
    
    # Creazione Nodi
    node_in = nodes.new('NodeGroupInput')
    node_out = nodes.new('NodeGroupOutput')
    node_inst = nodes.new('GeometryNodeInstanceOnPoints')
    node_info = nodes.new('GeometryNodeObjectInfo')
    
    # Configurazione e posizionamento nodi
    node_in.location = (-200, 0)
    node_info.location = (-200, -200)
    node_inst.location = (0, 0)
    node_out.location = (200, 0)
    
    # Assegna l'oggetto da istanziare al nodo Object Info
    node_info.inputs[0].default_value = instance_obj
    node_info.transform_space = 'RELATIVE' # Mantiene la scala/rotazione originale del prop
    
    # Connessione logica (Links) con supporto per identificatori dinamici in Blender 4.x/5.1
    # Connettiamo l'output del NodeGroupInput (Points) al nodo InstanceOnPoints
    output_socket = node_in.outputs.get(in_id) or node_in.outputs[0]
    links.new(output_socket, node_inst.inputs['Points'])
    
    # Connettiamo l'output di ObjectInfo (Geometry) al nodo InstanceOnPoints (Instance)
    links.new(node_info.outputs['Geometry'], node_inst.inputs['Instance'])
    
    # Connettiamo l'output di InstanceOnPoints al NodeGroupOutput
    input_socket = node_out.inputs.get(out_id) or node_out.inputs[0]
    links.new(node_inst.outputs['Geometry'], input_socket)
    
    return modifier

def generate_nostromo_props():
    clean_scene()
    
    # 1. Base di distribuzione (es. griglia di un corridoio)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=3, size=15)
    corridor_floor = bpy.context.active_object
    corridor_floor.name = "Base_Corridor"
    
    # 2. Creazione del Prop (es. Terminale o Tubatura)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.4, depth=1.5, location=(0, 0, 5))
    terminal_prop = bpy.context.active_object
    terminal_prop.name = "Prop_Terminal"
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # 3. Applicazione del sistema
    create_geometry_nodes_instancer(corridor_floor, terminal_prop)

generate_nostromo_props()
print("Execution succeeded!")
"""
        res = send_command(sock, "execute_code", {"code": fixed_code})
        print(f"Result: {res.get('result')}")
        
        # Capture viewport screenshot to verify
        print("Capturing viewport screenshot of generated Geometry Nodes setup...")
        target_dir = r"C:\Users\andre\Desktop\Nuova cartella (5)"
        if not os.path.exists(target_dir):
            target_dir = r"C:\Users\andre\OneDrive\Desktop\Nuova cartella (5)"
            os.makedirs(target_dir, exist_ok=True)
        
        screenshot_path = os.path.join(target_dir, "geonodes_test.png")
        screenshot_result = send_command(sock, "get_viewport_screenshot", {
            "max_size": 1024,
            "filepath": screenshot_path,
            "format": "png"
        })
        print(f"Screenshot result: {screenshot_result}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()

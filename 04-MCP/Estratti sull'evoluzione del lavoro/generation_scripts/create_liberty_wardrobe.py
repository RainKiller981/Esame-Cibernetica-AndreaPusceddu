import bpy
import math

# Clean up default Cube if present
if "Cube" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

# Create a dedicated collection
wardrobe_coll = bpy.data.collections.new("Stile_Liberty_Wardrobe")
bpy.context.scene.collection.children.link(wardrobe_coll)

# Set active collection to our new collection
bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Stile_Liberty_Wardrobe"]

# Create beautiful materials
# 1. Elegant Mahogany/Walnut Wood
wood_mat = bpy.data.materials.new(name="Walnut_Wood")
wood_mat.use_nodes = True
nodes = wood_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    # Warm dark reddish brown
    principled.inputs['Base Color'].default_value = (0.24, 0.12, 0.06, 1.0)
    principled.inputs['Roughness'].default_value = 0.28
    principled.inputs['Specular IOR Level'].default_value = 0.5

# 2. Polished Antique Brass
brass_mat = bpy.data.materials.new(name="Antique_Brass")
brass_mat.use_nodes = True
nodes = brass_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    # Rich gold brass color
    principled.inputs['Base Color'].default_value = (0.78, 0.58, 0.18, 1.0)
    principled.inputs['Metallic'].default_value = 1.0
    principled.inputs['Roughness'].default_value = 0.22

# Helper to apply material
def apply_material(obj, mat):
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

# Cabinet Dimensions
w_width = 1.6
w_depth = 0.6
w_height = 2.2
base_h = 0.15

# 1. MAIN CABINET BODY
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, w_height/2 + base_h))
body = bpy.context.active_object
body.name = "Wardrobe_Body"
body.scale = (w_width, w_depth, w_height)
bpy.ops.object.transform_apply(scale=True)
apply_material(body, wood_mat)

# Add bevel modifier for realistic edges
bevel_body = body.modifiers.new(name="Bevel", type='BEVEL')
bevel_body.width = 0.015
bevel_body.segments = 3

# 2. TOP CORNICE (Liberty style curved top)
# Organic arch shape on top of the cabinet
bpy.ops.mesh.primitive_cylinder_add(radius=w_width/2, depth=w_depth + 0.04, location=(0, 0, w_height + base_h), rotation=(math.radians(90), 0, 0))
top_arch = bpy.context.active_object
top_arch.name = "Wardrobe_Top_Arch"
top_arch.scale = (1.0, 1.0, 0.25)  # Flattened arch for elegant flow
bpy.ops.object.transform_apply(scale=True)
apply_material(top_arch, wood_mat)

bevel_arch = top_arch.modifiers.new(name="Bevel", type='BEVEL')
bevel_arch.width = 0.01
bevel_arch.segments = 3

# Decorative top shield (carved central motif)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.2, radius2=0.0, depth=0.1, location=(0, w_depth/2 + 0.01, w_height + base_h + 0.18), rotation=(math.radians(45), 0, 0))
motif = bpy.context.active_object
motif.name = "Top_Organic_Motif"
motif.scale = (1.0, 0.2, 1.5)
bpy.ops.object.transform_apply(scale=True)
apply_material(motif, wood_mat)

# 3. BASE / FOOT BOARD
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, base_h))
base_trim = bpy.context.active_object
base_trim.name = "Wardrobe_Base"
base_trim.scale = (w_width + 0.06, w_depth + 0.06, 0.12)
bpy.ops.object.transform_apply(scale=True)
apply_material(base_trim, wood_mat)

bevel_base = base_trim.modifiers.new(name="Bevel", type='BEVEL')
bevel_base.width = 0.008
bevel_base.segments = 3

# 4. ELEGANT SHORT LEGS (Cabriole feet)
leg_positions = [
    (w_width/2 - 0.06, w_depth/2 - 0.06),
    (-w_width/2 + 0.06, w_depth/2 - 0.06),
    (w_width/2 - 0.06, -w_depth/2 + 0.06),
    (-w_width/2 + 0.06, -w_depth/2 + 0.06)
]

for i, (lx, ly) in enumerate(leg_positions):
    # Elegant tapered cones for cabriole legs
    bpy.ops.mesh.primitive_cone_add(radius1=0.05, radius2=0.03, depth=0.1, location=(lx, ly, 0.05))
    leg = bpy.context.active_object
    leg.name = f"Wardrobe_Leg_{i+1}"
    apply_material(leg, wood_mat)

# 5. DOUBLE DOORS
door_w = w_width / 2 - 0.015
door_h = w_height - 0.08
door_d = 0.03

# Left Door
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-door_w/2 - 0.005, w_depth/2 + door_d/2, w_height/2 + base_h))
left_door = bpy.context.active_object
left_door.name = "Door_Left"
left_door.scale = (door_w, door_d, door_h)
bpy.ops.object.transform_apply(scale=True)
apply_material(left_door, wood_mat)
left_door.modifiers.new(name="Bevel", type='BEVEL').width = 0.004

# Left Door panel insert (Classic paneling)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-door_w/2 - 0.005, w_depth/2 + door_d, w_height/2 + base_h))
left_panel = bpy.context.active_object
left_panel.name = "Door_Left_Panel"
left_panel.scale = (door_w - 0.14, 0.01, door_h - 0.18)
bpy.ops.object.transform_apply(scale=True)
apply_material(left_panel, wood_mat)
left_panel.modifiers.new(name="Bevel", type='BEVEL').width = 0.003

# Right Door
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(door_w/2 + 0.005, w_depth/2 + door_d/2, w_height/2 + base_h))
right_door = bpy.context.active_object
right_door.name = "Door_Right"
right_door.scale = (door_w, door_d, door_h)
bpy.ops.object.transform_apply(scale=True)
apply_material(right_door, wood_mat)
right_door.modifiers.new(name="Bevel", type='BEVEL').width = 0.004

# Right Door panel insert
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(door_w/2 + 0.005, w_depth/2 + door_d, w_height/2 + base_h))
right_panel = bpy.context.active_object
right_panel.name = "Door_Right_Panel"
right_panel.scale = (door_w - 0.14, 0.01, door_h - 0.18)
bpy.ops.object.transform_apply(scale=True)
apply_material(right_panel, wood_mat)
right_panel.modifiers.new(name="Bevel", type='BEVEL').width = 0.003

# 6. ORGANIC ART NOUVEAU (LIBERTY) BRASS HANDLES
def create_liberty_handle(name, x_pos, y_pos, z_pos, mirror=False):
    # We use a Bezier curve to generate the flowing organic shape of Art Nouveau handles
    curve_data = bpy.data.curves.new(name=f"Handle_Curve_{name}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = 0.012
    curve_data.bevel_resolution = 4
    
    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(2)  # Generates 3 points total
    
    # Define curving points (resembles a plant stem/creeper)
    p0 = polyline.bezier_points[0]
    p0.co = (0, -0.02, -0.12)
    p0.handle_left = (0, -0.01, -0.15)
    p0.handle_right = (0, -0.04, -0.08)
    
    p1 = polyline.bezier_points[1]
    p1.co = (0, 0.05, 0.0)
    p1.handle_left = (0, 0.04, -0.04)
    p1.handle_right = (0, 0.04, 0.04)
    
    p2 = polyline.bezier_points[2]
    p2.co = (0, -0.02, 0.12)
    p2.handle_left = (0, -0.04, 0.08)
    p2.handle_right = (0, -0.01, 0.15)
    
    handle_obj = bpy.data.objects.new(f"Handle_{name}", curve_data)
    wardrobe_coll.objects.link(handle_obj)
    
    handle_obj.location = (x_pos, y_pos, z_pos)
    if mirror:
        handle_obj.rotation_euler = (0, 0, math.radians(180))
        
    apply_material(handle_obj, brass_mat)
    
    # Elegant mounting plates (floral shape approximation using flat cylinders)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.005, location=(x_pos, y_pos - 0.005, z_pos - 0.12), rotation=(math.radians(90), 0, 0))
    plate_bottom = bpy.context.active_object
    plate_bottom.scale = (0.5, 1.0, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    apply_material(plate_bottom, brass_mat)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.005, location=(x_pos, y_pos - 0.005, z_pos + 0.12), rotation=(math.radians(90), 0, 0))
    plate_top = bpy.context.active_object
    plate_top.scale = (0.5, 1.0, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    apply_material(plate_top, brass_mat)

# Place handles near the center line on both doors
create_liberty_handle("Left", -0.04, w_depth/2 + door_d + 0.005, w_height/2 + base_h, mirror=False)
create_liberty_handle("Right", 0.04, w_depth/2 + door_d + 0.005, w_height/2 + base_h, mirror=True)

# Select all objects of the wardrobe and join or group them?
# Let's keep them in the collection.

# Switch 3D viewports to Material preview so the user can admire the work immediately
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

print("Stile Liberty wardrobe created successfully!")

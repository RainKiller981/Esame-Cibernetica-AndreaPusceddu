import bpy
import math
import mathutils

print("Starting master clean-up and high-poly generation with enlarged jasmine petals...")

# ==========================================
# 1. SCENE CLEANUP (Wipe all mesh and curve objects)
# ==========================================
bpy.ops.object.select_all(action='DESELECT')

for obj in bpy.data.objects:
    if obj.type in ['MESH', 'CURVE']:
        obj.select_set(True)

bpy.ops.object.delete()

# Remove unused materials and collections
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat, do_unlink=True)

old_coll = bpy.data.collections.get("Stile_Liberty_Wardrobe")
if old_coll:
    for obj in old_coll.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old_coll)

for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh, do_unlink=True)
for curve in bpy.data.curves:
    bpy.data.curves.remove(curve, do_unlink=True)

# ==========================================
# 2. CREATING DEDICATED COLLECTION
# ==========================================
wardrobe_coll = bpy.data.collections.new("Stile_Liberty_Wardrobe")
bpy.context.scene.collection.children.link(wardrobe_coll)

bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Stile_Liberty_Wardrobe"]

# ==========================================
# 3. CREATING PHOTOREALISTIC MATERIALS
# ==========================================
# Material 1: Dark Warm Walnut Wood
wood_mat = bpy.data.materials.new(name="Walnut_Wood")
wood_mat.use_nodes = True
nodes = wood_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs['Base Color'].default_value = (0.24, 0.12, 0.06, 1.0)
    principled.inputs['Roughness'].default_value = 0.28
    principled.inputs['Specular IOR Level'].default_value = 0.5

# Material 2: Polished Antique Brass
brass_mat = bpy.data.materials.new(name="Antique_Brass")
brass_mat.use_nodes = True
nodes = brass_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs['Base Color'].default_value = (0.78, 0.58, 0.18, 1.0)
    principled.inputs['Metallic'].default_value = 1.0
    principled.inputs['Roughness'].default_value = 0.22

# Material 3: Realistic Pearly-White Jasmine Petals (with Subsurface Scattering)
petal_mat = bpy.data.materials.new(name="Jasmine_Petal")
petal_mat.use_nodes = True
nodes = petal_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs['Base Color'].default_value = (0.92, 0.90, 0.85, 1.0)
    principled.inputs['Roughness'].default_value = 0.45
    principled.inputs['Specular IOR Level'].default_value = 0.4
    principled.inputs['Subsurface Weight'].default_value = 0.2
    principled.inputs['Subsurface Radius'].default_value = (0.1, 0.1, 0.1)

# Material 4: Waxy Forest-Green Jasmine Leaves (with Subsurface Scattering)
leaf_mat = bpy.data.materials.new(name="Jasmine_Leaf")
leaf_mat.use_nodes = True
nodes = leaf_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs['Base Color'].default_value = (0.08, 0.22, 0.05, 1.0)
    principled.inputs['Roughness'].default_value = 0.32
    principled.inputs['Specular IOR Level'].default_value = 0.5
    principled.inputs['Subsurface Weight'].default_value = 0.15
    principled.inputs['Subsurface Radius'].default_value = (0.1, 0.1, 0.05)

# Material 5: Organic Plant Stem
stem_mat = bpy.data.materials.new(name="Jasmine_Stem")
stem_mat.use_nodes = True
nodes = stem_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs['Base Color'].default_value = (0.12, 0.18, 0.08, 1.0)
    principled.inputs['Roughness'].default_value = 0.5

# Helper to apply material
def apply_material(obj, mat):
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

# Helper to link to collection safely
def register_object(obj):
    if obj.name in bpy.context.scene.collection.objects:
        try:
            bpy.context.scene.collection.objects.unlink(obj)
        except:
            pass
    if obj.name not in wardrobe_coll.objects:
        wardrobe_coll.objects.link(obj)

# Helper to apply professional high-poly bevel + subsurf + smooth shading pipeline
def make_high_poly_hard_surface(obj, bevel_width=0.015, bevel_segments=3, subsurf_levels=2):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    
    bev = obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = bevel_width
    bev.segments = bevel_segments
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(30)
    
    sub = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub.levels = subsurf_levels
    sub.render_levels = subsurf_levels + 1
    
    register_object(obj)

# ==========================================
# 4. WARDROBE BASE STRUCTURE (HIGH POLY)
# ==========================================
w_width = 1.6
w_depth = 0.6
w_height = 2.2
base_h = 0.15

# Main Body
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, w_height/2 + base_h))
body = bpy.context.active_object
body.name = "Wardrobe_Body"
body.scale = (w_width, w_depth, w_height)
bpy.ops.object.transform_apply(scale=True)
apply_material(body, wood_mat)
make_high_poly_hard_surface(body, bevel_width=0.01, bevel_segments=4, subsurf_levels=2)

# Top Cornice Arch (Perfect round arch, 128 vertices)
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=w_width/2, depth=w_depth + 0.04, location=(0, 0, w_height + base_h), rotation=(math.radians(90), 0, 0))
top_arch = bpy.context.active_object
top_arch.name = "Wardrobe_Top_Arch"
top_arch.scale = (1.0, 1.0, 0.25)
bpy.ops.object.transform_apply(scale=True)
apply_material(top_arch, wood_mat)
make_high_poly_hard_surface(top_arch, bevel_width=0.008, bevel_segments=4, subsurf_levels=2)

# Base Trim
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, base_h))
base_trim = bpy.context.active_object
base_trim.name = "Wardrobe_Base"
base_trim.scale = (w_width + 0.06, w_depth + 0.06, 0.12)
bpy.ops.object.transform_apply(scale=True)
apply_material(base_trim, wood_mat)
make_high_poly_hard_surface(base_trim, bevel_width=0.006, bevel_segments=4, subsurf_levels=2)

# 4 Tapered Legs (High-poly 128 vertices, smooth shaded)
leg_positions = [
    (w_width/2 - 0.06, w_depth/2 - 0.06),
    (-w_width/2 + 0.06, w_depth/2 - 0.06),
    (w_width/2 - 0.06, -w_depth/2 + 0.06),
    (-w_width/2 + 0.06, -w_depth/2 + 0.06)
]
for i, (lx, ly) in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cone_add(vertices=128, radius1=0.05, radius2=0.03, depth=0.1, location=(lx, ly, 0.05))
    leg = bpy.context.active_object
    leg.name = f"Wardrobe_Leg_{i+1}"
    apply_material(leg, wood_mat)
    bpy.ops.object.shade_smooth()
    register_object(leg)

# ==========================================
# 5. DOUBLE DOORS & INSET PANELS (HIGH POLY)
# ==========================================
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
make_high_poly_hard_surface(left_door, bevel_width=0.003, bevel_segments=3, subsurf_levels=2)

# Left Panel
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-door_w/2 - 0.005, w_depth/2 + door_d, w_height/2 + base_h))
left_panel = bpy.context.active_object
left_panel.name = "Door_Left_Panel"
left_panel.scale = (door_w - 0.14, 0.01, door_h - 0.18)
bpy.ops.object.transform_apply(scale=True)
apply_material(left_panel, wood_mat)
make_high_poly_hard_surface(left_panel, bevel_width=0.002, bevel_segments=3, subsurf_levels=2)

# Right Door
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(door_w/2 + 0.005, w_depth/2 + door_d/2, w_height/2 + base_h))
right_door = bpy.context.active_object
right_door.name = "Door_Right"
right_door.scale = (door_w, door_d, door_h)
bpy.ops.object.transform_apply(scale=True)
apply_material(right_door, wood_mat)
make_high_poly_hard_surface(right_door, bevel_width=0.003, bevel_segments=3, subsurf_levels=2)

# Right Panel
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(door_w/2 + 0.005, w_depth/2 + door_d, w_height/2 + base_h))
right_panel = bpy.context.active_object
right_panel.name = "Door_Right_Panel"
right_panel.scale = (door_w - 0.14, 0.01, door_h - 0.18)
bpy.ops.object.transform_apply(scale=True)
apply_material(right_panel, wood_mat)
make_high_poly_hard_surface(right_panel, bevel_width=0.002, bevel_segments=3, subsurf_levels=2)

# ==========================================
# 6. BRASS ART NOUVEAU HANDLES
# ==========================================
def create_liberty_handle(name, x_pos, y_pos, z_pos, mirror=False):
    curve_data = bpy.data.curves.new(name=f"Handle_Curve_{name}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.resolution_u = 64
    curve_data.bevel_depth = 0.012
    curve_data.bevel_resolution = 10
    
    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(2)
    
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
    
    # Mounting plates (128 vertices cylinder)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.025, depth=0.005, location=(x_pos, y_pos - 0.005, z_pos - 0.12), rotation=(math.radians(90), 0, 0))
    plate_bottom = bpy.context.active_object
    plate_bottom.scale = (0.5, 1.0, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    apply_material(plate_bottom, brass_mat)
    bpy.ops.object.shade_smooth()
    register_object(plate_bottom)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.025, depth=0.005, location=(x_pos, y_pos - 0.005, z_pos + 0.12), rotation=(math.radians(90), 0, 0))
    plate_top = bpy.context.active_object
    plate_top.scale = (0.5, 1.0, 1.2)
    bpy.ops.object.transform_apply(scale=True)
    apply_material(plate_top, brass_mat)
    bpy.ops.object.shade_smooth()
    register_object(plate_top)

create_liberty_handle("Left", -0.04, w_depth/2 + door_d + 0.005, w_height/2 + base_h, mirror=False)
create_liberty_handle("Right", 0.04, w_depth/2 + door_d + 0.005, w_height/2 + base_h, mirror=True)

# ==========================================
# 7. MUCHA-STYLE TOP CREST (HIGH POLY)
# ==========================================
crest_x = 0
crest_y = w_depth/2 + 0.02
crest_z = w_height + base_h + 0.18

# Aureola Wood Backdrop (128 vertices cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.24, depth=0.02, location=(crest_x, crest_y, crest_z), rotation=(math.radians(90), 0, 0))
aureola = bpy.context.active_object
aureola.name = "Mucha_Aureola_Base"
aureola.scale = (1.0, 1.0, 0.4)
bpy.ops.object.transform_apply(scale=True)
apply_material(aureola, wood_mat)
bpy.ops.object.shade_smooth()
aureola.modifiers.new(name="Bevel", type='BEVEL').width = 0.003
register_object(aureola)

# Concentric Brass Ring (128 vertices cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.18, depth=0.005, location=(crest_x, crest_y + 0.005, crest_z), rotation=(math.radians(90), 0, 0))
brass_ring = bpy.context.active_object
brass_ring.name = "Mucha_Brass_Ring"
brass_ring.scale = (1.0, 1.0, 0.5)
bpy.ops.object.transform_apply(scale=True)
apply_material(brass_ring, brass_mat)
bpy.ops.object.shade_smooth()
register_object(brass_ring)

# Jewel-like Brass Beads semiround crown (Subdivisions 4)
num_beads = 16
bead_radius = 0.21
for i in range(num_beads):
    angle = math.radians(180 * i / (num_beads - 1))
    bx = crest_x + bead_radius * math.cos(angle)
    bz = crest_z + bead_radius * math.sin(angle)
    by = crest_y + 0.006
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.012, subdivisions=4, location=(bx, by, bz))
    bead = bpy.context.active_object
    bead.name = f"Mucha_Bead_{i}"
    apply_material(bead, brass_mat)
    bpy.ops.object.shade_smooth()
    register_object(bead)

# Sinuous Whiplash Ribbon Scrolls
def create_whiplash_scroll(name, points_data, mirror_x=False):
    curve_data = bpy.data.curves.new(name=f"Scroll_Curve_{name}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.resolution_u = 64
    curve_data.bevel_depth = 0.01
    curve_data.bevel_resolution = 10
    
    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(len(points_data) - 1)
    
    for idx, pt in enumerate(points_data):
        bp = polyline.bezier_points[idx]
        x = -pt["co"][0] if mirror_x else pt["co"][0]
        y = pt["co"][1]
        z = pt["co"][2]
        bp.co = (x, y, z)
        
        hl = pt["hl"]
        hr = pt["hr"]
        if mirror_x:
            bp.handle_left = (-hl[0], hl[1], hl[2])
            bp.handle_right = (-hr[0], hr[1], hr[2])
        else:
            bp.handle_left = (hl[0], hl[1], hl[2])
            bp.handle_right = (hr[0], hr[1], hr[2])
            
    scroll_obj = bpy.data.objects.new(f"Scroll_{name}", curve_data)
    wardrobe_coll.objects.link(scroll_obj)
    apply_material(scroll_obj, wood_mat)
    return scroll_obj

scroll_a_points = [
    {"co": (0.0, crest_y - 0.005, crest_z - 0.05), "hl": (-0.05, crest_y - 0.005, crest_z - 0.05), "hr": (0.05, crest_y - 0.005, crest_z - 0.05)},
    {"co": (0.28, crest_y - 0.01, crest_z + 0.05), "hl": (0.15, crest_y - 0.01, crest_z - 0.02), "hr": (0.42, crest_y - 0.01, crest_z + 0.12)},
    {"co": (0.55, crest_y - 0.015, crest_z - 0.08), "hl": (0.48, crest_y - 0.015, crest_z + 0.05), "hr": (0.62, crest_y - 0.015, crest_z - 0.22)},
    {"co": (0.75, crest_y - 0.02, crest_z - 0.28), "hl": (0.70, crest_y - 0.02, crest_z - 0.20), "hr": (0.80, crest_y - 0.02, crest_z - 0.35)}
]

scroll_b_points = [
    {"co": (0.12, crest_y - 0.005, crest_z + 0.12), "hl": (0.08, crest_y - 0.005, crest_z + 0.05), "hr": (0.18, crest_y - 0.005, crest_z + 0.18)},
    {"co": (0.32, crest_y - 0.01, crest_z + 0.22), "hl": (0.25, crest_y - 0.01, crest_z + 0.22), "hr": (0.38, crest_y - 0.01, crest_z + 0.22)},
    {"co": (0.45, crest_y - 0.01, crest_z + 0.12), "hl": (0.42, crest_y - 0.01, crest_z + 0.18), "hr": (0.48, crest_y - 0.01, crest_z + 0.05)}
]

create_whiplash_scroll("Right_A", scroll_a_points, mirror_x=False)
create_whiplash_scroll("Left_A", scroll_a_points, mirror_x=True)
create_whiplash_scroll("Right_B", scroll_b_points, mirror_x=False)
create_whiplash_scroll("Left_B", scroll_b_points, mirror_x=True)

# Mucha central Lily flower
# Left wood petal (subdivisions 4)
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.04, subdivisions=4, location=(crest_x - 0.05, crest_y + 0.01, crest_z - 0.02))
petal_l = bpy.context.active_object
petal_l.name = "Mucha_Petal_L"
petal_l.scale = (1.5, 0.2, 0.6)
petal_l.rotation_euler = (0, math.radians(-30), math.radians(-25))
bpy.ops.object.transform_apply(scale=True)
apply_material(petal_l, wood_mat)
bpy.ops.object.shade_smooth()
register_object(petal_l)

# Right wood petal
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.04, subdivisions=4, location=(crest_x + 0.05, crest_y + 0.01, crest_z - 0.02))
petal_r = bpy.context.active_object
petal_r.name = "Mucha_Petal_R"
petal_r.scale = (1.5, 0.2, 0.6)
petal_r.rotation_euler = (0, math.radians(30), math.radians(205))
bpy.ops.object.transform_apply(scale=True)
apply_material(petal_r, wood_mat)
bpy.ops.object.shade_smooth()
register_object(petal_r)

# Central brass stamen (128 vertices cone)
bpy.ops.mesh.primitive_cone_add(vertices=128, radius1=0.02, radius2=0.002, depth=0.12, location=(crest_x, crest_y + 0.015, crest_z + 0.02))
stamen = bpy.context.active_object
stamen.name = "Mucha_Stamen"
stamen.scale = (0.8, 0.4, 1.2)
bpy.ops.object.transform_apply(scale=True)
apply_material(stamen, brass_mat)
bpy.ops.object.shade_smooth()
register_object(stamen)

# Calyx cup (128 vertices cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.035, depth=0.04, location=(crest_x, crest_y + 0.008, crest_z - 0.06), rotation=(math.radians(90), 0, 0))
calyx = bpy.context.active_object
calyx.name = "Mucha_Calyx"
calyx.scale = (1.0, 1.0, 0.5)
bpy.ops.object.transform_apply(scale=True)
apply_material(calyx, wood_mat)
bpy.ops.object.shade_smooth()
register_object(calyx)

# Symmetrical arch leaves
crest_leaves = [
    {"loc": (0.15, w_depth/2 + 0.02, w_height + base_h + 0.09), "rot": (0, math.radians(-15), math.radians(-10)), "scale": (0.15, 0.02, 0.06)},
    {"loc": (-0.15, w_depth/2 + 0.02, w_height + base_h + 0.09), "rot": (0, math.radians(15), math.radians(190)), "scale": (0.15, 0.02, 0.06)},
    {"loc": (0.35, w_depth/2 + 0.015, w_height + base_h + 0.05), "rot": (0, math.radians(-30), math.radians(-25)), "scale": (0.18, 0.02, 0.05)},
    {"loc": (-0.35, w_depth/2 + 0.015, w_height + base_h + 0.05), "rot": (0, math.radians(30), math.radians(205)), "scale": (0.18, 0.02, 0.05)}
]

def create_wood_leaf(name, location, rotation, scale=(0.04, 0.012, 0.08), mat=leaf_mat):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=5, location=location)
    leaf = bpy.context.active_object
    leaf.name = f"Carved_Leaf_{name}"
    leaf.scale = scale
    leaf.rotation_euler = rotation
    apply_material(leaf, mat)
    bpy.ops.object.shade_smooth()
    
    leaf.modifiers.new(name="Bevel", type='BEVEL').width = 0.002
    sub = leaf.modifiers.new(name="Subsurf", type='SUBSURF')
    sub.levels = 2
    sub.render_levels = 3
    register_object(leaf)

for idx, cl in enumerate(crest_leaves):
    create_wood_leaf(f"Crest_{idx}", cl["loc"], cl["rot"], cl["scale"], mat=leaf_mat)

# ==========================================
# 8. ORGANIC JASMINE VINES CLIMBING DYNAMICALLY
# ==========================================
panel_y = w_depth/2 + door_d + 0.004

def create_wood_vine(name, points_data, mirror_x=False):
    curve_data = bpy.data.curves.new(name=f"Vine_Curve_{name}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.resolution_u = 128
    curve_data.bevel_depth = 0.008
    curve_data.bevel_resolution = 16
    
    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(len(points_data) - 1)
    
    for idx, pt in enumerate(points_data):
        bp = polyline.bezier_points[idx]
        x = -pt["co"][0] if mirror_x else pt["co"][0]
        y = pt["co"][1]
        z = pt["co"][2]
        bp.co = (x, y, z)
        
        hl = pt["hl"]
        hr = pt["hr"]
        if mirror_x:
            bp.handle_left = (-hl[0], hl[1], hl[2])
            bp.handle_right = (-hr[0], hr[1], hr[2])
        else:
            bp.handle_left = (hl[0], hl[1], hl[2])
            bp.handle_right = (hr[0], hr[1], hr[2])
            
    vine_obj = bpy.data.objects.new(f"Vine_{name}", curve_data)
    wardrobe_coll.objects.link(vine_obj)
    apply_material(vine_obj, stem_mat)
    return vine_obj

vine_a_points = [
    {"co": (-0.6, panel_y, 0.4), "hl": (-0.6, panel_y, 0.3), "hr": (-0.55, panel_y, 0.5)},
    {"co": (-0.3, panel_y, 0.8), "hl": (-0.45, panel_y, 0.7), "hr": (-0.2, panel_y, 0.9)},
    {"co": (-0.5, panel_y, 1.4), "hl": (-0.25, panel_y, 1.25), "hr": (-0.6, panel_y, 1.5)},
    {"co": (-0.2, panel_y, 1.8), "hl": (-0.4, panel_y, 1.7), "hr": (-0.1, panel_y, 1.9)},
    {"co": (-0.45, panel_y, 2.1), "hl": (-0.25, panel_y, 2.05), "hr": (-0.55, panel_y, 2.15)}
]

vine_b_points = [
    {"co": (-0.5, panel_y, 1.4), "hl": (-0.55, panel_y, 1.35), "hr": (-0.45, panel_y, 1.45)},
    {"co": (-0.2, panel_y, 1.2), "hl": (-0.35, panel_y, 1.3), "hr": (-0.15, panel_y, 1.15)},
    {"co": (-0.35, panel_y, 0.95), "hl": (-0.18, panel_y, 1.05), "hr": (-0.45, panel_y, 0.9)}
]

create_wood_vine("Left_Main", vine_a_points, mirror_x=False)
create_wood_vine("Left_Branch", vine_b_points, mirror_x=False)
create_wood_vine("Right_Main", vine_a_points, mirror_x=True)
create_wood_vine("Right_Branch", vine_b_points, mirror_x=True)

# Symmetrical Door Leaves
door_leaves = [
    {"loc": (-0.56, panel_y, 0.5), "rot": (0, math.radians(15), math.radians(45))},
    {"loc": (-0.35, panel_y, 0.9), "rot": (0, -math.radians(15), math.radians(-30))},
    {"loc": (-0.45, panel_y, 1.35), "rot": (0, math.radians(20), math.radians(60))},
    {"loc": (-0.28, panel_y, 1.75), "rot": (0, -math.radians(15), math.radians(-25))},
    {"loc": (-0.22, panel_y, 1.15), "rot": (0, math.radians(10), math.radians(15))}
]
for idx, dl in enumerate(door_leaves):
    lx, ly, lz = dl["loc"]
    rx, ry, rz = -lx, ly, lz
    
    create_wood_leaf(f"L_{idx}", (lx, ly, lz), dl["rot"], mat=leaf_mat)
    r_rot = (dl["rot"][0], -dl["rot"][1], -dl["rot"][2])
    create_wood_leaf(f"R_{idx}", (rx, ry, rz), r_rot, mat=leaf_mat)

# ==========================================
# 9. FIVE-PETAL JASMINE FLOWERS (ENLARGED HIGH POLY WITH SUBSURF)
# ==========================================
jasmine_locations = [
    {"loc": (-0.45, panel_y + 0.004, 2.1), "rot": (math.radians(90), 0, math.radians(45)), "name": "L_Upper"},
    {"loc": (-0.35, panel_y + 0.004, 0.95), "rot": (math.radians(90), 0, -math.radians(120)), "name": "L_Lower"},
    {"loc": (0.45, panel_y + 0.004, 2.1), "rot": (math.radians(90), 0, math.radians(135)), "name": "R_Upper"},
    {"loc": (0.35, panel_y + 0.004, 0.95), "rot": (math.radians(90), 0, -math.radians(60)), "name": "R_Lower"}
]

def create_jasmine_flower(name, location, rotation_angles):
    # Central brass stamen (radius increased to 0.009 for balance!)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.009, subdivisions=5, location=location)
    center = bpy.context.active_object
    center.name = f"Jasmine_Center_{name}"
    apply_material(center, brass_mat)
    bpy.ops.object.shade_smooth()
    register_object(center)
    
    rot_matrix = mathutils.Euler(rotation_angles).to_matrix()
    
    # 5 pointed jasmine star petals (Base radius increased from 0.01 to 0.017 for ENLARGED look!)
    for i in range(5):
        angle = math.radians(72 * i)
        px = 0.034 * math.cos(angle) # Offset scaled up to match larger petals!
        pz = 0.034 * math.sin(angle)
        py = 0.002
        
        local_pos = mathutils.Vector((px, py, pz))
        global_pos = rot_matrix @ local_pos
        world_pos = (location[0] + global_pos.x, location[1] + global_pos.y, location[2] + global_pos.z)
        
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.017, subdivisions=5, location=world_pos)
        petal = bpy.context.active_object
        petal.name = f"Jasmine_Petal_{name}_{i}"
        
        # Scale widened and lengthened for bold, striking shape
        petal.scale = (1.6, 0.25, 0.6)
        
        petal_rot = mathutils.Euler((0, 0, angle))
        combined_rot = (rot_matrix @ petal_rot.to_matrix()).to_euler()
        petal.rotation_euler = combined_rot
        
        bpy.ops.object.transform_apply(scale=True)
        apply_material(petal, petal_mat)
        bpy.ops.object.shade_smooth()
        
        # Micro bevel and subsurf
        petal.modifiers.new(name="Bevel", type='BEVEL').width = 0.001
        sub = petal.modifiers.new(name="Subsurf", type='SUBSURF')
        sub.levels = 2
        sub.render_levels = 3
        
        register_object(petal)

for jas in jasmine_locations:
    create_jasmine_flower(jas["name"], jas["loc"], jas["rot"])

# ==========================================
# 10. SHADING PREVIEW SETUP
# ==========================================
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

# ==========================================
# 11. AUTOSAVE THE MASTER CLEAN FILE
# ==========================================
filepath = r"C:\Users\andre\Desktop\Nuova cartella (5)\armadio_liberty.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print("SUCCESS: High-Poly Stile Liberty Wardrobe with ENLARGED Jasmine petals generated and saved successfully!")
except Exception as e:
    print(f"SUCCESS: Wardrobe generated but autosave failed: {str(e)}")

import bpy
import math
import mathutils

# Retrieve the wardrobe collection and materials
wardrobe_coll = bpy.data.collections.get("Stile_Liberty_Wardrobe")
wood_mat = bpy.data.materials.get("Walnut_Wood")
brass_mat = bpy.data.materials.get("Antique_Brass")

if not wardrobe_coll:
    wardrobe_coll = bpy.context.collection

# Helper to apply material
def apply_material(obj, mat):
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

# Clean up old simple crest objects to make space for Mucha's masterpiece
old_crest_names = [
    "Top_Organic_Motif", "Crest_Center", 
    "Carved_Leaf_Crest_0", "Carved_Leaf_Crest_1", 
    "Carved_Leaf_Crest_2", "Carved_Leaf_Crest_3"
]
for name in old_crest_names:
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

# Cabinet Dimensions
w_width = 1.6
w_depth = 0.6
w_height = 2.2
base_h = 0.15

# Mucha Crest Center position
crest_x = 0
crest_y = w_depth/2 + 0.02
crest_z = w_height + base_h + 0.18  # Sitting beautifully atop the arch

# 1. MUCHA AUREOLA (Circular Halo Backdrop)
# A gorgeous thin wood medallion with concentric brass rings
bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.02, location=(crest_x, crest_y, crest_z), rotation=(math.radians(90), 0, 0))
aureola = bpy.context.active_object
aureola.name = "Mucha_Aureola_Base"
aureola.scale = (1.0, 1.0, 0.4)
bpy.ops.object.transform_apply(scale=True)
apply_material(aureola, wood_mat)
aureola.modifiers.new(name="Bevel", type='BEVEL').width = 0.003

# Inner Brass Ring
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.005, location=(crest_x, crest_y + 0.005, crest_z), rotation=(math.radians(90), 0, 0))
brass_ring = bpy.context.active_object
brass_ring.name = "Mucha_Brass_Ring"
brass_ring.scale = (1.0, 1.0, 0.5)
bpy.ops.object.transform_apply(scale=True)
apply_material(brass_ring, brass_mat)

# 2. JEWEL-LIKE BRASS BEADS (Concentric pearl border typical of Mucha's halo drawings)
num_beads = 16
bead_radius = 0.21
for i in range(num_beads):
    # Place beads in a semi-circle (top half) for a crown/halo effect
    angle = math.radians(180 * i / (num_beads - 1))
    bx = crest_x + bead_radius * math.cos(angle)
    bz = crest_z + bead_radius * math.sin(angle)
    by = crest_y + 0.006
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.012, subdivisions=2, location=(bx, by, bz))
    bead = bpy.context.active_object
    bead.name = f"Mucha_Bead_{i}"
    apply_material(bead, brass_mat)
    if bead.name in bpy.context.scene.collection.objects:
        try:
            bpy.context.scene.collection.objects.unlink(bead)
        except:
            pass
    if bead.name not in wardrobe_coll.objects:
        wardrobe_coll.objects.link(bead)

# 3. WHIPLASH RIBBONS & SCROLLS (Flowing organic lines sweeping out from the halo)
def create_whiplash_scroll(name, points_data, mirror_x=False):
    curve_data = bpy.data.curves.new(name=f"Scroll_Curve_{name}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = 0.01  # Thick elegant ribbon
    curve_data.bevel_resolution = 3
    
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

# Scroll A: Long whiplash ribbon cascading down the top arch to the sides
scroll_a_points = [
    {"co": (0.0, crest_y - 0.005, crest_z - 0.05), "hl": (-0.05, crest_y - 0.005, crest_z - 0.05), "hr": (0.05, crest_y - 0.005, crest_z - 0.05)},
    {"co": (0.28, crest_y - 0.01, crest_z + 0.05), "hl": (0.15, crest_y - 0.01, crest_z - 0.02), "hr": (0.42, crest_y - 0.01, crest_z + 0.12)},
    {"co": (0.55, crest_y - 0.015, crest_z - 0.08), "hl": (0.48, crest_y - 0.015, crest_z + 0.05), "hr": (0.62, crest_y - 0.015, crest_z - 0.22)},
    {"co": (0.75, crest_y - 0.02, crest_z - 0.28), "hl": (0.70, crest_y - 0.02, crest_z - 0.20), "hr": (0.80, crest_y - 0.02, crest_z - 0.35)}
]

# Scroll B: Elegant inner loop curling back
scroll_b_points = [
    {"co": (0.12, crest_y - 0.005, crest_z + 0.12), "hl": (0.08, crest_y - 0.005, crest_z + 0.05), "hr": (0.18, crest_y - 0.005, crest_z + 0.18)},
    {"co": (0.32, crest_y - 0.01, crest_z + 0.22), "hl": (0.25, crest_y - 0.01, crest_z + 0.22), "hr": (0.38, crest_y - 0.01, crest_z + 0.22)},
    {"co": (0.45, crest_y - 0.01, crest_z + 0.12), "hl": (0.42, crest_y - 0.01, crest_z + 0.18), "hr": (0.48, crest_y - 0.01, crest_z + 0.05)}
]

create_whiplash_scroll("Right_A", scroll_a_points, mirror_x=False)
create_whiplash_scroll("Left_A", scroll_a_points, mirror_x=True)
create_whiplash_scroll("Right_B", scroll_b_points, mirror_x=False)
create_whiplash_scroll("Left_B", scroll_b_points, mirror_x=True)

# 4. CENTRAL STYLIZED LILY (Mucha's signature floral motif)
# Composed of detailed overlapping brass and wood petals
# Left petal
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.04, subdivisions=2, location=(crest_x - 0.05, crest_y + 0.01, crest_z - 0.02))
petal_l = bpy.context.active_object
petal_l.name = "Mucha_Petal_L"
petal_l.scale = (1.5, 0.2, 0.6)
petal_l.rotation_euler = (0, math.radians(-30), math.radians(-25))
bpy.ops.object.transform_apply(scale=True)
apply_material(petal_l, wood_mat)

# Right petal
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.04, subdivisions=2, location=(crest_x + 0.05, crest_y + 0.01, crest_z - 0.02))
petal_r = bpy.context.active_object
petal_r.name = "Mucha_Petal_R"
petal_r.scale = (1.5, 0.2, 0.6)
petal_r.rotation_euler = (0, math.radians(30), math.radians(205))
bpy.ops.object.transform_apply(scale=True)
apply_material(petal_r, wood_mat)

# Central Tall Brass Bud/Stamen
bpy.ops.mesh.primitive_cone_add(radius1=0.02, radius2=0.002, depth=0.12, location=(crest_x, crest_y + 0.015, crest_z + 0.02))
stamen = bpy.context.active_object
stamen.name = "Mucha_Stamen"
stamen.scale = (0.8, 0.4, 1.2)
bpy.ops.object.transform_apply(scale=True)
apply_material(stamen, brass_mat)

# Bottom organic calyx cup
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.04, location=(crest_x, crest_y + 0.008, crest_z - 0.06), rotation=(math.radians(90), 0, 0))
calyx = bpy.context.active_object
calyx.name = "Mucha_Calyx"
calyx.scale = (1.0, 1.0, 0.5)
bpy.ops.object.transform_apply(scale=True)
apply_material(calyx, wood_mat)

# Relink flower parts to wardrobe collection and ensure no duplicates
flower_parts = [petal_l, petal_r, stamen, calyx, aureola, brass_ring]
for obj in flower_parts:
    if obj.name in bpy.context.scene.collection.objects:
        try:
            bpy.context.scene.collection.objects.unlink(obj)
        except:
            pass
    if obj.name not in wardrobe_coll.objects:
        wardrobe_coll.objects.link(obj)

print("Mucha-style top decoration added successfully!")

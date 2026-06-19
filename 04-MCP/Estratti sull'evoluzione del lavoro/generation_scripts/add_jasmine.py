import bpy
import math
import mathutils

# Retrieve collection and materials
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

# Clean up the generic buds we created in add_carvings.py to make way for jasmine
generic_buds = [
    "Carved_Cup_L_4", "Carved_Petals_L_4",
    "Carved_Cup_L_5", "Carved_Petals_L_5",
    "Carved_Cup_R_4", "Carved_Petals_R_4",
    "Carved_Cup_R_5", "Carved_Petals_R_5"
]
for g_bud in generic_buds:
    if g_bud in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[g_bud], do_unlink=True)

w_depth = 0.6
door_d = 0.03

# Positions for the jasmine flowers (from previous bud locations)
jasmine_locations = [
    # Left Door upper bud
    {"loc": (-0.45, w_depth/2 + door_d + 0.004, 2.1), "rot": (math.radians(90), 0, math.radians(45)), "name": "L_Upper"},
    # Left Door lower bud
    {"loc": (-0.35, w_depth/2 + door_d + 0.004, 0.95), "rot": (math.radians(90), 0, -math.radians(120)), "name": "L_Lower"},
    # Right Door upper bud (Mirrored X)
    {"loc": (0.45, w_depth/2 + door_d + 0.004, 2.1), "rot": (math.radians(90), 0, math.radians(135)), "name": "R_Upper"},
    # Right Door lower bud (Mirrored X)
    {"loc": (0.35, w_depth/2 + door_d + 0.004, 0.95), "rot": (math.radians(90), 0, -math.radians(60)), "name": "R_Lower"}
]

# 1. JASMINE GENERATOR
def create_jasmine_flower(name, location, rotation_angles):
    # A beautiful carved star-like Jasmine flower with 5 petals and a central pistil
    # We rotate the petals along the face of the door panel (local space)
    
    # 1. Central Brass Pistil/Stamen (Spherical detail)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.006, subdivisions=2, location=location)
    center = bpy.context.active_object
    center.name = f"Jasmine_Center_{name}"
    apply_material(center, brass_mat)
    
    # Link center to collection safely
    if center.name in bpy.context.scene.collection.objects:
        try:
            bpy.context.scene.collection.objects.unlink(center)
        except:
            pass
    if center.name not in wardrobe_coll.objects:
        wardrobe_coll.objects.link(center)
        
    rot_matrix = mathutils.Euler(rotation_angles).to_matrix()
    
    # 2. Five star-shaped petals arranged circularly
    for i in range(5):
        angle = math.radians(72 * i)
        # Petal local offset (placed flat on door panel, star configuration)
        px = 0.02 * math.cos(angle)
        pz = 0.02 * math.sin(angle)
        py = 0.002  # Slightly forward
        
        local_pos = mathutils.Vector((px, py, pz))
        global_pos = rot_matrix @ local_pos
        world_pos = (location[0] + global_pos.x, location[1] + global_pos.y, location[2] + global_pos.z)
        
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.01, subdivisions=2, location=world_pos)
        petal = bpy.context.active_object
        petal.name = f"Jasmine_Petal_{name}_{i}"
        
        # Flatten and stretch to make it look like a pointed jasmine petal
        petal.scale = (1.4, 0.2, 0.5)
        
        # Symmetrical rotation of each individual petal outward from center
        petal_rot = mathutils.Euler((0, 0, angle))
        combined_rot = (rot_matrix @ petal_rot.to_matrix()).to_euler()
        petal.rotation_euler = combined_rot
        
        bpy.ops.object.transform_apply(scale=True)
        apply_material(petal, wood_mat)
        
        # Link petal to collection safely
        if petal.name in bpy.context.scene.collection.objects:
            try:
                bpy.context.scene.collection.objects.unlink(petal)
            except:
                pass
        if petal.name not in wardrobe_coll.objects:
            wardrobe_coll.objects.link(petal)

# Generate Jasmine Flowers on the doors
for jas in jasmine_locations:
    create_jasmine_flower(jas["name"], jas["loc"], jas["rot"])

# Save active session as updated blend file automatically
filepath = r"C:\Users\andre\Desktop\Nuova cartella (5)\armadio_liberty.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print("Jasmine decorations added and armadio_liberty.blend saved successfully!")
except Exception as e:
    print(f"Jasmine decorations added successfully (autosave failed: {str(e)})")

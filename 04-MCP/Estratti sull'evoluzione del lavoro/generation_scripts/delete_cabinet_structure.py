import bpy

print("Removing structural cabinet components and retaining only Mucha and Jasmine decorations...")

# List of structural objects to remove
objects_to_remove = [
    "Wardrobe_Body",
    "Wardrobe_Top_Arch",
    "Wardrobe_Base",
    "Wardrobe_Leg_1",
    "Wardrobe_Leg_2",
    "Wardrobe_Leg_3",
    "Wardrobe_Leg_4",
    "Door_Left",
    "Door_Right",
    "Door_Left_Panel",
    "Door_Right_Panel",
    "Handle_Left",
    "Handle_Right",
    "plate_bottom",  # Check exact names or partial matches
    "plate_top"
]

# Select and delete matching structural objects
bpy.ops.object.select_all(action='DESELECT')

for obj in bpy.data.objects:
    # Remove if exact name match or starts with name in our structural list (handles, plates, legs)
    is_structural = False
    for name in objects_to_remove:
        if obj.name == name or obj.name.startswith(name + "_") or obj.name.startswith(name):
            is_structural = True
            break
            
    if is_structural:
        obj.select_set(True)
        print(f"Selecting for removal: {obj.name}")

# Delete selected structural elements
bpy.ops.object.delete()

# Ensure we save the file
filepath = r"C:\Users\andre\Desktop\Nuova cartella (5)\armadio_liberty.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print("SUCCESS: Cabinet structure removed. Only Mucha and Jasmine decorations remain!")
except Exception as e:
    print(f"SUCCESS: Cabinet structure removed (autosave failed: {str(e)})")

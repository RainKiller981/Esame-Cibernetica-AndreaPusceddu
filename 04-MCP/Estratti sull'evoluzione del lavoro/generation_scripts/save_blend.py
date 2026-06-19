import bpy
import os

filepath = r"C:\Users\andre\Desktop\Nuova cartella (5)\armadio_liberty.blend"

try:
    # Save the current interactive scene to the workspace
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"Blender file saved successfully to: {filepath}")
except Exception as e:
    print(f"Failed to save Blender file: {str(e)}")

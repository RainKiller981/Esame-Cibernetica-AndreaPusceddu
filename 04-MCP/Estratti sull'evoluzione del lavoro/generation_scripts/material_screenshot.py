import bpy
import os

filepath = r"C:\Users\andre\Desktop\Nuova cartella (5)\wardrobe_screenshot.png"

try:
    # Ensure viewport is in MATERIAL shading mode to showcase all photorealistic textures
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    
    # Setup render paths
    bpy.context.scene.render.filepath = filepath
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    
    # Render viewport instantly with materials
    bpy.ops.render.opengl(write_still=True)
    
    print(f"SUCCESS: Photorealistic MATERIAL viewport screenshot saved successfully to {filepath}")
except Exception as e:
    print(f"Failed to capture material viewport screenshot: {str(e)}")

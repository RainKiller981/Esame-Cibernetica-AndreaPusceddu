import bpy
   import os
   
   filepath = r"C:\Users\andre\Desktop\Nuova cartella (5)\wardrobe_screenshot.png"
   
   try:
       # Temporarily switch viewport shading to SOLID to ensure instant draw and prevent timeouts
       for area in bpy.context.screen.areas:
           if area.type == 'VIEW_3D':
               for space in area.spaces:
                   if space.type == 'VIEW_3D':
                       space.shading.type = 'SOLID'
                       
       # Set render settings for viewport snapshot
       bpy.context.scene.render.filepath = filepath
       bpy.context.scene.render.image_settings.file_format = 'PNG'
       
       # Render the viewport using OpenGL (instant, high quality, highly reliable)
       bpy.ops.render.opengl(write_still=True)
       
       # Restore viewport shading to MATERIAL for the user's GUI
       for area in bpy.context.screen.areas:
           if area.type == 'VIEW_3D':
               for space in area.spaces:
                   if space.type == 'VIEW_3D':
                       space.shading.type = 'MATERIAL'
                       
       print(f"SUCCESS: Viewport screenshot saved successfully to {filepath}")
   except Exception as e:
       print(f"Failed to capture viewport screenshot: {str(e)}")

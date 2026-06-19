---
name: blender-3d
description: >
  Control Blender 3D from Antigravity CLI — create, modify, render, and export
  3D scenes via headless automation. Use when the user asks about 3D modeling,
  rendering, creating objects, materials, exporting models, or any Blender task.
---

# Blender 3D Specialist

This skill provides instructions for controlling Blender 3D in headless mode
via Python wrapper scripts. All operations run Blender in background mode
(`blender --background`) and produce structured JSON output.

## Prerequisites

1.  **Blender**: Must be installed and available in the system PATH. Verify
    with: `python scripts/blender_info.py check --output result.json`
2.  **Python**: Python 3.x must be available to run the wrapper scripts.
3.  **GPU**: The user's system uses **CUDA** for GPU rendering with Cycles.

## Quick Start

Create a red metallic cube and render it:

```bash
# 1. Create a new clean scene
python scripts/blender_scene.py new --save scene.blend --output result.json

# 2. Add a cube
python scripts/blender_objects.py create --type cube --name MyCube --size 2 --location "0,0,1" --blend scene.blend --save scene.blend --output result.json

# 3. Create and assign a red metal material
python scripts/blender_materials.py preset --preset gold --blend scene.blend --save scene.blend --output result.json
python scripts/blender_materials.py assign --material Gold --object MyCube --blend scene.blend --save scene.blend --output result.json

# 4. Setup camera and lights
python scripts/blender_camera.py camera --location "7,-6,5" --rotation "1.1,0,0.8" --set-active --blend scene.blend --save scene.blend --output result.json
python scripts/blender_camera.py studio --preset three_point --blend scene.blend --save scene.blend --output result.json

# 5. Render
python scripts/blender_render.py render --blend scene.blend --output render.png --engine EEVEE --resolution "1920x1080" --output-json result.json
```

## Core Rules

-   **Use the Wrapper Scripts**: ALWAYS execute the provided helper scripts in
    the `scripts/` directory to interact with Blender. Never call `blender`
    directly or write bpy scripts manually.
-   **Read JSON Output**: After each command, read the generated JSON output
    file to verify success and get details about what was created/modified.
-   **Blend Files Are State**: Blender has no persistent state between script
    calls. Always use `--blend` to load an existing scene and `--save` to
    persist changes.
-   **Path Handling**: Use absolute paths for all file references. The scripts
    handle Windows path separators automatically.
-   **Sequential Operations**: When building a scene, operations must be
    sequential — create scene → add objects → apply materials → setup
    camera/lights → render.
-   **Verify Facts**: Always run `blender_info.py check` before the first
    Blender operation in a session to verify the environment.

## Core Capabilities

### 1. Environment Diagnostics (`blender_info.py`)

Check Blender installation, GPU availability, and addon status.

```bash
# Verify Blender installation and version
python scripts/blender_info.py check --output result.json

# List GPU devices for Cycles CUDA rendering
python scripts/blender_info.py gpu --output result.json

# List enabled addons
python scripts/blender_info.py addons --output result.json
```

### 2. Scene Management (`blender_scene.py`)

Create, open, save, inspect, and clean scenes.

```bash
# Create a new empty scene
python scripts/blender_scene.py new --save myscene.blend --output result.json

# Open and inspect an existing scene
python scripts/blender_scene.py inspect --blend myscene.blend --output result.json

# Clean all objects from a scene
python scripts/blender_scene.py clean --blend myscene.blend --save myscene.blend --output result.json
```

### 3. Object Creation & Manipulation (`blender_objects.py`)

Create primitives, transform, duplicate, and delete objects.

```bash
# Create objects
python scripts/blender_objects.py create --type cube --name Box --size 2 --location "0,0,1" --blend scene.blend --save scene.blend --output result.json
python scripts/blender_objects.py create --type sphere --name Ball --radius 1.5 --location "3,0,0" --blend scene.blend --save scene.blend --output result.json
python scripts/blender_objects.py create --type cylinder --name Pillar --radius 0.5 --depth 4 --location "-2,0,2" --blend scene.blend --save scene.blend --output result.json

# Available types: cube, sphere, ico_sphere, cylinder, plane, cone, torus, monkey

# Transform objects
python scripts/blender_objects.py transform --object Box --rotation "0.5,0,0.3" --scale "1,1,2" --blend scene.blend --save scene.blend --output result.json

# Duplicate an object
python scripts/blender_objects.py duplicate --object Box --name BoxCopy --offset "5,0,0" --blend scene.blend --save scene.blend --output result.json

# List all objects
python scripts/blender_objects.py list --blend scene.blend --output result.json

# Delete objects
python scripts/blender_objects.py delete --objects Box Ball --blend scene.blend --save scene.blend --output result.json
```

### 4. Materials (`blender_materials.py`)

Create PBR materials, assign them, and use presets.

```bash
# Create a custom material
python scripts/blender_materials.py create --name RedMetal --color "0.8,0.1,0.1" --metallic 1.0 --roughness 0.2 --blend scene.blend --save scene.blend --output result.json

# Assign material to object
python scripts/blender_materials.py assign --material RedMetal --object MyCube --blend scene.blend --save scene.blend --output result.json

# Use a preset material (gold, silver, chrome, glass, plastic_red, plastic_blue, wood, rubber, emission_white, emission_neon)
python scripts/blender_materials.py preset --preset chrome --blend scene.blend --save scene.blend --output result.json

# List all materials
python scripts/blender_materials.py list --blend scene.blend --output result.json
```

### 5. Rendering (`blender_render.py`)

Configure render engines and produce images/animations.

```bash
# Quick preview render (low quality, fast)
python scripts/blender_render.py preview --blend scene.blend --output preview.png --output-json result.json

# Full Eevee render
python scripts/blender_render.py render --blend scene.blend --output render.png --engine EEVEE --resolution "1920x1080" --samples 64 --output-json result.json

# Cycles GPU render (high quality)
python scripts/blender_render.py render --blend scene.blend --output render.png --engine CYCLES --resolution "1920x1080" --samples 128 --gpu --output-json result.json

# Transparent background
python scripts/blender_render.py render --blend scene.blend --output render.png --engine EEVEE --transparent --output-json result.json

# Render animation
python scripts/blender_render.py animation --blend scene.blend --output-dir ./frames/ --engine EEVEE --start-frame 1 --end-frame 120 --format PNG --output-json result.json

# Configure render settings (saves to .blend)
python scripts/blender_render.py configure --blend scene.blend --save scene.blend --engine CYCLES --samples 256 --resolution "3840x2160" --gpu --output result.json
```

### 6. Import & Export (`blender_io.py`)

Import and export 3D models in various formats.

```bash
# Export entire scene to GLB
python scripts/blender_io.py export --blend scene.blend --output model.glb --output-json result.json

# Export to OBJ
python scripts/blender_io.py export --blend scene.blend --output model.obj --output-json result.json

# Export specific objects only
python scripts/blender_io.py export --blend scene.blend --output hero.glb --selection MyCube MySphere --output-json result.json

# Supported export formats: glb, gltf, fbx, obj, stl

# Import a model into scene
python scripts/blender_io.py import_file --input model.fbx --blend scene.blend --save scene.blend --output-json result.json

# Import without existing scene (creates new)
python scripts/blender_io.py import_file --input model.obj --save imported.blend --output-json result.json
```

### 7. Modifiers (`blender_modifiers.py`)

Add, apply, remove, and list modifiers on objects.

```bash
# Add subdivision surface
python scripts/blender_modifiers.py add --object MyCube --type SUBSURF --levels 2 --blend scene.blend --save scene.blend --output result.json

# Add bevel
python scripts/blender_modifiers.py add --object MyCube --type BEVEL --width 0.05 --segments 3 --blend scene.blend --save scene.blend --output result.json

# Add array modifier
python scripts/blender_modifiers.py add --object MyCube --type ARRAY --count 5 --offset "1.2,0,0" --blend scene.blend --save scene.blend --output result.json

# Add mirror
python scripts/blender_modifiers.py add --object MyCube --type MIRROR --axis X --blend scene.blend --save scene.blend --output result.json

# Supported types: SUBSURF, BEVEL, BOOLEAN, MIRROR, ARRAY, SOLIDIFY, WIREFRAME, DECIMATE, SMOOTH, REMESH

# Apply modifier permanently
python scripts/blender_modifiers.py apply --object MyCube --modifier "Subdivision" --blend scene.blend --save scene.blend --output result.json

# List modifiers on an object
python scripts/blender_modifiers.py list --object MyCube --blend scene.blend --output result.json

# Remove a modifier
python scripts/blender_modifiers.py remove --object MyCube --modifier "Bevel" --blend scene.blend --save scene.blend --output result.json
```

### 8. Camera & Lighting (`blender_camera.py`)

Set up cameras, lights, HDRI environments, and studio presets.

```bash
# Add and position camera
python scripts/blender_camera.py camera --location "7,-6,5" --rotation "1.1,0,0.8" --focal-length 50 --set-active --blend scene.blend --save scene.blend --output result.json

# Point camera at an object
python scripts/blender_camera.py look-at --camera Camera --target MyCube --blend scene.blend --save scene.blend --output result.json

# Add lights
python scripts/blender_camera.py light --type SUN --energy 3 --location "0,0,10" --blend scene.blend --save scene.blend --output result.json
python scripts/blender_camera.py light --type POINT --energy 1000 --location "4,1,6" --color "1,0.9,0.8" --blend scene.blend --save scene.blend --output result.json

# Load HDRI environment
python scripts/blender_camera.py hdri --path /path/to/env.hdr --strength 1.0 --blend scene.blend --save scene.blend --output result.json

# Studio lighting presets (three_point, rim, product, dramatic)
python scripts/blender_camera.py studio --preset product --blend scene.blend --save scene.blend --output result.json
```

## Advanced Usage & Workflows

-   **Product Visualization Pipeline**: For step-by-step workflows (product
    shots, batch rendering, scene assembly), read
    [references/workflows.md](references/workflows.md).
-   **Material Deep Dive**: For detailed PBR parameter guides and advanced
    node configurations, read
    [references/materials_guide.md](references/materials_guide.md).
-   **Troubleshooting**: For common errors and solutions, read
    [references/troubleshooting.md](references/troubleshooting.md).

## Fallback Strategies

-   **Blender not found**: Run `blender_info.py check` and report the error.
    Suggest adding Blender to PATH or setting the `BLENDER_PATH` environment
    variable.
-   **GPU not available**: Fall back to CPU rendering with Cycles, or use
    Eevee for faster results.
-   **Export format not supported**: Check the Blender version. Blender 5.x
    uses `bpy.ops.wm.obj_export()` and `bpy.ops.wm.stl_export()` instead of
    older operators.
-   **Script timeout**: Default timeout is 300 seconds. For complex renders or
    large scenes, the scripts accept a `--timeout` parameter.

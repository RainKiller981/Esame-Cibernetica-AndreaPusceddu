from PIL import Image
import numpy as np
import os

filepath = r"C:\Users\andre\Desktop\nostromo_shot_1_claustrophobia.png"
if os.path.exists(filepath):
    try:
        img = Image.open(filepath)
        img_arr = np.array(img)
        print(f"Image shape: {img_arr.shape}")
        # Calculate mean brightness
        mean_brightness = np.mean(img_arr)
        min_val = np.min(img_arr)
        max_val = np.max(img_arr)
        print(f"Mean brightness: {mean_brightness:.4f}")
        print(f"Min pixel val: {min_val}, Max pixel val: {max_val}")
        
        # Check if it's completely black or transparent
        if mean_brightness < 1.0:
            print("WARNING: The image is almost completely pitch black!")
        elif np.all(img_arr[:, :, 3] == 0) if img_arr.shape[2] == 4 else False:
            print("WARNING: The image is fully transparent!")
        else:
            print("The image has non-zero colors and brightness.")
    except Exception as e:
        print(f"Error reading image: {e}")
else:
    print("File does not exist!")

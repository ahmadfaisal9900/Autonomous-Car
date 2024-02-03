from PIL import Image, ImageDraw
from skimage import draw
import numpy as np
import json
import os
import argparse

def poly2mask(polygon, img_height, img_width):
    mask = np.zeros((img_height, img_width))
    fill_row_coords, fill_col_coords = draw.polygon(polygon[:, 1], polygon[:, 0])
    mask[fill_row_coords, fill_col_coords] = 1
    return mask

def assign_color_to_object(label):
    # Define RGB colors for each class
    class_colors = {
        'obs-str-bar-fallback': (255, 0, 0),   # Red
        'vegetation': (0, 255, 0),             # Green
        'drivable fallback': (0, 128, 255),    # Light Blue
        'pole': (0, 255, 255),                 # Cyan
        'motorcycle': (0, 0, 255),             # Blue
        'curb': (255, 255, 0),                 # Yellow
        'sky': (255, 255, 255),                # White
        'building': (128, 128, 0),             # Olive
        'rider': (128, 0, 128),                # Purple
        'animal': (255, 128, 0),               # Orange
        'road': (255, 165, 0),                 # Light Orange (Adjust as needed)
        'billboard': (128, 0, 0),              # Maroon
        'car': (255, 69, 0),                   # Red-Orange
        'non-drivable fallback': (128, 128, 128),  # Gray
        'person': (139, 69, 19),               # Saddle Brown
        'truck': (0, 0, 128)                   # Navy
    }
    
    # Get the RGB color for the current class
    rgb_color = class_colors.get(label, (128, 128, 128))  # Default to gray if label not found
    
    return rgb_color

def convert_dataturks_to_masks(dataturks_json_path, original_image_path, masks_folder):
    with open(dataturks_json_path, 'r') as file:
        data = json.load(file)

    original_image = Image.open(original_image_path).convert("RGB")
    img_height, img_width = data['imgHeight'], data['imgWidth']

    # Extract the file name (without extension) from the original image path
    image_file_name = os.path.splitext(os.path.basename(original_image_path))[0]

    # Create an empty color mask image
    color_mask = Image.new('RGB', (img_width, img_height), (255, 255, 255))
    draw = ImageDraw.Draw(color_mask)

    for annotation in data['objects']:
        label = annotation['label']
        if label != '':
            points = np.array(annotation['polygon'])
            mask_array = poly2mask(points, img_height, img_width)

            # Get a unique color for each label
            color = assign_color_to_object(label)

            # Overlay the mask with the assigned color on the color_mask image
            mask_image = Image.fromarray((mask_array * 255).astype(np.uint8))
            color_mask.paste(Image.new('RGB', color_mask.size, color), mask=mask_image)

    # Save the combined color mask image with the original image file name
    output_file_name = f"{image_file_name}_combined_color_mask.png"
    output_file_path = os.path.join(masks_folder, output_file_name)
    color_mask.save(output_file_path)

    print("Conversion completed. Combined color mask image saved to:", output_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Dataturks JSON annotations to combined color mask image.")
    parser.add_argument("json_path", help="Path to Dataturks JSON file")
    parser.add_argument("image_path", help="Path to original image")
    parser.add_argument("masks_folder", help="Path to the folder where masks will be saved")
    args = parser.parse_args()

    convert_dataturks_to_masks(args.json_path, args.image_path, args.masks_folder)

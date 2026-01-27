import os
from pathlib import Path
from PIL import Image

# The root folder of your newly split data
data_root = Path("consolidated_medical_data")

# Common image file extensions to check
image_exts = {".jpg", ".jpeg", ".png", ".bmp"}

bad_files_found = 0
print(f"Scanning for corrupt images in '{data_root}'...")

# Loop over train, val, and test folders
for split in ["train", "val", "test"]:
    split_path = data_root / split
    if not split_path.exists():
        print(f"Warning: {split_path} not found. Skipping.")
        continue

    print(f"\n--- Scanning {split} folder ---")

    # Loop over class subfolders (e.g., 01_NORMAL_LUNG)
    for class_folder in split_path.iterdir():
        if not class_folder.is_dir():
            continue

        # Loop over every image in the class folder
        for image_file in class_folder.iterdir():
            if image_file.suffix.lower() in image_exts:
                try:
                    # Try to open and load the image
                    img = Image.open(image_file)
                    img.load() 
                except Exception as e:
                    # If it fails, it's corrupt
                    print(f"Found corrupt file: {image_file}")
                    print(f"  Error: {e}")
                    bad_files_found += 1

                    # Delete the corrupt file
                    try:
                        os.remove(image_file)
                        print(f"  DELETED: {image_file}")
                    except Exception as del_e:
                        print(f"  ERROR DELETING {image_file}: {del_e}")

if bad_files_found == 0:
    print("\nScan complete. No corrupt images found!")
else:
    print(f"\nScan complete. Found and deleted {bad_files_found} corrupt file(s).")

print("Your dataset is now clean.")
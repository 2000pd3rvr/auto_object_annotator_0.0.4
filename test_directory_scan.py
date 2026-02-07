#!/usr/bin/env python3

import os
from os import walk

def test_directory_scan():
    directory = '/Users/pd3rvr/Desktop/rw/JAN25/object_detection/STOD/data/data_out copy'
    if directory[-1] != "/":
        directory += "/"
    
    print(f"Scanning directory: {directory}")
    
    # Collect folders with the three specific image types
    folder_sets = []
    required_suffixes = ['sr_int_full.png', '-tr_line.png', '-tr_int_full.png']
    
    for (dirpath, dirnames, filenames) in walk(directory):
        if dirpath == directory:  # Skip root directory
            continue
            
        print(f"Checking folder: {dirpath}")
        print(f"Files found: {len(filenames)}")
        
        # Find images with required suffixes in this folder
        found_images = {}
        for filename in filenames:
            for suffix in required_suffixes:
                if filename.endswith(suffix):
                    relative_path = os.path.relpath(os.path.join(dirpath, filename), directory)
                    found_images[suffix] = relative_path
                    print(f"Found {suffix}: {relative_path}")
                    break
        
        # Only include folders that have all three required images
        if len(found_images) == 3:
            folder_name = os.path.basename(dirpath)
            folder_sets.append({
                'folder': folder_name,
                'sr_int_full': found_images['sr_int_full.png'],
                'tr_line': found_images['-tr_line.png'],
                'tr_int_full': found_images['-tr_int_full.png']
            })
            print(f"✓ Folder {folder_name} has all required images")
        else:
            print(f"✗ Folder {os.path.basename(dirpath)} missing images: {set(required_suffixes) - set(found_images.keys())}")
        
        print("---")
    
    print(f"\nTotal valid folder sets found: {len(folder_sets)}")
    for i, folder_set in enumerate(folder_sets[:3]):  # Show first 3
        print(f"{i+1}. {folder_set['folder']}")
        print(f"   sr_int_full: {folder_set['sr_int_full']}")
        print(f"   tr_line: {folder_set['tr_line']}")
        print(f"   tr_int_full: {folder_set['tr_int_full']}")

if __name__ == "__main__":
    test_directory_scan()

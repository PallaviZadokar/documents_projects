import os
import shutil

def organize_files(folder_path):
    images_folder = os.path.join(folder_path, 'images')
    xml_folder = os.path.join(folder_path, 'xml')

    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(xml_folder, exist_ok=True)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG')):
            shutil.move(file_path, os.path.join(images_folder, filename))
        elif filename.lower().endswith('.xml'):
            shutil.move(file_path, os.path.join(xml_folder, filename))
        else:
            pass

if __name__ == "__main__":
    folder_path = r"D:\hf\data\fineweb"
    organize_files(folder_path)

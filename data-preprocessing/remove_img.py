import os

folder_path = r"D:\hf\data\annotated_downloaded\websight_after_std" 

def remove_images_without_xml(folder_path):
    image_files = []
    xml_files = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG')):
            image_files.append(filename)
        elif filename.lower().endswith('.xml'):
            xml_files.append(filename)

    for image_file in image_files:
        image_name, image_ext = os.path.splitext(image_file)
        corresponding_xml = f'{image_name}.xml'
        
        if corresponding_xml not in xml_files:
            image_path = os.path.join(folder_path, image_file)
            os.remove(image_path)
            print(f'Removed: {image_file}')

remove_images_without_xml(folder_path)

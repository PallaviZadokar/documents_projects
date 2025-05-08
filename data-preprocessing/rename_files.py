import os
import xml.etree.ElementTree as ET

def clean_and_rename_files(folder_path):

    for filename in os.listdir(folder_path):

        if is_image_file(filename):
            
            if not filename.lower().endswith('.jpg'):
                base_name, ext = os.path.splitext(filename)
                new_filename = base_name + '.jpg'
                os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
                filename = new_filename
            else:
                base_name, ext = os.path.splitext(filename)
            
            new_base_name = ''.join(c for c in base_name if c.isalnum())
            new_filename = new_base_name + '.jpg'
            os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))
            
            xml_filename = new_base_name + '.xml'
            os.rename(os.path.join(folder_path, base_name + '.xml'), os.path.join(folder_path, xml_filename))
            
            update_xml_content(folder_path, xml_filename, new_filename)

def is_image_file(filename):
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG'))


def update_xml_content(folder_path, xml_filename, new_image_filename):
    xml_path = os.path.join(folder_path, xml_filename)
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    folder_tag = root.find('folder')

    if folder_tag is None:
        folder_tag = ET.Element('folder')
        root.append(folder_tag)
    folder_tag.text = 'newdata'
    
    filename_tag = root.find('filename')

    if filename_tag is None:
        filename_tag = ET.Element('filename')
        root.append(filename_tag)
    filename_tag.text = new_image_filename
    
    path_tag = root.find('path')
    
    if path_tag is None:
        path_tag = ET.Element('path')
        root.append(path_tag)
    path_tag.text = os.path.join('newdata', new_image_filename)
    
    tree.write(xml_path)

if __name__ == "__main__":
    folder_path = r"D:\hf\data\annotated_downloaded\websight_after_std" 
    clean_and_rename_files(folder_path)

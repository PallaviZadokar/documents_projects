import os
import xml.etree.ElementTree as ET

class_mapping = {
    'mneu': 'menu',
    'tabel': 'table',
    'input_box': 'inputbox',
    'iogo': 'logo',
    'iocn': 'icon'
}

def process_xml_file(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for obj in root.findall('object'):
        name = obj.find('name').text
        if name in class_mapping:
            obj.find('name').text = class_mapping[name]
    
    tree.write(xml_file)

xml_folder = r"D:\hf\data\annotated_downloaded\websight_after_std"

for filename in os.listdir(xml_folder):
    if filename.endswith('.xml'):
        xml_path = os.path.join(xml_folder, filename)
        process_xml_file(xml_path)
        print(f"Processed: {filename}")


import os
import xml.etree.ElementTree as ET

def remove_annotations(xml_folder, class_names):
    for filename in os.listdir(xml_folder):
        if filename.endswith('.xml'):
            xml_path = os.path.join(xml_folder, filename)
            tree = ET.parse(xml_path)
            root = tree.getroot()

            objects = root.findall('object')
            
            for obj in objects[:]:  
                name = obj.find('name').text
                if name in class_names:
                    root.remove(obj)

            tree.write(xml_path)

if __name__ == '__main__':
    xml_folder = r"D:\hf\data\annotated_downloaded\websight_after_std"  
    class_names_to_remove = [
    'im',
    'header',
    'option',
    'table-rows'
]

    remove_annotations(xml_folder, class_names_to_remove)
    print('Annotation removal complete.')



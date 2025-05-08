import os
import cv2
import xml.etree.ElementTree as ET

def resize_image_and_xml(image_folder, output_folder, target_size=(800, 600)):
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.jpg')):
            image_path = os.path.join(image_folder, filename)
            base_name, ext = os.path.splitext(filename)
            
            xml_path = os.path.join(image_folder, base_name + '.xml')
            
            if not os.path.exists(xml_path):
                print(f"XML file not found for {filename}, skipping...")
                continue
            
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: Unable to read image {filename}, skipping...")
                continue
            
            height, width, _ = image.shape
            
            resized_image = cv2.resize(image, target_size)
            
            output_image_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_image_path, resized_image)
            
            tree = ET.parse(xml_path)
            root = tree.getroot()

            size_elem = root.find('size')
            if size_elem is None:
                size_elem = ET.SubElement(root, 'size')
            
            size_elem.find('width').text = str(target_size[0])
            size_elem.find('height').text = str(target_size[1])
            
            scale_x = target_size[0] / width
            scale_y = target_size[1] / height
            
            for obj in root.findall('object'):
                bbox = obj.find('bndbox')
                if bbox is None:
                    continue
                xmin = int(float(bbox.find('xmin').text) * scale_x)
                ymin = int(float(bbox.find('ymin').text) * scale_y)
                xmax = int(float(bbox.find('xmax').text) * scale_x)
                ymax = int(float(bbox.find('ymax').text) * scale_y)
                
                bbox.find('xmin').text = str(xmin)
                bbox.find('ymin').text = str(ymin)
                bbox.find('xmax').text = str(xmax)
                bbox.find('ymax').text = str(ymax)
            
            output_xml_path = os.path.join(output_folder, base_name + '.xml')
            tree.write(output_xml_path)
            
            print(f"Processed: {filename}")

image_folder = r"C:\Users\pallavi.zadokar\Downloads\tabel_last"  
output_folder = r"C:\Users\pallavi.zadokar\Downloads\tabel_last\resize"  
resize_image_and_xml(image_folder, output_folder)

import streamlit as st
import os
import xml.etree.ElementTree as ET
import json
import shutil
import zipfile

def pascal_voc_to_coco(x1, y1, x2, y2):
    return [x1, y1, x2 - x1, y2 - y1]

def get_label2id(labels_path):
    label2id = {}
    with open(labels_path, 'r') as f:
        for idx, label in enumerate(f):
            label = label.strip()
            label2id[label] = idx + 1
    return label2id

def convert_xml_to_coco(xml_folder_path, labels_path, output_folder):

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    os.makedirs(output_folder)


    label2id = get_label2id(labels_path)

    for xml_file in os.listdir(xml_folder_path):
        if not xml_file.endswith('.xml'):
            continue

        xml_path = os.path.join(xml_folder_path, xml_file)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        image_info = {}
        image_info['file_name'] = xml_file.replace('.xml', '.png')
        image_info['id'] = 1  
        image_info['height'] = int(root.find('size').find('height').text)
        image_info['width'] = int(root.find('size').find('width').text)

        coco_data = {'images': [], 'annotations': [], 'categories': []}
        annotation_id = 1

        coco_data['images'].append(image_info)

        for obj in root.findall('object'):
            category = obj.find('name').text
            if category not in label2id:
                continue

            bbox = obj.find('bndbox')
            x1 = int(bbox.find('xmin').text)
            y1 = int(bbox.find('ymin').text)
            x2 = int(bbox.find('xmax').text)
            y2 = int(bbox.find('ymax').text)
            bbox_coco = pascal_voc_to_coco(x1, y1, x2, y2)

            annotation = {
                'image_id': image_info['id'],
                'bbox': bbox_coco,
                'category_id': label2id[category],
                'iscrowd': 0,
                'area': (x2 - x1) * (y2 - y1),
                'id': annotation_id
            }
            coco_data['annotations'].append(annotation)
            annotation_id += 1

        for label, label_id in label2id.items():
            coco_data['categories'].append({'id': label_id, 'name': label})

        output_json_path = os.path.join(output_folder, f'{xml_file.replace(".xml", "")}_coco.json')
        with open(output_json_path, 'w') as f:
            json.dump(coco_data, f)

    st.success("COCO conversion completed successfully.")
    return output_folder

def main():
    st.title("Convert XML to COCO")

    xml_folder_path = r"D:\multi_page_app\batch2_zip_file 3"  
    labels_path = r"D:\multi_page_app\labels.txt"  
    output_folder = r"D:\multi_page_app\coco_data"  

    if st.checkbox("Convert XML to COCO"):
        try:
            output_folder = convert_xml_to_coco(xml_folder_path, labels_path, output_folder)
            shutil.make_archive(output_folder, 'zip', output_folder)
            zip_file_path = output_folder + ".zip"
            with open(zip_file_path, 'rb') as f:
                bytes_data = f.read()
            st.download_button(label="Download COCO Data", data=bytes_data, file_name='coco_data.zip')
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


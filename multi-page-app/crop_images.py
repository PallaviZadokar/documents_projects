import os
import xml.etree.ElementTree as ET
from PIL import Image
import zipfile
import io
import streamlit as st

# Function to create XML files for cropped images of a specific class
def create_xml_files_for_class(class_name, count, folder_path):
    cropped_count = 0  
    annotation_data = []  

    temp_dir = r"D:\multi_page_app\temp_xml"
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.endswith((".jpg", ".jpeg", ".png")) and cropped_count < count:
            image_file = os.path.join(folder_path, filename)
            xml_file = os.path.splitext(image_file)[0] + ".xml"

            if not os.path.exists(xml_file):
                continue

            tree = ET.parse(xml_file)
            root = tree.getroot()
            for obj in root.findall(".//object"):
                if obj.find("name").text == class_name:
                    bbox = obj.find("bndbox")
                    xmin = int(bbox.find("xmin").text)
                    ymin = int(bbox.find("ymin").text)
                    xmax = int(bbox.find("xmax").text)
                    ymax = int(bbox.find("ymax").text)

                    image = Image.open(image_file)
                    cropped_image = image.crop((xmin, ymin, xmax, ymax))

                    if cropped_image.mode != "RGB":
                        cropped_image = cropped_image.convert("RGB")

                    cropped_image_filename = f"{class_name}_{cropped_count}.jpg"
                    cropped_image_path = os.path.join(temp_dir, cropped_image_filename)
                    cropped_image.save(cropped_image_path)

                    annotation_data.append({
                        'filename': cropped_image_filename,
                        'bbox': (xmin, ymin, xmax, ymax)
                    })

                    cropped_count += 1

                    if cropped_count >= count:
                        break

        if cropped_count >= count:
            break

    for data in annotation_data:
        xml_root = ET.Element("annotation")
        obj = ET.SubElement(xml_root, "object")
        ET.SubElement(obj, "name").text = class_name
        bndbox = ET.SubElement(obj, "bndbox")
        xmin, ymin, xmax, ymax = data['bbox']
        ET.SubElement(bndbox, "xmin").text = str(xmin)
        ET.SubElement(bndbox, "ymin").text = str(ymin)
        ET.SubElement(bndbox, "xmax").text = str(xmax)
        ET.SubElement(bndbox, "ymax").text = str(ymax)
        xml_content = ET.tostring(xml_root)
        xml_filename = os.path.join(temp_dir, f"{os.path.splitext(data['filename'])[0]}.xml")
        with open(xml_filename, "wb") as xml_file:
            xml_file.write(xml_content)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for filename in os.listdir(temp_dir):
            if filename.endswith(".xml"):
                zip_file.write(os.path.join(temp_dir, filename), arcname=filename)

    for filename in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, filename))
    os.rmdir(temp_dir)

    return zip_buffer.getvalue()

def main():
    st.title("Classes and Annotations")

    dataset_dir = r"D:\hf\code\data_code\temporary\old_data" 
    class_names = set()  
    for filename in os.listdir(dataset_dir):
        if filename.endswith(".xml"):
            tree = ET.parse(os.path.join(dataset_dir, filename))
            root = tree.getroot()
            for obj in root.findall(".//object"):
                class_names.add(obj.find("name").text)
    class_names = list(class_names)
    selected_class = st.selectbox("Select class", class_names)

    count = st.number_input("Enter count", min_value=1, step=1)

    if st.button("Get Annotations"):
        xml_data = create_xml_files_for_class(selected_class, count, dataset_dir)
        st.download_button("Download XML files", xml_data, file_name=f"{selected_class}_xml_files.zip", mime="application/zip")

if __name__ == "__main__":
    main()

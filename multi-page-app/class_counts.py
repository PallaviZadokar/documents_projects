import streamlit as st
import os
import xml.etree.ElementTree as ET

# Function to get class names and their counts
def get_class_counts(folder_path):
    class_counts = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            xml_file = os.path.join(folder_path, filename)
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for obj in root.findall(".//object"):
                class_name = obj.find("name").text
                if class_name in class_counts:
                    class_counts[class_name] += 1
                else:
                    class_counts[class_name] = 1

    return class_counts


def main():
    
    if st.button("Show Class Counts"):
        dataset_dir = r"D:\hf\code\data_code\temporary\old_data"
        if os.path.exists(dataset_dir):
            class_counts = get_class_counts(dataset_dir)
            class_options = [f"{class_name} ({count})" for class_name, count in class_counts.items()]
            st.selectbox("Classes List with count", class_options)

        else:
            st.error("Dataset directory not found.")

if __name__ == "__main__":
    main()

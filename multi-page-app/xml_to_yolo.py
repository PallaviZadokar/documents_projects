import streamlit as st
import os
import zipfile
from io import BytesIO
from pylabel import importer
import shutil 

def main():
    st.title("Convert XML to YOLO")

    training_folder_path = r"D:\multi_page_app\training"

    if os.path.exists(training_folder_path):
        
        try:
            shutil.rmtree(training_folder_path)
        except OSError as e:
            st.error(f"Error: {training_folder_path} : {e.strerror}")

    
    if st.checkbox("YOLO"):
        xml_folder_path = r"D:\hf\code\data_code\temporary\540_data"  
        try:
            dataset = importer.ImportVOC(path=xml_folder_path)
            yolo_folder = dataset.export.ExportToYoloV5()
            st.success("YOLO conversion completed successfully.")
            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(training_folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zip_file.write(file_path, os.path.relpath(file_path, training_folder_path))
            zip_buffer.seek(0)

            
            st.download_button(
                label="Download Yolo data",
                data=zip_buffer,
                file_name="training_folder.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

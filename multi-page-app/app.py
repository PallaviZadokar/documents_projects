import streamlit as st
# homepage
def main():
    st.title("MultiPage data App")

    
    page = st.sidebar.selectbox("Select a page",
                                ["Home", "Class Counts", "Class Annotation", "Convert to COCO", "Convert to YOLO"])

    if page == "Home":
        st.write("Welcome to the MultiPage Data App!")

    elif page == "Class Counts":
        from class_counts import main as class_counts_app
        class_counts_app()

    elif page == "Class Annotation":
        from crop_images import main as crop_images_app
        crop_images_app()

    elif page == "Convert to COCO":
        from xml_to_coco import main as xml_to_coco_app
        xml_to_coco_app()

    elif page == "Convert to YOLO":
        from xml_to_yolo import main as xml_to_yolo_app
        xml_to_yolo_app()


if __name__ == "__main__":
    main()

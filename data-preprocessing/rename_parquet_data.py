import os

folder_path = r"D:\hf\data\annotated_downloaded\websight_krishna"

def rename_files(folder_path):
    for filename in os.listdir(folder_path):

        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG', '.gif')):
            new_filename = 'p6_' + filename
        elif filename.lower().endswith('.xml'):
            new_filename = 'p6_' + filename  
        else:
            continue  
        
        old_filepath = os.path.join(folder_path, filename)
        new_filepath = os.path.join(folder_path, new_filename)

        os.rename(old_filepath, new_filepath)
        print(f'Renamed: {filename} to {new_filename}')

rename_files(folder_path)

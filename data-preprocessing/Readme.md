This repository contains code for various data preprocessing operations

class_counts.py: Retrieves class counts to assess necessary dataset modifications.

img_sep.py: Separates images and xml files into distinct folders.

remove_class.py: Removes classes not included in a predefined standard list.

remove_img.py: Deletes images for which corresponding xml files are not present.

rename_class.py: Renames classes not included in a predefined standard list to handle spelling mistakes and other inconsistencies.

rename_files.py: Standardizes file names by removing special characters and converts images to .jpg format; updates corresponding xml files.

rename_parquet_data.py: Renames image and xml files extracted from parquet files.

resize.py: Resizes all images to a uniform size.

The final step of data cleaning and preprocessing involves verifying annotations using the labelImg tool.


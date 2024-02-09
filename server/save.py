import os
from pathlib import Path


MEDIA_PATH = 'media'

def get_file_names_by_time(directory: str):
    if not os.path.exists(MEDIA_PATH):
        os.mkdir(MEDIA_PATH)
    return [str(os.path.basename(file_path)) for file_path in sorted(Path(directory).iterdir(), key=os.path.getmtime, reverse=True)]
    
def save_image_file(img_data: bytes) -> str:
    image_file_names = get_file_names_by_time(MEDIA_PATH)
    number_suffix = 1
    
    if len(image_file_names) > 0:
        number_suffix = int(image_file_names[0].split('_')[-1].split('.')[0]) + 1

    formatted_save_path = f'media/image_{number_suffix}.png'
    save_path = os.path.join(MEDIA_PATH, f'image_{number_suffix}.png')
    
    with open(save_path, 'wb') as f:
        f.write(img_data)
        
    return formatted_save_path
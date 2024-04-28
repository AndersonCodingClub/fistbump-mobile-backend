import os
from pathlib import Path


POST_PATH = 'media/posts'
PROFILE_PATH = 'media/pfps'

def get_file_names_by_time(directory: str):
    if not os.path.exists(POST_PATH):
        os.makedirs(POST_PATH)
    return [str(os.path.basename(file_path)) for file_path in sorted(Path(directory).iterdir(), key=os.path.getmtime, reverse=True)]
    
def save_post(img_data: bytes) -> str:
    image_file_names = get_file_names_by_time(POST_PATH)
    number_suffix = 1
    
    if len(image_file_names) > 0:
        number_suffix = int(image_file_names[0].split('_')[-1].split('.')[0]) + 1

    save_path = os.path.join(POST_PATH, f'image_{number_suffix}.png')
    
    with open(save_path, 'wb') as f:
        f.write(img_data)
        
    return save_path
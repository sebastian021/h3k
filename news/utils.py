from PIL import Image as PILImage
import os

def create_thumbnails(image_path):
    image = PILImage.open(image_path)
    
    size_160 = (160, 160)
    thumbnail_160 = image.copy()
    thumbnail_160.thumbnail(size_160)
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    thumbnail_160_path = os.path.join(os.path.dirname(image_path), f'160-{image_name}.jpg')
    thumbnail_160.save(thumbnail_160_path)
    
    size_480 = (480, 480)
    thumbnail_480 = image.copy()
    thumbnail_480.thumbnail(size_480)
    thumbnail_480_path = os.path.join(os.path.dirname(image_path), f'480-{image_name}.jpg')
    thumbnail_480.save(thumbnail_480_path)
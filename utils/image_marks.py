import os
import django
import json
from urllib.parse import urljoin

# Set the Django settings module before importing any Django modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

from conf import settings
from basic_app.models import Images


# def mark_images():
#     base_url = settings.BASE_URL  # Assuming your base URL is defined in settings
#     media_url = settings.MEDIA_URL  # Assuming your media URL is defined in settings

#     # Use Images instead of models.Images
#     mark_images_data = Images.objects.values('id', 'mark_name_for_image', 'image')

#     # Create a list to store the updated data with full image URLs
#     updated_mark_images_data = []

#     for item in mark_images_data:
#         # Get the Image instance
#         image_instance = Images.objects.get(id=item['id'])

#         # Obtain the relative URL of the image
#         image_relative_url = image_instance.image.url

#         # Join the base URL with the media URL and relative URL to get the full image URL
#         full_image_url = urljoin(urljoin(base_url, media_url), image_relative_url)

#         # Add the 'full_image_url' key to the dictionary
#         item['full_image_url'] = full_image_url

#         # Remove the 'image' and 'id' keys if you don't need them in the output
#         item.pop('image')
#         item.pop('id')

#         updated_mark_images_data.append(item)

#     # print(json.dumps(updated_mark_images_data, indent=4, ensure_ascii=False))
#     return updated_mark_images_data

# # print(mark_images())


def build_img_url(media_url, image_relative_url):
    # Hypothetical function to construct the full image URL
    # This implementation depends on how your project constructs URLs
    return f"{settings.BASE_URL}{media_url}{image_relative_url}"

def mark_images():
    media_url = settings.MEDIA_URL  # Assuming your media URL is defined in settings

    # Use Images instead of Images.objects
    mark_images_data = Images.objects.values('id', 'mark_name_for_image', 'image')

    # Create a list to store the updated data with full image URLs
    updated_mark_images_data = []

    for item in mark_images_data:
        # Directly build the full image URL using a helper function
        full_image_url = build_img_url(media_url, item['image'])

        # Update the dictionary with the 'full_image_url' key
        item['full_image_url'] = full_image_url

        # Remove the 'image' and 'id' keys if you don't need them in the output
        item.pop('image')
        item.pop('id')

        updated_mark_images_data.append(item)

    return updated_mark_images_data

# Example usage
# print(mark_images())
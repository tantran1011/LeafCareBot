import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

cloudinary.config( 
    cloud_name = "dsag3z2tf", 
    api_key = "972445746237753", 
    api_secret = os.getenv("CLOUD_API_SECRET_KEY"),
    secure=True
)

def img2cloud(file, id):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"user{id}_{timestamp}"

    result = cloudinary.uploader.upload(
            file.file,
            public_id=f"leafcare/{new_filename}",  
            overwrite=True,
            resource_type="image"
        )
    file_cloud_url = result["secure_url"]
    return file_cloud_url
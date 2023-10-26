import boto3
import requests
from io import BytesIO
from dotenv import load_dotenv
import os
import hashlib
load_dotenv()

S3_REGION = os.getenv('S3_REGION')
S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
S3_ACCESS_SECRET_KEY = os.getenv('S3_ACCESS_SECRET_KEY')
S3_COMMON_BUCKET = os.getenv('S3_COMMON_BUCKET')
S3_UPLOAD_DOMAIN = os.getenv('S3_UPLOAD_DOMAIN')


def upload_image_to_s3(image_url):
   response = requests.get(image_url)
   object_name = hashlib.sha256(response.content).hexdigest() + '.jpg'
   
   if response.status_code == 200:
      image_data = BytesIO(response.content)
      s3 = boto3.client('s3',
                        region_name=S3_REGION,
                        aws_access_key_id=S3_ACCESS_KEY_ID,
                        aws_secret_access_key=S3_ACCESS_SECRET_KEY)
      s3.upload_fileobj(image_data,S3_COMMON_BUCKET, object_name, ExtraArgs={'ContentType': 'image/jpeg'})
      return f'https://{S3_COMMON_BUCKET}.s3.{S3_REGION}.amazonaws.com/{object_name}'
   else:
      print("Failed to download the image.")
      return image_url
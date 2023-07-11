from pyuploadcare import Uploadcare
import os

pub_key = os.environ.get('UploadCare_PUBLIC_KEY')
secret_key = os.environ.get('UploadCare_SECRET_KEY')

def uploadfile(file):
    uploadcare = Uploadcare(public_key=pub_key, secret_key=secret_key)
    with open(file, 'rb') as file_object:
        ucare_file = uploadcare.upload(file_object)

    return ucare_file.cdn_url

if __name__ == '__main__':
    file = "web_flask/main/pexels-adrien-olichon-2387793.jpg"
    data = uploadfile(file)
    print(data)

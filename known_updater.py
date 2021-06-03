#source: https://buraksenol.medium.com/pass-images-to-html-without-saving-them-as-files-using-python-flask-b055f29908a
from flask import Flask, render_template
from PIL import Image
import base64
import io
import os

app = Flask(__name__, template_folder= 'protecc_frontend')

dirname = os.path.dirname(__file__)
image_path = os.path.join(dirname, 'protecc_backend/known_faces')
i_listing = os.listdir(image_path)

#gets the latest image and saves it to img_data for the HTML tag to use
@app.route('/')
def start():
    l_img = get_latest_image(image_path)

    print(l_img)
    
    im = Image.open(l_img)
    data = io.BytesIO()
    im.save(data, "PNG")
    encoded_img_data = base64.b64encode(data.getvalue())

    return render_template("trustdir.html", img_data_t=encoded_img_data.decode('utf-8'))

#Gets the path of the latest image
def get_latest_image(dirpath, valid_extensions=('jpg','jpeg','png')):
    """
    Get the latest image file in the given directory
    """

    # get filepaths of all files and dirs in the given dir
    valid_files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath)]
    # filter out directories, no-extension, and wrong extension files
    valid_files = [f for f in valid_files if '.' in f and \
        f.rsplit('.',1)[-1] in valid_extensions and os.path.isfile(f)]

    if not valid_files:
        raise ValueError("No valid images in %s" % dirpath)

    return max(valid_files, key=os.path.getmtime) 


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
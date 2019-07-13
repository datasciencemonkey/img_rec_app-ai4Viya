import os
import imghdr
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, ValidationError
from wtforms.validators import DataRequired
import base64
import cv2
import requests
import sys
import time
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
bootstrap = Bootstrap(app)

esp_host = "http://esphost.yourserver.com"
http_port = 6123

if os.path.exists("C:\\Users\\sagang\\Google Drive\\work\\esp\\python-esp"):
    sys.path.append("C:\\Users\\sagang\\Google Drive\\work\\esp\\python-esp")
    import esppy

    print("INFO: ESPPY - Loaded & ready to be used")
else:
    print("ERROR: Cannot Load ESPPY!")

# Connect to ESP Server

# # Create publishers on the source window so we can send data when needed

#
print("INFO: Set Up Complete! publisher ready to push data into source")


# subscribing to the model_score window to get the results back.
# model_score = proj.windows['w_score']
# model_score.subscribe()
# print("INFO: Client subscribed to the scoring window")


class UploadForm(FlaskForm):
    image_file = FileField('Select Image file', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_image_file(self, field):
        if (field.data.filename[-4:].lower() != '.jpg') and (field.data.filename[-5:].lower() != '.jpeg'):
            raise ValidationError('Invalid file extension')
        # imghdr finds if the file format is correct
        if imghdr.what(field.data) != 'jpeg':
            raise ValidationError('Invalid image format')


@app.route('/', methods=['GET', 'POST'])
def index():
    image = None
    form = UploadForm()
    label = None
    result_series = None
    if form.validate_on_submit():
        image = 'uploads/' + form.image_file.data.filename
        form.image_file.data.save(os.path.join(app.static_folder, image))

        # read the image again, move it to ESP
        f = cv2.imread(os.path.join(app.static_folder, image))
        img_id = random.randint(10, 999999999)

        # Encode the image and ship to ESP
        returnvalue, array_in_buffer = cv2.imencode('.jpg', f)
        encoded_string = base64.b64encode(array_in_buffer)

        esp = esppy.ESP(f'{esp_host}:{http_port}')
        print(f"INFO: Connected to ESP Server :- {esp}")

        proj = esp.get_project('sir_fred_retail')

        model_request = proj.windows['w_request']

        # Load up ASTORE and set it up for hot loading

        # load the model
        pub = model_request.create_publisher(blocksize=1, rate=0, pause=0,
                                             dateformat='%Y%m%dT%H:%M:%S.%f', opcode='insert', format='csv')
        strToSend = 'i,n,1,"action","load"\n'
        pub.send(strToSend)

        strToSend = 'i,n,2,"type","astore"\n'
        pub.send(strToSend)

        strToSend = 'i,n,3,"reference","/home/cloud-user/race_img_bkp_full/s_Img_Recognition/resnet101_notop.astore"\n'
        pub.send(strToSend)

        strToSend = 'i,n,4,,\n'
        pub.send(strToSend)

        print("INFO: ASTORE loaded into ESP for Scoring")

        src = proj.windows['w_data']
        src_pub = src.create_publisher(blocksize=1, rate=0, pause=0,
                                       dateformat='%Y%m%dT%H:%M:%S.%f', opcode='insert', format='csv')

        model_score = proj.windows['w_score']
        model_score.subscribe()

        strToSend = f"i,n,{img_id}," + encoded_string.decode() + "\n";
        src_pub.send(strToSend)
        print(f"INFO: Image {img_id} published into ESP at {time.ctime()}")

        # request_url = f'{esp_host}:{http_port}/SASESP/windows/sir_fred_retail/contquery/w_data/state?value=injected'
        # payload = {"_body":{
        #             "id" :f"{img_id}",
        #             "image":f"{encoded_string.decode()}"
        #             }}
        # headers = {'content-type': 'application/json'}
        #
        # r = requests.put(request_url,payload,headers=headers)
        # try:
        #     r.raise_for_status()
        #     if r.status_code==200:
        #         print(f"INFO: Image {img_id} published into ESP at {time.ctime()}")
        # except requests.HTTPError as e:
        #     print("Could not send image to ESP!")
        #     print("Error" + str(e))
        # toy with this - n/w latency - might not need for a true edge deployment
        active_scoring = True
        start = time.time()
        while active_scoring:
            try:
                if len(model_score.data) > 0:
                    result_series = model_score.data.loc[img_id]

                    label = result_series[0].strip()
                    result_series = result_series.to_frame().to_html()

                    active_scoring = False
                    end = time.time()
                    score_time = end - start
                    print(f"total score time of {score_time} seconds")
                else:
                    pass
            except:
                pass

        # might want to refactor this later - but works for the demo
    request_url = f'{esp_host}:{http_port}/SASESP/server/state'
    payload = {"value": "reloaded"}

    r = requests.put(request_url, params=payload)
    try:
        r.raise_for_status()
        if r.status_code == 200:
            print("INFO: Remote ESP Server Reloaded for another run!")
    except requests.HTTPError as e:
        print("ERROR: Could not reload the remote ESP server - shutdown & reload manually")
        print("Error: " + str(e))

    return render_template('index.html', form=form, image=image, label=label,
                           result_series=result_series)


if __name__ == '__main__':
    app.run(debug=True)

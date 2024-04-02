from flask import Flask, render_template, Response, redirect
import cv2
import os
from simple_facerec import SimpleFacerec
import time

from twilio.rest import Client


account_sid = "AC01b517bb23832567b8957e0e72b961b2"
auth_token = "2c4db09705e70829913253463dbc82d9"
client = Client(account_sid, auth_token)

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Initialize SimpleFacerec
sfr = SimpleFacerec()
sfr.load_encoding_images(r"C:\Users\rajmu\source code\images")  # Update the path to your image directory
directory = r'C:\Users\rajmu\PycharmProjects\face\static\Image'

# Load Camera
cap = cv2.VideoCapture(0)

# Variable to store the current name
current_name = "NO_ONE"

def get_jpg_images(directory):
    jpg_images = []
    for filename in os.listdir(directory):
        if filename.endswith('.jpg'):
            jpg_images.append(filename)
    return jpg_images

def get_jpeg_images(directory):
    jpeg_images = []
    for filename in os.listdir(directory):
        if filename.endswith('.jpeg'):
            jpeg_images.append(filename)
    return jpeg_images

def detect_faces(frame):
    global current_name

    # Detect Faces
    face_locations, face_names = sfr.detect_known_faces(frame)
    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

        # Update the current name only if it's different from the new name
        if name != current_name:
            current_name = name
            print("Detected Name:", current_name)  # Print the detected name for debugging


        cv2.putText(frame, current_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 200), 4)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        cv2.imwrite(r'C:\Users\rajmu\source code\Output\img' + timestr + ".jpg", frame.copy())
        cv2.imwrite(r'C:\Users\rajmu\PycharmProjects\face\static\Image\img' + timestr + ".jpg", frame.copy())
        if (name == "Unknown"):
            call = client.calls.create(
                twiml='<Response><Say>Some Unknown person has entered your Property</Say></Response>',
                to="+919523812688",
                from_="+13343578518"
            )
            print(call.sid)

            message = client.messages.create(
                body="Someone Unknown Person has Entered",
                from_="+13343578518",
                to="+919523812688"
            )
            print(message.sid)


        else:
            message = client.messages.create(
                body="Someone Entered - " + name,
                from_="+13343578518",
                to="+919523812688"
            )
            print(message.sid)


        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            detect_faces(frame)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    global current_name
    print("Current Name in Index Function:", current_name)  # Print current_name for debugging
    return render_template('index.html', name=current_name)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/database')
def display_images():
    jpg_images = get_jpg_images(directory)
    return render_template('images.html', jpg_images=jpg_images)

@app.route('/redirect', methods=['POST'])
def redirect_to_image_website():
    # Redirect to the show_image
    jpg_images = get_jpg_images(directory)
    return redirect('/show_image')

@app.route('/show_image')
def show_image():
    jpg_images = get_jpg_images(directory)
    return render_template('images.html', jpg_images=jpg_images)


@app.route('/database')
def display_img():
    jpeg_images = get_jpeg_images(directory)
    return render_template('img.html', jpg_images=jpeg_images)

@app.route('/red', methods=['POST'])
def redirect_to_img_website():
    # Redirect to the show_image
    jpeg_images = get_jpeg_images(directory)
    return redirect('/show')

@app.route('/show')
def show_img():
    jpeg_images = get_jpeg_images(directory)
    return render_template('img.html', jpg_images=jpeg_images)

if __name__ == "__main__":
    app.run(debug=True)

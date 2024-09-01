import cv2
import numpy as np
import face_recognition
import os
import pickle
import requests
from PIL import Image
from io import BytesIO

def load_encodings(filename='encodings.pkl'):
    if os.path.isfile(filename):
        try:
            with open(filename, 'rb') as f:
                encodeListKnown = pickle.load(f)
            print("Encodings loaded from", filename)
        except Exception as e:
            print(f"Error loading encodings: {e}")
            encodeListKnown = None
    else:
        print("No encoding file found. Please compute encodings first.")
        print("Encoding creation time depends on the data...")
        encodeListKnown = None
    return encodeListKnown

def save_encodings(encodeListKnown, filename='encodings.pkl'):
    try:
        with open(filename, 'wb') as f:
            pickle.dump(encodeListKnown, f)
        print("Encodings saved to", filename)
    except Exception as e:
        print(f"Error saving encodings: {e}")

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(img)
        if face_encodings:
            encodeList.extend(face_encodings)
        else:
            print("No faces found in image.")
    return encodeList

def markAttendance(name):
    file_exists = os.path.isfile('Attendance.csv')
    
    if not file_exists:
        with open('Attendance.csv', 'w') as excel_file:
            excel_file.write('Name,Status\n')
    
    with open('Attendance.csv', 'r+') as excel_file:
        myDataList = excel_file.readlines()
        nameList = [line.strip().split(',')[0] for line in myDataList]
        
        if name not in nameList:
            excel_file.write(f'\n{name},present')
            print(f"Attendance for {name} recorded as present.")
        else:
            print(f"Attendance for {name} is already recorded.")

THRESHOLD = 0.2
IMAGE_URL = 'http://127.0.0.1:8000/uploads/two.png'

path = 'img'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    currentImg = cv2.imread(f'{path}/{cl}')
    images.append(currentImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

encodeListKnown = load_encodings()
if encodeListKnown is None:
    encodeListKnown = findEncodings(images)
    save_encodings(encodeListKnown)
    print('Encoding Complete')
else:
    print('Encoding loaded from file')

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
        return None

def process_image(img):
    if img is None:
        print("No image to process.")
        return
    
    imgS = cv2.resize(img, (0, 0), None, 0.15, 0.15)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    print(f"Detected {len(facesCurFrame)} faces in the image.")

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)
        
        if faceDis[matchIndex] < THRESHOLD:
            name = classNames[matchIndex].upper()
        else:
            name = "Unknown"

        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        if name != "Unknown":
            markAttendance(name)

    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

img = download_image(IMAGE_URL)
process_image(img)


# uvicorn fastAPI:app --reload
# https://www.montagesphoto.com/download/go/13/172502403787072.JPG
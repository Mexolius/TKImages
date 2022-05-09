import json
import cv2
from random import randrange
from Utils.Utils import get_comparator


def findFaces(img): 
    trained_face_data = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert to grayscale
    grayscaled_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    face_coordinates = trained_face_data.detectMultiScale(grayscaled_img)

    return len(face_coordinates)

def findSmiles(img): 
    number_of_smiles = 0
    # Load some pre-trained data on face frontals from opencv (haar cascade algorithm)
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    smile_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')


    # Convert to grayscale
    grayscaled_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_detector.detectMultiScale(grayscaled_img)

    # Run the face detector within each of these faces
    for (x, y, w, h) in faces:

        # Draw a rectangle around the face
        cv2.rectangle(img, (x, y), (x+w, y+h), (100, 200, 50), 4)

        # Get the sub frame (using numpy N-diminsional array slicing)
        the_face = img[y:y+h, x:x+w]

        # Change to grayscale
        face_grayscale = cv2.cvtColor(the_face, cv2.COLOR_BGR2GRAY)

        # Detects smiles
        smiles = smile_detector.detectMultiScale(
            face_grayscale, scaleFactor=1.7, minNeighbors=20)  # scaleFactors,min_neighbours

        number_of_smiles += len(smiles)
    return number_of_smiles



def process_request(body: str):
    body = json.loads(body)
    params = body["params"]
    threshold =  float(params['threshold']) if 'threshold' in params else 0
    paths=body["paths"]

    filtered_paths = []
    comparator = get_comparator(params["comparator"], threshold)

    for path in paths:
        img = cv2.imread(path)

        if "faces" in params["type"] and not comparator(findFaces(img), int(params["no faces"])):
            continue

        if "smiles" in params["type"] and not comparator(findSmiles(img), int(params["no smiles"])):
            continue
        
        filtered_paths.append(path)
    return filtered_paths
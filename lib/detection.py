import face_recognition
from PIL import Image
import numpy as np


def find_faces_from_image(img: Image.Image) -> [(int, int, int, int)]:
    img_data = np.array(img)
    return find_faces_from_array(img_data)


def find_faces_from_array(img_data: np.array) -> [(int, int, int, int)]:
    faces = face_recognition.face_locations(img_data)

    result = []

    for face in faces:
        top, right, bottom, left = face
        print(f'A face is located @ {top}, {left}, {bottom}, {right}')

        # expand out face locations
        top -= 10
        top = max(0, top)
        bottom += 15
        bottom = min(len(img_data), bottom)

        result.append((top, right, bottom, left))

    return result

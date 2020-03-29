import face_recognition
from PIL import Image
import numpy as np
from typing import List


class FaceMetadata(object):
    def __init__(self, face_location, facial_features):
        self.__face_location = face_location
        self.__facial_features = facial_features

        super().__init__()

    def get_bounding_box(self) -> (int, int, int, int):
        return self.__face_location

    def get_facial_feature_points(self, facial_feature: str) -> [(int, int)]:
        if facial_feature not in self.__facial_features:
            raise Exception(f'the feature {facial_feature} was not detected')

        return self.__facial_features[facial_feature]


def find_faces_from_image(img: Image.Image) -> [(int, int, int, int)]:
    img_data = np.array(img)
    return find_faces_from_array(img_data)


def find_faces_from_array(img_data: np.array) -> List[FaceMetadata]:
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

        features = face_recognition.face_landmarks(img_data,
                                                   [(top, right, bottom, left)])

        if len(features) != 0:
            raise Exception(f'unexpected number of faces found: {len(features)}')
        result.append(FaceMetadata((top, right, bottom, left), features[0]))

    return result

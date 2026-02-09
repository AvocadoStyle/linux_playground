from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np

import cv2
from linux_playground.utils.path_utils.specific_paths import relative_path


model_relative_path = relative_path('models/deploy.prototxt')
model_relative_path = relative_path('models/res10_300x300_ssd_iter_140000.caffemodel')


@dataclass
class FaceModel:
    model: str
    weights: Optional[str] = None


# @dataclass
# class ModelWeights:
#     entity: str


class Model(Enum):
    HaarModel = FaceModel(model=cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    DNNModel = FaceModel(model=relative_path('models/deploy.prototxt'),
                         weights=relative_path('models/res10_300x300_ssd_iter_140000.caffemodel'))






class PersonDetectionStrategy(ABC):
    def detect(self, frame: np.ndarray) -> tuple[np.ndarray, bool]:
        raise NotImplementedError


class HaarPersonDetection(PersonDetectionStrategy):
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(Model.HaarModel.value.model)

    def detect(self, frame: np.ndarray) -> tuple[np.ndarray, bool]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )
        is_face_detected = len(faces) > 0
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame, is_face_detected

class DNNPersonDetection(PersonDetectionStrategy):
    def __init__(self):
        prototxt_path = Model.DNNModel.value.model
        weights_path = Model.DNNModel.value.weights
        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, weights_path)

    def detect(self, frame: np.ndarray) -> tuple[np.ndarray, bool]:
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
        self.net.setInput(blob)
        detections = self.net.forward()

        is_face_detected = False
        h, w = frame.shape[:2]
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype(int)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                # cv2.triangulatePoints(frame)
                is_face_detected = True
        return frame, is_face_detected


# class DNNPersonDetection()


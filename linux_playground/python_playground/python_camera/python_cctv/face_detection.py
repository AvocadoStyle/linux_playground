from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


import numpy as np

import cv2
from cv2.dnn import Net

import onnxruntime as ort

from linux_playground.utils.path_utils.specific_paths import relative_path


@dataclass
class FaceModel:
    model: Optional[str] = None
    weights: Optional[str] = None


class Model(Enum):
    HaarModel = FaceModel(model=cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    DNNModel = FaceModel(model=relative_path('models/deploy.prototxt'),
                         weights=relative_path('models/res10_300x300_ssd_iter_140000.caffemodel'))
    CNNYolo5sOnnxModel = FaceModel(model=None, weights=relative_path('models/yolov5s.onnx'))


class PersonDetectionStrategy(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray) -> tuple[np.ndarray, bool]:
        pass


class HaarPersonFaceDetection(PersonDetectionStrategy):
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


class DeepLearningPersonDetection(PersonDetectionStrategy, ABC):
    def __init__(self):
        self.prototxt_path: Optional[str] = None
        self.weights_path: Optional[str] = None
        self.set_create_net()

    @abstractmethod
    def set_create_net(self):
        pass


class DNNPersonFaceDetection(DeepLearningPersonDetection):
    def __init__(self):
        super().__init__()

    def set_create_net(self):
        self.prototxt_path = Model.DNNModel.value.model
        self.weights_path = Model.DNNModel.value.weights
        self.net = cv2.dnn.readNetFromCaffe(Model.DNNModel.value.model, Model.DNNModel.value.weights)

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


class CNNPersonDetection(DeepLearningPersonDetection):
    def __init__(self):
        super().__init__()

    def set_create_net(self):
        self.input_width = 640   # YOLOv5 default input
        self.input_height = 640
        self.weights_path = Model.CNNYolo5sOnnxModel.value.weights
        self.session = ort.InferenceSession(self.weights_path)
        self.input_name = self.session.get_inputs()[0].name

    def detect(self, frame: np.ndarray) -> tuple[np.ndarray, bool]:
        orig_h, orig_w = frame.shape[:2]

        # Preprocess
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, (self.input_width, self.input_height))
        img_input = img_resized.astype(np.float32) / 255.0
        img_input = np.transpose(img_input, (2, 0, 1))  # HWC -> CHW
        img_input = np.expand_dims(img_input, axis=0)

        # Run ONNX inference
        outputs = self.session.run(None, {self.input_name: img_input})
        detections = outputs[0]  # shape: [1, N, 85]

        is_detected = False
        for det in detections[0]:
            conf = det[4]
            if conf > 0.5:
                # YOLOv5 outputs in input size scale
                cx, cy, bw, bh = det[:4]

                # scale coordinates to original frame size
                x_scale = orig_w / self.input_width
                y_scale = orig_h / self.input_height

                x1 = int((cx - bw/2) * x_scale)
                y1 = int((cy - bh/2) * y_scale)
                x2 = int((cx + bw/2) * x_scale)
                y2 = int((cy + bh/2) * y_scale)

                # Clip to frame boundaries
                x1 = max(0, min(orig_w - 1, x1))
                y1 = max(0, min(orig_h - 1, y1))
                x2 = max(0, min(orig_w - 1, x2))
                y2 = max(0, min(orig_h - 1, y2))

                # Draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                is_detected = True

        return frame, is_detected



from dataclasses import dataclass
from enum import Enum, auto

import cv2

from linux_playground.utils.dir_utils.config_utils import config_load_yaml
from linux_playground.utils.path_utils.specific_paths import relative_path


class CameraConfig(Enum):
    video_device = auto()
    device_id = auto()
    fps = auto()
    output_file = auto()


def load_camera_config() -> dict:
    config_camera_path: str = relative_path("../config/config_camera.yaml")
    camera_config_items = config_load_yaml(config_file=config_camera_path)
    return camera_config_items

def video_capture():
    camera_config: dict = load_camera_config()
    first_device = camera_config[CameraConfig.video_device.name][0]
    camera_id = first_device[CameraConfig.device_id.name]
    output_file_name = first_device[CameraConfig.output_file.name]
    fps = first_device[CameraConfig.fps.name]
    video_cap = cv2.VideoCapture(camera_id)
    if not video_cap:
        raise ValueError("VideoCamera Not initialized properly.")
    width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # codec + writer
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_file_name, fourcc, fps, (width, height))

    while True:
        ret, frame = video_cap.read()
        if not ret:
            break
        # writing frame
        out.write(frame)
        cv2.imshow("Recording", frame)

        # ending style
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Saved to output.avi")


if __name__ == '__main__':
    video_capture()

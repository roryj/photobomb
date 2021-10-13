import time
import cv2
from multiprocessing import Process, Queue


def _display_loop(camera_number: int, request_queue: Queue):
    my_cam = cv2.VideoCapture(camera_number)
    current_text = None
    while True:
        ret_val, img = my_cam.read()

        new_text = None

        if not request_queue.empty():
            req = request_queue.get_nowait()
            if req:
                type = req.get("type")
                if type == "clear":
                    current_text = None
                elif type == "set":
                    location_x = req.get("location_x")
                    location_y = req.get("location_y")
                    current_text = req

        img = cv2.flip(img, 1)

        if current_text:
            _draw_text(img, current_text.get("text"))

        cv2.imshow("my webcam", img)
        if cv2.waitKey(1) == 27:
            break  # esc to quit

        time.sleep(0.01)


def _draw_text(img, text="what what in my butt"):
    height, width, _ = img.shape
    font_scale = 7
    thickness = 4

    (text_width, text_height), _ = cv2.getTextSize(
        text,
        fontFace=cv2.FONT_HERSHEY_COMPLEX,
        fontScale=font_scale,
        thickness=thickness,
    )
    text_location = (
        int(width / 2 - text_width / 2),
        int(height / 2 + text_height / 2),
    )

    cv2.putText(
        img,
        text=text,
        org=text_location,
        fontFace=cv2.FONT_HERSHEY_COMPLEX,
        fontScale=font_scale,
        color=[0, 0, 0],
        lineType=cv2.LINE_AA,
        thickness=thickness,
    )
    cv2.putText(
        img,
        text=text,
        org=text_location,
        fontFace=cv2.FONT_HERSHEY_COMPLEX,
        fontScale=font_scale,
        color=[255, 255, 255],
        lineType=cv2.LINE_AA,
        thickness=(thickness - 2),
    )


class PhotoboothDisplay:
    def __init__(self, camera_to_use) -> "PhotoboothDisplay":

        self.request_queue = Queue()

        Process(
            target=_display_loop, args=(camera_to_use, self.request_queue), daemon=True
        ).start()

    def put_text(self, text) -> None:
        self.request_queue.put(
            {"type": "set", "text": text, "location_x": "1", "location_y": "b"}
        )

    def clear_text(self) -> None:
        self.request_queue.put({"type": "clear"})

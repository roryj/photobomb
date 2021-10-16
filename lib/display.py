import time
import cv2
from multiprocessing import Process, Queue
import threading

class PhotoboothDisplay:
    def __init__(self, camera_to_use) -> "PhotoboothDisplay":
        self.request_queue = Queue()
        self.camera_to_use = camera_to_use
        self.wait_keys = []
        self.latch = None
        self.current_text = None

        self.running_loop = Process(
            target=self._display_loop, daemon=True
        ).start()

    def put_text(self, text, subtext="") -> None:
        self.request_queue.put(
            {"type": "set", "text": text, "subtext": subtext}
        )

    def clear_text(self) -> None:
        self.request_queue.put({"type": "clear"})

    def wait_for_input(self, text, subtext="", keys=['\n', '\r']) -> None:
        self.put_text(text, subtext)
        self.wait_keys = keys
        self.latch = CountDownLatch()
        print(f'waiting... {self.latch}, {self.wait_keys}')
        self.latch.wait()
        print('done waiting...')

    def _display_loop(self):
        my_cam = cv2.VideoCapture(self.camera_to_use)
        while True:
            ret_val, img = my_cam.read()

            if not self.request_queue.empty():
                req = self.request_queue.get_nowait()
                if req:
                    type = req.get("type")
                    if type == "clear":
                        self.current_text = None
                    elif type == "set":
                        self.current_text = req

            img = cv2.flip(img, 1)

            if self.current_text:
                self._draw_main_text(img, self.current_text.get("text"))
                self._draw_sub_text(img, self.current_text.get("subtext"))

            cv2.imshow("my webcam", img)

            if self.latch and cv2.waitKey(1) in self.wait_keys:
                self.latch.count_down()
                self.latch = None
                print('yerp')
            else :
                print(f'nope {self.latch}, {self.wait_keys}, {cv2.waitKey(1)}')
            if cv2.waitKey(1) in [27]:
                break # esc to quit

            time.sleep(0.01)


    def _draw_main_text(self, img, text="Die!"):
        height, width, _ = img.shape
        font_scale = 7
        thickness = 4

        (text_width, text_height), _ = cv2.getTextSize(
            text,
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=font_scale,
            thickness=thickness,
        )
        while text_width >= width:
            font_scale -= 1
            (text_width, text_height), _ = cv2.getTextSize(
                text,
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=font_scale,
                thickness=thickness)
        text_location = (
            int(width / 2 - text_width / 2),
            int(height / 2 + text_height / 2),
        )
        self._draw_text(img, text, text_location, font_scale, thickness)


    def _draw_sub_text(self, img, text="Kill them!"):
        self._draw_text(img, text,
            text_location=(50, 50),
            font_scale=1,
            thickness=4)


    def _draw_text(self, img, text, text_location, font_scale, thickness):
        cv2.putText(img,
            text=text,
            org=text_location,
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=font_scale,
            color=[0, 0, 0],
            lineType=cv2.LINE_AA, thickness=thickness)
        cv2.putText(img,
            text=text,
            org=text_location,
            fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=font_scale,
            color=[255, 255, 255],
            lineType=cv2.LINE_AA, thickness=(thickness - 2))


class CountDownLatch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        self.lock.acquire()
        self.count -= 1
        if self.count <= 0:
            self.lock.notifyAll()
        self.lock.release()

    def wait(self):
        self.lock.acquire()
        while self.count > 0:
            self.lock.wait()
        self.lock.release()

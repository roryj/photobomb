#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
from typing import Optional
from pynput import keyboard
import json
import datetime

from lib.display import PhotoboothDisplay
from lib.photobooth import (
    PhotoEvent,
    Photobooth,
    PhotoPrinter,
    PhotoTaker,
    WebCamPhotoTaker,
)
from lib.mode import Mode


def main():
    print("Starting the photobooth server...")

    parser = argparse.ArgumentParser(description="Some spooky ass photobombing")
    parser.add_argument(
        "--num-photos",
        default=4,
        help="The number of photos to take",
    )
    parser.add_argument(
        "--border-size",
        default=5,
        help="The size of the border to put around all images",
    )
    parser.add_argument(
        "--photo-delay",
        default=5,
        help="The time (in seconds) to delay between taking photos",
    )
    parser.add_argument(
        "--use-webcam",
        help="Specify the index of the webcam to use. Built in webcam is usually 0.",
        default=-0,
    )
    parser.add_argument(
        "--should-print",
        dest="should_print",
        action="store_true",
        help="Whether the resulting photo should actually be printed",
    )
    parser.add_argument(
        "--mode",
        type=Mode.from_string,
        choices=list(Mode),
        help="Which mode to use for the displayed text and effects",
        default=Mode.spooky,
    )
    parser.add_argument(
        "--event-config",
        dest="event_json",
        help='Event to trigger at a specific photobooth moment. Should be a json in the format: {"photo_number": 2, "second_to_send_it": 2, "event_name": "spooky", "spooky_tech_client_port": 5425}',
    )

    args = parser.parse_args()
    print(f"Starting the photobooth with params: {args}")
    print(args.mode.ascii_art())

    printer = PhotoPrinter("./output", "photobooth", "png", args.should_print)

    webcam_to_use = int(args.use_webcam)

    photo_taker: PhotoTaker = WebCamPhotoTaker(webcam_to_use)
    display = PhotoboothDisplay(webcam_to_use)

    photo_event = PhotoEvent(**json.loads(args.event_json)) if args.event_json else None

    photobooth = Photobooth(
        display,
        photo_taker,
        printer,
        int(args.num_photos),
        int(args.border_size),
        float(args.photo_delay),
        args.mode,
        photo_event=photo_event,
    )

    server = PhotoboothServer(photobooth, display, args.mode.get_title(), args.mode.start_prompt())
    server.start()


@dataclass
class PhotoboothServer:
    photobooth: Photobooth
    display: PhotoboothDisplay
    title: str
    start_prompt: str
    should_send_text: bool
    display_text: Optional[str] = None
    sub_text: Optional[str] = None
    input_so_far: str = ""
    last_input: str = ""
    last_input_time: datetime.datetime = datetime.datetime.now()

    def __init__(self, photobooth: Photobooth, display: PhotoboothDisplay, title: str, start_prompt: str):
        self.photobooth = photobooth
        self.display = display
        self.display_text = None
        self.title = title
        self.start_prompt = start_prompt

    def reset(self):
        print("resetting")
        self.input_so_far = ""
        self.last_input = ""
        self.last_input_time = datetime.datetime.now()
        self.update_display_text(self.start_prompt, self.title)

    def start(self):
        print("Server starting...")
        self.reset()
        while True:
            try:
                self.update_display_text("Press ENTER to get SPOOKED!", "🦴in your bones🦴")
                _ = input("Press ENTER to start the photobooth...")
                print("Running photobooth")
                (original_photos, spooked_photos) = self.photobooth.run()

                self.reset()
            except KeyboardInterrupt:
                return

    def update_display_text(self, main_text, sub_text=""):
        # if self.display_text == main_text and self.sub_text == sub_text:
        #    return
        self.display_text = main_text
        self.sub_text = sub_text
        # do the actual update on the display
        self.display.clear_text()
        self.display.put_text(self.display_text, self.sub_text)


if __name__ == "__main__":
    main()

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
        "--send-text",
        dest="send_text",
        action="store_true",
        help="Whether to collect a phone number and text photos",
    )
    parser.add_argument(
        "--event-config",
        dest="event_json",
        help='Event to trigger at a specific photobooth moment. Should be a json in the format: {"photo_number": 2, "event_name": "spooky", "spooky_tech_client_port": 5425}',
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
        args.send_text,
        photo_event=photo_event,
    )

    server = PhotoboothServer(photobooth, display, args.mode.get_title(), args.mode.start_prompt(), args.send_text)
    server.start()


@dataclass
class PhotoboothServer:
    photobooth: Photobooth
    display: PhotoboothDisplay
    title: str
    start_prompt: str
    should_send_text: bool
    display_text: Optional[str] = None
    same_input_wait = datetime.timedelta(seconds=0.5)
    phone_number: str = None
    input_so_far: str = ""
    last_input: str = ""
    last_input_time: datetime.datetime = datetime.datetime.now()

    def __init__(
        self, photobooth: Photobooth, display: PhotoboothDisplay, title: str, start_prompt: str, should_send_text: bool
    ):
        self.photobooth = photobooth
        self.display = display
        self.display_text = None
        self.title = title
        self.start_prompt = start_prompt
        self.should_send_text = should_send_text

    def reset(self):
        print("resetting")
        self.phone_number = None
        self.input_so_far = ""
        self.last_input = ""
        self.last_input_time = datetime.datetime.now()
        self.update_display_text(self.start_prompt, self.title)

    def start(self):
        print("Server starting...")
        self.reset()
        while True:
            try:
                self.phone_number = self.collect_input(self.should_send_text)
                if self.phone_number is None:
                    print("We don't have a valid number yet, try again")
                    continue

                print(f"Running photobooth with number {self.phone_number}")
                (original_photos, spooked_photos) = self.photobooth.run(self.phone_number)

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

    def update_input(self, new_input):
        # Handle duplicate input from long-ish key press
        current_time = datetime.datetime.now()
        if len(self.input_so_far) >= 10:
            print(f"SKIP INPUT: TOO LONG!")
            return
        elif self.last_input == new_input and self.last_input_time + PhotoboothServer.same_input_wait > current_time:
            print(f"SKIP INPUT {new_input}")
            return

        if new_input in [str(n) for n in range(0, 10)]:
            print(f"Read number character {new_input}")
            self.__on_input_updated(new_input, self.input_so_far + new_input)
            print(f"Input so far is {self.input_so_far}")

    def __on_input_updated(self, new_input, input_so_far):
        self.last_input = new_input
        self.last_input_time = datetime.datetime.now()
        self.input_so_far = input_so_far
        print(f"Input so far is {input_so_far}")
        if len(self.input_so_far) == 0:
            self.update_display_text(self.start_prompt, self.title)
        else:
            display_phone_num = self.input_so_far[0:3]
            if len(self.input_so_far) >= 3:
                display_phone_num += "-"
                display_phone_num += self.input_so_far[3:6]
            if len(self.input_so_far) >= 6:
                display_phone_num += "-"
                display_phone_num += self.input_so_far[6:10]

            self.update_display_text(display_phone_num, self.start_prompt)

    def collect_input(self, need_phone_number):
        with keyboard.Events() as events:
            # Block for 30 seconds
            event = events.get(30.0)
            input_char = ""

            if not hasattr(event, "key"):
                return None

            if hasattr(event.key, "char"):
                input_char = event.key.char

            if event.key == keyboard.Key.backspace:
                self.__on_input_updated("", self.input_so_far[:-1])
            elif event.key == keyboard.Key.enter and (len(self.input_so_far) == 10 or not need_phone_number):
                return self.input_so_far if need_phone_number else ""
            elif need_phone_number:
                self.update_input(input_char)

            return None


if __name__ == "__main__":
    main()

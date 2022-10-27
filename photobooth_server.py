#!/usr/bin/env python3

import argparse
import threading
from pynput import keyboard
import re
import datetime

from lib.display import PhotoboothDisplay
from lib.photobooth import (
    Photobooth,
    PhotoPrinter,
    PhotoTaker,
    WebCamPhotoTaker,
)


def main():
    print("Starting the photobooth server...")
    print(
        """
  .-')     _ (`-.                           .-. .-')                     .-. .-')                             .-') _    ('-. .-.
 ( OO ).  ( (OO  )                          \  ( OO )                    \  ( OO )                           (  OO) )  ( OO )  /
(_)---\_)_.`     \ .-'),-----.  .-'),-----. ,--. ,--.   ,--.   ,--.       ;-----.\  .-'),-----.  .-'),-----. /     '._ ,--. ,--.
/    _ |(__...--''( OO'  .-.  '( OO'  .-.  '|  .'   /    \  `.'  /        | .-.  | ( OO'  .-.  '( OO'  .-.  '|'--...__)|  | |  |
\  :` `. |  /  | |/   |  | |  |/   |  | |  ||      /,  .-')     /         | '-' /_)/   |  | |  |/   |  | |  |'--.  .--'|   .|  |
 '..`''.)|  |_.' |\_) |  |\|  |\_) |  |\|  ||     ' _)(OO  \   /          | .-. `. \_) |  |\|  |\_) |  |\|  |   |  |   |       |
.-._)   \|  .___.'  \ |  | |  |  \ |  | |  ||  .   \   |   /  /\_         | |  \  |  \ |  | |  |  \ |  | |  |   |  |   |  .-.  |
\       /|  |        `'  '-'  '   `'  '-'  '|  |\   \  `-./  /.__)        | '--'  /   `'  '-'  '   `'  '-'  '   |  |   |  | |  |
 `-----' `--'          `-----'      `-----' `--' '--'    `--'             `------'      `-----'      `-----'    `--'   `--' `--'
    """
    )

    parser = argparse.ArgumentParser(description="Some spooky ass photobombing")
    parser.add_argument(
        "--num-photos",
        default=4,
        help="the number of photos to take",
    )
    parser.add_argument(
        "--border-size",
        default=5,
        help="the size of the border to put around all images",
    )
    parser.add_argument(
        "--photo-delay",
        default=5,
        help="the time (in seconds) to delay between taking photos",
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
        help="whether the resulting photo should actually be printed",
    )

    args = parser.parse_args()

    print(f"Starting the photobooth with params: {args}")

    printer = PhotoPrinter("./output", "photobooth", "png", args.should_print)

    webcam_to_use = int(args.use_webcam)

    photo_taker: PhotoTaker = WebCamPhotoTaker(webcam_to_use)
    display = PhotoboothDisplay(webcam_to_use)

    photobooth = Photobooth(
        display,
        photo_taker,
        printer,
        int(args.num_photos),
        int(args.border_size),
        float(args.photo_delay),
        False
    )

    server = PhotoboothServer(photobooth, display)
    server.start()


class PhotoboothServer:
    empty_prompt = "ENTER your phone number to get SPOOKED!"
    same_input_wait = datetime.timedelta(seconds = 0.5)

    def __init__(self, photobooth, display):
        self.photobooth = photobooth
        self.display = display
        self.display_text = None

    def reset(self):
        self.phone_number = None
        self.input_so_far = ''
        self.last_input = ''
        self.last_input_time = datetime.datetime.now()
        self.update_display_text(PhotoboothServer.empty_prompt)

    def start(self):
        print("Server starting...")
        self.reset()
        while True:
            self.phone_number = self.collect_phone_number()
            if not self.phone_number:
                print("We don't have a valid number yet, try again")
                continue

            print(f"Running photobooth with number {self.phone_number}")
            (original_photos, spooked_photos) = self.photobooth.run(self.phone_number)

            self.reset()

    def update_display_text(self, main_text, sub_text=''):
        if self.display_text == main_text and self.sub_text == sub_text:
            return
        self.display_text = main_text
        self.sub_text = sub_text
        # do the actual update on the display
        self.display.clear_text()
        self.display.put_text(self.display_text, self.sub_text)

    def update_input(self, new_input):
        # Handle duplicate input from long-ish key press
        current_time = datetime.datetime.now()
        if len(self.input_so_far) >= 10:
            print(f'SKIP INPUT: TOO LONG!')
            return
        elif self.last_input == new_input and self.last_input_time + PhotoboothServer.same_input_wait > current_time:
            print(f'SKIP INPUT {new_input}')
            return
    
        if new_input in [str(n) for n in range(0, 10)]:
            print(f'Read number character {new_input}')
            self.__on_input_updated(new_input, self.input_so_far + new_input)
            print(f'Input so far is {self.input_so_far}')

    def __on_input_updated(self, new_input, input_so_far):
        self.last_input = new_input
        self.last_input_time = datetime.datetime.now()
        self.input_so_far = input_so_far
        print(f'Input so far is {input_so_far}')
        if len(self.input_so_far) == 0:
            self.update_display_text(PhotoboothServer.empty_prompt)
        else:
            self.update_display_text(self.input_so_far, PhotoboothServer.empty_prompt)

    def collect_phone_number(self):
        with keyboard.Events() as events:
            # Block for 30 seconds
            event = events.get(30.0)
            input_char = ''

            if not hasattr(event, 'key'):
                return None

            if hasattr(event.key, 'char'):
                input_char = event.key.char
            
            if event.key == keyboard.Key.backspace:
                self.__on_input_updated('', self.input_so_far[:-1])
            elif event.key == keyboard.Key.enter and len(self.input_so_far) == 10:
                return self.input_so_far
            else:
                self.update_input(input_char)

            return None

if __name__ == "__main__":
    main()

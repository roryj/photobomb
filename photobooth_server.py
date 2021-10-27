#!/usr/bin/env python3

import argparse
import threading
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
    )

    print("Server starting. Waiting on enter press...")
    while True:
        display.clear_text()
        display.put_text("Press ENTER to get SPOOKED!")
        _ = input("waiting for input...\n")
        print("detected key press!")
        print("")
        photobooth.run()


if __name__ == "__main__":
    main()

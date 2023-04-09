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
    print("Starting the PIGGYbooth server...")
    print("""
 ____ ____   ____   ____  __ __  ____    ___    ___   ______  __ __ 
|    \    | /    | /    ||  |  ||    \  /   \  /   \ |      ||  |  |
|  o  )  | |   __||   __||  |  ||  o  )|     ||     ||      ||  |  |
|   _/|  | |  |  ||  |  ||  ~  ||     ||  O  ||  O  ||_|  |_||  _  |
|  |  |  | |  |_ ||  |_ ||___, ||  O  ||     ||     |  |  |  |  |  |
|  |  |  | |     ||     ||     ||     ||     ||     |  |  |  |  |  |
|__| |____||___,_||___,_||____/ |_____| \___/  \___/   |__|  |__|__|
                                                                    
""")

    parser = argparse.ArgumentParser(description="Some piggy ass photobombing")
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

    print(f"Starting the piggybooth with params: {args}")

    printer = PhotoPrinter("./output", "piggybooth", "png", args.should_print)

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
        True
    )

    print("Server starting. Waiting on enter press...")
    while True:
        display.clear_text()
        display.put_text("Press ENTER my PIGGIES!")
        _ = input("waiting for input...\n")
        print("detected key press!")
        print("")
        photobooth.run()


if __name__ == "__main__":
    main()

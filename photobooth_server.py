import argparse
import threading

from lib.photobooth import (
    Photobooth,
    PhotoPrinter,
    PhotoTaker,
    RandomStaticPhoto,
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
        "--num-photos", default=4, help="the number of photos to take",
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
        dest="use_webcam",
        action="store_true",
        help="whether to take actual pictures using the webcam or use local files",
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

    photo_taker: PhotoTaker
    if args.use_webcam:
        photo_taker = WebCamPhotoTaker("test")
    else:
        photo_taker = RandomStaticPhoto(["./resources/input/test-image.jpg"])

    photobooth = Photobooth(
        photo_taker,
        printer,
        int(args.num_photos),
        int(args.border_size),
        float(args.photo_delay),
    )

    print(f"Server starting. Waiting on enter press...")
    while True:
        _ = input("waiting for input...\n")
        print("detected key press!")
        print("")
        thread = threading.Thread(target=photobooth.run)
        thread.start()


def stop_server():
    print("killing the server...")
    print("goodbye!")
    exit(0)


if __name__ == "__main__":
    main()

import argparse
import threading
import keyboard

from lib.photobooth import (
    FilePrinter, Photobooth, PhotoPrinter, WebCamPhotoTaker, RandomStaticPhoto,
    PhotoTaker
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
        "--init-key",
        default="k",
        help="the key press to listen for to start the photobooth workflow",
    )
    parser.add_argument(
        "--num-photos", default=4, help="the number of photos to take",
    )
    parser.add_argument(
        "--border-size",
        default=5,
        help="the size of the border to put around all images",
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
    print(f"Press 'ctrl+q' to quit")

    keyboard.add_hotkey("ctrl+q", stop_server)

    # start listening for key
    print(f"Server starting. Waiting on key: '{args.init_key}''")

    printer: PhotoPrinter
    if args.should_print:
        # TODO: This should actually print using the printer
        # once we figure out how to do that
        printer = FilePrinter("./output/result.png")
    else:
        printer = FilePrinter("./output/result.png")

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
    )

    def run_workflow(e):
        print("detected keypress!")
        thread = threading.Thread(target=photobooth.run)
        thread.start()

    keyboard.on_press_key(args.init_key, run_workflow)

    keyboard.wait()


def stop_server():
    print("killing the server...")
    print("goodbye!")
    exit(0)


if __name__ == "__main__":
    main()

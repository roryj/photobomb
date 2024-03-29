import argparse
from pathlib import Path

from lib.photobooth import Photobooth, PhotoPrinter, RandomStaticPhoto


def main():
    parser = argparse.ArgumentParser(description="Some spooky ass photobombing")
    parser.add_argument(
        "--input-files",
        nargs="+",
        help="""the list of images to include in the photobooth image.
        All images must be the same size.""",
        required=True,
    )
    parser.add_argument(
        "--border-size",
        default=5,
        help="the size of the border to put around all images",
    )
    parser.add_argument(
        "--output-file",
        help="the name of the output file",
        default="photo_booth_pic.png",
    )

    args = parser.parse_args()

    p = Path(args.output_file)
    photobooth = Photobooth(
        RandomStaticPhoto(args.input_files),
        PhotoPrinter(p.parent, p.stem, p.suffix.replace(".", ""), False),
        len(args.input_files),
        int(args.border_size),
        0.0,
    )

    photobooth.run()


if __name__ == "__main__":
    main()

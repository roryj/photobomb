import argparse

from lib.photobooth import (
    FilePrinter, Photobooth, RandomStaticPhoto
)


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

    photobooth = Photobooth(
        RandomStaticPhoto(args.input_files),
        FilePrinter(args.output_file, True),
        len(args.input_files),
        args.border_size,
    )

    photobooth.run()


if __name__ == "__main__":
    main()

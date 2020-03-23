import argparse
import math
import random

import face_recognition
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from skimage.transform import swirl

from lib.effect import GhostEffect, FaceIdentifyEffect, SwirlFaceEffect


def main():
    parser = argparse.ArgumentParser(
        description="Some spooky ass photobombing")
    parser.add_argument("--input-file",
        help="the full path to the input image file",
        required=True)
    parser.add_argument("--output-file",
        help="the name of the output file",
        default="result.png")
    parser.add_argument("--effect",
        help="the output effect on the image",
        choices=["identify-face", "swirl", "ghost", "random"],
        default="swirl")

    args = parser.parse_args()

    input_file_path = args.input_file
    output_file = args.output_file

    result: Image.Image

    if args.effect == "identify-face":
        print('processing the image to identify the faces!')
        im = Image.open(input_file_path)
        image_processor = FaceIdentifyEffect()
        result = image_processor.process_image(im)
    elif args.effect == "swirl":
        print('processing for swirl effect')
        im = Image.open(input_file_path)
        image_processor = SwirlFaceEffect(5)
        result = image_processor.process_image(im)
    elif args.effect == "ghost":
        im = Image.open(input_file_path)
        image_processor = GhostEffect()
        result = image_processor.process_image(im)
    else:
        pass

    # write to the output file
    result.save(output_file, "PNG")


if __name__ == "__main__":
    main()

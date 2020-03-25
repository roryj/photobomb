import argparse

from PIL import Image

from lib.effect import (FaceIdentifyEffect, GhostEffect, ImageEffect,
                        SwirlFaceEffect, ImageProcessingContext)
from lib.detection import find_faces_from_array

import numpy as np


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
    parser.add_argument("--effects",
                        help="the output effect on the image",
                        default="swirl")

    args = parser.parse_args()

    input_file_path = args.input_file
    output_file = args.output_file

    img = Image.open(input_file_path)
    image_processor: ImageEffect
    result: Image.Image

    context = create_context_from_image(img)

    if args.effect == "identify-face":
        print('processing the image to identify the faces!')
        image_processor = FaceIdentifyEffect()
    elif args.effect == "swirl":
        print('processing for swirl effect')
        image_processor = SwirlFaceEffect(1)
    elif args.effect == "ghost":
        print('processing for ghost effect')
        image_processor = GhostEffect()
    else:
        raise Exception(f'the effect {args.effect} is currently unsupported')

    result = image_processor.process_image(context)
    # write to the output file
    result.save(output_file, "PNG")


def create_context_from_image(img: Image) -> ImageProcessingContext:
    img_data = np.array(img)
    faces = find_faces_from_array(img_data)
    return ImageProcessingContext(img, img_data, faces)


if __name__ == "__main__":
    main()

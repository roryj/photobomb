import argparse
import math

import numpy as np
from PIL import Image

from lib.detection import find_faces_from_array
from lib.effect import (FaceIdentifyEffect, GhostEffect, ImageEffect,
                        ImageProcessingContext, SaturationEffect,
                        SketchyEyeEffect, SwirlFaceEffect)


def main():
    parser = argparse.ArgumentParser(description="Some spooky ass photobombing")
    parser.add_argument(
        "--input-files",
        nargs="+",
        help="""the list of images to include in the photobooth image.
        All images must be the same size.""",
        required=True
    )
    parser.add_argument(
        "--border-size",
        default=5,
        help="the size of the border to put around all images",
    )
    parser.add_argument(
        "--output-file",
        help="the name of the output file",
        default="photo_booth_pic.png"
    )

    args = parser.parse_args()

    """
        to create a photobooth image, we need to:
        1) get all the input files
        2) using the images, create the "final image" as a blank
        3) for each image
            a. determmine which effects to run
            b. run the effects
            c. paste each image onto their expected location inside the "final image"
        4) save the "final image"
        5) ...
        6) profit?
    """

    # 1
    image_width, image_height, contexts = setup_images_for_processing(args.input_files)

    # 2
    result_width = image_width + (2 * args.border_size)
    result_height = (image_height * len(contexts)) + ((len(contexts) + 1) * args.border_size)
    print(f'final image size: {result_width}x{result_height}')
    final_image = Image.new("RGBA", (result_width, result_height), (255, 255, 255, 255))

    # 3
    count = 0
    for context in contexts:
        processed_image = run_image_effects(context)

        x = args.border_size
        y = (count * image_height) + ((count + 1) * args.border_size)
        print(f'putting image of size {processed_image.size} into: {x},{y}')

        final_image.paste(processed_image, (x, y))
        count += 1

    # 4
    final_image.save(args.output_file, "PNG")


def run_image_effects(img: Image.Image) -> Image.Image:
    # TODO: determine the list of effects to run randomly
    effects = [FaceIdentifyEffect]

    for effect in effects:
        img = effect().process_image(img)

    img.convert('RGBA')
    return img


def setup_images_for_processing(files: [str]) -> (int, int, [ImageProcessingContext]):
    if len(files) == 0:
        raise ValueError("there must be at least one file passed in")

    prev_img = None

    contexts = []
    for file_path in files:
        img = Image.open(file_path)
        if prev_img is not None and img.size != prev_img.size:
            raise ValueError(f'the image {img.filename} is not the same size as {prev_img.filename}')

        contexts.append(create_context_from_image(img))

        prev_img = img

    return prev_img.width, prev_img.height, contexts


def create_context_from_image(img: Image) -> ImageProcessingContext:
    img_data = np.array(img)
    faces = find_faces_from_array(img_data)
    return ImageProcessingContext(img, img_data, faces)


if __name__ == "__main__":
    main()

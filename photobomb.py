import argparse
import numpy as np
import os

from PIL import Image

from lib.detection import find_faces_from_array
from lib.effect import (
    FaceIdentifyEffect,
    GhostEffect,
    ImageEffect,
    ImageProcessingContext,
    SaturationEffect,
    SketchyEyeEffect,
    SwirlFaceEffect,
)


def main():
    parser = argparse.ArgumentParser(description="Some spooky ass photobombing")
    parser.add_argument(
        "--input-file",
        help="the full path to the input image file",
        required=True,
    )
    parser.add_argument(
        "--output-dir", help="the name of the output directory",
        default="output",
    )
    parser.add_argument(
        "--effects",
        nargs="+",
        help="""the effects to apply on an image. Will be
                processed in order they are defined.
                One of -> [identify-face, swirl, ghost, saturation, eyes]""",
        required=True,
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="whether to show the processed image",
        default=False,
    )

    args = parser.parse_args()
    input_file_path = args.input_file
    output_dir = args.output_dir
    effects = args.effects

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    input_file_name = os.path.basename(input_file_path)
    output_file_name = input_file_name.split(".")[0] + "-" + "-".join(effects) + ".png"
    output_file_path = os.path.join(output_dir, output_file_name)

    img = Image.open(input_file_path)
    image_processors = []
    result: Image.Image

    context = create_context_from_image(img)

    for effect in effects:
        image_processor: ImageEffect
        if effect == "identify-face":
            print("identify face effect added")
            image_processor = FaceIdentifyEffect()
        elif effect == "swirl":
            print("swirl effect added")
            image_processor = SwirlFaceEffect(1)
        elif effect == "ghost":
            print("ghost friend effect added")
            image_processor = GhostEffect()
        elif effect == "saturation":
            print("saturation effect added")
            image_processor = SaturationEffect(0.7)
        elif effect == "eyes":
            print("eye effect added")
            image_processor = SketchyEyeEffect()
        else:
            raise Exception(f"the effect {effect} is currently unsupported")

        image_processors.append(image_processor)

    if len(image_processors) < 1:
        raise Exception(f"you must choose at least one type of image effect")

    for p in image_processors:
        print(f"applying effect: {p.__class__.__name__}")
        result = p.process_image(context)
        context.img = result
        context.img_data = np.array(result)

    # write to the output file
    result.save(output_file_path, "PNG", quality=95)

    if args.show:
        result.show()


def create_context_from_image(img: Image) -> ImageProcessingContext:
    img_data = np.array(img)
    faces = find_faces_from_array(img_data)
    return ImageProcessingContext(img, img_data, faces)


if __name__ == "__main__":
    main()

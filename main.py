import argparse
import math
import random

import face_recognition
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from skimage.transform import swirl

from lib.effect import GhostEffect, FaceIdentifyEffect


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
        image = face_recognition.load_image_file(input_file_path)
        face_locations = face_recognition.face_locations(image)

        result = swirl_faces(image, face_locations)
    elif args.effect == "ghost":
        im = Image.open(input_file_path)
        image_processor = GhostEffect()
        result = image_processor.process_image(im)
    else:
        pass

    # write to the output file
    result.save(output_file, "PNG")

def swirl_faces(img: np.array, faces) -> Image.Image:

    im = Image.fromarray(img)

    for face_location in faces:

        # Print the location of each face in this image
        top, right, bottom, left = face_location 
        print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        # create a new image based on the current face
        face = Image.fromarray(img[top:bottom, left:right])
        
        # swirl the face
        processed_face = swirl(face, 5)
        # add some alpha to the swirled image to make it less opaque
        processed_face.putalpha(100)
        # add a little bit of blur so that it is not so perfectly swirled
        processed_face = processed_face.filter(ImageFilter.BLUR)

        # merge the face with the original image
        im.paste(processed_face, (left, top, right, bottom))

    return im


def swirl(img: Image.Image, strength: int) -> Image.Image:

    # create a copy so that the orignal is not changed
    # not necessarily needed, but does avoid weird side effects
    to_swirl = img.copy() 

    left = 0
    top = 0
    bottom = to_swirl.height - 1
    right = to_swirl.width - 1

    if bottom > right:
        radius = ((right - left) / 2) - 8
    else:
        radius = ((bottom - top) / 2) - 8 

    centerx = int(right / 2)
    centery = int(bottom / 2)

    for x in range(left, right):
        for y in range(top, bottom):
            # 1) convert to u,v space
            u = x - centerx
            v = y - centery

            # if w are at the center point of the swirl, do nothing
            if u == 0 and v == 0:
                break

            # 2) get the distance from pixel to the center and the angle
            # c = sqrt(u^2 + v^2)
            # thanks pythagoreous
            c = math.sqrt(math.pow(u, 2) + math.pow(v, 2))
            pixel_angle = math.atan2(v, u)

            # 3) figure out if we should apply the swirl
            swirl_amount = 1 - (c / radius)
            if swirl_amount <= 0:
                break

            # 3) find the angle to move the current pixel to. For pixels closer to the centre, we want them
            # to be more manipulated (which is what the swirl amount is for), further pixels from the centre
            # should be not swirled as much
            twist_angle = ((random.randint(98, 102) / 100) * strength) * swirl_amount * math.pi * 2

            # 4) add the angle to twist to the current angle where the pixel is located from centre
            pixel_angle += twist_angle

            # 5) convert back to standard x,y coordinates
            new_x = math.cos(pixel_angle) * c
            new_y = math.sin(pixel_angle) * c

            # 6) update the current x,y pixel to have the RGB values of the new calculated pixel based on
            # the above math
            new_pixel = to_swirl.getpixel((new_x, new_y))
            to_swirl.putpixel((x, y), new_pixel)

    return to_swirl


if __name__ == "__main__":
    main()

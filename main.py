import argparse
from PIL import Image, ImageDraw, ImageFilter
import face_recognition
from skimage.transform import swirl
import math
import random

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
        choices=["identify", "swirl", "random"],
        default="swirl")

    args = parser.parse_args()

    input_file_path = args.input_file
    output_file = args.output_file

    image = face_recognition.load_image_file(input_file_path)
    face_locations = face_recognition.face_locations(image)

    print("I found {} face(s) in this photograph.".format(len(face_locations)))

    im = Image.fromarray(image)
    draw = ImageDraw.Draw(im)

    for face_location in face_locations:

        # Print the location of each face in this image
        top, right, bottom, left = face_location
        print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        face = Image.fromarray(image[top:bottom, left:right])
        
        result = swirl_faces(face, 5)

        result.putalpha(100)
        result = result.filter(ImageFilter.BLUR)

        # print("og: %s" % str(image[top:bottom, left:right]))
        # print("new: %s" % str(result))

        im.paste(result, (left, top, right, bottom))

        # now draw a red box around this!
        # draw.rectangle([(left, top), (right, bottom)], None, (255, 0, 0), 1)

    del draw

    # write to stdout
    im.save(output_file, "PNG")

def swirl_faces(face, strength):

    to_swirl = face.copy() 

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
                continue

            # 3) do rotation?
            twist_angle = ((random.randint(98, 102) / 100) * strength) * swirl_amount * math.pi * 2

            pixel_angle += twist_angle

            # 5) convert back to standard x,y coordinates
            new_x = math.cos(pixel_angle) * c
            new_y = math.sin(pixel_angle) * c

            new_pixel = to_swirl.getpixel((new_x, new_y))
            to_swirl.putpixel((x, y), new_pixel)

    return to_swirl

if __name__ == "__main__":
    main()
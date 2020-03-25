import math
import os
import random
from abc import abstractmethod

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


class IllegalStateException(Exception):
    pass


class ImageProcessingContext(object):
    def __init__(self,
                 img: Image.Image,
                 img_data: np.array,
                 face_locations: [(int, int, int, int)]):
        self.img = img
        self.img_data = img_data
        self.face_locations = face_locations
        super().__init__()


class ImageEffect(object):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def process_image(self, context: ImageProcessingContext) -> Image.Image:
        raise NotImplementedError


class GhostEffect(ImageEffect):

    def __init__(self, ghost_image_paths="./resources/ghosts/"):
        self.__ghost_images = []

        for file in os.listdir(ghost_image_paths):
            full_path = os.path.join(ghost_image_paths, file)
            img = Image.open(full_path)
            self.__ghost_images.append(img)

        if len(self.__ghost_images) == 0:
            raise IllegalStateException(f'no images found in the path {ghost_image_paths}')

        super().__init__()

    def process_image(self, context: ImageProcessingContext):
        """
        for this, we need to:
            1. Create an all blank image the size of the passed in image
            2. Paste onto it all the ghost images we want
            3. Create a mask that is all blank, white where we want the image
            4. Composite ghost sheet onto OG image with mask
            5. ...
            6. profit?
        """
        img = context.img

        transparent_img = img.convert("RGBA")

        all_ghost_image = Image.new("RGBA", img.size, (255, 255, 255, 0))

        # TODO: This should not just take the first ghost image, but take
        # some randome number and smartly put them on the image
        ghost = self.__ghost_images[0]
        g_width, g_height = ghost.size

        # find a spot to put a ghost:
        # for now put it in the middle
        left = math.floor((img.width / 2)) - math.floor((g_width/2))
        top = 10
        right = left + ghost.width
        bottom = top + ghost.height

        # create the base ghost image
        all_ghost_image.paste(ghost, (left, top, right, bottom))

        # # Create mask that has the same setup
        ghost_mask = Image.new("L", img.size, 0)

        for x in range(left, right):
            for y in range(top, bottom):
                r, g, b, a = all_ghost_image.getpixel((x, y))

                if a == 0:
                    continue

                ghost_mask.putpixel((x, y), 150)

        blur_mask = ghost_mask.filter(ImageFilter.BLUR)

        return Image.composite(all_ghost_image, transparent_img, blur_mask)


class FaceIdentifyEffect(ImageEffect):

    def __init__(self):
        super().__init__()

    def process_image(self, context: ImageProcessingContext) -> Image.Image:
        img = context.img
        draw = ImageDraw.Draw(img)

        for face_location in context.face_locations:
            top, right, bottom, left = face_location

            # using the bounds of the face, draw a red box around it!
            draw.rectangle([(left, top), (right, bottom)],
                           None, (255, 0, 0), 1)

        return img


class SwirlFaceEffect(ImageEffect):
    def __init__(self, swirl_strength=5):
        self.__swirl_strength = swirl_strength
        super().__init__()

    def process_image(self, context: ImageProcessingContext) -> Image.Image:
        img = context.img

        for face_location in context.face_locations:
            top, right, bottom, left = face_location

            # create a new image based on the current face
            face = Image.fromarray(context.img_data[top:bottom, left:right])

            # swirl the face
            processed_face = self.__swirl_rect(face, self.__swirl_strength)
            # add some alpha to the swirled image to make it less opaque
            processed_face.putalpha(100)
            # add a little bit of blur so that it is not so perfectly swirled
            processed_face = processed_face.filter(ImageFilter.GaussianBlur(2))

            # merge the face with the original image
            img.paste(processed_face, (left, top, right, bottom))

        return img

    def __swirl_rect(self, img: Image.Image, swirl_strength: int) -> Image.Image:
        # create a copy so that the orignal is not changed
        # not necessarily needed, but does avoid weird side effects
        to_swirl = img.copy()
        ellipse_mask = Image.new("L", to_swirl.size, 0)

        left = 0
        top = 0
        bottom = to_swirl.height - 1
        right = to_swirl.width - 1

        semimajor_axis = ((bottom - top) / 2)
        semiminor_axis = ((right - left) / 2)

        centerx = int(right / 2)
        centery = int(bottom / 2)

        for x in range(left, right):
            for y in range(top, bottom):
                # 1) convert to u,v space
                u = x - centerx
                v = y - centery

                # if w are at the center point of the swirl, do nothing
                if u == 0 and v == 0:
                    continue

                # 2) get the distance from pixel to the center and the angle
                # c = sqrt(u^2 + v^2)
                # thanks pythagoreous
                c = math.sqrt(math.pow(u, 2) + math.pow(v, 2))
                theta_radians = math.atan2(v, u)
                a = semiminor_axis # horizontal axis
                b = semimajor_axis # vertical axis
                # https://math.stackexchange.com/questions/432902/how-to-get-the-radius-of-an-ellipse-at-a-specific-angle-by-knowing-its-semi-majo
                ellipse_radius = (a * b) / math.sqrt( (a * a) * (np.sin(theta_radians) *  np.sin(theta_radians)) + (b * b) * (np.cos(theta_radians) *  np.cos(theta_radians)))

                # 3) figure out if we should apply the swirl
                swirl_amount = 1 - (c / ellipse_radius)
                if swirl_amount <= 0:
                    continue

                # 3) find the angle to move the current pixel to. For pixels
                # closer to the centre, we want them to be more manipulated
                # (which is what the swirl amount is for), further pixels from
                # the centre should be not swirled as much
                twist_angle = (((random.randint(98, 102) / 100)
                               * swirl_strength)
                               * swirl_amount
                               * math.pi * 2)

                # 4) add the angle to twist to the current angle where the
                # pixel is located from centre
                theta_radians += twist_angle

                # 5) convert back to standard x,y coordinates
                new_x = math.cos(theta_radians) * c
                new_y = math.sin(theta_radians) * c

                # 6) update the current x,y pixel to have the RGB values of
                # the new calculated pixel based on the above math
                new_pixel = img.getpixel((new_x, new_y))
                to_swirl.putpixel((x, y), new_pixel)

        swirl_copy = to_swirl.copy()
        swirl_copy = swirl_copy.filter(ImageFilter.GaussianBlur(2))

        mask_blur = ellipse_mask.filter(ImageFilter.GaussianBlur(2))

        return Image.composite(to_swirl, swirl_copy, mask_blur)

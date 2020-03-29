import math
import os
import random
from abc import abstractmethod

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from lib.detection import FaceMetadata
from typing import List


class IllegalStateException(Exception):
    pass


class ImageProcessingContext(object):
    def __init__(self,
                 img: Image.Image,
                 img_data: np.array,
                 faces: List[FaceMetadata]):
        self.img = img
        self.img_data = img_data
        self.faces = faces
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

        max_ghost_width = 0
        for file in os.listdir(ghost_image_paths):
            full_path = os.path.join(ghost_image_paths, file)
            img = Image.open(full_path)
            max_ghost_width = max(max_ghost_width, img.width)
            self.__ghost_images.append(img)

        if len(self.__ghost_images) == 0:
            raise IllegalStateException(f'no images found in the path {ghost_image_paths}')

        self.__max_ghost_width = max_ghost_width

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

        for (ghost_image, left, top) in self.__get_ghost_locations(img):
            right = left + ghost_image.width
            bottom = top + ghost_image.height

            # create the base ghost image
            all_ghost_image.paste(ghost_image, (left, top, right, bottom))

        # # Create mask that has the same setup
        ghost_mask = Image.new("L", img.size, 0)

        for x in range(0, ghost_mask.width):
            for y in range(0, ghost_mask.height):
                r, g, b, a = all_ghost_image.getpixel((x, y))

                if a == 0:
                    continue

                ghost_mask.putpixel((x, y), 150)

        blur_mask = ghost_mask.filter(ImageFilter.BLUR)

        return Image.composite(all_ghost_image, transparent_img, blur_mask)

    def __get_ghost_locations(self, img: Image.Image) -> [(Image.Image, int, int)]:
        """
        Get all locations to put a ghost image

        For a given input image, determine how many ghost images to put on the
        image, and gives their top+left x,y coordinates

        Parameters:
        img (Image.Image): The image we want to add ghosts too

        Returns:
        [(Image.Image, int, int)]: list of ghosts including the (x,y)
                                   coordinates for the top+left location to
                                   place it on
                                   on the original image
        """

        # use the max ghost image width and the number of images to determine
        # how many ghosts to place
        num_ghosts_to_place = min(len(self.__ghost_images),
                                  4,  # we dont want to overload the image with ghosts
                                  math.floor(img.width/self.__max_ghost_width))

        result = []
        chosen_ghosts = set()
        for i in range(num_ghosts_to_place):
            while True:
                ghost_index = random.randint(0, len(self.__ghost_images) - 1)

                if str(ghost_index) not in chosen_ghosts:
                    chosen_ghosts.add(str(ghost_index))
                    break

            ghost = self.__ghost_images[ghost_index]

            # for the x location, we need to divide the main image width by
            # the number of ghosts to get where to put the ghost, and then
            # pick a random spot within that range
            # ex: two ghosts (x is final ghost location):
            # |           image           |
            # | ghost range | ghost range |
            # | x           |       x     |
            min_ghost_x = (img.width / num_ghosts_to_place) * i
            max_ghost_x = ((img.width / num_ghosts_to_place) * (i + 1) - 1) - ghost.width

            left = random.randint(min_ghost_x, max_ghost_x)
            top = random.randint(10, 30)
            result.append((ghost, left, top))

        return result


class FaceIdentifyEffect(ImageEffect):

    def __init__(self):
        super().__init__()

    def process_image(self, context: ImageProcessingContext) -> Image.Image:
        img = context.img
        draw = ImageDraw.Draw(img)

        for face in context.faces:
            top, right, bottom, left = face.get_bounding_box()

            # using the bounds of the face, draw a red box around it!
            draw.rectangle([(left, top), (right, bottom)],
                           None, (255, 0, 0), 1)

            mouth = face.get_mouth_points()
            draw.line(mouth, fill=(255, 0, 0, 64), width=1)

            left_eye, right_eye = face.get_eye_points()
            draw.line(left_eye, fill=(255, 0, 0, 64), width=1)
            draw.line(right_eye, fill=(255, 0, 0, 64), width=1)

        return img


class SaturationEffect(ImageEffect):

    def __init__(self, saturation_percentage):
        self.__saturation_percentage = saturation_percentage
        super().__init__()

    def process_image(self, context: ImageProcessingContext) -> Image.Image:
        enhancer = ImageEnhance.Contrast(context.img)
        return enhancer.enhance(self.__saturation_percentage)


class SwirlFaceEffect(ImageEffect):
    def __init__(self, swirl_strength=5):
        self.__swirl_strength = swirl_strength
        super().__init__()

    def process_image(self, context: ImageProcessingContext) -> Image.Image:
        img = context.img

        for face in context.faces:
            top, right, bottom, left = face.get_bounding_box()

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

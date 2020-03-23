from PIL import Image, ImageDraw, ImageFilter
from abc import abstractmethod
import os
import math


class IllegalStateException(Exception):
    pass


class ImageEffect(object):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def process_image(self, img: Image.Image) -> Image.Image: 
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

    def process_image(self, img):
        """
        for this, we need to:
            1. Create an all blank image the size of the passed in image
            2. Paste onto it all the ghost images we want
            3. Create a mask that is all blank, white where we want the image
            4. Composite ghost sheet onto OG image with mask
            5. ...
            6. profit?
        """

        transparent_img = img.convert("RGBA")

        all_ghost_image = Image.new("RGBA", img.size, (255, 255, 255, 0))

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

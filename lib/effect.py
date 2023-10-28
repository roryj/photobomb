import math
import os
import random
from abc import abstractmethod

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageColor
from lib.detection import FaceMetadata
from typing import List

class IllegalStateException(Exception):
    pass


class ImageProcessingContext(object):
    def __init__(self, img: Image.Image, img_data: np.array, faces: List[FaceMetadata], image_num: int):
        self.img = img
        self.img_data = img_data
        self.faces = faces
        self.image_num = image_num
        super().__init__()

    def filename(self):
        if hasattr(self.img, "filename"):
            return self.img.filename

        return "Unknown"


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

        print(f'Loaded {len(self.__ghost_images)} images from path {ghost_image_paths}')

        if len(self.__ghost_images) == 0:
            raise IllegalStateException(f"no images found in the path {ghost_image_paths}")

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
            print(f'Adding ghostie at {(left, top, right, bottom)}')

        # # Create mask that has the same setup
        ghost_mask = Image.new("L", img.size, 0)

        for x in range(0, ghost_mask.width):
            for y in range(0, ghost_mask.height):
                r, g, b, a = all_ghost_image.getpixel((x, y))

                # 'a' is the alpha value of the combinaton of all ghosts images at point x,y
                # An alpha of 0 means the pixel is transparent, which we use to create an image
                # mask only where the ghost pixels are located
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
        num_ghosts_to_place = min(
            len(self.__ghost_images),
            2,  # we dont want to overload the image with ghosts
            math.floor(img.width / self.__max_ghost_width),
        )

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
            min_ghost_x = int((img.width / num_ghosts_to_place) * i)
            max_ghost_x = int(((img.width / num_ghosts_to_place) * (i + 1) - 1) - ghost.width)

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
            draw.rectangle([(left, top), (right, bottom)], None, (255, 0, 0), 1)

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

        semimajor_axis = (bottom - top) / 2
        semiminor_axis = (right - left) / 2

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
                a = semiminor_axis  # horizontal axis
                b = semimajor_axis  # vertical axis
                # https://math.stackexchange.com/questions/432902/how-to-get-the-radius-of-an-ellipse-at-a-specific-angle-by-knowing-its-semi-majo
                ellipse_radius = (a * b) / math.sqrt(
                    (a * a) * (np.sin(theta_radians) * np.sin(theta_radians))
                    + (b * b) * (np.cos(theta_radians) * np.cos(theta_radians))
                )

                # 3) figure out if we should apply the swirl
                swirl_amount = 1 - (c / ellipse_radius)
                if swirl_amount <= 0:
                    continue

                # 3) find the angle to move the current pixel to. For pixels
                # closer to the centre, we want them to be more manipulated
                # (which is what the swirl amount is for), further pixels from
                # the centre should be not swirled as much
                twist_angle = ((random.randint(98, 102) / 100) * swirl_strength) * swirl_amount * math.pi * 2

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


class SketchyEyeEffect(ImageEffect):
    def __init__(self):
        super().__init__()

    def process_image(self, context: ImageProcessingContext):

        img = context.img
        draw = ImageDraw.Draw(img)

        for face in context.faces:

            for eye in face.get_eye_points():
                center_x, center_y, radius = self.__get_eye_dimensions(face.get_bounding_box(), eye)

                draw.ellipse(
                    [(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)], (0, 0, 0, 100)
                )

        return img

    def __get_eye_dimensions(self, face_bounding_box: (int, int, int, int), eye_points: [(int, int)]) -> (int, int):
        face_top, face_right, face_bottom, face_left = face_bounding_box

        # find center of the each eye
        min_x = face_right
        max_x = face_left
        min_y = face_bottom
        max_y = face_top
        for (x, y) in eye_points:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        center_x = min_x + ((max_x - min_x) / 2)
        center_y = min_y + ((max_y - min_y) / 2)
        radius = max((max_x - min_x) / 2, (max_y - min_y) / 2)

        return center_x, center_y, radius

class PigNoseEffect(ImageEffect):
    def __init__(self, pig_nose_path="./resources/facial_accessories/Pig_Nose.png"):
        img = Image.open(pig_nose_path)
        self.__pig_nose_image = img
        self.__pig_nose_width_ratio = img.width / img.height
        super().__init__()

    def process_image(self, context: ImageProcessingContext):
        img = context.img.convert("RGBA")
        draw = ImageDraw.Draw(img)

        all_piggies_image = Image.new("RGBA", img.size, (255, 255, 255, 0))

        for face in context.faces:
            nose = face.get_nose_tip()
            bridge = face.get_middle_of_nose()

            actual_nose_height = abs(bridge[1] - nose[1])
            pig_nose_height = int(actual_nose_height * 4 / 3)
            pig_nose_width = int(pig_nose_height * self.__pig_nose_width_ratio)

            pig_nose_top = int(bridge[1])
            pig_nose_bottom = int(pig_nose_top + pig_nose_height)
            pig_nose_left = int(nose[0] - pig_nose_width / 2)
            pig_nose_right = int(nose[0] + pig_nose_width / 2)

            pig_nose = self.__pig_nose_image.convert("RGBA").resize((pig_nose_width, pig_nose_height))

            print(f'box: {(pig_nose_left, pig_nose_top, pig_nose_right, pig_nose_bottom)}')
            print(f'image size: {img.size}')
            all_piggies_image.paste(pig_nose, (pig_nose_left, pig_nose_top))

        # # Create mask that has the same setup
        piggy_mask = Image.new("L", img.size, 0)
        for x in range(0, piggy_mask.width):
            for y in range(0, piggy_mask.height):
                r, g, b, a = all_piggies_image.getpixel((x, y))
                # 'a' is the alpha value of the combinaton of all pig images at point x,y
                # An alpha of 0 means the pixel is transparent, which we use to create an image
                # mask only where the ghost pixels are located
                if a == 0:
                    continue
                piggy_mask.putpixel((x, y), 222)
        blur_mask = piggy_mask.filter(ImageFilter.BLUR)

        return Image.composite(all_piggies_image, img, blur_mask)

class PigLogoEffect(ImageEffect):
    def __init__(self, pig_path="./resources/pigs/hog-hole-22.png", num_photos=4):
        self.pig_image = Image.open(pig_path)
        self.pig_width_ratio = self.pig_image.width / self.pig_image.height
        self.num_photos = num_photos
        super().__init__()

    def process_image(self, context: ImageProcessingContext):
        if self.num_photos != context.image_num:
            print(f'Skipping PigLogoEffect for image number {context.image_num}')
            return context.img

        img = context.img.convert("RGBA")
        draw = ImageDraw.Draw(img)

        size = int(img.width / 7)
        padding = int(img.height / 16)

        resized = self.pig_image.convert("RGBA").resize((size, size))

        all_piggies_image = Image.new("RGBA", img.size, (255, 255, 255, 0))

        left = img.width - padding - size
        top = img.height - padding - size

        print(f'Put image at {(left, top)} with size {size}')
        all_piggies_image.paste(resized, (left, top))

        # # Create mask that has the same setup
        piggy_mask = Image.new("L", img.size, 0)
        for x in range(0, piggy_mask.width):
            for y in range(0, piggy_mask.height):
                r, g, b, a = all_piggies_image.getpixel((x, y))
                # 'a' is the alpha value of the combinaton of all pig images at point x,y
                # An alpha of 0 means the pixel is transparent, which we use to create an image
                # mask only where the ghost pixels are located
                if a == 0:
                    continue
                piggy_mask.putpixel((x, y), 175)
        blur_mask = piggy_mask.filter(ImageFilter.BLUR)

        return Image.composite(all_piggies_image, img, blur_mask)

class FlyingPigsEffect(ImageEffect):
    def __init__(self, pig_path="./resources/pigs/flying-pig.png", reverse_pig_path="./resources/pigs/flying-pig-reverse.png"):
        self.pig_image = Image.open(pig_path)
        self.reverse_pig = Image.open(reverse_pig_path)
        self.pig_width_ratio = self.pig_image.width / self.pig_image.height
        super().__init__()

    def process_image(self, context: ImageProcessingContext):
        insert_left = bool(random.getrandbits(1))
        insert_right = bool(random.getrandbits(1))
        reverse_pigs = bool(random.getrandbits(1))

        if not insert_left and not insert_right:
            return context.img

        img = context.img.convert("RGBA")
        draw = ImageDraw.Draw(img)

        min_size = int(img.width / 8)
        max_size = int(img.width / 4)
        padding = int(img.height / 48)

        size = random.randint(min_size, max_size)

        pig_image = self.pig_image.convert("RGBA").resize((size, size))
        reverse_pig = self.reverse_pig.convert("RGBA").resize((size, size))

        all_piggies_image = Image.new("RGBA", img.size, (255, 255, 255, 0))

        if insert_left:
            max_pos = int(img.width / 3)

            print(f'Size {size}, Left pos f{(max_pos)}')

            min_top = padding
            max_top = int(img.height / 2) - size
            min_left = padding
            max_left = max_pos - size

            print(f'tops {min_top, max_top}, lefts {min_left, max_left}')

            top = random.randint(min_top, max_top)
            left = random.randint(min_left, max_left)

            print(f'Put left flying pig at {(left, top)} with size {size}')
            if reverse_pigs:
                all_piggies_image.paste(pig_image, (left, top))
            else:
                all_piggies_image.paste(reverse_pig, (left, top))

        if insert_right:
            min_pos = int(2 * img.width / 3)

            print(f'Size {size}, Right pos f{(min_pos)}')

            min_top = padding
            max_top = int(img.height / 2) - size
            min_left = min_pos
            max_left = img.width - padding - size

            print(f'tops {min_top, max_top}, right {min_left, max_left}')

            top = random.randint(min_top, max_top)
            left = random.randint(min_left, max_left)

            print(f'Put left flying pig at {(left, top)} with size {size}')
            if reverse_pigs:
                all_piggies_image.paste(reverse_pig, (left, top))
            else:
                all_piggies_image.paste(pig_image, (left, top))

        # # Create mask that has the same setup
        piggy_mask = Image.new("L", img.size, 0)
        for x in range(0, piggy_mask.width):
            for y in range(0, piggy_mask.height):
                r, g, b, a = all_piggies_image.getpixel((x, y))
                # 'a' is the alpha value of the combinaton of all pig images at point x,y
                # An alpha of 0 means the pixel is transparent, which we use to create an image
                # mask only where the ghost pixels are located
                if a == 0:
                    continue
                piggy_mask.putpixel((x, y), 175)
        blur_mask = piggy_mask.filter(ImageFilter.BLUR)

        return Image.composite(all_piggies_image, img, blur_mask)

class FullFrameEffect(ImageEffect):
    def __init__(self, image_path="./resources/pigs/flying-pig.png"):
        self.image = Image.open(image_path) if image_path else None
        super().__init__()

    def process_image(self, context: ImageProcessingContext):
        base_image = context.img.convert("RGBA")
        image_size = base_image.size

        draw = ImageDraw.Draw(base_image)
        overlay_image = self.image.convert("RGBA").resize(image_size)
        final_image = Image.new("RGBA", image_size, (255, 255, 255, 0))

        final_image.paste(overlay_image, (0, 0))

        # # Create mask that has the same setup. Why? Nobody knows. Or has time to test.
        mask = Image.new("L", image_size, 0)
        for x in range(0, mask.width):
            for y in range(0, mask.height):
                r, g, b, a = final_image.getpixel((x, y))
                # 'a' is the alpha value of the combinaton of all pig images at point x,y
                # An alpha of 0 means the pixel is transparent, which we use to create an image
                # mask only where the ghost pixels are located
                if a == 0:
                    continue
                mask.putpixel((x, y), 255)

        blur_mask = mask.filter(ImageFilter.BLUR)

        return Image.composite(final_image, base_image, blur_mask)

class RandomFullFrameEffect(FullFrameEffect):
    def __init__(self, image_dir="./resources/pigs/"):
        self.images = [Image.open(os.path.join(image_dir, im)) for im in os.listdir(image_dir) if (im.endswith('.png') or im.endswith('.jpg'))]
        random.shuffle(self.images)
        super().__init__(None)

    def process_image(self, context: ImageProcessingContext):
        self.image = self.images.pop(0)
        return super().process_image(context)

class FinalFrameEffect(FullFrameEffect):
    def __init__(self, image_path="./resources/pigs/hog-hole-22.png", num_photos=4):
        self.num_photos = num_photos
        super().__init__(image_path)

    def process_image(self, context: ImageProcessingContext):
        if self.num_photos != context.image_num:
            return context.img
        else:
            return super().process_image(context)

class RandomFrame:
    def __init__(self, image_paths, x_offset, y_offset, strip_width):
        self.frames = [PhotoStripFrame(image, x_offset, y_offset, strip_width) for image in image_paths]

    def process_image(self, photo_strip: Image.Image) -> Image.Image:
        frame_num = random.randint(0, len(self.frames) - 1)
        print(f'Picked random frame number {frame_num+1} of {len(self.frames)}')
        return self.frames[frame_num].process_image(photo_strip)

class PhotoStripFrame:
    def __init__(self, image_path, x_offset, y_offset, strip_width):
        self.image = Image.open(image_path)
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.strip_width = strip_width

    def process_image(self, photo_strip: Image.Image) -> Image.Image:
        strip_image = photo_strip.convert("RGBA")
        strip_image_size = strip_image.size
        print(f'Photo strip has size of {strip_image_size}')
        print(f'Photo frame has size of {self.image.size}')

        # scale the frame
        scale = strip_image_size[0] / self.strip_width
        image_size = (int(self.image.size[0] * scale), int(self.image.size[1] * scale))
        print(f'Photo frame was scaled to size of {image_size}')

        base_image = Image.new("RGBA", image_size, (255, 255, 255, 0))
        base_image.paste(strip_image, (int(self.x_offset * scale), int(self.y_offset * scale)))

        overlay_image = self.image.convert("RGBA").resize(image_size)
        final_image = Image.new("RGBA", image_size, (255, 255, 255, 0))

        final_image.paste(overlay_image, (0, 0))

        # # Create mask that has the same setup. Why? Nobody knows. Or has time to test.
        mask = Image.new("L", image_size, 0)
        for x in range(0, mask.width):
            for y in range(0, mask.height):
                r, g, b, a = final_image.getpixel((x, y))
                # 'a' is the alpha value of the combinaton of all pig images at point x,y
                # An alpha of 0 means the pixel is transparent, which we use to create an image
                # mask only where the ghost pixels are located
                if a == 0:
                    continue
                mask.putpixel((x, y), 255)

        blur_mask = mask.filter(ImageFilter.BLUR)

        return Image.composite(final_image, base_image, blur_mask)

class SideBySideEffect:

    def __init__(self):
        pass

    def process_image(self, photo_strip: Image.Image) -> Image.Image:
        strip_image = photo_strip.convert("RGBA")
        strip_image_size = strip_image.size
        print(f'Photo strip has size of {strip_image_size}')

        image_size = (strip_image_size[0] * 2 + 4, strip_image_size[1])
        print(f'Photo frame was scaled to size of {image_size}')

        base_image = Image.new("RGBA", image_size, (255, 255, 255, 0))

        base_image.paste(strip_image, (0, 0))
        base_image.paste(strip_image, (strip_image.size[0] + 4, 0))
        base_image = base_image.resize((1134, 1702))

        # Actually bluey-purple. Need to refactor this to be based on mode :/
        pink_background = Image.new(mode="RGB", size=(1200, 1800), color=ImageColor.getrgb("#290069"))
        pink_background.paste(base_image, (33, 49))

        draw = ImageDraw.Draw(pink_background)
        draw.line([(600, 0), (600, 1800)], fill ="white", width = 1)

        return pink_background

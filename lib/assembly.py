from typing import List, Tuple
from PIL import Image, ImageColor

# Photo strips are 2x6 inches
PRINTER_DPI = 300
PHOTO_STRIP_WIDTH = PRINTER_DPI * 2
PHOTO_STRIP_HEIGHT = PRINTER_DPI * 6

BORDER = 24
PHOTO_WIDTH = (PRINTER_DPI - BORDER) * 2
PHOTO_HEIGHT = PRINTER_DPI + int(PRINTER_DPI * 2 / 16) * 2
BOTTOM_SPACE_HEIGHT = PHOTO_STRIP_HEIGHT - (PHOTO_HEIGHT + BORDER) * 4

BOTTOM_PANEL_WIDTH = PHOTO_STRIP_WIDTH
BOTTOM_PANEL_HEIGHT = int(PRINTER_DPI * 4 / 3)
BOTTOM_PANEL_OVERLAP = BOTTOM_PANEL_HEIGHT - BOTTOM_SPACE_HEIGHT


def print_photo_info():
    print(
        f"""
----------
Photo strip will be {PHOTO_STRIP_WIDTH} x {PHOTO_STRIP_HEIGHT}px
Border size is {BORDER}px
Each photo will be {PHOTO_WIDTH} x {PHOTO_HEIGHT}px
The bottom panel is {BOTTOM_SPACE_HEIGHT}px high
The bottom panel image is {BOTTOM_PANEL_WIDTH} x {BOTTOM_PANEL_HEIGHT}px with {BOTTOM_PANEL_OVERLAP}px of overlap
----------
        """
    )


class PhotoTakingContext:

    def __init__(self, args):
        self.images = []
        self.spooky_images = []
        self.test = args.test
        self.mode = args.mode
        self.args = args

    def set_images(self, images: List[Image.Image]):
        self.images = images

    def set_spooky_images(self, images: List[Image.Image]):
        self.spooky_images = images


class PhotoStrip:

    @staticmethod
    def process_image(photo_context: PhotoTakingContext) -> Image.Image:
        final_image = Image.new(
            mode="RGB",
            size=(PHOTO_STRIP_WIDTH, PHOTO_STRIP_HEIGHT),
            color=ImageColor.getrgb(photo_context.mode.get_background_color()),
        )

        next_image_y = BORDER
        for image in photo_context.images:
            scale = float(PHOTO_HEIGHT) / image.height
            new_image_width = int(image.width * scale)
            overflow = new_image_width - PHOTO_WIDTH
            trim = int(overflow / 2)
            print(f"scale is {scale} and new image width is {new_image_width}")
            print(f"overflow is {overflow} with trim {trim}")

            image = image.resize((new_image_width, PHOTO_HEIGHT))
            image = image.crop((trim, 0, trim + PHOTO_WIDTH, image.height))

            final_image.paste(image, (BORDER, next_image_y))

            next_image_y += BORDER + PHOTO_HEIGHT

        bottom_panel = Image.open(photo_context.mode.get_bottom_panel())
        # # Create mask that has the same setup
        bottom_panel_top = PHOTO_STRIP_HEIGHT - bottom_panel.height
        for x in range(0, bottom_panel.width):
            for y in range(0, bottom_panel.height):
                r, g, b, a = bottom_panel.getpixel((x, y))
                # 'a' is the alpha value of the combination of all pig images at point x,y
                # An alpha of 0 means the pixel is transparent, which we use to create an image
                # mask only where the ghost pixels are located
                if a == 0:
                    continue
                final_image.putpixel((x, bottom_panel_top + y), (r, g, b, a))

        # final_image.paste(bottom_panel, (0, PHOTO_STRIP_HEIGHT - bottom_panel.height))

        return final_image


class DoublePhotoStrip:

    @staticmethod
    def process_image(photo_context: PhotoTakingContext) -> Image.Image:
        """Takes the photos and turns it into two identical photo strips side by side

        This method takes the incoming photographed images, creates a single photo strip out of them, and then
        duplicates photo strip so we can save and print out two photo strips on one paper

        :param photo_context: The photo context containing both the unedited and edited photos
        :type photo_context: PhotoTakingContext
        :return: Returns the generated photo strip image
        :rtype: Image.Image
        """
        photo_strip = PhotoStrip.process_image(photo_context)

        color = photo_context.mode.get_background_color()

        double_photo = Image.new(
            mode="RGB",
            # Add 40 additional pixels to account for the DNP printer's small cutoff on each side.
            # Border will be 10 pixels on the left and bottom, 30 pixels on the right and top.
            size=(PHOTO_STRIP_WIDTH * 2 + 30, PHOTO_STRIP_HEIGHT + 30),
            color=ImageColor.getrgb(color),
        )

        colored_background = Image.new(mode="RGB", size=(1200, 1800), )

        # (x, y) of (10, 30) is the upper left corner. We're adding a border as noted above.
        double_photo.paste(photo_strip, (10, 20))
        double_photo.paste(photo_strip, (PHOTO_STRIP_WIDTH + 10, 20))
        _add_cut_line(double_photo, line_x_coordinate=PHOTO_STRIP_WIDTH+10)

        return double_photo


def _add_cut_line(img: Image.Image, line_x_coordinate: int, line_colour: Tuple[int, int, int] = (255, 255, 255)):
    """Adds a cut line to the middle of an image

    :param img: The image to add the cut line too
    :type img: Image.Image
    :param line_colour: The colour for the cutline, defaults to (255, 255, 255) aka white
    :type line_colour: Tuple[int, int, int], optional
    """

    line_width_pixels = 2
    line_length_pixels = 20
    on_cut_lint = False
    count = 0

    for y in range(PHOTO_STRIP_HEIGHT):

        if count >= line_length_pixels:
            on_cut_lint = not on_cut_lint
            count = 0

        if not on_cut_lint:
            # print("skipping")
            count += 1
            continue

        for x in range(-line_width_pixels, line_width_pixels):
            # print(f"putting pixel @({middle + x}, {y}) -> {line_colour}")
            img.putpixel((line_x_coordinate + x, y), line_colour)

        count += 1

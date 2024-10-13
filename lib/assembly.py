from typing import List
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageColor
from lib.mode import Mode
from lib.printer import PhotoPrinter

# Photo strips are 2x6 inches
PRINTER_DPI = 300
PHOTO_STRIP_WIDTH = PRINTER_DPI * 2
PHOTO_STRIP_HEIGHT = PRINTER_DPI * 6

BORDER = int(PRINTER_DPI * 2 / 16 / 2)
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

    def process_image(self, photo_context: PhotoTakingContext, printer: PhotoPrinter) -> Image.Image:
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
                # 'a' is the alpha value of the combinaton of all pig images at point x,y
                # An alpha of 0 means the pixel is transparent, which we use to create an image
                # mask only where the ghost pixels are located
                if a == 0:
                    continue
                final_image.putpixel((x, bottom_panel_top + y), (r, g, b, a))

        # final_image.paste(bottom_panel, (0, PHOTO_STRIP_HEIGHT - bottom_panel.height))

        return final_image


class DoublePhotoStrip:

    def process_image(self, photo_context: PhotoTakingContext, printer: PhotoPrinter) -> Image.Image:
        """Takes the photos and turns it into two identical photo strips side by side

        This method takes the incoming photographed images, creates a single photo strip out of them, and then
        duplicates photo strip so we can save and print out two photo strips on one paper

        TODO: add a line to the middle for people to cut

        :param photo_context: _description_
        :type photo_context: PhotoTakingContext
        :param printer: _description_
        :type printer: PhotoPrinter
        :return: _description_
        :rtype: Image.Image
        """
        photo_strip = PhotoStrip().process_image(photo_context, printer)

        double_photo = Image.new(
            mode="RGB",
            size=(PHOTO_STRIP_WIDTH * 2, PHOTO_STRIP_HEIGHT),
            color=ImageColor.getrgb(photo_context.mode.get_background_color()),
        )

        double_photo.paste(photo_strip, (0, 0))
        double_photo.paste(photo_strip, (PHOTO_STRIP_WIDTH, 0))

        return double_photo

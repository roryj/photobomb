import os
import random
import time
from typing import List, Tuple
from abc import abstractmethod
from datetime import datetime, timedelta
import traceback

import cv2
import numpy as np
from PIL import Image

from lib.detection import find_faces_from_array
from lib.display import PhotoboothDisplay
from lib.effect import (
    GhostEffect,
    ImageEffect,
    ImageProcessingContext,
    SaturationEffect,
    SketchyEyeEffect,
    SwirlFaceEffect,
)


class PhotoTaker(object):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def take_photo(self) -> Image.Image:
        raise NotImplementedError


class WebCamPhotoTaker(PhotoTaker):
    def __init__(self, camera_to_use: int):
        # somehow this needs to be more configurable. Right now it just picks
        # the first webcam which for me (rory) is my front facing webcam. When
        # we add the photobooth webcam we will want a way to select that one
        # in particular
        self.cam = cv2.VideoCapture(camera_to_use)

    def take_photo(self) -> Image.Image:
        success, data = self.cam.read()

        if not success:
            raise Exception("couldnt take a photo :(")

        img = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

        return Image.fromarray(img)


class RandomStaticPhoto(PhotoTaker):
    def __init__(self, file_paths: List[str]):
        if len(file_paths) <= 0:
            raise ValueError("there must be at least one photo path")

        self.file_paths = file_paths
        super().__init__()

    def take_photo(self) -> Image.Image:
        index = random.randint(0, len(self.file_paths) - 1)
        return Image.open(self.file_paths[index])


class PhotoPrinter(object):
    def __init__(
        self,
        output_dir: str,
        output_file_prefix: str,
        image_type: str,
        should_print: bool,
    ):
        self.output_dir = output_dir
        self.output_file_prefix = output_file_prefix
        self.image_type = image_type
        self.should_print = should_print
        super().__init__()

    def __get_output_file_path(self) -> str:
        curr_time = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
        output_file_name = f"{self.output_file_prefix}_{curr_time}"
        return f"{self.output_dir}/{output_file_name}.{self.image_type}"

    def print(self, img: Image.Image):
        output_file_path = self.__get_output_file_path()
        print(f"Saving the image to {output_file_path}")
        img.save(output_file_path, self.image_type.upper(), quality=95)

        if self.should_print:
            print("Attempting to print the image")
            result = os.system(f"lpr {output_file_path}")
            if result == 0:
                print("Printing was successfull")
            else:
                print("Printing failed :(")
        else:
            print("Not printing!")


class Photobooth(object):
    def __init__(
        self,
        display: PhotoboothDisplay,
        photo_taker: PhotoTaker,
        printer: PhotoPrinter,
        num_photos: int,
        image_border_size: int,
        photo_delay_seconds: float,
    ):
        if num_photos <= 0:
            raise ValueError("there must be at least one picture to be taken")

        self.display = display
        self.photo_taker = photo_taker
        self.printer = printer
        self.num_photos = num_photos
        self.image_border_size = image_border_size
        self.photo_delay_seconds = photo_delay_seconds
        self.is_running = False

    def run(self):
        """
        run:
            to create a photobooth image, we need to:
            1) get all the input files (from a camera, from files)
            2) using the images, create the "final image" as a blank
            3) for each image
                a. determmine which effects to run
                b. run the effects
                c. paste each image onto their expected location inside the "final image"
            4) print the resulting image
            5) ...
            6) profit?
        """

        if self.is_running:
            print("[WARN]: The photobooth workflow is already running! Ignoring...")
            print("")
            return

        self.is_running = True
        try:

            # 1) take the pictures!
            imgs = self.__take_pictures()

            self.display.put_text("Detecting ghosts...")

            # 2) process images
            # 2a) convert images to image processing context
            (
                image_width,
                image_height,
                processing_contexts,
            ) = self.__setup_images_for_processing(imgs)

            # setup the final image
            result_width = image_width + (2 * self.image_border_size)
            result_height = (image_height * self.num_photos) + (
                (self.num_photos + 1) * self.image_border_size
            )
            print(f"final image size: {result_width}x{result_height}")
            final_image = Image.new(
                "RGBA", (result_width, result_height), (255, 255, 255, 255)
            )

            # 2b) for each image:
            #   - determine which spooky effects to run
            #   - spookify them
            #   - add to the final image
            count = 0
            for context in processing_contexts:
                effects = self.__determine_effects_to_run()

                print(
                    f"running effects {[e.__class__.__name__ for e in effects]} on {context.filename()}"
                )
                for effect in effects:
                    context.img = effect.process_image(context)

                x = self.image_border_size
                y = (count * image_height) + ((count + 1) * self.image_border_size)
                print(f"putting image of size {context.img.size} into: {x},{y}")

                final_image.paste(context.img, (x, y))
                count += 1

            self.display.clear_text()
            self.display.put_text("Printing your pictures!")

            # 3) print images!
            print("Printing the resulting image")
            self.printer.print(final_image)
            print("Printing complete!")

            self.display.clear_text()

            end_time = datetime.now() + timedelta(seconds=30)

            while (now := datetime.now()) < end_time:
                text = "Still printing"
                for dot in range(now.second % 4):
                    text += "."
                self.display.clear_text()
                self.display.put_text(text)
                time.sleep(1)

            self.display.clear_text()
            self.display.put_text("All done!")

        except Exception as e:
            print(f"An exception occurred running the photobooth: {e}")
            traceback.print_exc()

        self.is_running = False

        print("Photobooth workflow done")

    def __take_pictures(self) -> List[Image.Image]:
        """
        take_pictures

        take pictures that will be processed. The number of pictures to be taken is passed in as a
        parameter
        """
        self.display.clear_text()
        imgs = []

        for i in range(self.num_photos):

            # loop from number of seconds down to 0 sleeping in between
            # display the number going down
            # at 0, take picture, maybe do a flash thing on the pic
            start_time = datetime.now()
            photo_num = i + 1
            sub_text = f"photo {photo_num}/{self.num_photos}"
            print(f"taking {sub_text} in {self.photo_delay_seconds} seconds")

            while (datetime.now() - start_time).seconds < self.photo_delay_seconds:
                time_left = int(
                    self.photo_delay_seconds - (datetime.now() - start_time).seconds
                )
                self.display.put_text(str(time_left), sub_text)
                # print(f"time left: {time_left}")
                # update image :D
                time.sleep(1)

            if photo_num == 3:
                self.display.put_text("Die!", sub_text)
            else:
                self.display.put_text("Cheese!", sub_text)

            time.sleep(0.5)
            self.display.clear_text()
            img = self.photo_taker.take_photo()
            imgs.append(img)
            print("photo taken")
            time.sleep(0.5)

        print("all photos taken!")
        return imgs

    def __setup_images_for_processing(
        self, imgs: List[Image.Image]
    ) -> Tuple[int, int, List[ImageProcessingContext]]:
        prev_img = None

        contexts = []
        for img in imgs:
            if prev_img is not None and img.size != prev_img.size:
                raise ValueError(
                    f"the image {img.filename} is not the same size as {prev_img.filename}"
                )

            contexts.append(self.__create_context_from_image(img))

            prev_img = img

        return prev_img.width, prev_img.height, contexts

    def __create_context_from_image(self, img: Image) -> ImageProcessingContext:
        img_data = np.array(img)
        faces = find_faces_from_array(img_data)
        return ImageProcessingContext(img, img_data, faces)

    def __determine_effects_to_run(self) -> List[ImageEffect]:
        all_effects = [
            GhostEffect(),
            SketchyEyeEffect(),
            SwirlFaceEffect(1),
        ]
        chance_for_next_effect = 100

        selected_effects = []

        while (
            len(selected_effects) < 4
            and random.randint(0, 100) < chance_for_next_effect
        ):
            index = random.randint(0, len(all_effects) - 1)
            selected = all_effects[index]
            print(f"selected effect {selected.__class__.__name__}")
            selected_effects.append(selected)

            all_effects.remove(selected)

            # special case ghost effect since having it before other effects
            # causes weird issues
            if isinstance(selected, GhostEffect):
                break

            chance_for_next_effect = chance_for_next_effect * (2 / 3)

        # run saturation effect at the end, maybe
        if random.randint(0, 100) < 50:
            print("selected effect SaturationEffect")
            selected_effects.append(SaturationEffect(0.7))

        return selected_effects

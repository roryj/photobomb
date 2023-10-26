from dataclasses import dataclass
import os
import random
import time
from typing import List, Optional, Tuple
from abc import abstractmethod
from datetime import datetime
import traceback
import requests

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
    PigNoseEffect,
    FlyingPigsEffect,
    PigLogoEffect,
    RandomFullFrameEffect,
    FinalFrameEffect,
    RandomFrame,
    PhotoStripFrame,
    SideBySideEffect,
)
from lib.mms import send_text
from lib.s3 import upload_file
from lib.mode import Mode


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

    def __get_output_file_path(self, now, prefix="") -> str:
        curr_time = now.strftime("%d_%m_%Y-%H_%M_%S")
        output_file_name = f"{prefix}{self.output_file_prefix}_{curr_time}"
        return f"{self.output_dir}/{output_file_name}.{self.image_type}"

    def save_for_printing(self, now, img: Image.Image):
        path = self.__get_output_file_path(now, prefix="double_")
        self.save(img, path)
        return path

    def save_unspooked(self, now, img: Image.Image):
        path = self.__get_output_file_path(now, prefix="original_")
        self.save(img, path)
        return path

    def save(self, img: Image.Image, output_file_path):
        print(f"Saving the image to {output_file_path}")
        img.save(output_file_path, self.image_type.upper(), quality=95)

    def save_and_print(self, now, img: Image.Image):
        output_file_path = self.__get_output_file_path(now)
        self.save(img, output_file_path)

        final_image = SideBySideEffect().process_image(img)
        print_path = self.save_for_printing(now, final_image)
        if self.should_print:
            print("Attempting to print the image")
            # Available printer sizes should be available in /etc/cups/ppd/<printer-name>.ppd as a *PageSize
            result = os.system(f'lpr {print_path} -o media="4x6.Fullbleed"')
            if result == 0:
                print("Printing was successfull")
            else:
                print("Printing failed :(")
        else:
            print("Not printing!")
        return output_file_path


@dataclass(frozen=True)
class PhotoEvent:
    photo_number: int
    second_to_send_it: int
    event_name: str
    spooky_tech_client_port: int

    def should_send_event(self, current_photo_number: int, current_second: int) -> bool:
        return self.photo_number == current_photo_number and self.second_to_send_it == current_second

    def send_event(self):
        print(f"Sending event {self.event_name} to spooky tech")
        try:
            requests.post(
                f"http://localhost:{self.spooky_tech_client_port}/event",
                json={"sensorId": self.event_name, "sensorType": "manual", "data": True},
            )
        except Exception as e:
            print(f"Error sending post request: {e}")


class Photobooth(object):
    def __init__(
        self,
        display: PhotoboothDisplay,
        photo_taker: PhotoTaker,
        printer: PhotoPrinter,
        num_photos: int,
        image_border_size: int,
        photo_delay_seconds: float,
        mode: Mode,
        photo_event: Optional[PhotoEvent] = None,
    ):
        if num_photos <= 0:
            raise ValueError("there must be at least one picture to be taken")

        self.display = display
        self.photo_taker = photo_taker
        self.printer = printer
        self.num_photos = num_photos
        self.image_border_size = image_border_size
        self.photo_delay_seconds = int(photo_delay_seconds)
        self.is_running = False
        self.mode = mode
        self.photo_event = photo_event

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
            # 0) Tell the user what we're up to!
            self.display.put_text("The Photo Booth will take 4 photos")
            time.sleep(3)
            self.display.put_text("GET READY!")
            time.sleep(2)

            # 1) take the pictures!
            imgs = self.__take_pictures()

            # 2) process images
            self.display.put_text(self.mode.processing_images_prompt())
            # 2a) convert images to image processing context
            (
                image_width,
                image_height,
                processing_contexts,
            ) = self.__setup_images_for_processing(imgs)

            # setup the final image
            result_width = image_width + (2 * self.image_border_size)
            result_height = (image_height * self.num_photos) + ((self.num_photos + 1) * self.image_border_size)
            print(f"final image size: {result_width}x{result_height}")

            unspooked_image = Image.new("RGBA", (result_width, result_height), (255, 255, 255, 255))
            final_image = Image.new("RGBA", (result_width, result_height), (255, 255, 255, 255))

            # 2b) for each image:
            #   - determine which spooky effects to run
            #   - spookify them
            #   - add to the final image
            count = 0
            for context in processing_contexts:
                x = self.image_border_size
                y = (count * image_height) + ((count + 1) * self.image_border_size)

                unspooked_image.paste(context.img, (x, y))

                effects = self.__determine_effects_to_run()

                for effect in effects:
                    print(f"Running effect {effect.__class__.__name__} on {context.filename()}")
                    context.img = effect.process_image(context)

                print(f"putting image of size {context.img.size} into: {x},{y}")

                final_image.paste(context.img, (x, y))
                count += 1

            # 2c) Optionally frame the image with some more effects
            photo_strip_effect = self.__get_photo_strip_effect()
            if photo_strip_effect:
                print(f"Running photo strip effect {photo_strip_effect.__class__.__name__} on {context.filename()}")
                final_image = photo_strip_effect.process_image(final_image)

            # 3) print images!
            print("Printing the resulting image")
            now = datetime.now()
            unspooked_path = self.printer.save_unspooked(now, unspooked_image)
            spooked_path = self.printer.save_and_print(now, final_image)

            self.display.clear_text()
            self.display.put_text("All done!")
            time.sleep(3.5)

        except Exception as e:
            print(f"An exception occurred running the photobooth: {e}")
            traceback.print_exc()
            self.is_running = False
            return ("", "")

        self.is_running = False

        print("Photobooth workflow done")
        return (unspooked_path, spooked_path)

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
            photo_num = i + 1
            sub_text = f"photo {photo_num}/{self.num_photos}"
            print(f"taking {sub_text} in {self.photo_delay_seconds} seconds")

            time_left = self.photo_delay_seconds
            while time_left > 0:
                self.display.put_text(str(time_left), sub_text)
                time_left -= 1
                if self.photo_event and self.photo_event.should_send_event(
                    current_photo_number=photo_num, current_second=time_left
                ):
                    self.photo_event.send_event()
                    time.sleep(0.2)
                time.sleep(1.25)

            self.display.put_text(self.mode.get_prompts()[photo_num - 1], sub_text)
            time.sleep(0.2)
            img = self.photo_taker.take_photo()
            time.sleep(0.5)
            self.display.clear_text()

            imgs.append(img)
            print("photo taken")
            time.sleep(0.5)

        print("all photos taken!")
        return imgs

    def __setup_images_for_processing(self, imgs: List[Image.Image]) -> Tuple[int, int, List[ImageProcessingContext]]:
        prev_img = None

        contexts = []
        image_num = 1
        for img in imgs:
            if prev_img is not None and img.size != prev_img.size:
                raise ValueError(f"the image {img.filename} is not the same size as {prev_img.filename}")

            contexts.append(self.__create_context_from_image(img, image_num))
            image_num += 1

            prev_img = img

        return prev_img.width, prev_img.height, contexts

    def __create_context_from_image(self, img: Image, image_num: int) -> ImageProcessingContext:
        img_data = np.array(img)
        faces = find_faces_from_array(img_data)
        return ImageProcessingContext(img, img_data, faces, image_num)

    def __get_photo_strip_effect(self) -> Optional[PhotoStripFrame]:
        if self.mode == Mode.barbie:
            return PhotoStripFrame("./resources/barbie/barbie-frame-sara.png", 10, 247, 580)
        if self.mode == Mode.piggy_3:
            return RandomFrame(
                [
                    "./resources/pigs/2023/pig-pit-2023-1.png",
                    "./resources/pigs/2023/pig-pit-2023-2.png",
                    "./resources/pigs/2023/pig-pit-2023-3.png",
                ],
                10,
                247,
                580,
            )
        return None

    def __determine_effects_to_run(self) -> List[ImageEffect]:
        if self.mode == Mode.piggy:
            return [FlyingPigsEffect(), PigNoseEffect(), PigLogoEffect()]
        elif self.mode == Mode.casey:
            return [
                RandomFullFrameEffect("./resources/casey/"),
                FinalFrameEffect("./resources/casey/logo/casey_logo.png"),
            ]
        elif self.mode == Mode.barbie:
            return []
        elif self.mode == Mode.piggy_3:
            return []

        all_effects = [
            GhostEffect(),
            SketchyEyeEffect(),
            SwirlFaceEffect(1),
        ]
        chance_for_next_effect = 100

        selected_effects = []

        while len(selected_effects) < 4 and random.randint(0, 100) < chance_for_next_effect:
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

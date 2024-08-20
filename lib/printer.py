from PIL import Image
from lib.mode import Mode

class PhotoPrinter(object):
    def __init__(
        self,
        output_dir: str,
        output_file_prefix: str,
        image_type: str,
        should_print: bool,
        mode: Mode,
    ):
        self.output_dir = output_dir
        self.output_file_prefix = output_file_prefix
        self.image_type = image_type
        self.should_print = should_print
        self.mode = mode
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
        print_path = self.save_for_printing(now, img)
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


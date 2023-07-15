from enum import Enum

SPOOKY="""
  .-')     _ (`-.                           .-. .-')                     .-. .-')                             .-') _    ('-. .-.
 ( OO ).  ( (OO  )                          \  ( OO )                    \  ( OO )                           (  OO) )  ( OO )  /
(_)---\_)_.`     \ .-'),-----.  .-'),-----. ,--. ,--.   ,--.   ,--.       ;-----.\  .-'),-----.  .-'),-----. /     '._ ,--. ,--.
/    _ |(__...--''( OO'  .-.  '( OO'  .-.  '|  .'   /    \  `.'  /        | .-.  | ( OO'  .-.  '( OO'  .-.  '|'--...__)|  | |  |
\  :` `. |  /  | |/   |  | |  |/   |  | |  ||      /,  .-')     /         | '-' /_)/   |  | |  |/   |  | |  |'--.  .--'|   .|  |
 '..`''.)|  |_.' |\_) |  |\|  |\_) |  |\|  ||     ' _)(OO  \   /          | .-. `. \_) |  |\|  |\_) |  |\|  |   |  |   |       |
.-._)   \|  .___.'  \ |  | |  |  \ |  | |  ||  .   \   |   /  /\_         | |  \  |  \ |  | |  |  \ |  | |  |   |  |   |  .-.  |
\       /|  |        `'  '-'  '   `'  '-'  '|  |\   \  `-./  /.__)        | '--'  /   `'  '-'  '   `'  '-'  '   |  |   |  | |  |
 `-----' `--'          `-----'      `-----' `--' '--'    `--'             `------'      `-----'      `-----'    `--'   `--' `--'
"""

PIGGY="""
 ____ ____   ____   ____  __ __  ____    ___    ___   ______  __ __ 
|    \    | /    | /    ||  |  ||    \  /   \  /   \ |      ||  |  |
|  o  )  | |   __||   __||  |  ||  o  )|     ||     ||      ||  |  |
|   _/|  | |  |  ||  |  ||  ~  ||     ||  O  ||  O  ||_|  |_||  _  |
|  |  |  | |  |_ ||  |_ ||___, ||  O  ||     ||     |  |  |  |  |  |
|  |  |  | |     ||     ||     ||     ||     ||     |  |  |  |  |  |
|__| |____||___,_||___,_||____/ |_____| \___/  \___/   |__|  |__|__|
                                                                    
"""

CASEY="""
                                                                ___                         ___       ___       
                                                               (   )                       (   )     (   )      
  .--.      .---.      .--.      .--.    ___  ___               | |.-.     .--.     .--.    | |_      | | .-.   
 /    \    / .-, \   /  _  \    /    \  (   )(   )              | /   \   /    \   /    \  (   __)    | |/   \  
|  .-. ;  (__) ; |  . .' `. ;  |  .-. ;  | |  | |    .------.   |  .-. | |  .-. ; |  .-. ;  | |       |  .-. .  
|  |(___)   .'`  |  | '   | |  |  | | |  | |  | |   (________)  | |  | | | |  | | | |  | |  | | ___   | |  | |  
|  |       / .'| |  _\_`.(___) |  |/  |  | '  | |               | |  | | | |  | | | |  | |  | |(   )  | |  | |  
|  | ___  | /  | | (   ). '.   |  ' _.'  '  `-' |               | |  | | | |  | | | |  | |  | | | |   | |  | |  
|  '(   ) ; |  ; |  | |  `\ |  |  .'.-.   `.__. |               | '  | | | '  | | | '  | |  | ' | |   | |  | |  
'  `-' |  ' `-'  |  ; '._,' '  '  `-' /   ___ | |               ' `-' ;  '  `-' / '  `-' /  ' `-' ;   | |  | |  
 `.__,'   `.__.'_.   '.___.'    `.__.'   (   )' |                `.__.    `.__.'   `.__.'    `.__.   (___)(___) 
                                          ; `-' '                                                               
                                           .__.'                                                                
"""

BARBIE="""
 ______                  __         _          ______                    _   __       
|_   _ \                [  |       (_)        |_   _ \                  / |_[  |      
  | |_) |  ,--.   _ .--. | |.--.   __  .---.    | |_) |   .--.    .--. `| |-'| |--.   
  |  __'. `'_\ : [ `/'`\]| '/'`\ \[  |/ /__\\   |  __'. / .'`\ \/ .'`\ \| |  | .-. |  
 _| |__) |// | |, | |    |  \__/ | | || \__.,  _| |__) || \__. || \__. || |, | | | |  
|_______/ \'-;__/[___]  [__;.__.' [___]'.__.' |_______/  '.__.'  '.__.' \__/[___]|__] 
                                                                                      
"""


class Mode(Enum):
    spooky = 0
    piggy  = 1
    casey  = 2
    barbie = 3

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return Mode[s]
        except KeyError:
            raise ValueError()

    def ascii_art(self):
        return [
            SPOOKY,
            PIGGY,
            CASEY,
            BARBIE,
        ][self.value]

    def get_title(self):
        return [
            "Spooky Booth",
            "Piggy Booth",
            "Casey's 30th B-Day Photo Booth",
            "Barbie Booth",
        ][self.value]

    def start_prompt(self):
        return [
            "ENTER your phone number to get SPOOKED!",
            "ENTER your phone number PIGGIES!",
            "Enter your phone number party people!",
            "Press ENTER to get started!"
        ][self.value]

    def get_prompts(self):
        return [
            ["Cheese!", "Cheese!", "Die!", "Cheese!"],
            ["Cheese!", "Cheese!", "Bacon!", "Cheese!"],
            ["Cheese!", "Cheese!", "Mashed Potato!", "Cheese!"],
            ["Cheese!", "Cheese!", "Work it Cowgirl!", "That's it Cowgirl!"],
        ][self.value]

    def processing_images_prompt(self):
        return [
            "Detecting ghosts...",
            "Finding little piggies...",
            "Assembling your photos...",
            "Assembling your photos...",
        ][self.value]

    
    def get_mms_content(self, unspooked_url, spooked_url):
        return [
            f"Your Halloween Photobooth photos are ready! Download now!\n\nSpooked: {spooked_url}\n\nOriginal: {unspooked_url}",
            f"Your Piggy Booth photos are ready! Download now!\n\nPiggies: {spooked_url}\n\nOriginal: {unspooked_url}",
            f"Your Photo Booth photos are ready! Download now!\n\nCaseyfied: {spooked_url}\n\nOriginal: {unspooked_url}\n\nHappy 30th Casey!",
            f"Your Photo Booth photos are ready! Download now!\n\nBarbified: {spooked_url}\n\nOriginal: {unspooked_url}\n\nHappy Birthday Sara!",
        ][self.value]

    def get_mms_preview_image(self):
        return [
            "https://is4-ssl.mzstatic.com/image/thumb/Purple128/v4/72/d9/21/72d92136-dd8b-42c0-8d87-c242fa6468c7/source/256x256bb.jpg",
            "https://pbs.twimg.com/profile_images/668934629680791552/b7WMPIlK_400x400.jpg",
            "https://jmattfong-halloween-public.s3.us-west-2.amazonaws.com/casey_256.jpg",
            "https://ih1.redbubble.net/image.3764780822.3959/flat,128x,075,f-pad,128x128,f8f8f8.jpg",
        ][self.value]

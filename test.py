import cv2

# Write some Text

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,500)
fontScale              = 1
fontColor              = (255,255,255)
lineType               = 2


def show_webcam(mirror=False):
    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        if mirror:
            img = cv2.flip(img, 1)
        draw_countdown_text(img, '5')
        draw_photo_num_text(img, 'photo 1/4')
        cv2.imshow('my webcam', img)
        key_press = cv2.waitKey(1)
        if ord('\n') == key_press or key_press == ord('\r'):
            break  # esc to quit
    cv2.destroyAllWindows()

def draw_countdown_text(img, text="what what in my butt"):
    height, width, _ = img.shape
    font_scale = 7
    thickness = 7

    (text_width, text_height), _ = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=font_scale, thickness=thickness)
    text_location = (int(width / 2 - text_width / 2), int(height / 2 + text_height / 2))

    cv2.putText(img,
        text=text,
        org=text_location,
        fontFace=cv2.FONT_HERSHEY_COMPLEX,
        fontScale=font_scale,
        color=[0, 0, 0],
        lineType=cv2.LINE_AA, thickness=thickness)
    cv2.putText(img,
        text=text,
        org=text_location,
        fontFace=cv2.FONT_HERSHEY_COMPLEX,
        fontScale=font_scale,
        color=[255, 255, 255],
        lineType=cv2.LINE_AA, thickness=(thickness - 3))

def draw_photo_num_text(img, text="you wanna do it my butt?"):
    height, width, _ = img.shape
    font_scale = 1
    thickness = 4

    (text_width, text_height), _ = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=font_scale, thickness=thickness)
    text_location = (50, 50)

    cv2.putText(img,
        text=text,
        org=text_location,
        fontFace=cv2.FONT_HERSHEY_COMPLEX,
        fontScale=font_scale,
        color=[0, 0, 0],
        lineType=cv2.LINE_AA, thickness=thickness)
    cv2.putText(img,
        text=text,
        org=text_location,
        fontFace=cv2.FONT_HERSHEY_COMPLEX,
        fontScale=font_scale,
        color=[255, 255, 255],
        lineType=cv2.LINE_AA, thickness=(thickness - 2))


def main():
    show_webcam(mirror=True)


if __name__ == '__main__':
    main()
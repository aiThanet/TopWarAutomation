import cv2
import math
import time
import numpy as np
import pytesseract

def get_length_by_ratio(ratio, length):
    if ratio == 0:
        return 0
    return int(length * ratio)

def get_ratio_postion(pos, width, height):
    x_pos_1 = get_length_by_ratio(pos['x'][0], width) 
    x_pos_2 = get_length_by_ratio(pos['x'][1], width) 
    y_pos_1 = get_length_by_ratio(pos['y'][0], height) 
    y_pos_2 = get_length_by_ratio(pos['y'][1], height)
    return (x_pos_1, x_pos_2, y_pos_1, y_pos_2)

def get_partial_image(img, pos):
    tmp_img = img.copy()
    return tmp_img[pos[2]:pos[3], pos[0]:pos[1], :]

def get_partial_image_by_key(key, config, img):
    height, width, _ = img.shape
    key_pos = config[key]['pos']
    ratio_pos = get_ratio_postion(key_pos, width, height)
    return get_partial_image(img, ratio_pos)

def click(device, x, y, description="", sleep_after_click=0.2):
    if description:
        print(description)
    device.shell(f"input tap {x} {y}")
    time.sleep(sleep_after_click)

def match_template(img, template, threshold=0.9):
    """
    Matches template image in a target grayscaled image
    """
    img_grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_grayscale, template, cv2.TM_CCOEFF_NORMED)
    matches = np.where(res >= threshold)
    return list(zip(*matches[::-1]))

def search_image_by_key(key, config, screen, menu_key='img'):
    image_part = get_partial_image_by_key(key, config, screen)
    # cv2.imshow('a',image_part)
    # cv2.waitKey(0)
    template_img = cv2.imread(config[key][menu_key], 0)
    template_h, template_w  = template_img.shape
    matches = match_template(image_part, template_img)
    
    return matches, template_w, template_h

def search_img_and_click(img_path, screen, device, img_name, sleep_after_click, threshold = 0.8):
    img = cv2.imread(img_path)
    template_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width, _ = img.shape
    matches = match_template(screen, template_img, threshold)

    print(matches)

    click(device, matches[0][0]+width//2, matches[0][1]+height//2, f"click {img_name} image", sleep_after_click)

def get_number_from_image(img):
    img_cv = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_cv = cv2.bitwise_not(img_cv)

    # (_, blackAndWhiteImage) = cv2.threshold(img_cv, 127, 255, cv2.THRESH_BINARY)
 
    # cv2.imshow('Black white image', blackAndWhiteImage)
    # cv2.waitKey(0)
    # # img_cv = cv2.adaptiveThreshold(img_cv,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    # #         cv2.THRESH_BINARY,11,2)

    # # img_cv = cv2.threshold(img_cv, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]



    # edges = cv2.Canny(img_cv, 80, 120)
    # lines = cv2.HoughLinesP(edges, 1, math.pi/2, 2, None, 30, 1)
    # print(lines)
    # for line in lines[0]:
    #     pt1 = (line[0],line[1])
    #     pt2 = (line[2],line[3])
    #     cv2.line(img_cv, pt1, pt2, (0,0,255), 3)


    # cv2.imshow('a',img_cv)
    # cv2.waitKey(0)
    
    custom_config = '--oem 3 --psm 7 outputbase digits'
    text = pytesseract.image_to_string(img_cv, config=custom_config)
    result = list(filter(lambda x: x.isnumeric(), text.split('\n')))
    if result:
        return int(result[0])
    else:
        return -1
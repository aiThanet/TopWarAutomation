import cv2
import time
import uuid
import numpy as np
import pytesseract
from datetime import datetime

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

def get_postion(pos):
    return (pos['x'][0], pos['x'][1], pos['y'][0], pos['y'][1])

def get_partial_image(img, pos):
    tmp_img = img.copy()
    return tmp_img[pos[2]:pos[3], pos[0]:pos[1], :]

def get_partial_image_by_key(pos, img, debug= False):
    
    # height, width, _ = img.shape
    key_pos = pos['pos']
    
    ratio_pos = get_postion(key_pos)
    if debug:
        img_tmp = img.copy()
        cv2.rectangle(img_tmp, (ratio_pos[0], ratio_pos[2]),(ratio_pos[1], ratio_pos[3]), color=(0, 0, 255),thickness=5)
        uid = uuid.uuid1()
        cv2.imwrite(f'{uid}.jpg',img_tmp)
    return get_partial_image(img, ratio_pos)

def click(device, x, y, description="", sleep_after_click=0.2, debug=False):
    if description:
        printLog(description)
    
    if debug:
        cur_screen = device.screencap()
        with open('screen.png','wb') as f:
            f.write(cur_screen)
        cur_screen = cv2.imread('screen.png')
        cv2.circle(cur_screen, (x, y), 10, color=(0, 0, 255),thickness=-1)
        cv2.imwrite(f'{description}.jpg',cur_screen)

    device.shell(f"input tap {x} {y}")
    time.sleep(sleep_after_click)

def click_by_pos(device, pos, description="", sleep_after_click=0.2):
    click(device, pos['click_pos']['x'], pos['click_pos']['y'], description, sleep_after_click)
        

def match_template(img, template, threshold=0.9):
    """
    Matches template image in a target grayscaled image
    """
    img_grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_grayscale, template, cv2.TM_CCOEFF_NORMED)
    matches = np.where(res >= threshold)
    return list(zip(*matches[::-1]))

def search_image_by_key(key, config, screen, menu_key='img'):
    image_part = get_partial_image_by_key(config[key], screen)
    template_img = cv2.imread(config[key][menu_key], 0)
    template_h, template_w  = template_img.shape
    matches = match_template(image_part, template_img)
    
    return matches, template_w, template_h

def search_img(img_path, screen, threshold = 0.8):
    img = cv2.imread(img_path)
    template_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width, _ = img.shape
    matches = match_template(screen, template_img, threshold)

    if matches:
        return True, matches[0][0]+width//2, matches[0][1]+height//2
    else:
        return False, -1, -1

def search_img_by_part(img_path, screen, pos, threshold = 0.8):
    
    image_part = get_partial_image_by_key(pos, screen)
    # h, w, _ = screen.shape
    is_found, x, y = search_img(img_path, image_part, threshold)
    
    x_offset, _, y_offset, _ = get_postion(pos['pos'])

    return is_found, x_offset + x, y_offset + y

def get_number_from_image(img, debug= True):
    
    custom_config = '--oem 3 --psm 7 outputbase -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(img, config=custom_config)
    result = ''.join([char for char in text if str(char).isdigit()])

    now = datetime.now()
    
    # print(text)
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
    if result:
        res = int(result)
        if debug:
            cv2.imwrite(f'./debug/num/{dt_string}-C{res}.jpg', img)
        return res
    else:
        if debug:
            cv2.imwrite(f'./debug/num/{dt_string}-W.jpg', img)
        return -1

def compare_image(image1, image2, similar_threshold = 0.8):
    img1 = cv2.imread(image1)
    img2 = cv2.imread(image2)
    img1_hsv = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
    img2_hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

    hist_img1 = cv2.calcHist([img1_hsv],[0,1], None, [180,256], [0,180,0,256])
    hist_img2 = cv2.calcHist([img2_hsv],[0,1], None, [180,256], [0,180,0,256])

    metric_val = cv2.compareHist(hist_img1,hist_img2, cv2.HISTCMP_CORREL)
    return metric_val >= similar_threshold

def printLog(*texts):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time, ':', ' '.join([str(text) for text in texts]))
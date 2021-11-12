from ctypes import resize
from ppadb.client import Client as AdbClient
from PIL import Image
import numpy as np
import time
import sys
import json
import cv2
import utils


class Topwar():
    def __init__(self, clientIP = "127.0.0.1", clientPort = 5037, device = 0, config_file = './config.json'):
        self.version = "0.1"
        self.adbClient = AdbClient(host=clientIP, port=clientPort)
        self.devices = self.adbClient.devices()
        if len(self.devices) < (device + 1):
            sys.exit("Error: Not found device")
        self.device = self.devices[device]
        self.number_attack_warhammer = 0
        self.first_time_warhammer = True
        self.get_cur_screen()
        

        # load config
        with open(config_file,'r') as f:
            self.config = json.load(f)

        
        # img = cv2.imread("screen.png")
        # cv2.imshow("a",img)
        # cv2.waitKey(0)
        # sys.exit()

        
        
        # self.get_vit()
        # self.attack_warhammer()
        # utils.search_img_and_click('./assets/10rally.jpg', self.cur_screen, self.device, 'Rally Button 10 Vits', 3)
        self.loop_attack_warhammer()

    def loop_attack_warhammer(self, start_vit = 100, max_queue = 5):
        self.vit = start_vit
        while(self.vit >= 10):
            while(self.get_march_queue() >= max_queue):
                print("Exceed number of queue")
                time.sleep(15)
            print("Attack WarHammer:", self.number_attack_warhammer)
            self.attack_warhammer()
            self.number_attack_warhammer += 1
            time.sleep(60 * 2.5)
            
        
    def get_cur_screen(self, debug = False):
        cur_screen = self.device.screencap()
        with open('screen.png','wb') as f:
            f.write(cur_screen)
        self.cur_screen = cv2.imread('screen.png')
        self.height, self.width, _ = self.cur_screen.shape

        if debug:
            cv2.imshow("screen", self.cur_screen)
            cv2.waitKey(0)

    def attack_warhammer(self, level = 50):
        print("==============================================")
        print('Start attack WarHammer current vit:', self.vit)

        self.click_bottom_menu(menu='world', sleep_after_click=3)
        # current_vit = self.get_vit()
        # if current_vit < 10:
        #     print('Not enough vit current vit:', current_vit)
        #     return
        # print('Start attack WarHammer current vit:', current_vit)

        self.click_bottom_menu(menu='search')
        click_add_level = {
            10: 0,
            20: 1,
            30: 2,
            40: 3,
            50: 4
        }
        time_to_add_level = click_add_level[level]
        warhammer_seq = self.config['sequence']['warhammer']['seq']
        warhammer_description = self.config['sequence']['warhammer']['description']
        for idx, click in enumerate(warhammer_seq):
            if warhammer_description[idx] == 'click add level' and self.first_time_warhammer:
                for i in range(time_to_add_level):
                    utils.click(self.device, click[0], click[1], warhammer_description[idx], click[2])
                self.first_time_warhammer = False
            else:
                utils.click(self.device, click[0], click[1], warhammer_description[idx], click[2])

        # utils.search_img_and_click('./assets/10rally.jpg', self.cur_screen, self.device, 'Rally Button 10 Vits', 3)
        utils.click(self.device, self.width//2, 600, 'click cally Button 10 Vits', 1)
        utils.click(self.device, 470, 1350, 'click formation 2', 0.5)
        utils.click(self.device, self.width//2, 600, 'click battle', 0.3)

        self.vit -= 8

    def get_march_queue(self):
        self.click_bottom_menu('world')
        self.get_cur_screen()
        image_part = utils.get_partial_image_by_key('march_queue', self.config, self.cur_screen)
        gray_img = cv2.cvtColor(image_part, cv2.COLOR_BGR2GRAY)
        bitwise_gray_img = cv2.bitwise_not(gray_img)
        h,w = bitwise_gray_img.shape
        resized_bitwise_gray_img = cv2.resize(bitwise_gray_img, (w*2,h*2))

        circles = cv2.HoughCircles(resized_bitwise_gray_img, cv2.HOUGH_GRADIENT, 1, 20)
            
        try:
            return circles.shape[1]
        except:
            print("Please open march queue tap")
            return 999

    
    def get_vit(self, vit_bar_length = 150):
        """
        get remaining vit (need to call when in world map)
        """
        matches, template_w, template_h = utils.search_image_by_key('vit', self.config, self.cur_screen)
    
        if matches:
            vit_state_image = self.cur_screen.copy()[matches[0][1]:(matches[0][1] + template_h),(matches[0][0] + template_w):(matches[0][0] + template_w + vit_bar_length),:]
            vit = utils.get_number_from_image(vit_state_image)
            return vit
        else:
            print("Can't find vit bar")
            return 0


    def click_bottom_menu(self, menu='base', sleep_after_click=2.5):
        """
        have 3 options: base , world and search
        """
        self.get_cur_screen()
        matches, menu_w, menu_h = utils.search_image_by_key('bottom_menu', self.config, self.cur_screen, menu_key=menu)

        y_offset = int(self.config['bottom_menu']['pos']['y'][0] * self.height)
        if matches:
            utils.click(self.device, (matches[0][0] + menu_w//2), (y_offset + matches[0][1] + menu_h//2), description = f'click {menu} button', sleep_after_click=sleep_after_click)
        else:
            print('not found menu:', menu)
            return
           
topwar = Topwar()




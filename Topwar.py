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
    def __init__(self, clientIP = "127.0.0.1", clientPort = 5037, device = 0, config_file = './config.json', max_queue = 5, is_allow_add_vit = False, is_allow10vit = True, is_allow50vit = True, war_hammer_vit_consume = 8, war_hammer_level = 50):
        self.version = "0.1"
        self.adbClient = AdbClient(host=clientIP, port=clientPort)
        self.devices = self.adbClient.devices()
        if len(self.devices) < (device + 1):
            sys.exit("Error: Not found device")
        self.device = self.devices[device]
        self.number_attack_warhammer = 0
        self.first_time_warhammer = True
        self.max_queue = max_queue
        self.is_allow_add_vit = is_allow_add_vit
        self.is_allow10vit = is_allow10vit
        self.is_allow50vit = is_allow50vit
        self.war_hammer_vit_consume = war_hammer_vit_consume
        self.war_hammer_level = war_hammer_level
        self.get_cur_screen()
       
        # load config
        with open(config_file,'r') as f:
            self.config = json.load(f)

        self.vit = self.get_vit()
        print("Start vit:", self.vit)


    def loop_attack_warhammer(self):
        
        while(self.vit >= 10):
            while(self.get_march_queue() >= self.max_queue):
                print("Exceed number of queue")
                time.sleep(15)
            print("Attack WarHammer:", self.number_attack_warhammer)
            self.attack_warhammer()
            self.number_attack_warhammer += 1
            time.sleep(60 * 1.5)

            if self.vit  < 10 and self.is_allow_add_vit:
                self.add_vit()     
        
    def get_cur_screen(self, debug = False):
        cur_screen = self.device.screencap()
        with open('screen.png','wb') as f:
            f.write(cur_screen)
        self.cur_screen = cv2.imread('screen.png')
        self.height, self.width, _ = self.cur_screen.shape

        if debug:
            cv2.imshow("screen", self.cur_screen)
            cv2.waitKey(0)

    def attack_warhammer(self):
        print("==============================================")
        print('Start attack WarHammer current vit:', self.vit)

        self.click_bottom_menu(menu='world', sleep_after_click=3)
        self.vit = self.get_vit()
        if self.vit < 10:
            print('Not enough vit current vit:', self.vit)
            return
        print('Start attack WarHammer current vit:', self.vit)

        self.click_bottom_menu(menu='search')
        click_add_level = {
            10: 0,
            20: 1,
            30: 2,
            40: 3,
            50: 4
        }
        time_to_add_level = click_add_level[self.war_hammer_level]
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

        self.vit -= self.war_hammer_vit_consume

    def get_march_queue(self):
        """
        get number of march in queue
        """
        print("Check march queue")
        self.click_bottom_menu('world')
        self.get_cur_screen()
        image_part = utils.get_partial_image_by_key(self.config['march_queue'], self.cur_screen)
        gray_img = cv2.cvtColor(image_part, cv2.COLOR_BGR2GRAY)
        bitwise_gray_img = cv2.bitwise_not(gray_img)
        h,w = bitwise_gray_img.shape
        resized_bitwise_gray_img = cv2.resize(bitwise_gray_img, (w*2,h*2))


        circles = cv2.HoughCircles(resized_bitwise_gray_img, cv2.HOUGH_GRADIENT, 1, 20)
            
        
        try:
            print("num queue:",circles.shape)
            return circles.shape[1]
        except:
            print("Please open march queue tap")
            return 999
    
    def get_vit(self):
        """
        get remaining vit
        """
        self.click_bottom_menu("world")
        utils.click_by_pos(self.device, self.config['vit_bar'], "Click vit bar", 1)
        self.get_cur_screen()

        image_part = utils.get_partial_image_by_key(self.config['vit_area'], self.cur_screen)

        # remove green color range
        hsv = cv2.cvtColor(image_part, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (36, 25, 25), (70, 255,255))
        imask = mask>0
        image_part[imask] = [0,0,0]

        # remove black color range
        black_mask = cv2.inRange(image_part, (0, 0, 0), (100, 95, 95))

        num_image = black_mask[:,210:290]
        h, w = num_image.shape
        num_image = cv2.resize(num_image, (w*3, h*3))
        # cv2.imshow('r',num_image)
        # cv2.waitKey(0)
        vit = utils.get_number_from_image(num_image)

        utils.click_by_pos(self.device, self.config['close_btn'], "Close vit bar", 1)
        return int(vit)

    def add_vit(self):
        self.click_bottom_menu("world")
        utils.click_by_pos(self.device, self.config['vit_bar'], "Click vit bar", 1)
        self.get_cur_screen()

        self.vit += 10

        if self.is_allow10vit:
            is10vit_found, x, y = utils.search_img_by_part('./assets/vit_item10.jpg', self.cur_screen, self.config['vit_item_area'], 0.95)
            if is10vit_found:
                utils.click(self.device, x, y, description="Click vit item +10")
                utils.click_by_pos(self.device, self.config['use_btn'], "Click use vit item +10", 1)
                utils.click_by_pos(self.device, self.config['vit_bar'], "Click vit bar", 1)
                self.vit += 10
                return

        if self.is_allow50vit:
            is50vit_found, x, y = utils.search_img_by_part('./assets/vit_item50.jpg', self.cur_screen, self.config['vit_item_area'], 0.95)
            if is50vit_found:
                utils.click(self.device, x, y, description="Click vit item +50")
                utils.click_by_pos(self.device, self.config['use_btn'], "Click use vit item +50", 1)
                utils.click_by_pos(self.device, self.config['vit_bar'], "Click vit bar", 1)
                self.vit += 50
                return

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
        
    def start(self):
        self.loop_attack_warhammer()

topwar = Topwar()
topwar.start()




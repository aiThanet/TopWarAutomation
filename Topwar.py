from ppadb.client import Client as AdbClient
from datetime import datetime
import numpy as np
import time
import sys
import json
import cv2
import utils


class Topwar():
    def __init__(self, clientIP = "127.0.0.1", clientPort = 5037, device = 0, config_file = './config.json', max_queue = 4, is_allow_add_vit = False, is_allow10vit = True, is_allow50vit = True, war_hammer_level = 50):
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
        self.war_hammer_level = war_hammer_level
        self.get_cur_screen()
       
        # load config
        with open(config_file,'r') as f:
            self.config = json.load(f)


    def loop_attack_warhammer(self):
        self.vit = self.get_vit()
        utils.printLog("Start vit:", self.vit)
        while(self.vit >= 10):
            while(self.get_march_queue() >= self.max_queue):
                utils.printLog("Exceed number of queue")
                time.sleep(15)
            utils.printLog("Attack WarHammer:", self.number_attack_warhammer)
            self.attack_warhammer()
            
            self.vit = self.get_vit()
            if self.vit  < 10 and self.is_allow_add_vit and self.vit != -1:
                self.add_vit()

            self.number_attack_warhammer += 1
            time.sleep(60 * 2)
            
        
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
        print("====================================================")
        self.click_bottom_menu(menu='world', sleep_after_click=3)
        
        if self.vit < 10:
            utils.printLog(f'Not enough vit current vit: {self.vit}')
            return
        utils.printLog('Start attack WarHammer current vit:', self.vit)
        

        self.click_bottom_menu(menu='search')
        click_add_level = {
            10: 0,
            20: 1,
            30: 2,
            40: 3,
            50: 4
        }
        time_to_add_level = click_add_level[self.war_hammer_level]
        warhammer_click_pos = self.config['sequence']['warhammer']['click_pos']
        warhammer_wait_duration = self.config['sequence']['warhammer']['wait_duration']
        warhammer_description = self.config['sequence']['warhammer']['description']
        for idx, click in enumerate(warhammer_click_pos):
            if warhammer_description[idx] == 'click add level':
                if self.first_time_warhammer:
                    for _ in range(time_to_add_level):
                        utils.click(self.device, click['x'], click['y'], warhammer_description[idx], warhammer_wait_duration[idx])
                    self.first_time_warhammer = False
            else:
                utils.click(self.device, click['x'], click['y'], warhammer_description[idx], warhammer_wait_duration[idx])

        utils.click_by_pos(self.device, self.config['rally_btn'], "Click Rally", 1)
        utils.click_by_pos(self.device, self.config['formation_2_btn'], "Click formation 2", 0.3)
        self.get_cur_screen()
        is_found, _, _ = utils.search_img_by_part('./assets/addHero.jpg', self.cur_screen, self.config['select_hero_area'])
        if is_found:
            utils.printLog("Hero in formation is empty!")
            utils.click_by_pos(self.device, self.config['back_btn'], "Go back to world map")
            utils.click_by_pos(self.device, self.config['ok_btn'], "Click OK", 0.5)
            return

        utils.click_by_pos(self.device, self.config['battle_btn'], "Click battle btn", 0.3)

    def get_march_queue(self, debug=True):
        """
        get number of march in queue
        """
        utils.printLog("Check march queue")
        self.click_bottom_menu('world')
        self.get_cur_screen()
        image_part = utils.get_partial_image_by_key(self.config['march_queue_area'], self.cur_screen)
        gray_img = cv2.cvtColor(image_part, cv2.COLOR_BGR2GRAY)
        bitwise_gray_img = cv2.bitwise_not(gray_img)
        # cv2.imshow('test', bitwise_gray_img)
        # cv2.imwrite('./test.jpg', bitwise_gray_img)
        # cv2.waitKey(0)
        circles = cv2.HoughCircles(bitwise_gray_img, cv2.HOUGH_GRADIENT, 1,  minDist=20, param1=200, param2=50, minRadius=18)
        # print(circles.shape)
        if debug and circles is not None:
        
            image_part_tmp = image_part.copy()
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
            cv2.imwrite(f'./debug/march/{dt_string}-C{circles.shape[1]}-RGB-NC.jpg', image_part_tmp)
            circles2 = np.uint16(np.around(circles))
            for i in circles2[0,:]:
                # draw the outer circle
                cv2.circle(image_part,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(image_part,(i[0],i[1]),2,(0,0,255),3)
                
                try:
                    cv2.imwrite(f'./debug/march/{dt_string}-C{circles.shape[1]}-RGB-C.jpg', image_part)
                    cv2.imwrite(f'./debug/march/{dt_string}-C{circles.shape[1]}-BW.jpg', bitwise_gray_img)
                except:
                    cv2.imwrite(f'./debug/march/{dt_string}-W.jpg', image_part)
            
        try:
            utils.printLog("num queue:",circles.shape)
            return circles.shape[1]
        except:
            utils.printLog("Please open march queue tap")
            return 999
    
    def get_vit(self):
        """
        get remaining vit
        """
        self.click_bottom_menu("world")
        utils.click_by_pos(self.device, self.config['vit_bar_btn'], "Click vit bar", 1)
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
        vit = utils.get_number_from_image(num_image)

        utils.printLog("GET VIT:", vit)

        utils.click_by_pos(self.device, self.config['close_btn'], "Close vit bar", 1)
        return int(vit)

    def add_vit(self):
        self.click_bottom_menu("world")
        utils.click_by_pos(self.device, self.config['vit_bar_btn'], "Click vit bar", 1)
        self.get_cur_screen()

        if self.is_allow10vit:
            is10vit_found, x, y = utils.search_img_by_part('./assets/vit_item10.jpg', self.cur_screen, self.config['vit_item_area'], 0.95)
            if is10vit_found:
                utils.click(self.device, x, y, description="Click vit item +10")
                utils.click_by_pos(self.device, self.config['use_btn'], "Click use vit item +10", 1)
                utils.click_by_pos(self.device, self.config['vit_bar_btn'], "Click vit bar", 1)
                self.vit += 10
                return

        if self.is_allow50vit:
            is50vit_found, x, y = utils.search_img_by_part('./assets/vit_item50.jpg', self.cur_screen, self.config['vit_item_area'], 0.95)
            if is50vit_found:
                utils.click(self.device, x, y, description="Click vit item +50")
                utils.click_by_pos(self.device, self.config['use_btn'], "Click use vit item +50", 1)
                utils.click_by_pos(self.device, self.config['vit_bar_btn'], "Click vit bar", 1)
                self.vit += 50
                return

    def click_bottom_menu(self, menu='base', sleep_after_click=2.5):
        """
        have 3 options: base , world and search
        """
        self.get_cur_screen()
        is_found, x, y = utils.search_img_by_part(self.config['bottom_menu_area'][menu], self.cur_screen, self.config['bottom_menu_area'], 0.9)

        if is_found:
            utils.click(self.device, x, y, description = f'click {menu} button', sleep_after_click=sleep_after_click)
        else:
            utils.printLog('not found menu:', menu)
            return

    def join_rally(self):
        is_join = False

        utils.click_by_pos(self.device, self.config['guild_btn'], "Click guild btn", 0.3)
        utils.click_by_pos(self.device, self.config['guild_battle_btn'], "Click guild battle btn", 1)
        self.get_cur_screen()
        is_found, x, y = utils.search_img_by_part("./assets/close_btn.jpg",self.cur_screen,  self.config['close_area'])
        print('find close btn', is_found,x ,y)
        while(is_found):
            time.sleep(1)
            utils.click_by_pos(self.device, self.config['guild_battle_btn'], "Click guild battle btn", 0.3)
            self.get_cur_screen()
            is_found, _, _ = utils.search_img_by_part("./assets/close_btn.jpg",self.cur_screen,  self.config['close_area'])
        
        while(not is_join):
            self.get_cur_screen()
            is_found, x, y = utils.search_img_by_part("./assets/join_rally.jpg",self.cur_screen,  self.config['guild_rally_area'])
            print('find join rally btn', is_found,x ,y)

            if is_found:
                utils.click(self.device, x, y, description="join rally", sleep_after_click=1)
                utils.click_by_pos(self.device, self.config['first_unit_btn'], "Click first unit btn", 0.3)
                utils.click_by_pos(self.device, self.config['battle_btn'], "Click battle btn", 0.3)
                self.get_cur_screen()
                is_found, x, y = utils.search_img_by_part("./assets/cancel.jpg", self.cur_screen,  self.config['cancel_area'])
                if is_found:
                    utils.click(self.device, x, y, description="click cancel")
                    time.sleep(1)
                else:
                    is_join = True
                    utils.click_by_pos(self.device, self.config['back_btn'], "Go back to guild page")
                    utils.click_by_pos(self.device, self.config['back_btn'], "Go back to world map")
                    self.click_bottom_menu(menu="world")
                    time.sleep(60)
            else:
                time.sleep(1)
                utils.click_by_pos(self.device, self.config['refresh_btn'], "Click refresh",0.5)

            

    def loop_join_rally(self):

        while(True):
            while(self.get_march_queue() >= self.max_queue):
                    utils.printLog("Exceed number of queue")
                    time.sleep(15)
            self.join_rally()
        
    def start(self, bot_type = 'warhammer'):
        if bot_type == 'warhammer':
            self.loop_attack_warhammer()
        elif bot_type == 'join_rally':
            self.loop_join_rally()

topwar = Topwar()
topwar.start(bot_type="join_rally")




from ppadb.client import Client as AdbClient
from datetime import datetime
import numpy as np
import time
import sys
import json
import cv2
import utils
import argparse


class Topwar():
    def __init__(self, clientIP = "127.0.0.1", clientPort = 5037, device = 0, config_file = './config.json', max_queue = 4, is_allow_add_vit = True, is_allow10vit = True, is_allow50vit = True, war_hammer_level = 70, skip_refugee = True):
        self.version = "0.1"
        self.adbClient = AdbClient(host=clientIP, port=clientPort)
        self.devices = self.adbClient.devices()
        if len(self.devices) < (device + 1):
            sys.exit("Error: Not found device")
        self.device = self.devices[device]
        self.number_attack_warhammer = 0
        self.number_attack_refugee = 0
        self.first_time_warhammer = True
        self.max_queue = max_queue
        self.is_allow_add_vit = is_allow_add_vit
        self.is_allow10vit = is_allow10vit
        self.is_allow50vit = is_allow50vit
        self.war_hammer_level = war_hammer_level
        self.skip_refugee = skip_refugee
        self.get_cur_screen()

        
        # load config
        with open(config_file,'r') as f:
            self.config = json.load(f)
        self.config['march_queue_area']["pos"]["y"][1] += self.max_queue * 65

        utils.printLog("===^^^ Start Top War BOT ^^^===")

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
            50: 4,
            60: 5,
            70: 6,
            80: 7,
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
        utils.click_by_pos(self.device, self.config['formation_2_btn'], "Click formation 2", 0.5)
        self.get_cur_screen()
        is_found, _, _ = utils.search_img_by_part('./assets/addHero.jpg', self.cur_screen, self.config['select_hero_area'])
        if is_found:
            utils.printLog("Hero in formation is empty!")
            utils.click_by_pos(self.device, self.config['back_btn'], "Go back to world map")
            utils.click_by_pos(self.device, self.config['ok_btn'], "Click OK", 0.5)
            return

        utils.click_by_pos(self.device, self.config['battle_btn'], "Click battle btn", 0.5)

    def attack_refugee(self):
        print("====================================================")
        self.click_bottom_menu(menu='world', sleep_after_click=3)
        
        if self.vit < 5:
            utils.printLog(f'Not enough vit current vit: {self.vit}')
            return
        utils.printLog('Start attack Refugee current vit:', self.vit)
        
        
        click_pos = self.config['sequence']['refugee']['click_pos']
        wait_duration = self.config['sequence']['refugee']['wait_duration']
        description = self.config['sequence']['refugee']['description']

        utils.click(self.device, click_pos[0]['x'], click_pos[0]['y'], description[0], wait_duration[0])

        self.get_cur_screen()
        is_found, x, y = utils.search_img_by_part('./assets/refugee_letter.jpg', self.cur_screen, self.config['inventory_area'],threshold=0.5)
        if(is_found):
            utils.printLog("Found refugee letter")
            utils.click(self.device, x, y, description="Click refugee letter", sleep_after_click=0.5)
        else:
            utils.printLog("Can not find refugee letter")
            utils.click_by_pos(self.device, self.config['back_btn'], "Go back")
            return False
        
        for idx, click in enumerate(click_pos[1:]):
            utils.click(self.device, click['x'], click['y'], description[idx], wait_duration[idx])
        return True
    
    def get_march_queue(self, debug=False):
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
        circles = cv2.HoughCircles(bitwise_gray_img, cv2.HOUGH_GRADIENT, 1,  minDist=40, param1=200, param2=50, minRadius=18, maxRadius=28)
        # print(circles.shape)
        if debug and circles is not None:
        
            image_part_tmp = image_part.copy()
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
            cv2.imwrite(f'./debug/march/{dt_string}-C{circles.shape[1]}-RGB-NC.jpg', image_part_tmp)
            circles2 = np.uint16(np.around(circles))
            min_circle_radius = 999
            max_circle_radius = 0
            for i in circles2[0,:]:
                # draw the outer circle
                cv2.circle(image_part,(i[0],i[1]),i[2],(0,255,0),2)
                # draw the center of the circle
                cv2.circle(image_part,(i[0],i[1]),2,(0,0,255),3)
                if i[2] > max_circle_radius:
                    max_circle_radius = i[2]
                if i[2] < min_circle_radius:
                    min_circle_radius = i[2]
                try:
                    cv2.imwrite(f'./debug/march/{dt_string}-C{circles.shape[1]}-RGB-C.jpg', image_part)
                    cv2.imwrite(f'./debug/march/{dt_string}-C{circles.shape[1]}-BW.jpg', bitwise_gray_img)
                except:
                    cv2.imwrite(f'./debug/march/{dt_string}-W.jpg', image_part)
            print("max_circle_radius",max_circle_radius,"min_circle_radius",min_circle_radius)
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
        
        #dilate to imporve accuracy
        kernel = np.ones((3,3), np.uint8) 
        new_img = cv2.dilate(num_image, kernel, iterations=3)

        vit = utils.get_number_from_image(new_img)

        utils.printLog("GET VIT:", vit)

        utils.click_by_pos(self.device, self.config['close_btn'], "Close vit bar", 1)
        return int(vit)

    def add_vit(self):
        self.click_bottom_menu("world")
        utils.click_by_pos(self.device, self.config['vit_bar_btn'], "Click vit bar", 1)
        self.get_cur_screen()

        if self.is_allow10vit:
            is10vit_found, x, y = utils.search_img_by_part('./assets/vit_item10.jpg', self.cur_screen, self.config['vit_item_area'], 0.8)
            utils.printLog(f"found vit 10 {is10vit_found} {x} {y}")
            if is10vit_found:
                utils.click(self.device, x, y, description="Click vit item +10")
                utils.click_by_pos(self.device, self.config['use_btn'], "Click use vit item +10", 1)
                utils.click_by_pos(self.device, self.config['vit_bar_btn'], "Click vit bar", 1)
                self.vit += 10
                return

        if self.is_allow50vit:
            is50vit_found, x, y = utils.search_img_by_part('./assets/vit_item50.jpg', self.cur_screen, self.config['vit_item_area'], 0.8)
            utils.printLog(f"found vit 50 {is50vit_found} {x} {y}")
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

    def loop_attack_warhammer(self):
        self.vit = self.get_vit()
        utils.printLog("Start vit:", self.vit)
        while(self.vit >= 10):
            while(self.get_march_queue() >= self.max_queue):
                utils.printLog("Exceed number of queue")
                time.sleep(5)
            utils.printLog("Number Attack WarHammer:", self.number_attack_warhammer)
            self.attack_warhammer()
            
            self.vit = self.get_vit()
            if self.vit  < 10 and self.is_allow_add_vit and self.vit != -1:
                self.add_vit()

            self.number_attack_warhammer += 1
            time.sleep(60 * 2)

    def join_rally(self):
        not_found_refresh_count = 0
        is_join = False

        utils.click_by_pos(self.device, self.config['guild_btn'], "Click guild btn", 2)
        utils.click_by_pos(self.device, self.config['guild_battle_btn'], "Click guild battle btn", 2)
        self.get_cur_screen()
        is_close_btn_found, x, y = utils.search_img_by_part("./assets/close_btn.jpg",self.cur_screen,  self.config['close_area_guild_battle_btn'])
        print('find close guild battke btn', is_close_btn_found)
        while(is_close_btn_found):
            time.sleep(1)
            utils.click(self.device, x, y, "Click close btn", 0.5)
            utils.click_by_pos(self.device, self.config['guild_battle_btn'], "Click guild battle btn", 0.5)
            self.get_cur_screen()
            is_close_btn_found, x, y = utils.search_img_by_part("./assets/close_btn.jpg",self.cur_screen,  self.config['close_area_guild_battle_btn'])
            print('find close guild battke btn', is_close_btn_found)

        while(not is_join):
            self.get_cur_screen()
            is_join_found, x, y = utils.search_img_by_part("./assets/join_rally.jpg",self.cur_screen,  self.config['guild_rally_area'])
            print('find join rally btn', is_join_found)

            if is_join_found:
                rally_type = utils.get_partial_image(self.cur_screen,[x+200, x+300, y-50, y+50])
                cv2.imwrite("rally_type.jpg", rally_type)
                if self.skip_refugee and utils.compare_image("./rally_type.jpg", "./assets/refugee_camp.jpg"):
                    utils.printLog("Skip Found refugee camp")
                    continue

                utils.click(self.device, x, y, description="join rally", sleep_after_click=1)
                utils.click_by_pos(self.device, self.config['first_unit_btn'], "Click first unit btn", 0.5)
                utils.click_by_pos(self.device, self.config['battle_btn'], "Click battle btn", 0.5)
                self.get_cur_screen()
                is_overtime_found, _, _ = utils.search_img_by_part("./assets/close_btn.jpg",self.cur_screen,  self.config['close_area_overtime_rally'])
                print('found over time rally', is_overtime_found)
                if is_overtime_found: 
                    utils.click_by_pos(self.device, self.config['confirm_cancel_btn'], "Confirm cancel")
                    utils.click_by_pos(self.device, self.config['back_btn'], "Go back")
                    utils.click_by_pos(self.device, self.config['confirm_ok_btn'], "Confirm go back")
                    time.sleep(1)
                else:
                    is_join = True
                    utils.click_by_pos(self.device, self.config['back_btn'], "Go back to guild page")
                    utils.click_by_pos(self.device, self.config['back_btn'], "Go back to world map")
                    self.click_bottom_menu(menu="world")
                    time.sleep(30)
            else:
                time.sleep(1)
                self.get_cur_screen()
                is_refresh_found, x, y = utils.search_img_by_part("./assets/refresh_btn.jpg",self.cur_screen,  self.config['refresh_area'])
                print('found refresh button', is_refresh_found)
                if is_refresh_found:
                    utils.click(self.device, x, y, "Click refresh btn")
                else:
                    self.get_cur_screen()
                    is_world_found, _, _ = utils.search_img_by_part(self.config['bottom_menu_area']['world'], self.cur_screen, self.config['bottom_menu_area'], 0.9)
                    if is_world_found:
                        return

                    not_found_refresh_count += 1
                    if not_found_refresh_count >= 10:
                        utils.click_by_pos(self.device, self.config['back_btn'], "Go back to world map 1")
                        utils.click_by_pos(self.device, self.config['back_btn'], "Go back to world map 2")
                        return
            


    def loop_join_rally(self):
        self.click_bottom_menu(menu="world")
        while(True):
            while(self.get_march_queue() >= self.max_queue):
                    utils.printLog("Exceed number of queue")
                    time.sleep(5)
            self.join_rally()

    def loop_attack_refugee(self):
        self.vit = self.get_vit()
        utils.printLog("Start vit:", self.vit)
        while(self.vit >= 5):
            while(self.get_march_queue() >= self.max_queue):
                utils.printLog("Exceed number of queue")
                time.sleep(5)
            utils.printLog("Number Attack Refugee Camp:", self.number_attack_refugee)
            attack_result = self.attack_refugee()
            
            self.vit = self.get_vit()
            if self.vit  < 5 and self.is_allow_add_vit and self.vit != -1:
                self.add_vit()

            if attack_result:
                self.number_attack_refugee += 1
                time.sleep(65)
        
    def start(self, bot_type = 'warhammer'):
        if bot_type == 'warhammer':
            self.loop_attack_warhammer()
        elif bot_type == 'join_rally':
            self.loop_join_rally()
        elif bot_type == 'refugee':
            self.loop_attack_refugee()



# Create the parser
my_parser = argparse.ArgumentParser()

# Add the arguments
my_parser.add_argument('--type', action='store', type=str, required=True, help="w - warhammer bot, j - join rally bot, r - refugee camp")
my_parser.add_argument('--queue', default=4, action='store', type=int, help="max number of queue")
my_parser.add_argument('--skip', default=False, action='store_true', help="add this flag to skip joining refugee camp")


# Execute the parse_args() method
args = my_parser.parse_args()

topwar = Topwar(max_queue=args.queue, skip_refugee=args.skip)
if args.type == 'w':
    topwar.start(bot_type="warhammer")
elif args.type == 'j':
    topwar.start(bot_type="join_rally")
elif args.type == 'r':
    topwar.start(bot_type="refugee")




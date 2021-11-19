# TOP WAR AUTOMATION

Download on [Play store](https://play.google.com/store/apps/details?id=com.topwar.gp)

### Requirement
1. python3
2. ADB tools [link](https://developer.android.com/studio/command-line/adb)
3. Enable `developer option` on Andriod
4. Recommend screen size: `900 x 1600`

### How to run
1. ` pip install -r requirements.txt `
2. Open Top War game
3. `python3 Topwar.py`


### Feature
1. Auto Farm Warhammer
1. Auto check remaining vit
1. Auto use vit item
1. Auto check available march queue
1. Auto join guidl rally

### Instruction
There are some required parameters, you need to fill this with your information
- `max_queue`: the maximum number of your march queue ex.5
- `is_allow_add_vit`: if you set this flag as `True`, it will auto use your VIT capsure when it doesn't have enough VIT to use
- `is_allow10vit`: if you set this flag as `True`, it will only use your small VIT capsure
- `is_allow50vit`: if you set this flag as `True`, it will only use your Large VIT capsure
- `war_hammer_level`: level of war hammer you can only put 10, 20, 30, 40 or 50

### Set up & Limitation
- **important1** you need to set your warhammer formation at 2nd formation
- **important2** please go to `config.json` to set your position depend on your screen size
- it will freeze at some page and you need to manually go to base/world map
- your current vit can't exceed 100 otherwise it can't get the VIT

### Show Case
![example](./images/Example.gif)


### Configuration
```
// format 
(x1,y1) is TOP LEFT corner of red rectangle
(x2,y2) is BOTTOM RIGHT corner of red rectangle
"name_area" : {
        "pos" : {
            "x" : [x1,x2],
            "y": [y1,y2]
        }
    }

(x1, y2) is the coordination of red point
"name_btn" : {
        "pos" : {
            "x" : x1,
            "y": y1
        }
    }
```
1. vit_area 
- ![vit_area](./images/area/vit_area.jpg)
2. vit_item_area
- ![vit_item_area](./images/area/vit_item_area.jpg)
3. select_hero_area
- ![select_hero_area](./images/area/select_hero_area.jpg)
4. march_queue_area **please get rectangle cover only up to your max queue**
- ![march_queue_area](./images/area/march_queue_area.jpg)
5. bottom_menu_area
- ![bottom_menu_area](./images/area/bottom_menu_area.jpg)
6. vit_bar_btn
- ![vit_bar_btn](./images/btn/vit_bar_btn.jpg)
7. close_btn
- ![close_btn](./images/btn/close_btn.jpg)
8. use_btn
- ![use_btn](./images/btn/use_btn.jpg)
9.  back_btn
- ![back_btn](./images/btn/back_btn.jpg)
10. ok_btn
- ![ok_btn](./images/btn/ok_btn.jpg)
11. rally_btn
- ![rally_btn](./images/btn/rally_btn.jpg)
12. formation_2_btn
- ![formation_2_btn](./images/btn/formation_2_btn.jpg)
14. battle_btn
- ![battle_btn](./images/btn/battle_btn.jpg)
15. click rally tap
- ![click_rally_tap](./images/seq_click/click_rally_tap.jpg)    
12. click warhammer icon
- ![click_warhammer_icon.jpg](./images/seq_click/click_warhammer_icon.jpg)    
13. click add level
- ![click_add_level](./images/seq_click/click_add_level.jpg)    
14. click search button
- ![click_search_button](./images/seq_click/click_search_button.jpg)    
15. click warhammer model
- ![click_warhammer_model](./images/seq_click/click_warhammer_model.jpg)    
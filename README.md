# TOP WAR AUTOMATION

Download on [Play store](https://play.google.com/store/apps/details?id=com.topwar.gp)

### Requirement
1. python3
2. ADB tools [link](https://developer.android.com/studio/command-line/adb)
3. Enable `developer option` on Andriod

### How to run
1. ` pip install -r requirements.txt `
2. Open Top War game
3. `python3 Topwar.py`


### Feature
1. Auto Farm Warhammer
1. Auto check remaining vit
1. Auto use vit item
1. Auto check available march queue

### Instruction
There are some required parameters, you need to fill this with your information
- max_queue: the maximum number of your march queue ex.5
- is_allow_add_vit: if you set this flag as `True`, it will auto use your VIT capsure when it doesn't have enough VIT to use
- is_allow10vit: if you set this flag as `True`, it will only use your small VIT capsure
- is_allow50vit: if you set this flag as `True`, it will only use your Large VIT capsure
- war_hammer_vit_consume: set the number of VIT will be consume when attack to warhammer (Normally it would be 10, unless you rally with Diana it will consume 8)
- war_hammer_level: level of war hammer you can only put 10, 20, 30, 40 or 50

### Limitation
- it will freeze at some page and you need to manually go to base/world map
- your current vit can't exceed 100 otherwise it can't get the VIT

### Show Case
![example](./images/Example.gif)
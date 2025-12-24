from module.island.assets import *
from module.ui.page import *
from module.base.timer import Timer
from module.handler.info_handler import InfoHandler
from module.ocr.ocr import *
from datetime import datetime
from module.island.island_select_character import *
from module.island.warehouse import *
from module.handler.login import LoginHandler
from module.ui.ui import *


class Island(SelectCharacter):
    def __init__(self, *args, **kwargs):
        # 调用两个父类的初始化
        UI.__init__(self, *args, **kwargs)
        SelectCharacter.__init__(self, *args, **kwargs)
        self.island_error = False

    def goto_postmanage(self):
        page = self.ui_get_current_page()
        valid_pages = ['page_island_management', 'page_island_postmanage', 'page_island', 'page_island_warehouse']
        if page.name in valid_pages:
            self.ui_goto(page_island_postmanage,get_ship=False)
        else:
            self.goto_management()
            self.ui_goto(page_island_postmanage,get_ship=False)
    def goto_management(self):
        self.ui_goto(page_island,get_ship=False)
        while True:
            self.device.screenshot()
            if self.appear(ISLAND_CHECK, offset=(5, 5)):
                self.device.click(ISLAND_GOTO_MANAGEMENT)
            if self.appear(ISLAND_MANAGEMENT_CHECK, offset=(5, 5)):
                break
    def goto_island_map(self):
        self.ui_goto(page_island,get_ship=False)
        while True:
            self.device.screenshot()
            if self.appear_then_click(ISLAND_GOTO_MAP):
                continue
            if self.appear(ISLAND_MAP_CHECK):
                break

    def island_map_goto(self,destination):
        button_map = {
            'mine_forest': {
                'click': ISLAND_MAP_MINE_FOREST,
                'check': ISLAND_MAP_MINE_FOREST_CHECK
            },
            'farm': {
                'click': ISLAND_MAP_FARM,
                'check': ISLAND_MAP_FARM_CHECK
            },
            'nursery': {
                'click': ISLAND_MAP_NURSERY,
                'check': ISLAND_MAP_NURSERY_CHECK
            }
        }
        destination_button = button_map.get(destination, {}).get('click')
        check_button = button_map.get(destination, {}).get('check')
        self.goto_island_map()
        while True:
            self.device.screenshot()
            if self.appear(check_button):
                self.device.click(ISLAND_MAP_CONFIRM)
                break
            if self.appear_then_click(destination_button, interval=1):
                pass
        self.goto_management()
        self.ui_goto(page_island)
    def post_manage_mode(self, post_manage_mode):
        post_manage_button = POST_MANAGE_BUSINESS if post_manage_mode == POST_MANAGE_PRODUCTION else POST_MANAGE_PRODUCTION
        while True:
            self.device.screenshot()
            if self.appear_then_click(post_manage_button):
                continue
            elif self.appear(post_manage_mode):
                break

    def select_product(self,product_selection,product_selection_check):
        max_attempts = 6  # 最大尝试次数
        attempt = 0
        while attempt < max_attempts:
            self.device.screenshot()
            if self.appear(product_selection_check, offset=1):
                return True
            if self.appear_then_click(product_selection, offset=300):
                continue
            self.device.swipe_vector(vector=(0, -200), box=(333, 142, 431, 602), name="SelectionUpSwipe")
            attempt += 1
        return False
    def post_close(self):
        while 1:
            self.device.screenshot()
            if self.appear(ISLAND_POSTMANAGE_CHECK, offset=1) and self.appear(POST_MANAGE_GETTED_CHECK,threshold=1) and not self.appear(ISLAND_POST_CHECK):
                break
            if self.appear(ISLAND_GET,offset=1):
                self.device.click(ISLAND_POST_SAFE_AREA)
                continue
            if  self.appear(ISLAND_POST_CHECK,offset=1):
                self.device.click(POST_CLOSE)
                continue
    def post_get_and_close(self):
        while 1:
            self.device.screenshot()
            if self.appear(ISLAND_POSTMANAGE_CHECK,offset=1) and self.appear(POST_MANAGE_GETTED_CHECK,threshold=5) and not self.appear(ISLAND_POST_CHECK):
                break
            if self.appear(ERROR1,offset=30):
                self.device.click(POST_CLOSE)
                self.island_error = True
                continue
            if self.appear(ISLAND_GET,offset=1):
                self.device.click(ISLAND_POST_SAFE_AREA)
                self.device.click(ISLAND_POST_SAFE_AREA)
                self.device.sleep(0.5)
                continue
            if self.appear_then_click(POST_GET,offset=(50,0)):
                continue
            if  self.appear(ISLAND_POST_CHECK,offset=1) and not self.appear(POST_GET,offset=(50,0)):
                self.device.click(POST_CLOSE)
                continue


    def post_get_and_add(self,product_selection,product_selection_check):
        while 1:
            self.device.screenshot()
            if self.appear(ERROR1,offset=30):
                self.device.click(POST_CLOSE)
                self.island_error = True
                continue
            if self.appear(ISLAND_GET,offset=1):
                self.device.click(ISLAND_POST_SAFE_AREA)
                continue
            if self.appear_then_click(POST_ADD):
                continue
            if self.appear_then_click(POST_GET,offset=(50,0)):
                self.device.click(ISLAND_POST_SAFE_AREA)
                self.device.click(ISLAND_POST_SAFE_AREA)
                self.device.sleep(0.5)
                continue
            if self.appear_then_click(ISLAND_POST_SELECT,offset=1):
                continue
            if self.appear(ISLAND_SELECT_CHARACTER_CHECK,offset=1):
                if self.select_character():
                    self.device.sleep(0.3)
                    self.appear_then_click(SELECT_UI_CONFIRM)
                continue
            if self.appear(ISLAND_SELECT_PRODUCT_CHECK,offset=1):
                if self.select_product(product_selection,product_selection_check):
                    self.device.sleep(0.3)
                    self.device.click(POST_MAX)
                    self.device.sleep(0.3)
                    self.device.click(POST_ADD_ORDER)
                    break
                continue
            if (
                    self.appear(ISLAND_POST_CHECK, offset=1)
                    and not self.appear(POST_GET, offset=(50, 0))
                    and not self.appear(POST_ADD)
                    and not self.appear(ISLAND_POST_SELECT, offset=1)
            ):
                self.device.click(POST_CLOSE)
                break

    def post_open(self,post):
        template = TEMPLATE_POST_LOCK
        while True:
            image = self.device.screenshot()
            if self.appear(post,offset=300):
                cell_image = crop(image, post.button)
                if template.match(cell_image, similarity=0.85):
                    return False
            if self.appear(ISLAND_POST_CHECK):
                return True
            if self.appear_then_click(post,offset=300):
                continue
    def post_manage_up_swipe(self,distance):
        self.device.swipe_vector(vector=(0, -distance), box=(688, 69, 725, 656), name="PostUpSwipe")
        self.device.click(ISLAND_WORKING)
    def post_manage_down_swipe(self,distance):
        self.device.swipe_vector(vector=(0, distance), box=(688, 69, 725, 656), name="PostDownSwipe")
        self.device.click(ISLAND_WORKING)
    def post_manage_swipe(self,count):
        if count >= 2:
            for _ in range(count):
                self.post_manage_up_swipe(450)
        elif count == 1:
            if self.appear(ISLAND_FARM_POST1, offset=100):
                for _ in range(count):
                    self.post_manage_up_swipe(450)
            else:
                self.post_manage_down_swipe(450)
                self.device.sleep(0.3)
                self.post_manage_down_swipe(450)
                self.device.sleep(0.3)
                for _ in range(count):
                    self.post_manage_up_swipe(450)
        elif count == 0:
            if not self.appear(ISLAND_FARM_POST1, offset=100):
                self.post_manage_down_swipe(450)
                self.device.sleep(0.3)
                self.post_manage_down_swipe(450)
                self.device.sleep(0.3)

    def island_up(self,hold_time):
        p1 = (218, 507)
        p2 = (218, 441)
        self.device.island_swipe_hold(p1, p2,hold_time)
    def island_down(self,hold_time):
        p1 = (218, 507)
        p2 = (218, 572)
        self.device.island_swipe_hold(p1, p2,hold_time)
    def island_right(self,hold_time):
        p1 = (218, 507)
        p2 = (282, 507)
        self.device.island_swipe_hold(p1, p2,hold_time)
    def island_left(self,hold_time):
        p1 = (218, 507)
        p2 = (152, 507)
        self.device.island_swipe_hold(p1, p2,hold_time)

    def goto_mill(self, max_attempts=3):
        for attempt in range(max_attempts):
            print(f"尝试前往磨坊，第{attempt + 1}次尝试")
            self.island_map_goto('farm')
            self.island_up(800)
            self.island_left(1300)
            self.island_down(1000)
            self.island_left(500)
            self.island_down(2500)
            start_time = time.time()
            while True:
                self.device.screenshot()
                if self.appear_then_click(ISLAND_MILL):
                    continue
                if self.appear(ISLAND_MILL_CHECK):
                    print("成功到达磨坊")
                    return True
                if time.time() - start_time > 5:
                    print("超时，重新尝试")
                    break
        print(f"尝试{max_attempts}次后仍然失败")
        return False




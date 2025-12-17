from module.island_farm.assets import *
from module.island.island import *
from datetime import datetime
from module.handler.login import LoginHandler
from module.island.warehouse import *


class IslandFarm(Island, WarehouseOCR, LoginHandler):
    def __init__(self, *args, **kwargs):
        Island.__init__(self, *args, **kwargs)
        WarehouseOCR.__init__(self)
        # 直接使用配置变量，不再使用farm_config字典
        self.farm_positions = self.config.IslandFarm_Positions  # 农田岗位数量 1-4
        self.orchard_positions = self.config.IslandOrchard_Positions  # 果园岗位数量 1-4
        self.nursery_positions = self.config.IslandNursery_Positions  # 苗圃岗位数量 1-2
        self.ignore_avocado = self.config.IslandOrchard_IgnoreAvocado  # 是否忽略牛油果
        self.farm_threshold = self.config.IslandFarm_MinFarm  # 农田库存阈值
        self.orchard_threshold = self.config.IslandOrchard_MinOrchard  # 果园库存阈值
        self.nursery_threshold = self.config.IslandNursery_MinNursery  # 苗圃库存阈值
        self.ranch_chicken_threshold = self.config.IslandRanch_MinChicken
        self.ranch_pork_threshold = self.config.IslandRanch_MinPork

        # 保留默认作物配置
        self.plant_config = {  # 默认作物配置
            'farm': {
                'plant_default': self.config.IslandFarm_PlantPotatoes,
                'default_crop': 'potato'
            },
            'orchard': {
                'plant_default': self.config.IslandOrchard_PlantRubber,
                'default_crop': 'rubber'  # 即使有默认作物也不种
            },
            'nursery': {
                'plant_default': self.config.IslandNursery_PlantLavender,
                'default_crop': 'lavender'
            }
        }

        self.INVENTORY_CONFIG = {
            'farm': {
                'filter': FILTER_FARM,
                'threshold': self.farm_threshold,  # 直接使用变量
                'items': [
                    {'name': 'wheat', 'template': TEMPLATE_WHEAT, 'var_name': 'wheat',
                     'selection': SELECT_WHEAT, 'selection_check': SELECT_WHEAT_CHECK,
                     'post_action': POST_WHEAT, 'category': 'farm', 'seed_number': 99,
                     'shop': SHOP_SEED_WHEAT},
                    {'name': 'corn', 'template': TEMPLATE_CORN, 'var_name': 'corn',
                     'selection': SELECT_CORN, 'selection_check': SELECT_CORN_CHECK,
                     'post_action': POST_CORN, 'category': 'farm', 'seed_number': 99,
                     'shop': SHOP_SEED_CORN},
                    {'name': 'rice', 'template': TEMPLATE_RICE, 'var_name': 'rice',
                     'selection': SELECT_RICE, 'selection_check': SELECT_RICE_CHECK,
                     'post_action': POST_RICE, 'category': 'farm', 'seed_number': 45,
                     'shop': SHOP_SEED_RICE},
                    {'name': 'chinese_cabbage', 'template': TEMPLATE_CHINESE_CABBAGE, 'var_name': 'chinese_cabbage',
                     'selection': SELECT_CHINESE_CABBAGE, 'selection_check': SELECT_CHINESE_CABBAGE_CHECK,
                     'post_action': POST_CHINESE_CABBAGE, 'category': 'farm', 'seed_number': 99,
                     'shop': SHOP_SEED_CHINESE_CABBAGE},
                    {'name': 'potato', 'template': TEMPLATE_POTATO, 'var_name': 'potato',
                     'selection': SELECT_POTATO, 'selection_check': SELECT_POTATO_CHECK,
                     'post_action': POST_POTATO, 'category': 'farm', 'seed_number': 36,
                     'shop': SHOP_SEED_POTATO},
                    {'name': 'soybean', 'template': TEMPLATE_SOYBEAN, 'var_name': 'soybean',
                     'selection': SELECT_SOYBEAN, 'selection_check': SELECT_SOYBEAN_CHECK,
                     'post_action': POST_SOYBEAN, 'category': 'farm', 'seed_number': 45,
                     'shop': SHOP_SEED_SOYBEAN},
                    {'name': 'pasture', 'template': TEMPLATE_PASTURE, 'var_name': 'pasture',
                     'selection': SELECT_PASTURE, 'selection_check': SELECT_PASTURE_CHECK,
                     'post_action': POST_PASTURE, 'category': 'farm', 'seed_number': 99,
                     'shop': SHOP_SEED_PASTURE},
                    {'name': 'coffee_bean', 'template': TEMPLATE_COFFEE_BEAN, 'var_name': 'coffee_bean',
                     'selection': SELECT_COFFEE_BEAN, 'selection_check': SELECT_COFFEE_BEAN_CHECK,
                     'post_action': POST_COFFEE_BEAN, 'category': 'farm', 'seed_number': 36,
                     'shop': SHOP_SEED_COFFEE_BEAN},
                ]
            },
            'orchard': {
                'filter': FILTER_ORCHARD,
                'threshold': self.orchard_threshold,  # 直接使用变量
                'items': [
                    {'name': 'apple', 'template': TEMPLATE_APPLE, 'var_name': 'apple',
                     'selection': SELECT_APPLE, 'selection_check': SELECT_APPLE_CHECK,
                     'post_action': POST_APPLE, 'category': 'orchard', 'seed_number': 20,
                     'shop': SHOP_SEED_APPLE},
                    {'name': 'citrus', 'template': TEMPLATE_CITRUS, 'var_name': 'citrus',
                     'selection': SELECT_CITRUS, 'selection_check': SELECT_CITRUS_CHECK,
                     'post_action': POST_CITRUS, 'category': 'orchard', 'seed_number': 20,
                     'shop': SHOP_SEED_CITRUS},
                    {'name': 'banana', 'template': TEMPLATE_BANANA, 'var_name': 'banana',
                     'selection': SELECT_BANANA, 'selection_check': SELECT_BANANA_CHECK,
                     'post_action': POST_BANANA, 'category': 'orchard', 'seed_number': 16,
                     'shop': SHOP_SEED_BANANA},
                    {'name': 'mango', 'template': TEMPLATE_MANGO, 'var_name': 'mango',
                     'selection': SELECT_MANGO, 'selection_check': SELECT_MANGO_CHECK,
                     'post_action': POST_MANGO, 'category': 'orchard', 'seed_number': 16,
                     'shop': SHOP_SEED_MANGO},
                    {'name': 'lemon', 'template': TEMPLATE_LEMON, 'var_name': 'lemon',
                     'selection': SELECT_LEMON, 'selection_check': SELECT_LEMON_CHECK,
                     'post_action': POST_LEMON, 'category': 'orchard', 'seed_number': 28,
                     'shop': SHOP_SEED_LEMON},
                    {'name': 'avocado', 'template': TEMPLATE_AVOCADO, 'var_name': 'avocado',
                     'selection': SELECT_AVOCADO, 'selection_check': SELECT_AVOCADO_CHECK,
                     'post_action': POST_AVOCADO, 'category': 'orchard', 'seed_number': 16,
                     'shop': SHOP_SEED_AVOCADO},
                    {'name': 'rubber', 'template': TEMPLATE_RUBBER, 'var_name': 'rubber',
                     'selection': SELECT_RUBBER, 'selection_check': SELECT_RUBBER_CHECK,
                     'post_action': POST_RUBBER, 'category': 'orchard', 'seed_number': 16,
                     'shop': SHOP_SEED_RUBBER},
                ]
            },
            'nursery': {
                'filter': FILTER_NURSERY,
                'threshold': self.nursery_threshold,  # 直接使用变量
                'items': [
                    {'name': 'carrot', 'template': TEMPLATE_CARROT, 'var_name': 'carrot',
                     'selection': SELECT_CARROT, 'selection_check': SELECT_CARROT_CHECK,
                     'post_action': POST_CARROT, 'category': 'nursery', 'seed_number': 33,
                     'shop': SHOP_SEED_CARROT},
                    {'name': 'onion', 'template': TEMPLATE_ONION, 'var_name': 'onion',
                     'selection': SELECT_ONION, 'selection_check': SELECT_ONION_CHECK,
                     'post_action': POST_ONION, 'category': 'nursery', 'seed_number': 12,
                     'shop': SHOP_SEED_ONION},
                    {'name': 'flax', 'template': TEMPLATE_FLAX, 'var_name': 'flax',
                     'selection': SELECT_FLAX, 'selection_check': SELECT_FLAX_CHECK,
                     'post_action': POST_FLAX, 'category': 'nursery', 'seed_number': 33,
                     'shop': SHOP_SEED_FLAX},
                    {'name': 'strawberry', 'template': TEMPLATE_STRAWBERRY, 'var_name': 'strawberry',
                     'selection': SELECT_STRAWBERRY, 'selection_check': SELECT_STRAWBERRY_CHECK,
                     'post_action': POST_STRAWBERRY, 'category': 'nursery', 'seed_number': 12,
                     'shop': SHOP_SEED_STRAWBERRY},
                    {'name': 'cotton', 'template': TEMPLATE_COTTON, 'var_name': 'cotton',
                     'selection': SELECT_COTTON, 'selection_check': SELECT_COTTON_CHECK,
                     'post_action': POST_COTTON, 'category': 'nursery', 'seed_number': 21,
                     'shop': SHOP_SEED_COTTON},
                    {'name': 'tea', 'template': TEMPLATE_TEA, 'var_name': 'tea',
                     'selection': SELECT_TEA, 'selection_check': SELECT_TEA_CHECK,
                     'post_action': POST_TEA, 'category': 'nursery', 'seed_number': 12,
                     'shop': SHOP_SEED_TEA},
                    {'name': 'lavender', 'template': TEMPLATE_LAVENDER, 'var_name': 'lavender',
                     'selection': SELECT_LAVENDER, 'selection_check': SELECT_LAVENDER_CHECK,
                     'post_action': POST_LAVENDER, 'category': 'nursery', 'seed_number': 12,
                     'shop': SHOP_SEED_LAVENDER},
                ]
            },
            'mill': {
                'filter': FILTER_PROCESSED,
                'items': [
                    {'name': 'chicken_feed', 'template': TEMPLATE_CHICKEN_FEED, 'var_name': 'chicken_feed',
                     'category': 'mill', 'number': 11, 'mill': MILL_CHICKEN_FEED, 'required_material': 'wheat'},
                    {'name': 'pig_feed', 'template': TEMPLATE_PIG_FEED, 'var_name': 'pig_feed',
                     'category': 'mill', 'number': 11, 'mill': MILL_PIG_FEED, 'required_material': 'corn'},
                    {'name': 'cattle_feed', 'template': TEMPLATE_CATTLE_FEED, 'var_name': 'cattle_feed',
                     'category': 'mill', 'number': 11, 'mill': MILL_CATTLE_FEED, 'required_material': 'pasture'},
                    {'name': 'sheep_feed', 'template': TEMPLATE_SHEEP_FEED, 'var_name': 'sheep_feed',
                     'category': 'mill', 'number': 11, 'mill': MILL_SHEEP_FEED, 'required_material': 'pasture'},
                    {'name': 'wheat_flour', 'template': TEMPLATE_WHEAT_FLOUR, 'var_name': 'wheat_flour',
                     'category': 'mill', 'number': 55, 'mill': MILL_WHEAT_FLOUR, 'required_material': 'wheat'},
                ]
            },
            'ranch': {
                'filter': FILTER_RANCH,
                'items': [
                    {'name': 'chicken', 'template': TEMPLATE_CHICKEN, 'var_name': 'chicken',
                     'category': 'ranch', 'threshold': self.config.IslandRanch_MinChicken},
                    {'name': 'pork', 'template': TEMPLATE_PORK, 'var_name': 'pork',
                     'category': 'ranch', 'threshold': self.config.IslandRanch_MinPork},
                ]
            }
        }
        self.posts = {
            # 农场岗位
            'ISLAND_FARM_POST1': {'status': 'none', 'button': ISLAND_FARM_POST1},
            'ISLAND_FARM_POST2': {'status': 'none', 'button': ISLAND_FARM_POST2},
            'ISLAND_FARM_POST3': {'status': 'none', 'button': ISLAND_FARM_POST3},
            'ISLAND_FARM_POST4': {'status': 'none', 'button': ISLAND_FARM_POST4},

            # 果园岗位
            'ISLAND_ORCHARD_POST1': {'status': 'none', 'button': ISLAND_ORCHARD_POST1},
            'ISLAND_ORCHARD_POST2': {'status': 'none', 'button': ISLAND_ORCHARD_POST2},
            'ISLAND_ORCHARD_POST3': {'status': 'none', 'button': ISLAND_ORCHARD_POST3},
            'ISLAND_ORCHARD_POST4': {'status': 'none', 'button': ISLAND_ORCHARD_POST4},

            # 苗圃岗位
            'ISLAND_NURSERY_POST1': {'status': 'none', 'button': ISLAND_NURSERY_POST1},
            'ISLAND_NURSERY_POST2': {'status': 'none', 'button': ISLAND_NURSERY_POST2}
        }
        self.posts_ranch = {
            'ISLAND_RANCH_POST1': ISLAND_RANCH_POST1,
            'ISLAND_RANCH_POST2': ISLAND_RANCH_POST2,
            'ISLAND_RANCH_POST3': ISLAND_RANCH_POST3,
            'ISLAND_RANCH_POST4': ISLAND_RANCH_POST4
        }
        self.to_plant_lists = {
            'farm': [],
            'orchard': [],
            'nursery': []
        }
        self.name_to_config = {}
        for category in self.INVENTORY_CONFIG.values():
            for item in category.get('items', []):
                self.name_to_config[item['name']] = item
        self.inventory_counts = {
            'farm': {},
            'orchard': {},
            'nursery': {},
            'mill': {},
            'ranch': {}
        }

    def check_inventory_and_prepare_lists(self):
        """检查库存并准备需要补种的列表"""
        for category in ['farm', 'orchard', 'nursery']:
            inventory = self.warehouse_inventory(category)  # 改为只返回数量
            config = self.INVENTORY_CONFIG[category]
            threshold = config['threshold']
            self.inventory_counts[category] = inventory
            for item_name, count in inventory.items():  # 现在item_name是作物名，count是数量
                if category == 'orchard' and item_name == 'avocado' and self.ignore_avocado:
                    continue
                if count < threshold:
                    self.to_plant_lists[category].append(item_name)

    def warehouse_inventory(self, category):
        """获取仓库库存信息"""
        config = self.INVENTORY_CONFIG[category]
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(config['filter'])
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()

        results = {}
        for item_config in config['items']:
            count = self.ocr_item_quantity(image, item_config['template'])
            # 现在只返回数量，不返回完整信息
            results[item_config['name']] = count
            setattr(self, item_config['var_name'], count)
            print(f"{item_config['name']}: {count}")

        return results

    def warehouse_mill_ranch(self):
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_PROCESSED)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()
        self.inventory_counts['mill'] = {}

        for item_config in self.INVENTORY_CONFIG['mill']['items']:
            count = self.ocr_item_quantity(image, item_config['template'])
            self.inventory_counts['mill'][item_config['name']] = count
            print(f"{item_config['name']}: {count}")
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_RANCH)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()
        self.inventory_counts['ranch'] = {}

        for item_config in self.INVENTORY_CONFIG['ranch']['items']:
            count = self.ocr_item_quantity(image, item_config['template'])
            self.inventory_counts['ranch'][item_config['name']] = count
            print(f"{item_config['name']}: {count}")

    def post_plant_check(self, category):
        config = self.INVENTORY_CONFIG[category]
        for item in config['items']:
            if self.appear(item['post_action']):
                return item['name']
        return None

    def decided_lists(self, post_button, post_id, category, time_var_name):
        # post_button: Button对象
        # post_id: 字符串岗位ID，如 'ISLAND_FARM_POST1'
        while True:
            self.device.screenshot()
            if not self.appear(ISLAND_POST_CHECK):
                break
            self.device.click(POST_CLOSE)
        self.post_open(post_button)  # 使用按钮对象
        self.device.screenshot()
        if self.appear(ISLAND_WORK_COMPLETE, offset=(5, 5)):
            while True:
                self.device.screenshot()
                if self.appear(ISLAND_POST_SELECT, offset=(5, 5)):
                    break
                if self.device.click(POST_GET):
                    continue
            self.posts[post_id]['status'] = 'idle'  # 使用字符串ID

            setattr(self, time_var_name, None)
        elif self.appear(ISLAND_WORKING):
            product_name = self.post_plant_check(category)
            if product_name in self.to_plant_lists[category]:
                self.to_plant_lists[category].remove(product_name)
            time_work = Duration(ISLAND_WORKING_TIME)
            time_value = time_work.ocr(self.device.image)
            finish_time = datetime.now() + time_value
            setattr(self, time_var_name, finish_time)
            # 从post_id字符串中提取索引
            post_index = int(post_id[-1]) - 1  # 从 POST1 中提取 0
            if category in self.time_vars and post_index < len(self.time_vars[category]):
                self.time_vars[category][post_index] = finish_time
            self.posts[post_id]['status'] = 'working'  # 使用字符串ID
            self.device.click(ISLAND_POST_CHECK)
        elif self.appear(ISLAND_POST_SELECT, offset=(5, 5)):
            self.device.click(ISLAND_POST_CHECK)
            self.posts[post_id]['status'] = 'idle'  # 使用字符串ID
            setattr(self, time_var_name, None)
        while True:
            self.device.screenshot()
            if not self.appear(ISLAND_POST_CHECK):
                break
            self.device.click(POST_CLOSE)

    def ranch_post(self, post_id, time_var_name):
        """牧场岗位处理"""
        post_button = self.posts_ranch[post_id]  # post_id是字符串，获取按钮对象
        while True:
            self.device.screenshot()
            if not self.appear(ISLAND_POST_CHECK):
                break
            self.device.click(POST_CLOSE)
        self.post_open(post_button)
        self.device.screenshot()

        time_work = Duration(ISLAND_WORKING_TIME)

        if self.appear(ISLAND_WORKING):
            if self.appear(POST_GET,offset=(50,0)):
                self.ranch_max()
                self.post_open(post_button)
                time_value = time_work.ocr(self.device.image)
                setattr(self, time_var_name, datetime.now() + time_value)
                self.device.click(POST_CLOSE)
            else:
                time_value = time_work.ocr(self.device.image)
                setattr(self, time_var_name, datetime.now() + time_value)
                self.device.click(POST_CLOSE)

        elif self.appear(ISLAND_WORK_COMPLETE):
            while not self.appear(ISLAND_POST_SELECT):
                self.device.screenshot()
                if self.appear_then_click(POST_GET):
                    continue

            if self.appear_then_click(ISLAND_POST_SELECT):
                self.wait_until_appear(ISLAND_SELECT_CHARACTER_CHECK)
                self.select_character()
                self.appear_then_click(SELECT_UI_CONFIRM)
                self.ranch_max()

            time_value = time_work.ocr(self.device.image)
            setattr(self, time_var_name, datetime.now() + time_value)
            self.device.click(POST_CLOSE)

        elif self.appear(ISLAND_POST_SELECT):
            self.wait_until_appear(ISLAND_SELECT_CHARACTER_CHECK)
            self.select_character()
            self.appear_then_click(SELECT_UI_CONFIRM)
            self.ranch_max()

            time_value = time_work.ocr(self.device.image)
            setattr(self, time_var_name, datetime.now() + time_value)
            self.device.click(POST_CLOSE)

    def ranch_max(self):
        """处理最大数量检查"""
        while True:
            self.device.screenshot()
            if self.appear(POST_MAX_CHECK):
                self.device.click(POST_ADD_ORDER)
                break
            if self.appear(ERROR1):
                self.device.app_stop()
                self.device.app_start()
                self.handle_app_login()
                break
            if self.appear_then_click(POST_MAX):
                continue
            if self.appear_then_click(POST_GET):
                continue
            if self.device.click(POST_ADD):
                continue

    def post_plant(self, post_button, product, category, time_var_name):
        # post_button: Button对象
        self.device.click(POST_CLOSE)
        self.post_open(post_button)  # 使用按钮对象
        self.device.screenshot()
        time_work = Duration(ISLAND_WORKING_TIME)
        selection = self.name_to_config[product]['selection']
        selection_check = self.name_to_config[product]['selection_check']
        if self.appear_then_click(ISLAND_POST_SELECT):
            self.wait_until_appear(ISLAND_SELECT_CHARACTER_CHECK)
            if product == 'rubber' and self.config.PersonnelManagement_AmagiChanRubber:
                self.select_character(character_name="Amagi_chan")
            else:
                self.select_character()
            self.appear_then_click(SELECT_UI_CONFIRM)
            self.select_product(selection, selection_check)
            self.appear_then_click(POST_MAX)
            self.device.click(POST_ADD_ORDER)
            self.post_open(post_button)  # 使用按钮对象
            time_value = time_work.ocr(self.device.image)
            finish_time = datetime.now() + time_value
            setattr(self, time_var_name, finish_time)
        self.device.click(POST_CLOSE)

    def buy_seeds(self, seed, category):
        category_map = {
            'farm': (SHOP_FARM_CHECK, SHOP_FARM),
            'orchard': (SHOP_ORCHARD_CHECK, SHOP_ORCHARD),
            'nursery': (SHOP_NURSERY_CHECK, SHOP_NURSERY)
        }
        check_const, click_const = category_map[category]
        seed_config = self.name_to_config[seed]
        target = seed_config['seed_number']
        seed_button = seed_config['shop']
        while 1:
            self.device.screenshot()
            if self.appear(check_const):
                break
            if self.appear_then_click(click_const, interval=0.3):
                pass
        while 1:
            self.device.screenshot()
            if self.appear(ISLAND_SHOPPING_CHECK):
                break
            if self.appear_then_click(seed_button, interval=0.3):
                pass
        if self.appear(ISLAND_SHOPPING_CHECK):
            self.set_buy_number(target)
        while 1:
            self.device.screenshot()
            if self.appear(ISLAND_SHOP_CHECK, offset=1):
                break
            if self.appear_then_click(ISLAND_SHOP_CONFIRM):
                continue
            self.device.click(ISLAND_SHOP_CONFIRM)

    def mill_process(self, mill_item):
        """磨坊加工"""
        mill_config = self.name_to_config[mill_item]
        mill_button = mill_config['mill']
        target = mill_config['number']
        required_material = mill_config['required_material']
        # 检查原材料是否充足（需要至少330）
        if required_material in self.inventory_counts['farm']:
            if self.inventory_counts['farm'][required_material] < 330:
                print(f"原材料{required_material}不足，无法加工{mill_item}")
                return False
        while True:
            self.device.screenshot()
            if self.appear(ISLAND_SHOPPING_CHECK):
                break
            if self.appear_then_click(mill_button, interval=0.3):
                pass
        # 设置购买数量
        if self.appear(ISLAND_SHOPPING_CHECK):
            self.set_buy_number(target)
        # 确认购买
        while True:
            self.device.screenshot()
            if self.appear(ISLAND_MILL_CHECK, offset=1):
                break
            if self.appear_then_click(ISLAND_SHOP_CONFIRM):
                continue
            self.device.click(ISLAND_SHOP_CONFIRM)
        if self.appear(ISLAND_GET):
            self.device.click(ISLAND_MILL_CHECK)
        # 扣除原材料
        if required_material in self.inventory_counts['farm']:
            self.inventory_counts['farm'][required_material] -= 330
            print(f"扣除原材料{required_material} 330单位")
        # 增加磨坊产品
        self.inventory_counts['mill'][mill_item] = self.inventory_counts['mill'].get(mill_item, 0) + target*10
        print(f"加工完成：{mill_item} +{target}")

        return True

    def check_mill_needs(self):
        """检查磨坊需求"""
        mill_needs = []

        # 检查面粉需求（优先级最高）
        wheat_flour_count = self.inventory_counts['mill'].get('wheat_flour', 0)
        wheat_count = self.inventory_counts['farm'].get('wheat', 0)

        if wheat_flour_count < 50 and wheat_count > 330:
            mill_needs.append('wheat_flour')
            print("需要加工面粉")

        # 检查鸡饲料需求,饲料10倍产量,11份会产出110个饲料
        chicken_count = self.inventory_counts['ranch'].get('chicken', 0)
        chicken_feed_count = self.inventory_counts['mill'].get('chicken_feed', 0)

        if (chicken_count < self.config.IslandRanch_MinChicken and
                wheat_count > 330 and
                chicken_feed_count < 50 and
                'wheat_flour' not in mill_needs):  # 面粉优先级更高
            mill_needs.append('chicken_feed')
            print("需要加工鸡饲料")

        # 检查猪饲料需求
        pork_count = self.inventory_counts['ranch'].get('pork', 0)
        pig_feed_count = self.inventory_counts['mill'].get('pig_feed', 0)
        corn_count = self.inventory_counts['farm'].get('corn', 0)

        if (pork_count < self.config.IslandRanch_MinPork and
                corn_count > 330 and
                pig_feed_count < 50):
            mill_needs.append('pig_feed')
            print("需要加工猪饲料")

        # 检查牛饲料需求
        cattle_feed_count = self.inventory_counts['mill'].get('cattle_feed', 0)
        pasture_count = self.inventory_counts['farm'].get('pasture', 0)

        if cattle_feed_count < 50 and pasture_count > 330:
            mill_needs.append('cattle_feed')
            print("需要加工牛饲料")

        # 检查羊饲料需求
        sheep_feed_count = self.inventory_counts['mill'].get('sheep_feed', 0)

        if sheep_feed_count < 50 and pasture_count > 330:
            mill_needs.append('sheep_feed')
            print("需要加工羊饲料")

        return mill_needs

    def set_buy_number(self, target):
        increment = target - 1
        add_ten_clicks = increment // 10
        add_one_clicks = increment % 10
        while True:
            if add_ten_clicks == 0:
                break
            self.device.click(ADD_TEN_A)
            add_ten_clicks -= 1
            if add_ten_clicks == 0:
                break
            self.device.click(ADD_TEN_B)
            add_ten_clicks -= 1
            if add_ten_clicks == 0:
                break
            self.device.click(ADD_TEN_C)
            add_ten_clicks -= 1
        while True:
            if add_one_clicks == 0:
                break
            self.device.click(ADD_ONE_A)
            add_one_clicks -= 1
            if add_one_clicks == 0:
                break
            self.device.click(ADD_ONE_B)
            add_one_clicks -= 1
            if add_one_clicks == 0:
                break
            self.device.click(ADD_ONE_C)
            add_one_clicks -= 1

    def check_ranch_needs(self):
        """检查牧场需求"""
        ranch_needs = []

        # 检查岗位1（养鸡）
        chicken_count = self.inventory_counts['ranch'].get('chicken', 0)
        chicken_feed_count = self.inventory_counts['mill'].get('chicken_feed', 0)

        if chicken_count < self.ranch_chicken_threshold and chicken_feed_count >= 50:
            ranch_needs.append('ISLAND_RANCH_POST1')
            print("需要执行养鸡任务")

        # 检查岗位2（养猪）
        pork_count = self.inventory_counts['ranch'].get('pork', 0)
        pig_feed_count = self.inventory_counts['mill'].get('pig_feed', 0)

        if pork_count < self.ranch_pork_threshold and pig_feed_count >= 50:
            ranch_needs.append('ISLAND_RANCH_POST2')
            print("需要执行养猪任务")

        # 检查岗位3（养牛）
        cattle_feed_count = self.inventory_counts['mill'].get('cattle_feed', 0)
        if cattle_feed_count >= 50:
            ranch_needs.append('ISLAND_RANCH_POST3')
            print("需要执行养牛任务")

        # 检查岗位4（养羊）
        sheep_feed_count = self.inventory_counts['mill'].get('sheep_feed', 0)
        if sheep_feed_count >= 50:
            ranch_needs.append('ISLAND_RANCH_POST4')
            print("需要执行养羊任务")

        return ranch_needs

    def run(self):
        self.check_inventory_and_prepare_lists()
        self.warehouse_mill_ranch()
        # 打印当前库存
        print("\n当前库存统计:")
        print(f"农场库存: {self.inventory_counts['farm']}")
        print(f"磨坊库存: {self.inventory_counts['mill']}")
        print(f"牧场库存: {self.inventory_counts['ranch']}")

        # 3. 磨坊加工
        print("\n[3/5] 检查并执行磨坊加工...")
        mill_needs = self.check_mill_needs()
        if mill_needs:
            self.goto_mill()
            print(f"需要加工的项目: {mill_needs}")
            # 按照优先级加工：面粉 > 鸡饲料 > 猪饲料 > 牛饲料 > 羊饲料
            priority_order = ['wheat_flour', 'chicken_feed', 'pig_feed', 'cattle_feed', 'sheep_feed']
            for item in priority_order:
                if item in mill_needs:
                    success = self.mill_process(item)
                    if success:
                        break
        else:
            print("没有磨坊加工需求")
        ranch_needs = self.check_ranch_needs()
        self.goto_postmanage()
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)
        self.post_manage_down_swipe(450)
        self.post_manage_down_swipe(450)

        if ranch_needs:
            print(f"需要执行的牧场岗位: {ranch_needs}")
            # 执行牧场岗位
            for post_id in ranch_needs:
                time_var_name = f'ranch_time_{post_id[-1]}'  # 使用岗位编号作为时间变量
                self.ranch_post(post_id, time_var_name)
        self.time_vars = {
            'farm': [None] * self.farm_positions,  # 直接使用变量
            'orchard': [None] * self.orchard_positions,  # 直接使用变量
            'nursery': [None] * self.nursery_positions  # 直接使用变量
        }

        # 岗位映射，这里存储的是按钮对象
        post_button_mapping = {
            'farm': [self.posts['ISLAND_FARM_POST1']['button'],
                     self.posts['ISLAND_FARM_POST2']['button'],
                     self.posts['ISLAND_FARM_POST3']['button'],
                     self.posts['ISLAND_FARM_POST4']['button']],
            'orchard': [self.posts['ISLAND_ORCHARD_POST1']['button'],
                        self.posts['ISLAND_ORCHARD_POST2']['button'],
                        self.posts['ISLAND_ORCHARD_POST3']['button'],
                        self.posts['ISLAND_ORCHARD_POST4']['button']],
            'nursery': [self.posts['ISLAND_NURSERY_POST1']['button'],
                        self.posts['ISLAND_NURSERY_POST2']['button']]
        }

        # 根据配置取相应数量的岗位
        post_buttons = {
            'farm': post_button_mapping['farm'][:self.farm_positions],  # 直接使用变量
            'orchard': post_button_mapping['orchard'][:self.orchard_positions],  # 直接使用变量
            'nursery': post_button_mapping['nursery'][:self.nursery_positions]  # 直接使用变量
        }

        # 创建岗位ID到按钮的映射
        post_id_to_button = {}
        for category in ['farm', 'orchard', 'nursery']:
            positions_count = getattr(self, f'{category}_positions')  # 获取对应类别的岗位数量
            for i, button in enumerate(post_buttons[category]):
                post_id = f'ISLAND_{category.upper()}_POST{i + 1}'
                post_id_to_button[post_id] = button

        idle_posts = {'farm': [], 'orchard': [], 'nursery': []}

        # 检查岗位状态
        for category in ['farm', 'orchard', 'nursery']:
            positions = len(self.time_vars[category])
            for i in range(positions):
                post_id = f'ISLAND_{category.upper()}_POST{i + 1}'
                time_var_name = f'{category}_time_{i}'

                # 获取按钮对象
                button = post_id_to_button[post_id]

                # 传递按钮对象和岗位ID字符串给decided_lists
                self.decided_lists(button, post_id, category, time_var_name)

                if self.posts[post_id]['status'] == 'idle':
                    idle_posts[category].append({
                        'post_id': post_id,
                        'button': button,
                        'index': i,
                        'time_var_name': time_var_name
                    })

        print(f"\n空闲岗位统计:")
        for category in ['farm', 'orchard', 'nursery']:
            print(f"{category}: {len(idle_posts[category])}个空闲岗位")

        # 2. 统计所有需要购买的种子
        all_plants_to_buy = {'farm': [], 'orchard': [], 'nursery': []}

        for category in ['farm', 'orchard', 'nursery']:
            if not idle_posts[category]:
                continue
            idle_count = len(idle_posts[category])
            plant_config = self.plant_config[category]  # 使用保留的plant_config
            to_plant_list = self.to_plant_lists[category]
            num_from_list = min(len(to_plant_list), idle_count)

            for i in range(num_from_list):
                crop_name = to_plant_list[i]
                all_plants_to_buy[category].append(crop_name)

            remaining_idle = idle_count - num_from_list
            if remaining_idle > 0 and plant_config['plant_default']:
                default_crop = plant_config['default_crop']
                if default_crop not in to_plant_list:
                    for _ in range(remaining_idle):
                        all_plants_to_buy[category].append(default_crop)

            if all_plants_to_buy[category]:
                print(f"\n{category}需要购买的作物: {all_plants_to_buy[category]}")

        # 3. 如果有需要购买的种子，统一购买
        need_to_buy_seeds = any(all_plants_to_buy.values())

        if need_to_buy_seeds:
            self.ui_goto(page_island_shop)

            # 按类别购买种子
            for category in ['farm', 'orchard', 'nursery']:
                if not all_plants_to_buy[category]:
                    continue

                # 统计该类别需要购买的作物和数量
                crop_counts = {}
                for crop_name in all_plants_to_buy[category]:
                    crop_counts[crop_name] = crop_counts.get(crop_name, 0) + 1

                # 切换到对应的商店标签页
                category_map = {
                    'farm': (SHOP_FARM_CHECK, SHOP_FARM),
                    'orchard': (SHOP_ORCHARD_CHECK, SHOP_ORCHARD),
                    'nursery': (SHOP_NURSERY_CHECK, SHOP_NURSERY)
                }
                check_const, click_const = category_map[category]

                # 切换到对应标签页
                while 1:
                    self.device.screenshot()
                    if self.appear(check_const):
                        break
                    if self.appear_then_click(click_const, interval=0.3):
                        pass

                # 购买该类别所有种子
                for crop, count in crop_counts.items():
                    print(f"购买{category}类别的{crop}种子，{count}份")
                    for _ in range(count):
                        self.buy_seeds(crop, category)

            # 购买完成后返回岗位管理界面
            self.goto_management()
            self.ui_goto(page_island_postmanage)
            self.post_manage_mode(POST_MANAGE_PRODUCTION)
            self.device.click(POST_CLOSE)

        # 4. 播种空闲岗位
        for category in ['farm', 'orchard', 'nursery']:
            if not idle_posts[category]:
                continue

            idle_posts_list = idle_posts[category]
            to_plant_list = self.to_plant_lists[category]
            plant_config = self.plant_config[category]  # 使用保留的plant_config

            # 我们需要跟踪哪些作物已经播种了
            planted_crops = []

            for i, post_info in enumerate(idle_posts_list):
                post_id = post_info['post_id']
                button = post_info['button']
                index = post_info['index']
                time_var_name = post_info['time_var_name']

                crop_to_plant = None

                # 首先尝试从补种列表中取作物
                if i < len(to_plant_list):
                    crop_to_plant = to_plant_list[i]
                # 如果还有空闲岗位并且配置了种植默认作物
                elif plant_config['plant_default']:
                    default_crop = plant_config['default_crop']
                    # 检查默认作物是否已经在补种列表中
                    if default_crop not in to_plant_list:
                        crop_to_plant = default_crop
                    else:
                        print(f"跳过{category}岗位{post_id}: 默认作物{default_crop}已在补种列表中")
                        continue
                else:
                    print(f"跳过{category}岗位{post_id}: 没有需要种植的作物")
                    continue

                if crop_to_plant:
                    print(f"播种{category}岗位{post_id}: {crop_to_plant}")
                    success = self.post_plant(button, crop_to_plant, category, time_var_name)
                    if success:
                        planted_crops.append(crop_to_plant)

            # 播种完成后，从补种列表中移除已成功播种的作物
            for crop in planted_crops:
                if crop in self.to_plant_lists[category]:
                    self.to_plant_lists[category].remove(crop)

        print("\n农田管理完成！")
        future_finish = []

        # 使用正确的时间变量名格式收集时间
        for category in ['farm', 'orchard', 'nursery']:
            positions = len(self.time_vars[category])
            for i in range(positions):
                var_name = f'{category}_time_{i}'  # 与decided_lists中的格式一致
                if hasattr(self, var_name):
                    time_var = getattr(self, var_name)
                    if time_var is not None:
                        future_finish.append(time_var)

        # 排序并设置延迟
        if future_finish:
            future_finish.sort()
            self.config.task_delay(target=future_finish)
            print(f'下次运行时间: {future_finish[0]}')
        else:
            self.config.task_delay(success=True)

    def test(self):
        self.select_product(SELECT_RUBBER,SELECT_RUBBER_CHECK)
if __name__ == "__main__":
    az =IslandFarm('alas', task='Alas')
    az.device.screenshot()
    az.run()
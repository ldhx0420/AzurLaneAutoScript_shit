from module.island_farm.assets import *
from module.island.island import *
from datetime import datetime
from module.handler.login import LoginHandler
from module.island.warehouse import *

class IslandFarm(Island,WarehouseOCR,LoginHandler):
    def __init__(self, *args, **kwargs):
        Island.__init__(self, *args, **kwargs)
        WarehouseOCR.__init__(self)
        self.farm_config = {
            'farm_positions': 3,  # 农田岗位数量 1-4
            'orchard_positions': 4,  # 果园岗位数量 1-4
            'nursery_positions': 2,  # 苗圃岗位数量 1-2
            'ignore_avocado': True,  # 是否忽略牛油果
            'farm_threshold': 300,  # 农田库存阈值
            'orchard_threshold': 300,  # 果园库存阈值
            'nursery_threshold': 50,  # 苗圃库存阈值
            'plant_config': {  # 默认作物配置
                'farm': {
                    'plant_default': True,
                    'default_crop': 'potato'
                },
                'orchard': {
                    'plant_default': False,  # 果园不种植默认作物
                    'default_crop': 'rubber'  # 即使有默认作物也不种
                },
                'nursery': {
                    'plant_default': True,
                    'default_crop': 'lavender'
                }
            }
        }
        self.INVENTORY_CONFIG = {
            'farm': {
                'filter': FILTER_FARM,
                'threshold': self.farm_config['farm_threshold'],
                'items': [
                    {'name': 'wheat', 'template': TEMPLATE_WHEAT, 'var_name': 'wheat',
                     'selection': WHEAT_SELECTION, 'selection_check': WHEAT_SELECTION_CHECK,
                     'post_action': POST_WHEAT, 'category': 'farm', 'seed_number': 99,
                     'shop': SHOP_SEED_WHEAT},
                    {'name': 'corn', 'template': TEMPLATE_CORN, 'var_name': 'corn',
                     'selection': CORN_SELECTION, 'selection_check': CORN_SELECTION_CHECK,
                     'post_action': POST_CORN, 'category': 'farm', 'seed_number': 99,
                     'shop': SHOP_SEED_CORN},
                    {'name': 'rice', 'template': TEMPLATE_RICE, 'var_name': 'rice',
                     'selection': RICE_SELECTION, 'selection_check': RICE_SELECTION_CHECK,
                     'post_action': POST_RICE, 'category': 'farm', 'seed_number': 45,
                     'shop': SHOP_SEED_RICE},
                    {'name': 'chinese_cabbage', 'template': TEMPLATE_CHINESE_CABBAGE, 'var_name': 'chinese_cabbage',
                     'selection': CHINESE_CABBAGE_SELECTION, 'selection_check': CHINESE_CABBAGE_SELECTION_CHECK,
                     'post_action': POST_CHINESE_CABBAGE, 'category': 'farm', 'seed_number': 99,
                     'shop': SHOP_SEED_CHINESE_CABBAGE},
                    {'name': 'potato', 'template': TEMPLATE_POTATO, 'var_name': 'potato',
                     'selection': POTATO_SELECTION, 'selection_check': POTATO_SELECTION_CHECK,
                     'post_action': POST_POTATO, 'category': 'farm', 'seed_number': 36,
                     'shop': SHOP_SEED_POTATO},
                    {'name': 'soybean', 'template': TEMPLATE_SOYBEAN, 'var_name': 'soybean',
                     'selection': SOYBEAN_SELECTION, 'selection_check': SOYBEAN_SELECTION_CHECK,
                     'post_action': POST_SOYBEAN, 'category': 'farm', 'seed_number': 45,
                     'shop': SHOP_SEED_SOYBEAN},
                    {'name': 'pasture', 'template': TEMPLATE_PASTURE, 'var_name': 'pasture',
                     'selection': PASTURE_SELECTION, 'selection_check': PASTURE_SELECTION_CHECK,
                     'post_action': POST_PASTURE, 'category': 'farm', 'seed_number': 99,
                     'shop': SHOP_SEED_PASTURE},
                    {'name': 'coffee_bean', 'template': TEMPLATE_COFFEE_BEAN, 'var_name': 'coffee_bean',
                     'selection': COFFEE_BEAN_SELECTION, 'selection_check': COFFEE_BEAN_SELECTION_CHECK,
                     'post_action': POST_COFFEE_BEAN, 'category': 'farm', 'seed_number': 36,
                     'shop': SHOP_SEED_COFFEE_BEAN},
                ]
            },
            'orchard': {
                'filter': FILTER_ORCHARD,
                'threshold': self.farm_config['orchard_threshold'],
                'items': [
                    {'name': 'apple', 'template': TEMPLATE_APPLE, 'var_name': 'apple',
                     'selection': APPLE_SELECTION, 'selection_check': APPLE_SELECTION_CHECK,
                     'post_action': POST_APPLE, 'category': 'orchard', 'seed_number': 20,
                     'shop': SHOP_SEED_APPLE},
                    {'name': 'citrus', 'template': TEMPLATE_CITRUS, 'var_name': 'citrus',
                     'selection': CITRUS_SELECTION, 'selection_check': CITRUS_SELECTION_CHECK,
                     'post_action': POST_CITRUS, 'category': 'orchard', 'seed_number': 20,
                     'shop': SHOP_SEED_CITRUS},
                    {'name': 'banana', 'template': TEMPLATE_BANANA, 'var_name': 'banana',
                     'selection': BANANA_SELECTION, 'selection_check': BANANA_SELECTION_CHECK,
                     'post_action': POST_BANANA, 'category': 'orchard', 'seed_number': 16,
                     'shop': SHOP_SEED_BANANA},
                    {'name': 'mango', 'template': TEMPLATE_MANGO, 'var_name': 'mango',
                     'selection': MANGO_SELECTION, 'selection_check': MANGO_SELECTION_CHECK,
                     'post_action': POST_MANGO, 'category': 'orchard', 'seed_number': 16,
                     'shop': SHOP_SEED_MANGO},
                    {'name': 'lemon', 'template': TEMPLATE_LEMON, 'var_name': 'lemon',
                     'selection': LEMON_SELECTION, 'selection_check': LEMON_SELECTION_CHECK,
                     'post_action': POST_LEMON, 'category': 'orchard', 'seed_number': 28,
                     'shop': SHOP_SEED_LEMON},
                    {'name': 'avocado', 'template': TEMPLATE_AVOCADO, 'var_name': 'avocado',
                     'selection': AVOCADO_SELECTION, 'selection_check': AVOCADO_SELECTION_CHECK,
                     'post_action': POST_AVOCADO, 'category': 'orchard', 'seed_number': 16,
                     'shop': SHOP_SEED_AVOCADO},
                    {'name': 'rubber', 'template': TEMPLATE_RUBBER, 'var_name': 'rubber',
                     'selection': RUBBER_SELECTION, 'selection_check': RUBBER_SELECTION_CHECK,
                     'post_action': POST_RUBBER, 'category': 'orchard', 'seed_number': 16,
                     'shop': SHOP_SEED_RUBBER},
                ]
            },
            'nursery': {
                'filter': FILTER_NURSERY,
                'threshold': self.farm_config['nursery_threshold'],
                'items': [
                    {'name': 'carrot', 'template': TEMPLATE_CARROT, 'var_name': 'carrot',
                     'selection': CARROT_SELECTION, 'selection_check': CARROT_SELECTION_CHECK,
                     'post_action': POST_CARROT, 'category': 'nursery', 'seed_number': 33,
                     'shop': SHOP_SEED_CARROT},
                    {'name': 'onion', 'template': TEMPLATE_ONION, 'var_name': 'onion',
                     'selection': ONION_SELECTION, 'selection_check': ONION_SELECTION_CHECK,
                     'post_action': POST_ONION, 'category': 'nursery', 'seed_number': 12,
                     'shop': SHOP_SEED_ONION},
                    {'name': 'flax', 'template': TEMPLATE_FLAX, 'var_name': 'flax',
                     'selection': FLAX_SELECTION, 'selection_check': FLAX_SELECTION_CHECK,
                     'post_action': POST_FLAX, 'category': 'nursery', 'seed_number': 33,
                     'shop': SHOP_SEED_FLAX},
                    {'name': 'strawberry', 'template': TEMPLATE_STRAWBERRY, 'var_name': 'strawberry',
                     'selection': STRAWBERRY_SELECTION, 'selection_check': STRAWBERRY_SELECTION_CHECK,
                     'post_action': POST_STRAWBERRY, 'category': 'nursery', 'seed_number': 12,
                     'shop': SHOP_SEED_STRAWBERRY},
                    {'name': 'cotton', 'template': TEMPLATE_COTTON, 'var_name': 'cotton',
                     'selection': COTTON_SELECTION, 'selection_check': COTTON_SELECTION_CHECK,
                     'post_action': POST_COTTON, 'category': 'nursery', 'seed_number': 21,
                     'shop': SHOP_SEED_COTTON},
                    {'name': 'tea', 'template': TEMPLATE_TEA, 'var_name': 'tea',
                     'selection': TEA_SELECTION, 'selection_check': TEA_SELECTION_CHECK,
                     'post_action': POST_TEA, 'category': 'nursery', 'seed_number': 12,
                     'shop': SHOP_SEED_TEA},
                    {'name': 'lavender', 'template': TEMPLATE_LAVENDER, 'var_name': 'lavender',
                     'selection': LAVENDER_SELECTION, 'selection_check': LAVENDER_SELECTION_CHECK,
                     'post_action': POST_LAVENDER, 'category': 'nursery', 'seed_number': 12,
                     'shop': SHOP_SEED_LAVENDER},
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
        self.to_plant_lists = {
            'farm': [],
            'orchard': [],
            'nursery': []
        }
        self.name_to_config = {
            item['name']: {
                'selection': item['selection'],
                'selection_check': item['selection_check'],
                'template': item['template'],
                'var_name': item['var_name'],
                'post_action': item['post_action'],
                'category': item['category'],
                'seed_number': item['seed_number'],
                'shop': item['shop']
            }
            for category in self.INVENTORY_CONFIG.values()
            for item in category['items']
        }

    def check_inventory_and_prepare_lists(self):
        for category in ['farm', 'orchard', 'nursery']:
            inventory = self.warehouse_inventory(category, return_full_info=True)
            config = self.INVENTORY_CONFIG[category]
            threshold = config['threshold']
            for item_name, item_info in inventory.items():
                if category == 'orchard' and item_name == 'avocado' and self.farm_config['ignore_avocado']:
                    continue
                if item_info['count'] < threshold:
                    self.to_plant_lists[category].append(item_name)

    def warehouse_inventory(self, category, return_full_info=False):
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
            if return_full_info:
                results[item_config['name']] = {
                    'count': count,
                    'selection': item_config.get('selection'),
                    'selection_check': item_config.get('selection_check'),
                    'post_action': item_config.get('post_action'),
                    'category': item_config.get('category'),
                    'seed_number': item_config.get('seed_number'),
                    'template': item_config.get('template'),
                    'var_name': item_config.get('var_name')
                }
            else:
                results[item_config['name']] = count
            setattr(self, item_config['var_name'], count)
            print(f"{item_config['name']}: {count}")
        return results

    def post_plant_check(self,category):
        config = self.INVENTORY_CONFIG[category]
        for item in config['items']:
            if self.appear(item['post_action']):
                return item['name']
        return None

    def decided_lists(self,post_id,category,time_var_name):
        self.device.click(POST_CLOSE)
        self.post_open(post_id)
        self.device.screenshot()
        if self.appear(ISLAND_WORK_COMPLETE,offset=(5,5)):
            while True:
                self.device.screenshot()
                if self.appear(ISLAND_POST_SELECT,offset=(5,5)):
                    break
                if self.device.click(POST_GET):
                    continue
            self.posts[post_id]['status'] = 'idle'
            self.device.click(POST_CLOSE)
            setattr(self, time_var_name, None)
        elif self.appear(ISLAND_WORKING):
            product_name = self.post_plant_check(category)
            if product_name in self.to_plant_lists[category]:
                self.to_plant_lists[category].remove(product_name)
            time_work = Duration(ISLAND_WORKING_TIME)
            time_value = time_work.ocr(self.device.image)
            finish_time = datetime.now() + time_value
            setattr(self, time_var_name, finish_time)
            self.posts[post_id]['status'] = 'working'
            self.device.click(ISLAND_POST_CHECK)
        elif self.appear(ISLAND_POST_SELECT,offset=(5,5)):
            self.device.click(ISLAND_POST_CHECK)
            self.posts[post_id]['status'] = 'idle'
            setattr(self, time_var_name, None)
        self.device.click(POST_CLOSE)

    def post_plant(self, post_id, product, category, time_var_name):
        self.device.click(POST_CLOSE)
        self.post_open(post_id)
        self.device.screenshot()
        time_work = Duration(ISLAND_WORKING_TIME)
        selection = self.name_to_config[product]['selection']
        selection_check = self.name_to_config[product]['selection_check']
        if self.appear_then_click(ISLAND_POST_SELECT):
            self.select_character()
            self.select_product(selection, selection_check)
            self.appear_then_click(POST_MAX)
            self.device.click(POST_ADD_ORDER)
            self.post_open(post_id)
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
            if self.appear_then_click(click_const,interval=0.3):
                pass
        while 1:
            self.device.screenshot()
            if self.appear(ISLAND_SHOPPING_CHECK):
                break
            if self.appear_then_click(seed_button,interval=0.3):
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
    def set_buy_number(self,target):
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

    def run(self):
        self.check_inventory_and_prepare_lists()
        self.time_vars = {
            'farm': [None] * self.farm_config['farm_positions'],
            'orchard': [None] * self.farm_config['orchard_positions'],
            'nursery': [None] * self.farm_config['nursery_positions']
        }
        self.goto_management()
        self.ui_goto(page_island_postmanage)
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)

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
            'farm': post_button_mapping['farm'][:self.farm_config['farm_positions']],
            'orchard': post_button_mapping['orchard'][:self.farm_config['orchard_positions']],
            'nursery': post_button_mapping['nursery'][:self.farm_config['nursery_positions']]
        }

        # 创建岗位ID到按钮的映射
        post_id_to_button = {}
        for category in ['farm', 'orchard', 'nursery']:
            for i, button in enumerate(post_buttons[category]):
                post_id = f'ISLAND_{category.upper()}_POST{i + 1}'
                post_id_to_button[post_id] = button

        idle_posts = {'farm': [], 'orchard': [], 'nursery': []}

        for category in ['farm', 'orchard', 'nursery']:
            positions = len(self.time_vars[category])
            for i in range(positions):
                post_id = f'ISLAND_{category.upper()}_POST{i + 1}'
                time_var_name = f'{category}_time_{i}'

                # 获取按钮对象
                button = post_id_to_button[post_id]

                # 传递按钮对象给decided_lists
                self.decided_lists(button, category, time_var_name)

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
            plant_config = self.farm_config['plant_config'][category]
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
            plant_config = self.farm_config['plant_config'][category]

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

        # 按照时间排序
        future_finish = sorted(future_finish)

        # 如果有时间信息，反馈给调度器
        if len(future_finish):
            self.config.task_delay(target=future_finish)
            # 使用print替代logger，或确保logger已导入
            print(f'农田岗位完成时间: {[str(f) for f in future_finish]}')
            print(f'找到 {len(future_finish)} 个农田岗位计时器，下一次运行在 {future_finish[0]}')
        else:
            print('没有找到农田岗位计时器')
            self.config.task_delay(success=True)
        self.ui_goto_main()
    def test(self):
        self.select_product(LAVENDER_SELECTION,LAVENDER_SELECTION_CHECK)
if __name__ == "__main__":
    az =IslandFarm('alas', task='Alas')
    az.device.screenshot()
    az.run()
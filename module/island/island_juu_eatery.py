from module.island_juu_eatery.assets import *
from module.island.assets import *
from module.island.island import *
from collections import Counter
from datetime import datetime
from module.handler.login import LoginHandler
from module.ocr.ocr import *

class IslandJuuEatery(Island, LoginHandler):
    def __init__(self, *args, **kwargs):
        Island.__init__(self, *args, **kwargs)
        self.ISLAND_JUU_EATERY = [
            {'name': 'apple_pie', 'template': TEMPLATE_APPLE_PIE, 'var_name': 'apple_pie',
             'selection': APPLE_PIE_SELECTION, 'selection_check': APPLE_PIE_SELECTION_CHECK,
             'post_action': POST_APPLE_PIE},
            {'name': 'corn_cup', 'template': TEMPLATE_CORN_CUP, 'var_name': 'corn_cup',
             'selection': CORN_CUP_SELECTION, 'selection_check': CORN_CUP_SELECTION_CHECK,
             'post_action': POST_CORN_CUP},
            {'name': 'orange_pie', 'template': TEMPLATE_ORANGE_PIE, 'var_name': 'orange_pie',
             'selection': ORANGE_PIE_SELECTION, 'selection_check': ORANGE_PIE_SELECTION_CHECK,
             'post_action': POST_ORANGE_PIE},
            {'name': 'banana_crepe', 'template': TEMPLATE_BANANA_CREPE, 'var_name': 'banana_crepe',
             'selection': BANANA_CREPE_SELECTION, 'selection_check': BANANA_CREPE_SELECTION_CHECK,
             'post_action': POST_BANANA_CREPE},
            {'name': 'orchard_duo', 'template': TEMPLATE_ORCHARD_DUO, 'var_name': 'orchard_duo',
             'selection': ORCHARD_DUO_SELECTION, 'selection_check': ORCHARD_DUO_SELECTION_CHECK,
             'post_action': POST_ORCHARD_DUO},
            {'name': 'rice_mango', 'template': TEMPLATE_RICE_MANGO, 'var_name': 'rice_mango',
             'selection': RICE_MANGO_SELECTION, 'selection_check': RICE_MANGO_SELECTION_CHECK,
             'post_action': POST_RICE_MANGO},
            {'name': 'succulently_sweet', 'template': TEMPLATE_SUCCULENTLY_SWEET, 'var_name': 'succulently_sweet',
             'selection': SUCCULENTLY_SWEET_SELECTION, 'selection_check': SUCCULENTLY_SWEET_SELECTION_CHECK,
             'post_action': POST_SUCCULENTLY_SWEET},
            {'name': 'berry_orange', 'template': TEMPLATE_BERRY_ORANGE, 'var_name': 'berry_orange',
             'selection': BERRY_ORANGE_SELECTION, 'selection_check': BERRY_ORANGE_SELECTION_CHECK,
             'post_action': POST_BERRY_ORANGE},
            {'name': 'strawberry_charlotte', 'template': TEMPLATE_STRAWBERRY_CHARLOTTE,
             'var_name': 'strawberry_charlotte',
             'selection': STRAWBERRY_CHARLOTTE_SELECTION, 'selection_check': STRAWBERRY_CHARLOTTE_SELECTION_CHECK,
             'post_action': POST_STRAWBERRY_CHARLOTTE},
            {'name': 'cheese', 'template': TEMPLATE_CHEESE, 'var_name': 'cheese',
             'selection': CHEESE_SELECTION, 'selection_check': CHEESE_SELECTION_CHECK,
             'post_action': POST_CHEESE},
        ]
        self.name_to_config = {item['name']: item for item in self.ISLAND_JUU_EATERY}
        self.posts = {
            'ISLAND_JUU_EATERY_POST1': {'status': 'none', 'button': ISLAND_JUU_EATERY_POST1},
            'ISLAND_JUU_EATERY_POST2': {'status': 'none', 'button': ISLAND_JUU_EATERY_POST2}
        }
        self.post_check_meal = {}

        self.post_products = {}
        meal_keys = [
            ('IslandJuuEatery_Meal1', 'IslandJuuEatery_MealNumber'),
            ('IslandJuuEatery_Meal2', 'IslandJuuEatery_MealNumber'),
            ('IslandJuuEatery_Meal3', 'IslandJuuEatery_MealNumber'),
            ('IslandJuuEatery_Meal4', 'IslandJuuEatery_MealNumber')
        ]
        for meal_key, number_key in meal_keys:
            meal_name = getattr(self.config, meal_key, None)
            if meal_name is not None and meal_name != "None":
                meal_number = getattr(self.config, number_key, 0)
                self.post_products[meal_name] = meal_number

        self.post_products_task = {}
        task_keys = [
            ('IslandJuuEateryNextTask_MealTask1', 'IslandJuuEateryNextTask_MealTaskNumber1'),
            ('IslandJuuEateryNextTask_MealTask2', 'IslandJuuEateryNextTask_MealTaskNumber2'),
            ('IslandJuuEateryNextTask_MealTask3', 'IslandJuuEateryNextTask_MealTaskNumber3'),
            ('IslandJuuEateryNextTask_MealTask4', 'IslandJuuEateryNextTask_MealTaskNumber4')
        ]
        for task_key, number_key in task_keys:
            meal_name = getattr(self.config, task_key, None)
            if meal_name is not None and meal_name != "None":
                meal_number = getattr(self.config, number_key, 0)
                if meal_number > 0:
                    self.post_products_task[meal_name] = meal_number

        self.warehouse_counts = {}
        self.to_post_products = {}
        self.doubled = False
        self.task_completed = False

    def post_check(self, post_id, time_var_name):
        post_button = self.posts[post_id]['button']
        self.device.click(POST_CLOSE)
        self.post_open(post_button)
        image = self.device.screenshot()
        ocr_post_number = Digit(OCR_POST_NUMBER, letter=(57, 58, 60), threshold=100,
                                alphabet='0123456789')

        if self.appear(ISLAND_WORK_COMPLETE,offset=(5,5)):
            while True:
                self.device.screenshot()
                if self.appear(ISLAND_POST_SELECT,offset=1):
                    break
                if self.device.click(POST_GET):
                    continue
            self.device.click(POST_CLOSE)
            self.posts[post_id]['status'] = 'idle'
            setattr(self, time_var_name, None)
        elif self.appear(ISLAND_WORKING):
            product = self.post_product_check()
            number = ocr_post_number.ocr(image)
            time_work = Duration(ISLAND_WORKING_TIME)
            time_value = time_work.ocr(self.device.image)
            finish_time = datetime.now() + time_value
            setattr(self, time_var_name, finish_time)
            self.posts[post_id]['status'] = 'working'
            if product in self.post_check_meal:
                self.post_check_meal[product] += number
            else:
                self.post_check_meal[product] = number
            if self.appear_then_click(POST_GET, offset=(5, 5)):
                while True:
                    self.device.screenshot()
                    self.device.click(ISLAND_POST_CHECK)
                    if self.appear(ISLAND_GET):
                        self.device.click(ISLAND_POST_CHECK)
                        continue
                    if self.appear(ISLAND_WORKING):
                        self.device.click(ISLAND_POST_CHECK)
                        break
                self.device.click(ISLAND_POST_CHECK)
            self.device.click(POST_CLOSE)
        elif self.appear(ISLAND_POST_SELECT):
            self.posts[post_id]['status'] = 'idle'
            self.device.click(POST_CLOSE)
            setattr(self, time_var_name, None)

    def post_product_check(self):
        config = self.ISLAND_JUU_EATERY
        for item in config:
            if self.appear(item['post_action']):
                return item['name']
        return None

    def get_warehouse_counts(self):
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_ISLAND_JUU_EATERY)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()
        for dish in self.ISLAND_JUU_EATERY:
            self.warehouse_counts[dish['name']] = self.ocr_item_quantity(image, dish['template'])
            if self.warehouse_counts[dish['name']]:
                print(f"{dish['name']}",self.warehouse_counts[dish['name']])
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_ISLAND_JUU_COFFEE)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image_cheese = self.device.screenshot()
        self.warehouse_counts['cheese'] = self.ocr_item_quantity(image_cheese, TEMPLATE_CHEESE)
        if self.warehouse_counts['cheese']:
            print(f'cheese', self.warehouse_counts['cheese'])
        return self.warehouse_counts

    def post_eatery(self, post_id, product, number, time_var_name):
        post_button = self.posts[post_id]['button']
        self.device.click(POST_CLOSE)
        self.post_open(post_button)
        self.device.screenshot()
        time_work = Duration(ISLAND_WORKING_TIME)
        selection = self.name_to_config[product]['selection']
        selection_check = self.name_to_config[product]['selection_check']
        if self.appear_then_click(ISLAND_POST_SELECT):
            self.select_character()
            self.select_product(selection, selection_check)
            for _ in range(number):
                self.device.click(POST_ADD_ONE)
            self.device.click(POST_ADD_ORDER)
            self.wait_until_appear(ISLAND_POSTMANAGE_CHECK)
            self.post_manage_up_swipe(450)
            self.post_open(post_button)
            time_value = time_work.ocr(self.device.image)
            finish_time = datetime.now() + time_value
            setattr(self, time_var_name, finish_time)
            self.posts[post_id]['status'] = 'working'

            # 处理套餐的前置材料扣除
            if product in ['berry_orange', 'orchard_duo', 'succulently_sweet']:
                if product == 'berry_orange':
                    if 'strawberry_charlotte' in self.warehouse_counts:
                        self.warehouse_counts['strawberry_charlotte'] -= number
                    if 'orange_pie' in self.warehouse_counts:
                        self.warehouse_counts['orange_pie'] -= number
                    print(f"扣除前置材料：strawberry_charlotte -{number}, orange_pie -{number}")
                elif product == 'orchard_duo':
                    if 'apple_pie' in self.warehouse_counts:
                        self.warehouse_counts['apple_pie'] -= number
                    if 'banana_crepe' in self.warehouse_counts:
                        self.warehouse_counts['banana_crepe'] -= number
                    print(f"扣除前置材料：apple_pie -{number}, banana_crepe -{number}")
                elif product == 'succulently_sweet':
                    if 'corn_cup' in self.warehouse_counts:
                        self.warehouse_counts['corn_cup'] -= number
                    if 'rice_mango' in self.warehouse_counts:
                        self.warehouse_counts['rice_mango'] -= number
                    print(f"扣除前置材料：corn_cup -{number}, rice_mango -{number}")

            # 处理特殊餐品的前置材料扣除（strawberry_charlotte需要2个cheese）
            elif product == 'strawberry_charlotte':
                cheese_needed = number * 2
                if 'cheese' in self.warehouse_counts:
                    self.warehouse_counts['cheese'] -= cheese_needed
                print(f"扣除前置材料：cheese -{cheese_needed} (用于制作 strawberry_charlotte)")

            if product in self.to_post_products:
                self.to_post_products[product] -= number
                if self.to_post_products[product] <= 0:
                    del self.to_post_products[product]
            print(f"已安排生产：{product} x{number}")
            self.device.click(POST_CLOSE)

    def run(self):
        self.goto_management()
        self.ui_goto(page_island_postmanage)
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)
        self.post_manage_up_swipe(450)
        post_count = self.config.IslandJuuEatery_PostNumber
        time_vars = []
        for i in range(post_count):
            time_var_name = f'time_eatery{i + 1}'
            time_vars.append(time_var_name)
            setattr(self, time_var_name, None)
            post_id = f'ISLAND_JUU_EATERY_POST{i + 1}'
            self.post_check(post_id, time_var_name)
        self.get_warehouse_counts()
        self.ui_goto(page_island_postmanage)
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)
        self.post_manage_up_swipe(450)

        # 保存原始需求
        original_post_products = self.post_products.copy()

        total_subtract = Counter(self.post_check_meal)
        total_subtract.update(self.warehouse_counts)

        # 计算剩余需求，但不删除为0或负数的项
        remaining_products = {}
        for item, target_count in self.post_products.items():
            current_count = total_subtract.get(item, 0)
            remaining = target_count - current_count
            if remaining > 0:
                remaining_products[item] = remaining

        self.post_check_meal.clear()

        if not self.task_completed:
            if not self.doubled:
                # 使用剩余需求
                self.process_meal_requirements(remaining_products)
                if not self.to_post_products:
                    print("正常需求为空，检查是否需要翻倍")
                    # 检查是否有需求项存在
                    has_any_demand = any(count > 0 for count in original_post_products.values())
                    if has_any_demand:
                        print("存在需求，但库存已满足，尝试翻倍需求")
                        self.doubled = True
                        # 翻倍原始需求
                        doubled_demand = {}
                        for key, value in original_post_products.items():
                            doubled_demand[key] = value * 2

                        # 重新计算翻倍后的剩余需求
                        remaining_after_double = {}
                        for item, target_count in doubled_demand.items():
                            current_count = total_subtract.get(item, 0)
                            remaining = target_count - current_count
                            if remaining > 0:
                                remaining_after_double[item] = remaining

                        self.process_meal_requirements(remaining_after_double)
                    else:
                        print("没有设置任何需求")
                else:
                    print(f"需要生产的餐品: {self.to_post_products}")
            else:
                # 翻倍模式下，使用翻倍后的需求
                doubled_demand = {}
                for key, value in original_post_products.items():
                    doubled_demand[key] = value * 2

                # 重新计算翻倍后的剩余需求
                remaining_after_double = {}
                for item, target_count in doubled_demand.items():
                    current_count = total_subtract.get(item, 0)
                    remaining = target_count - current_count
                    if remaining > 0:
                        remaining_after_double[item] = remaining

                self.process_meal_requirements(remaining_after_double)

                if not self.to_post_products:
                    print("翻倍后需求为空，进入任务模式")
                    self.process_task_requirements()
        else:
            print("任务已完成，进入挂机模式")
            self.process_away_cook()

        if self.to_post_products:
            self.schedule_production()

        finish_times = []
        for var in time_vars:
            time_value = getattr(self, var)
            if time_value is not None:
                finish_times.append(time_value)
        if finish_times:
            finish_times.sort()
            self.config.task_delay(target=finish_times)
        else:
            self.config.task_delay(success=True)
        self.ui_goto_main()

    def process_meal_requirements(self, source_products):
        meal_compositions = {
            'berry_orange': {
                'required': ['strawberry_charlotte', 'orange_pie'],
                'quantity_per': 1
            },
            'orchard_duo': {
                'required': ['apple_pie', 'banana_crepe'],
                'quantity_per': 1
            },
            'succulently_sweet': {
                'required': ['corn_cup', 'rice_mango'],
                'quantity_per': 1
            }
        }
        # 特殊餐品的需求转换：strawberry_charlotte需要2个cheese
        special_meal_requirements = {
            'strawberry_charlotte': {
                'required': ['cheese'],
                'quantity_per': 2
            }
        }

        self.to_post_products = {}

        # 第一步：计算套餐所需的前置单品
        for meal, quantity in source_products.items():
            if meal in meal_compositions:
                required_meals = meal_compositions[meal]['required']
                required_quantity = meal_compositions[meal]['quantity_per'] * quantity
                for req_meal in required_meals:
                    if req_meal in self.to_post_products:
                        self.to_post_products[req_meal] += required_quantity
                    else:
                        self.to_post_products[req_meal] = required_quantity

        # 第二步：计算特殊餐品所需的cheese
        for meal, quantity in source_products.items():
            if meal in special_meal_requirements:
                required_meals = special_meal_requirements[meal]['required']
                required_quantity = special_meal_requirements[meal]['quantity_per'] * quantity
                for req_meal in required_meals:
                    if req_meal in self.to_post_products:
                        self.to_post_products[req_meal] += required_quantity
                    else:
                        self.to_post_products[req_meal] = required_quantity

        # 第三步：添加套餐本身到 to_post_products
        for meal, quantity in source_products.items():
            if meal in meal_compositions:
                if meal in self.to_post_products:
                    self.to_post_products[meal] += quantity
                else:
                    self.to_post_products[meal] = quantity

        # 第四步：添加其余单品到 to_post_products
        for meal, quantity in source_products.items():
            if meal not in meal_compositions and meal not in special_meal_requirements:
                if meal in self.to_post_products:
                    self.to_post_products[meal] += quantity
                else:
                    self.to_post_products[meal] = quantity

        print(f"转换完成：source_products -> to_post_products")
        print(f"原始需求: {source_products}")
        print(f"生产计划: {self.to_post_products}")

    def process_task_requirements(self):
        task_products = self.post_products_task.copy()
        for item, quantity in self.warehouse_counts.items():
            if item in task_products:
                task_products[item] -= quantity
                if task_products[item] <= 0:
                    del task_products[item]
        self.process_meal_requirements(task_products)
        if not self.to_post_products:
            self.task_completed = True
            print("任务需求已完成")

    def process_away_cook(self):
        away_cook = self.config.IslandJuuEateryNextTask_AwayCook
        if away_cook:
            self.to_post_products = {away_cook: 9999}
            print(f"挂机模式：生产 {away_cook}，无限数量")
        else:
            self.to_post_products = {}
            print("未设置挂机餐品")

    def schedule_production(self):
        if not self.to_post_products:
            print("没有需要生产的餐品")
            return
        idle_posts = [post_id for post_id, post_info in self.posts.items()
                      if post_info['status'] == 'idle']
        if not idle_posts:
            print("没有空闲的岗位")
            return
        for product, required_quantity in list(self.to_post_products.items()):
            if required_quantity <= 0:
                continue
            idle_posts = [post_id for post_id, post_info in self.posts.items()
                          if post_info['status'] == 'idle']
            if not idle_posts:
                print("所有岗位都在工作中")
                break
            batch_size = min(5, required_quantity)

            # 处理套餐的前置材料检查
            if product in ['berry_orange', 'orchard_duo', 'succulently_sweet']:
                if product == 'berry_orange':
                    strawberry_charlotte_stock = self.warehouse_counts.get('strawberry_charlotte', 0)
                    orange_pie_stock = self.warehouse_counts.get('orange_pie', 0)
                    possible_batch = min(batch_size, strawberry_charlotte_stock, orange_pie_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['strawberry_charlotte'] -= batch_size
                    self.warehouse_counts['orange_pie'] -= batch_size
                elif product == 'orchard_duo':
                    apple_pie_stock = self.warehouse_counts.get('apple_pie', 0)
                    banana_crepe_stock = self.warehouse_counts.get('banana_crepe', 0)
                    possible_batch = min(batch_size, apple_pie_stock, banana_crepe_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['apple_pie'] -= batch_size
                    self.warehouse_counts['banana_crepe'] -= batch_size
                elif product == 'succulently_sweet':
                    corn_cup_stock = self.warehouse_counts.get('corn_cup', 0)
                    rice_mango_stock = self.warehouse_counts.get('rice_mango', 0)
                    possible_batch = min(batch_size, corn_cup_stock, rice_mango_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['corn_cup'] -= batch_size
                    self.warehouse_counts['rice_mango'] -= batch_size

            # 处理特殊餐品的前置材料检查（strawberry_charlotte需要2个cheese）
            elif product == 'strawberry_charlotte':
                cheese_needed_per_batch = 2
                cheese_stock = self.warehouse_counts.get('cheese', 0)
                # 计算最多可以生产多少个（每个需要2个cheese）
                possible_batch = min(batch_size, cheese_stock // cheese_needed_per_batch)
                if possible_batch <= 0:
                    print(f"餐品 {product} 的前置材料不足，跳过")
                    continue
                batch_size = possible_batch
                self.warehouse_counts['cheese'] -= batch_size * cheese_needed_per_batch

            post_id = idle_posts[0]
            post_num = post_id[-1]
            time_var_name = f'time_eatery{post_num}'

            self.post_eatery(post_id, product, batch_size, time_var_name)
        print(f"生产安排完成，剩余需求: {self.to_post_products}")

    def test(self):
        for item in self.ISLAND_JUU_EATERY:
            if self.appear(item['post_action']):
                print(item['name'])

    def test1(self):
        self.get_warehouse_counts()
        print(self.warehouse_counts)

    def test2(self):
        if self.appear_then_click(POST_GET, offset=(5, 5)):
            while True:
                self.device.screenshot()
                self.device.click(ISLAND_POST_CHECK)
                if self.appear(ISLAND_GET):
                    self.device.click(ISLAND_POST_CHECK)
                    continue
                if self.appear(ISLAND_WORKING):
                    self.device.click(ISLAND_POST_CHECK)
                    break
if __name__ == "__main__":
    az = IslandJuuEatery('alas', task='Alas')
    az.device.screenshot()
    az.run()

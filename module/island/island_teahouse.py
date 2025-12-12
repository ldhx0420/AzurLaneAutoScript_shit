from module.island_teahouse.assets import *
from module.island.assets import *
from module.island.island import *
from collections import Counter
from datetime import datetime
from module.handler.login import LoginHandler
from module.ocr.ocr import *


class IslandTeahouse(Island, LoginHandler):
    def __init__(self, *args, **kwargs):
        Island.__init__(self, *args, **kwargs)
        self.ISLAND_TEAHOUSE = [
            {'name': 'apple_juice', 'template': TEMPLATE_APPLE_JUICE, 'var_name': 'apple_juice',
             'selection': APPLE_JUICE_SELECTION, 'selection_check': APPLE_JUICE_SELECTION_CHECK,
             'post_action': POST_APPLE_JUICE},
            {'name': 'banana_mango', 'template': TEMPLATE_BANANA_MANGO, 'var_name': 'banana_mango',
             'selection': BANANA_MANGO_SELECTION, 'selection_check': BANANA_MANGO_SELECTION_CHECK,
             'post_action': POST_BANANA_MANGO},
            {'name': 'honey_lemon', 'template': TEMPLATE_HONEY_LEMON, 'var_name': 'honey_lemon',
             'selection': HONEY_LEMON_SELECTION, 'selection_check': HONEY_LEMON_SELECTION_CHECK,
             'post_action': POST_HONEY_LEMON},
            {'name': 'strawberry_lemon', 'template': TEMPLATE_STRAWBERRY_LEMON, 'var_name': 'strawberry_lemon',
             'selection': STRAWBERRY_LEMON_SELECTION, 'selection_check': STRAWBERRY_LEMON_SELECTION_CHECK,
             'post_action': POST_STRAWBERRY_LEMON},
            {'name': 'strawberry_honey', 'template': TEMPLATE_STRAWBERRY_HONEY, 'var_name': 'strawberry_honey',
             'selection': STRAWBERRY_HONEY_SELECTION, 'selection_check': STRAWBERRY_HONEY_SELECTION_CHECK,
             'post_action': POST_STRAWBERRY_HONEY},
            {'name': 'floral_fruity', 'template': TEMPLATE_FLORAL_FRUITY, 'var_name': 'floral_fruity',
             'selection': FLORAL_FRUITY_SELECTION, 'selection_check': FLORAL_FRUITY_SELECTION_CHECK,
             'post_action': POST_FLORAL_FRUITY},
            {'name': 'fruit_paradise', 'template': TEMPLATE_FRUIT_PARADISE, 'var_name': 'fruit_paradise',
             'selection': FRUIT_PARADISE_SELECTION, 'selection_check': FRUIT_PARADISE_SELECTION_CHECK,
             'post_action': POST_FRUIT_PARADISE},
            {'name': 'lavender_tea', 'template': TEMPLATE_LAVENDER_TEA, 'var_name': 'lavender_tea',
             'selection': LAVENDER_TEA_SELECTION, 'selection_check': LAVENDER_TEA_SELECTION_CHECK,
             'post_action': POST_LAVENDER_TEA},
            {'name': 'sunny_honey', 'template': TEMPLATE_SUNNY_HONEY, 'var_name': 'sunny_honey',
             'selection': SUNNY_HONEY_SELECTION, 'selection_check': SUNNY_HONEY_SELECTION_CHECK,
             'post_action': POST_SUNNY_HONEY},
        ]
        self.name_to_config = {item['name']: item for item in self.ISLAND_TEAHOUSE}
        self.posts = {
            'ISLAND_TEAHOUSE_POST1': {'status': 'none', 'button': ISLAND_TEAHOUSE_POST1},
            'ISLAND_TEAHOUSE_POST2': {'status': 'none', 'button': ISLAND_TEAHOUSE_POST2}
        }
        self.post_check_meal = {}

        self.post_products = {}
        meal_keys = [
            ('IslandTeahouse_Meal1', 'IslandTeahouse_MealNumber'),
            ('IslandTeahouse_Meal2', 'IslandTeahouse_MealNumber'),
            ('IslandTeahouse_Meal3', 'IslandTeahouse_MealNumber'),
            ('IslandTeahouse_Meal4', 'IslandTeahouse_MealNumber')
        ]
        for meal_key, number_key in meal_keys:
            meal_name = getattr(self.config, meal_key, None)
            if meal_name is not None and meal_name != "None":
                meal_number = getattr(self.config, number_key, 0)
                self.post_products[meal_name] = meal_number

        self.post_products_task = {}
        task_keys = [
            ('IslandTeahouseNextTask_MealTask1', 'IslandTeahouseNextTask_MealTaskNumber1'),
            ('IslandTeahouseNextTask_MealTask2', 'IslandTeahouseNextTask_MealTaskNumber2'),
            ('IslandTeahouseNextTask_MealTask3', 'IslandTeahouseNextTask_MealTaskNumber3'),
            ('IslandTeahouseNextTask_MealTask4', 'IslandTeahouseNextTask_MealTaskNumber4')
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
            if self.appear_then_click(POST_GET,offset=(5,5)):
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
        self.device.click(POST_CLOSE)
    def post_product_check(self):
        config = self.ISLAND_TEAHOUSE
        for item in config:
            if self.appear(item['post_action']):
                return item['name']
        return None

    def get_warehouse_counts(self):
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_ISLAND_TEAHOUSE)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()
        for dish in self.ISLAND_TEAHOUSE:
            self.warehouse_counts[dish['name']] = self.ocr_item_quantity(image, dish['template'])
            if self.warehouse_counts[dish['name']]:
                print(f"{dish['name']}", self.warehouse_counts[dish['name']])
        return self.warehouse_counts

    def post_tea_house(self, post_id, product, number, time_var_name):
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

            if product in ['floral_fruity', 'fruit_paradise', 'sunny_honey']:
                if product == 'floral_fruity':
                    if 'lavender_tea' in self.warehouse_counts:
                        self.warehouse_counts['lavender_tea'] -= number
                    if 'apple_juice' in self.warehouse_counts:
                        self.warehouse_counts['apple_juice'] -= number
                    print(f"扣除前置材料：lavender_tea -{number}, apple_juice -{number}")
                elif product == 'fruit_paradise':
                    if 'banana_mango' in self.warehouse_counts:
                        self.warehouse_counts['banana_mango'] -= number
                    if 'strawberry_honey' in self.warehouse_counts:
                        self.warehouse_counts['strawberry_honey'] -= number
                    print(f"扣除前置材料：banana_mango -{number}, strawberry_honey -{number}")
                elif product == 'sunny_honey':
                    if 'strawberry_lemon' in self.warehouse_counts:
                        self.warehouse_counts['strawberry_lemon'] -= number
                    if 'honey_lemon' in self.warehouse_counts:
                        self.warehouse_counts['honey_lemon'] -= number
                    print(f"扣除前置材料：strawberry_lemon -{number}, honey_lemon -{number}")
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
        post_count = self.config.IslandTeahouse_PostNumber
        time_vars = []
        for i in range(post_count):
            time_var_name = f'time_tea{i + 1}'
            time_vars.append(time_var_name)
            setattr(self, time_var_name, None)
            post_id = f'ISLAND_TEAHOUSE_POST{i + 1}'
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
            'floral_fruity': {
                'required': ['lavender_tea', 'apple_juice'],
                'quantity_per': 1
            },
            'fruit_paradise': {
                'required': ['banana_mango', 'strawberry_honey'],
                'quantity_per': 1
            },
            'sunny_honey': {
                'required': ['strawberry_lemon', 'honey_lemon'],
                'quantity_per': 1
            }
        }
        self.to_post_products = {}
        for meal, quantity in source_products.items():
            if meal in meal_compositions:
                required_meals = meal_compositions[meal]['required']
                required_quantity = meal_compositions[meal]['quantity_per'] * quantity
                for req_meal in required_meals:
                    if req_meal in self.to_post_products:
                        self.to_post_products[req_meal] += required_quantity
                    else:
                        self.to_post_products[req_meal] = required_quantity
        for meal, quantity in source_products.items():
            if meal in meal_compositions:
                if meal in self.to_post_products:
                    self.to_post_products[meal] += quantity
                else:
                    self.to_post_products[meal] = quantity
        for meal, quantity in source_products.items():
            if meal not in meal_compositions:
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
        away_cook = self.config.IslandTeahouseNextTask_AwayCook
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
            if product in ['floral_fruity', 'fruit_paradise', 'sunny_honey']:
                if product == 'floral_fruity':
                    lavender_stock = self.warehouse_counts.get('lavender_tea', 0)
                    apple_stock = self.warehouse_counts.get('apple_juice', 0)
                    possible_batch = min(batch_size, lavender_stock, apple_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['lavender_tea'] -= batch_size
                    self.warehouse_counts['apple_juice'] -= batch_size
                elif product == 'fruit_paradise':
                    banana_stock = self.warehouse_counts.get('banana_mango', 0)
                    strawberry_stock = self.warehouse_counts.get('strawberry_honey', 0)
                    possible_batch = min(batch_size, banana_stock, strawberry_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['banana_mango'] -= batch_size
                    self.warehouse_counts['strawberry_honey'] -= batch_size
                elif product == 'sunny_honey':
                    strawberry_lemon_stock = self.warehouse_counts.get('strawberry_lemon', 0)
                    honey_lemon_stock = self.warehouse_counts.get('honey_lemon', 0)
                    possible_batch = min(batch_size, strawberry_lemon_stock, honey_lemon_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['strawberry_lemon'] -= batch_size
                    self.warehouse_counts['honey_lemon'] -= batch_size

            post_id = idle_posts[0]
            post_num = post_id[-1]
            time_var_name = f'time_tea{post_num}'

            self.post_tea_house(post_id, product, batch_size, time_var_name)
        print(f"生产安排完成，剩余需求: {self.to_post_products}")

    def test(self):
        print(self.post_products, self.post_products_task)
    def test1(self):

        print(self.config.IslandTeahouse_PostNumber)
if __name__ == "__main__":
    az = IslandTeahouse('alas', task='Alas')
    az.device.screenshot()
    az.run()


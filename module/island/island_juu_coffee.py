from module.island_juu_coffee.assets import *
from module.island.assets import *
from module.island.island import *
from collections import Counter
from datetime import datetime
from module.handler.login import LoginHandler
from module.island.warehouse import *
from module.ocr.ocr import *

class IslandJuuCoffee(Island, WarehouseOCR, LoginHandler):
    def __init__(self, *args, **kwargs):
        Island.__init__(self, *args, **kwargs)
        WarehouseOCR.__init__(self)
        self.ISLAND_JUU_COFFEE = [
            {'name': 'iced_coffee', 'template': TEMPLATE_ICED_COFFEE, 'var_name': 'iced_coffee',
             'selection': ICED_COFFEE_SELECTION, 'selection_check': ICED_COFFEE_SELECTION_CHECK,
             'post_action': POST_ICED_COFFEE},
            {'name': 'omelette', 'template': TEMPLATE_OMELETTE, 'var_name': 'omelette',
             'selection': OMELETTE_SELECTION, 'selection_check': OMELETTE_SELECTION_CHECK,
             'post_action': POST_OMELETTE},
            {'name': 'cheese', 'template': TEMPLATE_CHEESE, 'var_name': 'cheese',
             'selection': CHEESE_SELECTION, 'selection_check': CHEESE_SELECTION_CHECK,
             'post_action': POST_CHEESE},
            {'name': 'latte', 'template': TEMPLATE_LATTE, 'var_name': 'latte',
             'selection': LATTE_SELECTION, 'selection_check': LATTE_SELECTION_CHECK,
             'post_action': POST_LATTE},
            {'name': 'citrus_coffee', 'template': TEMPLATE_CITRUS_COFFEE, 'var_name': 'citrus_coffee',
             'selection': CITRUS_COFFEE_SELECTION, 'selection_check': CITRUS_COFFEE_SELECTION_CHECK,
             'post_action': POST_CITRUS_COFFEE},
            {'name': 'strawberry_milkshake', 'template': TEMPLATE_STRAWBERRY_MILKSHAKE,
             'var_name': 'strawberry_milkshake',
             'selection': STRAWBERRY_MILKSHAKE_SELECTION, 'selection_check': STRAWBERRY_MILKSHAKE_SELECTION_CHECK,
             'post_action': POST_STRAWBERRY_MILKSHAKE},
            {'name': 'morning_light', 'template': TEMPLATE_MORNING_LIGHT, 'var_name': 'morning_light',
             'selection': MORNING_LIGHT_SELECTION, 'selection_check': MORNING_LIGHT_SELECTION_CHECK,
             'post_action': POST_MORNING_LIGHT},
            {'name': 'wake_up_call', 'template': TEMPLATE_WAKE_UP_CALL, 'var_name': 'wake_up_call',
             'selection': WAKE_UP_CALL_SELECTION, 'selection_check': WAKE_UP_CALL_SELECTION_CHECK,
             'post_action': POST_WAKE_UP_CALL},
            {'name': 'fruity_fruitier', 'template': TEMPLATE_FRUITY_FRUITIER, 'var_name': 'fruity_fruitier',
             'selection': FRUITY_FRUITIER_SELECTION, 'selection_check': FRUITY_FRUITIER_SELECTION_CHECK,
             'post_action': POST_FRUITY_FRUITIER},
        ]
        self.name_to_config = {item['name']: item for item in self.ISLAND_JUU_COFFEE}
        self.posts = {
            'ISLAND_JUU_COFFEE_POST1': {'status': 'none', 'button': ISLAND_JUU_COFFEE_POST1},
            'ISLAND_JUU_COFFEE_POST2': {'status': 'none', 'button': ISLAND_JUU_COFFEE_POST2}
        }
        self.post_check_meal = {}

        self.post_products = {}
        meal_keys = [
            ('IslandJuuCoffee_Meal1', 'IslandJuuCoffee_MealNumber'),
            ('IslandJuuCoffee_Meal2', 'IslandJuuCoffee_MealNumber'),
            ('IslandJuuCoffee_Meal3', 'IslandJuuCoffee_MealNumber'),
            ('IslandJuuCoffee_Meal4', 'IslandJuuCoffee_MealNumber')
        ]
        for meal_key, number_key in meal_keys:
            meal_name = getattr(self.config, meal_key, None)
            if meal_name is not None and meal_name != "None":
                meal_number = getattr(self.config, number_key, 0)
                self.post_products[meal_name] = meal_number

        self.post_products_task = {}
        task_keys = [
            ('IslandJuuCoffeeNextTask_MealTask1', 'IslandJuuCoffeeNextTask_MealTaskNumber1'),
            ('IslandJuuCoffeeNextTask_MealTask2', 'IslandJuuCoffeeNextTask_MealTaskNumber2'),
            ('IslandJuuCoffeeNextTask_MealTask3', 'IslandJuuCoffeeNextTask_MealTaskNumber3'),
            ('IslandJuuCoffeeNextTask_MealTask4', 'IslandJuuCoffeeNextTask_MealTaskNumber4')
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
        config = self.ISLAND_JUU_COFFEE
        for item in config:
            if self.appear(item['post_action']):
                return item['name']
        return None

    def get_warehouse_counts(self):
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_ISLAND_JUU_COFFEE)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()
        for dish in self.ISLAND_JUU_COFFEE:
            self.warehouse_counts[dish['name']] = self.ocr_item_quantity(image, dish['template'])
            if self.warehouse_counts[dish['name']]:
                print(f"{dish['name']}", self.warehouse_counts[dish['name']])
        return self.warehouse_counts

    def post_coffee(self, post_id, product, number, time_var_name):
        post_button = self.posts[post_id]['button']
        self.device.click(POST_CLOSE)
        self.post_open(post_button)
        self.device.screenshot()
        time_work = Duration(ISLAND_WORKING_TIME)
        selection = self.name_to_config[product]['selection']
        selection_check = self.name_to_config[product]['selection_check']
        if self.appear_then_click(ISLAND_POST_SELECT):
            self.select_worker_juu()
            self.select_product(selection, selection_check)
            for _ in range(number):
                self.device.click(POST_ADD_ONE)
            self.device.click(POST_ADD_ORDER)
            self.wait_until_appear(ISLAND_POSTMANAGE_CHECK)
            self.post_manage_up_swipe(450)
            self.post_manage_up_swipe(450)# 或执行两次 self.post_manage_up_swipe(450)
            self.post_open(post_button)
            time_value = time_work.ocr(self.device.image)
            finish_time = datetime.now() + time_value
            setattr(self, time_var_name, finish_time)
            self.posts[post_id]['status'] = 'working'

            # 处理套餐的前置材料扣除
            if product in ['morning_light', 'wake_up_call', 'fruity_fruitier']:
                if product == 'morning_light':
                    if 'latte' in self.warehouse_counts:
                        self.warehouse_counts['latte'] -= number
                    if 'omelette' in self.warehouse_counts:
                        self.warehouse_counts['omelette'] -= number
                    print(f"扣除前置材料：latte -{number}, omelette -{number}")
                elif product == 'wake_up_call':
                    if 'cheese' in self.warehouse_counts:
                        self.warehouse_counts['cheese'] -= number
                    if 'iced_coffee' in self.warehouse_counts:
                        self.warehouse_counts['iced_coffee'] -= number
                    print(f"扣除前置材料：cheese -{number}, iced_coffee -{number}")
                elif product == 'fruity_fruitier':
                    if 'citrus_coffee' in self.warehouse_counts:
                        self.warehouse_counts['citrus_coffee'] -= number
                    if 'strawberry_milkshake' in self.warehouse_counts:
                        self.warehouse_counts['strawberry_milkshake'] -= number
                    print(f"扣除前置材料：citrus_coffee -{number}, strawberry_milkshake -{number}")

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
        self.post_manage_up_swipe(450)# 初始滑动
        post_count = self.config.IslandJuuCoffee_PostNumber
        time_vars = []
        for i in range(post_count):
            time_var_name = f'time_coffee{i + 1}'
            time_vars.append(time_var_name)
            setattr(self, time_var_name, None)
            post_id = f'ISLAND_JUU_COFFEE_POST{i + 1}'
            self.post_check(post_id, time_var_name)
        self.get_warehouse_counts()
        self.ui_goto(page_island_postmanage)
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)
        self.post_manage_up_swipe(450)
        self.post_manage_up_swipe(450)# JuuCoffee需要滑动900
        total_subtract = Counter(self.post_check_meal)
        total_subtract.update(self.warehouse_counts)
        for item, total in total_subtract.items():
            if item in self.post_products:
                self.post_products[item] -= total
                if self.post_products[item] <= 0:
                    del self.post_products[item]
        self.post_check_meal.clear()
        if not self.task_completed:
            if not self.doubled:
                self.process_meal_requirements(self.post_products)
                if not self.to_post_products:
                    print("正常需求为空，翻倍需求")
                    self.doubled = True
                    for key in list(self.post_products.keys()):
                        self.post_products[key] *= 2
                    self.process_meal_requirements(self.post_products)
            else:
                self.process_meal_requirements(self.post_products)
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
            'morning_light': {
                'required': ['latte', 'omelette'],
                'quantity_per': 1
            },
            'wake_up_call': {
                'required': ['cheese', 'iced_coffee'],
                'quantity_per': 1
            },
            'fruity_fruitier': {
                'required': ['citrus_coffee', 'strawberry_milkshake'],
                'quantity_per': 1
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

        # 第二步：添加套餐本身到 to_post_products
        for meal, quantity in source_products.items():
            if meal in meal_compositions:
                if meal in self.to_post_products:
                    self.to_post_products[meal] += quantity
                else:
                    self.to_post_products[meal] = quantity

        # 第三步：添加其余单品到 to_post_products
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
        away_cook = self.config.IslandJuuCoffeeNextTask_AwayCook
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
            if product in ['morning_light', 'wake_up_call', 'fruity_fruitier']:
                if product == 'morning_light':
                    latte_stock = self.warehouse_counts.get('latte', 0)
                    omelette_stock = self.warehouse_counts.get('omelette', 0)
                    possible_batch = min(batch_size, latte_stock, omelette_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['latte'] -= batch_size
                    self.warehouse_counts['omelette'] -= batch_size
                elif product == 'wake_up_call':
                    cheese_stock = self.warehouse_counts.get('cheese', 0)
                    iced_coffee_stock = self.warehouse_counts.get('iced_coffee', 0)
                    possible_batch = min(batch_size, cheese_stock, iced_coffee_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['cheese'] -= batch_size
                    self.warehouse_counts['iced_coffee'] -= batch_size
                elif product == 'fruity_fruitier':
                    citrus_coffee_stock = self.warehouse_counts.get('citrus_coffee', 0)
                    strawberry_milkshake_stock = self.warehouse_counts.get('strawberry_milkshake', 0)
                    possible_batch = min(batch_size, citrus_coffee_stock, strawberry_milkshake_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['citrus_coffee'] -= batch_size
                    self.warehouse_counts['strawberry_milkshake'] -= batch_size

            post_id = idle_posts[0]
            post_num = post_id[-1]
            time_var_name = f'time_coffee{post_num}'

            self.post_coffee(post_id, product, batch_size, time_var_name)
        print(f"生产安排完成，剩余需求: {self.to_post_products}")

    def test(self):
        self.post_manage_up_swipe(450)
        self.post_manage_up_swipe(450)

    def test1(self):
        self.get_warehouse_counts()
        print(self.warehouse_counts)
if __name__ == "__main__":
    az = IslandJuuCoffee('alas', task='Alas')
    az.device.screenshot()
    az.run()

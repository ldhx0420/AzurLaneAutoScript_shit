from module.island_grill.assets import *
from module.island.assets import *
from module.island.island import *
from collections import Counter
from datetime import datetime
from module.handler.login import LoginHandler
from module.island.warehouse import *
from module.ocr.ocr import *


class IslandGrill(Island, WarehouseOCR, LoginHandler):
    def __init__(self, *args, **kwargs):
        Island.__init__(self, *args, **kwargs)
        WarehouseOCR.__init__(self)
        self.ISLAND_GRILL = [
            {'name': 'roasted_skewer', 'template': TEMPLATE_ROASTED_SKEWER, 'var_name': 'roasted_skewer',
             'selection': ROASTED_SKEWER_SELECTION, 'selection_check': ROASTED_SKEWER_SELECTION_CHECK,
             'post_action': POST_ROASTED_SKEWER},
            {'name': 'chicken_potato', 'template': TEMPLATE_CHICKEN_POTATO, 'var_name': 'chicken_potato',
             'selection': CHICKEN_POTATO_SELECTION, 'selection_check': CHICKEN_POTATO_SELECTION_CHECK,
             'post_action': POST_CHICKEN_POTATO},
            {'name': 'carrot_omelette', 'template': TEMPLATE_CARROT_OMELETTE, 'var_name': 'carrot_omelette',
             'selection': CARROT_OMELETTE_SELECTION, 'selection_check': CARROT_OMELETTE_SELECTION_CHECK,
             'post_action': POST_CARROT_OMELETTE},
            {'name': 'stir_fried_chicken', 'template': TEMPLATE_STIR_FRIED_CHICKEN, 'var_name': 'stir_fried_chicken',
             'selection': STIR_FRIED_CHICKEN_SELECTION, 'selection_check': STIR_FRIED_CHICKEN_SELECTION_CHECK,
             'post_action': POST_STIR_FRIED_CHICKEN},
            {'name': 'steak_bowl', 'template': TEMPLATE_STEAK_BOWL, 'var_name': 'steak_bowl',
             'selection': STEAK_BOWL_SELECTION, 'selection_check': STEAK_BOWL_SELECTION_CHECK,
             'post_action': POST_STEAK_BOWL},
            {'name': 'carnival', 'template': TEMPLATE_CARNIVAL, 'var_name': 'carnival',
             'selection': CARNIVAL_SELECTION, 'selection_check': CARNIVAL_SELECTION_CHECK,
             'post_action': POST_CARNIVAL},
            {'name': 'double_energy', 'template': TEMPLATE_DOUBLE_ENERGY, 'var_name': 'double_energy',
             'selection': DOUBLE_ENERGY_SELECTION, 'selection_check': DOUBLE_ENERGY_SELECTION_CHECK,
             'post_action': POST_DOUBLE_ENERGY},
        ]
        self.name_to_config = {item['name']: item for item in self.ISLAND_GRILL}
        self.posts = {
            'ISLAND_GRILL_POST1': {'status': 'none', 'button': ISLAND_GRILL_POST1},
            'ISLAND_GRILL_POST2': {'status': 'none', 'button': ISLAND_GRILL_POST2}
        }
        self.post_check_meal = {}
        self.post_products = {}
        meal_keys = [
            ('IslandGrill_Meal1', 'IslandGrill_MealNumber'),
            ('IslandGrill_Meal2', 'IslandGrill_MealNumber'),
            ('IslandGrill_Meal3', 'IslandGrill_MealNumber'),
            ('IslandGrill_Meal4', 'IslandGrill_MealNumber')
        ]

        for meal_key, number_key in meal_keys:
            meal_name = getattr(self.config, meal_key, None)
            if meal_name is not None and meal_name != "None":  # 过滤掉 None
                meal_number = getattr(self.config, number_key, 0)
                self.post_products[meal_name] = meal_number

        # 同样的方式处理任务餐品
        self.post_products_task = {}
        task_keys = [
            ('IslandGGrillNextTask_MealTask1', 'IslandGGrillNextTask_MealTaskNumber1'),
            ('IslandGGrillNextTask_MealTask2', 'IslandGGrillNextTask_MealTaskNumber2'),
            ('IslandGGrillNextTask_MealTask3', 'IslandGGrillNextTask_MealTaskNumber3'),
            ('IslandGGrillNextTask_MealTask4', 'IslandGGrillNextTask_MealTaskNumber4')
        ]

        for task_key, number_key in task_keys:
            meal_name = getattr(self.config, task_key, None)
            if meal_name is not None and meal_name != "None":
                meal_number = getattr(self.config, number_key, 0)
                if meal_number > 0:  # 只添加数量大于0的
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
                if self.appear(ISLAND_POST_SELECT):
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
            if self.appear_then_click(POST_GET ,offset=(5,5)):
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
        config = self.ISLAND_GRILL
        for item in config:
            if self.appear(item['post_action']):
                return item['name']
        return None

    def get_warehouse_counts(self):
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_ISLAND_GRILL)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()
        for dish in self.ISLAND_GRILL:
            self.warehouse_counts[dish['name']] = self.ocr_item_quantity(image, dish['template'])
            if self.warehouse_counts[dish['name']]:
                print(f"{dish['name']}", self.warehouse_counts[dish['name']])
        return self.warehouse_counts

    def post_grill(self, post_id, product, number, time_var_name):
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
            self.post_open(post_button)
            time_value = time_work.ocr(self.device.image)
            finish_time = datetime.now() + time_value
            setattr(self, time_var_name, finish_time)
            self.posts[post_id]['status'] = 'working'

            if product in ['double_energy', 'carnival']:
                if product == 'double_energy':
                    if 'stir_fried_chicken' in self.warehouse_counts:
                        self.warehouse_counts['stir_fried_chicken'] -= number
                    if 'steak_bowl' in self.warehouse_counts:
                        self.warehouse_counts['steak_bowl'] -= number
                    print(f"扣除前置材料：stir_fried_chicken -{number}, steak_bowl -{number}")
                elif product == 'carnival':
                    if 'chicken_potato' in self.warehouse_counts:
                        self.warehouse_counts['chicken_potato'] -= number
                    if 'roasted_skewer' in self.warehouse_counts:
                        self.warehouse_counts['roasted_skewer'] -= number
                    print(f"扣除前置材料：chicken_potato -{number}, roasted_skewer -{number}")
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
        post_count = self.config.IslandGrill_PostNumber
        time_vars = []
        for i in range(post_count):
            time_var_name = f'time_meal{i + 1}'
            time_vars.append(time_var_name)
            setattr(self, time_var_name, None)
            post_id = f'ISLAND_GRILL_POST{i + 1}'
            self.post_check(post_id, time_var_name)
        self.get_warehouse_counts()
        self.ui_goto(page_island_postmanage)
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)
        self.post_manage_up_swipe(450)
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
            'double_energy': {
                'required': ['stir_fried_chicken', 'steak_bowl'],
                'quantity_per': 1
            },
            'carnival': {
                'required': ['chicken_potato', 'roasted_skewer'],
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
        away_cook = self.config.IslandGrillNextTask_AwayCook
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
            if product in ['double_energy', 'carnival']:
                if product == 'double_energy':
                    chicken_stock = self.warehouse_counts.get('stir_fried_chicken', 0)
                    steak_stock = self.warehouse_counts.get('steak_bowl', 0)
                    possible_batch = min(batch_size, chicken_stock, steak_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['stir_fried_chicken'] -= batch_size
                    self.warehouse_counts['steak_bowl'] -= batch_size
                elif product == 'carnival':
                    potato_stock = self.warehouse_counts.get('chicken_potato', 0)
                    skewer_stock = self.warehouse_counts.get('roasted_skewer', 0)
                    possible_batch = min(batch_size, potato_stock, skewer_stock)
                    if possible_batch <= 0:
                        print(f"套餐 {product} 的前置材料不足，跳过")
                        continue
                    batch_size = possible_batch
                    self.warehouse_counts['chicken_potato'] -= batch_size
                    self.warehouse_counts['roasted_skewer'] -= batch_size

            post_id = idle_posts[0]
            post_num = post_id[-1]
            time_var_name = f'time_meal{post_num}'

            self.post_grill(post_id, product, batch_size, time_var_name)
        print(f"生产安排完成，剩余需求: {self.to_post_products}")

    def test(self):
        print(self.post_products, self.post_products_task)
    def test1(self):
        self.get_warehouse_counts()
        print(self.warehouse_counts)
if __name__ == "__main__":
    az =IslandGrill('alas', task='Alas')
    az.device.screenshot()
    az.run()


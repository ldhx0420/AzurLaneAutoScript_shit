# island_shop_base.py
from module.island.assets import *
from module.island.island import *
from collections import Counter
from datetime import datetime
from module.handler.login import LoginHandler
from module.ocr.ocr import *
from module.island.warehouse import *
from module.island.island_select_character import *


class IslandShopBase(Island, WarehouseOCR, SelectCharacter, LoginHandler):
    """所有岛屿商店的基类"""

    def __init__(self, *args, **kwargs):
        Island.__init__(self, *args, **kwargs)
        WarehouseOCR.__init__(self)

        # 子类必须设置的属性
        self.shop_items = []  # 商品列表
        self.shop_type = ""  # 店铺类型：grill, teahouse, tailor, toolshop, furniture
        self.filter_asset = None  # 仓库筛选资产
        self.post_buttons = {}  # 岗位按钮
        self.time_prefix = "time_meal"  # 时间变量前缀

        # 通用属性
        self.name_to_config = {}
        self.posts = {}
        self.post_check_meal = {}
        self.post_products = {}
        self.post_products_task = {}
        self.warehouse_counts = {}
        self.to_post_products = {}
        self.doubled = False
        self.task_completed = False
        self.current_totals = {}

        # 特殊材料（子类可覆盖）
        self.special_materials = {}

        # 套餐组成（子类可覆盖）
        self.meal_compositions = {}

        # 配置前缀（子类可覆盖）
        self.config_meal_prefix = "Island_Meal"
        self.config_number_prefix = "Island_MealNumber"
        self.config_task_prefix = "IslandNextTask_MealTask"
        self.config_task_number_prefix = "IslandNextTask_MealTaskNumber"
        self.config_post_number = "Island_PostNumber"
        self.config_away_cook = "IslandNextTask_AwayCook"

        # 滑动配置（子类可覆盖）
        self.post_manage_swipe_count = 1  # 默认滑动1次450
        self.post_produce_swipe_count = 1  # post_produce中滑动次数，默认1次450

    def setup_config(self, config_meal_prefix, config_number_prefix,
                     config_task_prefix, config_task_number_prefix,
                     config_post_number, config_away_cook):
        """从配置中读取餐品需求"""
        # 设置配置前缀
        self.config_meal_prefix = config_meal_prefix
        self.config_number_prefix = config_number_prefix
        self.config_task_prefix = config_task_prefix
        self.config_task_number_prefix = config_task_number_prefix
        self.config_post_number = config_post_number
        self.config_away_cook = config_away_cook

        # 读取正常餐品需求
        self.post_products = {}
        meal_keys = [
            (f'{self.config_meal_prefix}1', f'{self.config_number_prefix}'),
            (f'{self.config_meal_prefix}2', f'{self.config_number_prefix}'),
            (f'{self.config_meal_prefix}3', f'{self.config_number_prefix}'),
            (f'{self.config_meal_prefix}4', f'{self.config_number_prefix}')
        ]

        for meal_key, number_key in meal_keys:
            meal_name = getattr(self.config, meal_key, None)
            if meal_name is not None and meal_name != "None":
                meal_number = getattr(self.config, number_key, 0)
                self.post_products[meal_name] = meal_number

        # 读取任务餐品需求
        self.post_products_task = {}
        task_keys = [
            (f'{self.config_task_prefix}1', f'{self.config_task_number_prefix}1'),
            (f'{self.config_task_prefix}2', f'{self.config_task_number_prefix}2'),
            (f'{self.config_task_prefix}3', f'{self.config_task_number_prefix}3'),
            (f'{self.config_task_prefix}4', f'{self.config_task_number_prefix}4')
        ]

        for task_key, number_key in task_keys:
            meal_name = getattr(self.config, task_key, None)
            if meal_name is not None and meal_name != "None":
                meal_number = getattr(self.config, number_key, 0)
                if meal_number > 0:
                    self.post_products_task[meal_name] = meal_number

    def initialize_shop(self):
        """初始化店铺，子类必须在__init__中调用"""
        self.name_to_config = {item['name']: item for item in self.shop_items}

        # 初始化岗位状态
        for post_id, button in self.post_buttons.items():
            self.posts[post_id] = {'status': 'none', 'button': button}

    # ============ 通用方法 ============

    def post_check(self, post_id, time_var_name):
        """检查岗位状态（通用）"""
        post_button = self.posts[post_id]['button']
        self.device.click(POST_CLOSE)
        self.post_open(post_button)
        image = self.device.screenshot()
        ocr_post_number = Digit(OCR_POST_NUMBER, letter=(57, 58, 60), threshold=100,
                                alphabet='0123456789')

        if self.appear(ISLAND_WORK_COMPLETE, offset=(5, 5)):
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
        self.device.click(POST_CLOSE)

    def post_product_check(self):
        """检查岗位生产的产品（通用）"""
        for item in self.shop_items:
            if self.appear(item['post_action']):
                return item['name']
        return None

    def get_warehouse_counts(self):
        """获取仓库数量（通用）"""
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.device.click(self.filter_asset)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()

        for dish in self.shop_items:
            self.warehouse_counts[dish['name']] = self.ocr_item_quantity(image, dish['template'])
            if self.warehouse_counts[dish['name']]:
                print(f"{dish['name']}", self.warehouse_counts[dish['name']])

        return self.warehouse_counts

    def post_produce(self, post_id, product, number, time_var_name):
        """生产产品（通用）"""
        post_button = self.posts[post_id]['button']
        self.device.click(POST_CLOSE)
        self.post_open(post_button)
        self.device.screenshot()
        time_work = Duration(ISLAND_WORKING_TIME)
        selection = self.name_to_config[product]['selection']
        selection_check = self.name_to_config[product]['selection_check']

        if self.appear_then_click(ISLAND_POST_SELECT):
            self.select_character()
            self.appear_then_click(SELECT_UI_CONFIRM)
            self.select_product(selection, selection_check)

            for _ in range(number):
                self.device.click(POST_ADD_ONE)

            # 截图识别实际生产的数量
            self.device.screenshot()
            ocr_production_number = Digit(OCR_PRODUCTION_NUMBER, letter=(57, 58, 60), threshold=100,
                                          alphabet='0123456789')
            actual_number = ocr_production_number.ocr(self.device.image)

            self.device.click(POST_ADD_ORDER)
            self.wait_until_appear(ISLAND_POSTMANAGE_CHECK)

            # 滑动以看到岗位（使用post_produce_swipe_count配置）
            for _ in range(self.post_produce_swipe_count):
                self.post_manage_up_swipe(450)

            self.post_open(post_button)

            time_value = time_work.ocr(self.device.image)
            finish_time = datetime.now() + time_value
            setattr(self, time_var_name, finish_time)
            self.posts[post_id]['status'] = 'working'

            # 扣除前置材料（子类可覆盖）
            self.deduct_materials(product, actual_number)

            # 更新需求
            if product in self.to_post_products:
                self.to_post_products[product] -= actual_number
                if self.to_post_products[product] <= 0:
                    del self.to_post_products[product]

            print(f"已安排生产：{product} x{actual_number}")
            self.device.click(POST_CLOSE)

    def deduct_materials(self, product, number):
        """扣除前置材料（可被子类覆盖）"""
        if self.meal_compositions and product in self.meal_compositions:
            composition = self.meal_compositions[product]
            for material in composition['required']:
                if material in self.warehouse_counts:
                    self.warehouse_counts[material] -= number
                    print(f"扣除前置材料：{material} -{number}")

    def get_idle_posts(self):
        """获取空闲的岗位ID列表（通用）"""
        return [post_id for post_id, post_info in self.posts.items()
                if post_info['status'] == 'idle']

    # ============ 核心逻辑 ============

    def run(self):
        """运行店铺逻辑（通用）"""
        self.goto_postmanage()
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)
        self.post_manage_down_swipe(450)
        self.post_manage_down_swipe(450)

        # 滑动以看到岗位（使用post_manage_swipe_count配置）
        for _ in range(self.post_manage_swipe_count):
            self.post_manage_up_swipe(450)

        # 检查岗位状态
        post_count = getattr(self.config, self.config_post_number, 2)
        time_vars = []
        for i in range(post_count):
            time_var_name = f'{self.time_prefix}{i + 1}'
            time_vars.append(time_var_name)
            setattr(self, time_var_name, None)
            post_id = f'ISLAND_{self.shop_type.upper()}_POST{i + 1}'
            self.post_check(post_id, time_var_name)

        # 获取仓库数量
        self.get_warehouse_counts()

        self.ui_goto(page_island_postmanage)
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)

        # 滑动以看到岗位（使用post_manage_swipe_count配置）
        for _ in range(self.post_manage_swipe_count):
            self.post_manage_up_swipe(450)

        # 计算当前总库存
        total_subtract = Counter(self.post_check_meal)
        total_subtract.update(self.warehouse_counts)
        self.current_totals = {}
        for item in set(self.post_products.keys()) | set(total_subtract.keys()):
            self.current_totals[item] = total_subtract.get(item, 0)

        # 清空待生产列表
        self.to_post_products = {}

        # 根据状态进入不同阶段
        if not self.task_completed:
            # 检查是否所有基础需求都已完成
            all_basic_done = all(
                self.current_totals.get(item, 0) >= target
                for item, target in self.post_products.items()
            )

            if not all_basic_done:
                print("阶段：基础需求")
                # 计算基础需求
                for item, target in self.post_products.items():
                    current = self.current_totals.get(item, 0)
                    if current < target:
                        self.to_post_products[item] = target - current
            else:
                # 基础需求已完成，检查是否所有翻倍需求都已完成
                all_double_done = all(
                    self.current_totals.get(item, 0) >= target * 2
                    for item, target in self.post_products.items()
                )

                if not all_double_done:
                    print("阶段：翻倍需求")
                    self.doubled = True
                    # 计算翻倍需求
                    for item, target in self.post_products.items():
                        current = self.current_totals.get(item, 0)
                        double_target = target * 2
                        if current < double_target:
                            self.to_post_products[item] = double_target - current
                else:
                    # 翻倍需求已完成，检查是否有任务需求
                    print("阶段：任务需求")
                    if self.post_products_task:  # 如果有任务需求
                        self.process_task_requirements()
                    else:
                        # 没有任务需求，直接进入挂机模式
                        self.task_completed = True
                        print("没有设置任务需求，进入挂机模式")
                        self.process_away_cook()
        else:
            # 任务已完成，进入挂机模式
            print("阶段：挂机模式")
            self.process_away_cook()

        # 处理套餐分解
        if self.to_post_products:
            self.process_meal_requirements(self.to_post_products)

        # 安排生产
        if self.to_post_products:
            self.schedule_production()

        # 设置任务延迟
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

    def process_meal_requirements(self, source_products):
        """处理套餐分解（通用）"""
        result = {}

        # 处理套餐需求
        for meal, quantity in source_products.items():
            if meal in self.meal_compositions:
                composition = self.meal_compositions[meal]
                required_materials = composition['required']
                required_quantity = composition['quantity_per'] * quantity
                for req_material in required_materials:
                    if req_material in result:
                        result[req_material] += required_quantity
                    else:
                        result[req_material] = required_quantity

        # 添加非套餐需求
        for meal, quantity in source_products.items():
            if meal not in self.meal_compositions:
                if meal in result:
                    result[meal] += quantity
                else:
                    result[meal] = quantity

        self.to_post_products = result
        print(f"转换完成：source_products -> to_post_products")
        print(f"原始需求: {source_products}")
        print(f"生产计划: {self.to_post_products}")

    def process_task_requirements(self):
        """处理任务需求（通用）"""
        task_products = self.post_products_task.copy()

        # 使用 current_totals 减去库存
        for item, quantity in self.current_totals.items():
            if item in task_products:
                task_products[item] -= quantity
                if task_products[item] <= 0:
                    del task_products[item]

        if task_products:
            self.process_meal_requirements(task_products)
            print(f"任务需求剩余: {task_products}")
        else:
            self.to_post_products = {}
            self.task_completed = True
            print("任务需求已完成")

    def process_away_cook(self):
        """处理挂机模式（通用）"""
        away_cook = getattr(self.config, self.config_away_cook, None)
        if away_cook:
            self.to_post_products = {away_cook: 9999}
            print(f"挂机模式：生产 {away_cook}，无限数量")
        else:
            self.to_post_products = {}
            print("未设置挂机餐品")

    def schedule_production(self):
        """安排生产（通用）"""
        if not self.to_post_products:
            print("没有需要生产的餐品")
            return

        # 获取空闲岗位
        idle_posts = self.get_idle_posts()
        if not idle_posts:
            print("没有空闲的岗位")
            return

        # 按需求数量排序（需求大的优先）
        sorted_products = sorted(
            self.to_post_products.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 复制一份需求，用于遍历
        products_to_process = sorted_products.copy()

        for product, required_quantity in products_to_process:
            if required_quantity <= 0:
                continue

            # 重新获取空闲岗位（因为可能已经安排了）
            idle_posts = self.get_idle_posts()
            if not idle_posts:
                print("所有岗位都在工作中")
                break

            # 检查前置材料限制
            batch_size = min(5, required_quantity)
            batch_size = self.check_material_limits(product, batch_size)

            if batch_size <= 0:
                print(f"生产 {product} 的前置材料不足，跳过")
                continue

            # 分配生产
            post_id = idle_posts[0]
            post_num = post_id[-1]
            time_var_name = f'{self.time_prefix}{post_num}'

            self.post_produce(post_id, product, batch_size, time_var_name)

        print(f"生产安排完成，剩余需求: {self.to_post_products}")

    def check_material_limits(self, product, batch_size):
        """检查材料限制（可被子类覆盖）"""
        if product in self.meal_compositions:
            composition = self.meal_compositions[product]
            required_materials = composition['required']

            # 检查所有前置材料是否足够
            for material in required_materials:
                material_stock = self.warehouse_counts.get(material, 0)
                if material_stock < batch_size:
                    batch_size = min(batch_size, material_stock)

            # 如果检查特殊材料
            if hasattr(self, 'check_special_materials'):
                batch_size = self.check_special_materials(product, batch_size)

        return batch_size

    def check_special_materials(self, product, batch_size):
        """检查特殊材料（子类可覆盖）"""
        # 默认实现不检查特殊材料
        return batch_size
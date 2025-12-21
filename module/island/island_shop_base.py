from module.island.island import *
from collections import Counter
from datetime import datetime, timedelta
from module.handler.login import LoginHandler
from module.island.warehouse import *
import logging

logger = logging.getLogger(__name__)


class IslandShopBase(Island, WarehouseOCR):
    def __init__(self, config, device=None, task=None):
        # 分别初始化每个父类
        Island.__init__(self, config=config, device=device, task=task)
        WarehouseOCR.__init__(self)  # WarehouseOCR 可能不需要参数

        # 子类必须设置的属性
        self.shop_items = []  # 商品列表
        self.shop_type = ""  # 店铺类型：grill, teahouse, tailor, toolshop, furniture
        self.filter_asset = None  # 仓库筛选资产
        self.post_buttons = {}  # 岗位按钮
        self.time_prefix = "time_meal"  # 时间变量前缀

        # 角色选择配置
        self.chef_config = None

        # 通用属性
        self.high_priority_products = {}
        self.name_to_config = {}
        self.posts = {}
        self.post_check_meal = {}  # 岗位生产中的产品
        self.post_products = {}
        self.post_products_task = {}
        self.warehouse_counts = {}  # 仓库识别到的产品
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

    # ============ 角色选择方法 ============
    def select_character_for_shop(self):
        """根据chef_config选择角色"""
        if self.chef_config == "WorkerJuu":
            self.select_character()  # 默认WorkerJuu
        elif self.chef_config == "a":
            self.select_character_a()
        elif self.chef_config == "b":
            self.select_character_b()
        elif self.chef_config == "YingSwei":
            self.select_character(character_name="YingSwei")
        else:
            self.select_character()

    # ============ 通用方法 ============
    def post_check(self, post_id, time_var_name):
        """检查岗位状态（通用）"""
        post_button = self.posts[post_id]['button']
        self.post_close()
        self.post_open(post_button)
        image = self.device.screenshot()
        ocr_post_number = Digit(OCR_POST_NUMBER, letter=(57, 58, 60), threshold=100,
                                alphabet='0123456789')
        if self.appear(ISLAND_WORK_COMPLETE, offset=1):
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
            if product is not None:
                if product in self.post_check_meal:
                    self.post_check_meal[product] += number
                else:
                    self.post_check_meal[product] = number
        elif self.appear(ISLAND_POST_SELECT):
            self.posts[post_id]['status'] = 'idle'
            setattr(self, time_var_name, None)
        self.post_get_and_close()
        self.device.sleep(0.3)

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
        self.device.sleep(0.3)
        image = self.device.screenshot()

        for dish in self.shop_items:
            self.warehouse_counts[dish['name']] = self.ocr_item_quantity(image, dish['template'])
            if self.warehouse_counts[dish['name']]:
                print(f"{dish['name']}", self.warehouse_counts[dish['name']])
        return self.warehouse_counts

    def post_produce(self, post_id, product, number, time_var_name):
        """生产产品（通用）"""
        post_button = self.posts[post_id]['button']
        self.post_close()
        self.post_open(post_button)
        self.device.screenshot()
        time_work = Duration(ISLAND_WORKING_TIME)
        selection = self.name_to_config[product]['selection']
        selection_check = self.name_to_config[product]['selection_check']
        while 1:
            self.device.screenshot()
            if self.appear_then_click(ISLAND_POST_SELECT, offset=1):
                continue
            if self.appear(ISLAND_SELECT_CHARACTER_CHECK, offset=1):
                self.select_character_for_shop()
                self.appear_then_click(SELECT_UI_CONFIRM)
                continue
            if self.appear(ISAND_SELECT_PRODUCT_CHECK, offset=1):
                self.select_product(selection, selection_check)
                for _ in range(number - 1):
                    self.device.click(POST_ADD_ONE)
                self.device.click(POST_ADD_ORDER)
                break
        self.wait_until_appear(ISLAND_POSTMANAGE_CHECK)
        self.device.sleep(0.3)
        for _ in range(self.post_produce_swipe_count):
            self.post_manage_up_swipe(450)
        print(post_button)
        self.post_open(post_button)
        image = self.device.screenshot()
        ocr_post_number = Digit(OCR_POST_NUMBER, letter=(57, 58, 60), threshold=100,
                                alphabet='0123456789')
        actual_number = ocr_post_number.ocr(image)
        time_value = time_work.ocr(self.device.image)
        finish_time = datetime.now() + time_value
        setattr(self, time_var_name, finish_time)
        self.posts[post_id]['status'] = 'working'
        # 扣除前置材料（子类可覆盖）
        self.deduct_materials(product, actual_number)
        print(f"已安排生产：{product} x{actual_number}")
        self.post_close()
        # 返回实际生产数量
        return actual_number

    def deduct_materials(self, product, number):
        """扣除前置材料（包括套餐原材料）"""
        # 扣除套餐原材料
        if product in self.meal_compositions:
            composition = self.meal_compositions[product]
            quantity_per = composition.get('quantity_per', 1)
            for material in composition['required']:
                material_needed = number * quantity_per
                if material in self.warehouse_counts:
                    self.warehouse_counts[material] -= material_needed
                    print(f"扣除原材料：{material} -{material_needed} (用于制作 {product})")

    def get_idle_posts(self):
        """获取空闲的岗位ID列表（通用）"""
        return [post_id for post_id, post_info in self.posts.items()
                if post_info['status'] == 'idle']

    # ============ 核心逻辑 ============

    def run(self):
        self.island_error = False
        """运行店铺逻辑（通用）- 修改版本，支持高优先级"""
        self.goto_postmanage()
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.post_close()
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

        self.goto_postmanage()
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.post_close()
        self.post_manage_down_swipe(450)
        self.post_manage_down_swipe(450)

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

        # ============ 修复：高优先级任务处理 ============
        if self.high_priority_products:
            print("=== 处理高优先级任务 ===")

            # 清空待生产列表
            self.to_post_products = {}

            # 直接使用高优先级需求，不重复扣减库存
            for product, required_quantity in self.high_priority_products.items():
                self.to_post_products[product] = required_quantity

            # 清空高优先级任务（避免重复处理）
            self.high_priority_products = {}

            if self.to_post_products:
                # 处理套餐需求（只处理一次）
                self.to_post_products = self.process_meal_requirements(self.to_post_products)
                print(f"高优先级生产计划: {self.to_post_products}")

                # 安排高优先级任务的生产
                self.schedule_production()

                # 如果有安排了生产，直接设置延迟并返回
                finish_times = []
                for var in time_vars:
                    time_value = getattr(self, var)
                    if time_value is not None:
                        finish_times.append(time_value)
                if finish_times:
                    finish_times.sort()
                    self.config.task_delay(target=finish_times)
                    return
            else:
                print("所有高优先级任务已满足")
            print("=== 高优先级任务处理完成 ===")

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
            self.to_post_products = self.process_meal_requirements(self.to_post_products)

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
            next_check = datetime.now() + timedelta(hours=12)
            logger.info(f'没有任务需要安排，下次检查时间：{next_check.strftime("%H:%M")}')
            self.config.task_delay(target=[next_check])
        if self.island_error:
            from module.exception import GameBugError
            raise GameBugError("检测到岛屿ERROR1，需要重启")

    def process_meal_requirements(self, source_products):
        """修复版本：智能需求处理，避免重复扣减库存"""
        result = {}

        # 1. 将需求分为套餐需求和基础餐品需求
        meal_demands = {}
        base_demands = {}

        for product, quantity in source_products.items():
            if quantity <= 0:
                continue
            if product in self.meal_compositions:
                meal_demands[product] = quantity
            else:
                base_demands[product] = quantity

        # 2. 处理套餐需求
        material_needs = {}

        for meal, meal_quantity in meal_demands.items():
            # 计算套餐净需求（减去当前总库存）
            meal_stock = self.current_totals.get(meal, 0)
            net_meal_needed = max(0, meal_quantity - meal_stock)

            if net_meal_needed > 0:
                # 套餐需求加入结果
                result[meal] = net_meal_needed

                # 计算套餐所需原材料
                composition = self.meal_compositions[meal]
                for material in composition['required']:
                    material_needs[material] = material_needs.get(material, 0) + (
                            net_meal_needed * composition.get('quantity_per', 1)
                    )

        # 3. 处理基础需求，并合并原材料需求（一次性计算）
        for base_product, base_quantity in base_demands.items():
            # 获取当前库存
            warehouse_stock = self.warehouse_counts.get(base_product, 0)

            # 总需求 = 基础需求 + 套餐原材料需求（如果该产品是原材料）
            total_needed = base_quantity
            if base_product in material_needs:
                total_needed += material_needs[base_product]
                # 从material_needs中移除，避免重复计算
                del material_needs[base_product]

            # 计算净需求（一次性扣减库存）
            net_needed = max(0, total_needed - warehouse_stock)
            if net_needed > 0:
                result[base_product] = net_needed

        # 4. 处理剩余的原材料需求（非基础产品的原材料）
        for material, material_quantity in material_needs.items():
            warehouse_stock = self.warehouse_counts.get(material, 0)
            net_needed = max(0, material_quantity - warehouse_stock)
            if net_needed > 0:
                result[material] = net_needed

        # 5. 考虑特殊材料限制
        result = self.apply_special_material_constraints(result)

        print(f"需求处理结果:")
        print(f"  原始需求: {source_products}")
        print(f"  生产计划: {result}")

        return result

    def get_max_producible(self, product, requested_quantity):
        """获取最大可生产数量"""
        max_producible = requested_quantity

        # 1. 如果是套餐，检查原材料库存
        if product in self.meal_compositions:
            composition = self.meal_compositions[product]
            for material in composition['required']:
                # 使用仓库实际库存
                material_stock = self.warehouse_counts.get(material, 0)
                quantity_per = composition.get('quantity_per', 1)
                if quantity_per == 0:
                    continue
                max_by_material = material_stock // quantity_per
                max_producible = min(max_producible, max_by_material)
                if max_by_material <= 0:
                    print(f"  {product} 缺少原材料: {material}")
                    return 0

        # 2. 检查岗位数量限制（每个岗位最多5个）
        max_producible = min(max_producible, 5)

        # 3. 检查特殊材料（被子类覆盖）
        max_producible = self.check_special_materials(product, max_producible)

        return max_producible

    def apply_special_material_constraints(self, requirements):
        """应用特殊材料限制（需求阶段）。子类可覆盖此方法。

        Args:
            requirements: 字典，{产品名: 需求数量}

        Returns:
            调整后的需求字典
        """
        return requirements

    def process_task_requirements(self):
        """修复：处理任务需求"""
        task_products = self.post_products_task.copy()

        # 使用 current_totals 减去库存
        for item, target_quantity in task_products.items():
            current_quantity = self.current_totals.get(item, 0)
            still_needed = target_quantity - current_quantity

            if still_needed > 0:
                self.to_post_products[item] = still_needed

        if self.to_post_products:
            print(f"任务需求剩余: {self.to_post_products}")
        else:
            self.task_completed = True
            print("任务需求已完成")

    def process_away_cook(self):
        """处理挂机模式（通用）"""
        away_cook = getattr(self.config, self.config_away_cook, None)

        # 检查 away_cook 是否有效
        if away_cook and away_cook != "None" and away_cook in self.name_to_config:
            self.to_post_products = {away_cook: 9999}
            print(f"挂机模式：生产 {away_cook}，无限数量")
        else:
            self.to_post_products = {}
            if away_cook is None or away_cook == "None":
                print("挂机模式：未设置挂机餐品，跳过生产")
            elif away_cook not in self.name_to_config:
                print(f"挂机模式：餐品 '{away_cook}' 不在商品列表中，跳过生产")
            else:
                print("挂机模式：跳过生产")

    def schedule_production(self):
        """修复：智能安排生产，利用所有空闲岗位"""
        if not self.to_post_products:
            print("没有需要生产的餐品")
            return

        # 获取空闲岗位
        idle_posts = self.get_idle_posts()
        if not idle_posts:
            print("没有空闲的岗位")
            return

        # 检查是否为挂机模式（无限数量生产）
        is_away_cook_mode = False
        away_cook_product = None
        for product, quantity in self.to_post_products.items():
            if quantity == 9999:  # 挂机模式的标识
                is_away_cook_mode = True
                away_cook_product = product
                break

        if is_away_cook_mode:
            print(f"挂机模式：为所有空闲岗位安排生产 {away_cook_product}")
            # 为每个空闲岗位安排生产
            for post_id in idle_posts:
                # 检查材料限制
                batch_size = min(5, 9999)  # 最大5个
                batch_size = self.get_max_producible(away_cook_product, batch_size)

                if batch_size <= 0:
                    print(f"生产 {away_cook_product} 的前置材料不足，跳过岗位 {post_id}")
                    continue

                # 分配生产
                post_num = post_id[-1]
                time_var_name = f'{self.time_prefix}{post_num}'
                self.post_produce(post_id, away_cook_product, batch_size, time_var_name)

            print("挂机模式：已为所有空闲岗位安排生产")
            return

        # 非挂机模式：处理所有产品需求
        products_to_process = list(self.to_post_products.items())

        # 如果有多个产品需求，按优先级排序
        if len(products_to_process) > 1:
            def production_priority(item):
                product, quantity = item
                if product in self.meal_compositions:
                    # 检查套餐原材料是否充足
                    max_producible = self.get_max_producible(product, min(5, quantity))
                    if max_producible > 0:
                        return 0  # 最高优先级：可立即生产的套餐
                    else:
                        return 2  # 低优先级：原材料不足的套餐
                else:
                    # 基础餐品：检查是否可以生产
                    max_producible = self.get_max_producible(product, min(5, quantity))
                    if max_producible > 0:
                        return 1  # 中等优先级：可生产的基础餐品
                    else:
                        return 3  # 最低优先级：无法生产的基础餐品

            products_to_process = sorted(products_to_process, key=production_priority)

        # 为每个空闲岗位分配生产任务
        post_index = 0
        total_idle_posts = len(idle_posts)

        for product, required_quantity in products_to_process:
            if required_quantity <= 0:
                continue

            # 获取当前还有需求的量
            remaining_need = self.to_post_products.get(product, 0)
            if remaining_need <= 0:
                continue

            # 为每个空闲岗位分配生产（直到需求满足或没有空闲岗位）
            while remaining_need > 0 and post_index < total_idle_posts:
                post_id = idle_posts[post_index]

                # 计算最大可生产数量
                max_producible = self.get_max_producible(product, min(5, remaining_need))

                if max_producible <= 0:
                    print(f"生产 {product} 的材料不足，跳过")
                    break

                # 分配生产
                post_num = post_id[-1]
                time_var_name = f'{self.time_prefix}{post_num}'

                # 安排生产并获取实际生产数量
                actual_number = self.post_produce(post_id, product, max_producible, time_var_name)

                # 更新需求
                if product in self.to_post_products:
                    self.to_post_products[product] -= actual_number
                    if self.to_post_products[product] <= 0:
                        del self.to_post_products[product]

                # 更新剩余需求
                remaining_need = self.to_post_products.get(product, 0)

                # 移动到下一个岗位
                post_index += 1

            # 如果所有岗位都已分配，退出循环
            if post_index >= total_idle_posts:
                break

        print(f"生产安排完成，剩余需求: {self.to_post_products}")

        # 如果还有空闲岗位且没有其他需求，可以安排挂机产品
        if post_index < total_idle_posts and not self.to_post_products:
            # 检查是否有挂机产品配置
            away_cook = getattr(self.config, self.config_away_cook, None)
            if away_cook and away_cook != "None" and away_cook in self.name_to_config:
                print(f"仍有空闲岗位，安排挂机产品: {away_cook}")

                # 为剩余的空闲岗位安排挂机生产
                for i in range(post_index, total_idle_posts):
                    post_id = idle_posts[i]

                    # 检查材料限制
                    batch_size = min(5, 9999)
                    batch_size = self.get_max_producible(away_cook, batch_size)

                    if batch_size <= 0:
                        print(f"生产 {away_cook} 的前置材料不足，跳过岗位 {post_id}")
                        continue

                    # 分配生产
                    post_num = post_id[-1]
                    time_var_name = f'{self.time_prefix}{post_num}'
                    self.post_produce(post_id, away_cook, batch_size, time_var_name)

    def check_material_limits(self, product, batch_size):
        """检查材料限制（通用）"""
        return self.get_max_producible(product, batch_size)

    def check_special_materials(self, product, batch_size):
        """检查特殊材料（子类可覆盖）"""
        # 默认实现不检查特殊材料
        return batch_size

    def add_high_priority_product(self, product, quantity):
        """添加高优先级餐品（子类调用）"""
        if product in self.high_priority_products:
            self.high_priority_products[product] += quantity
        else:
            self.high_priority_products[product] = quantity
        print(f"添加高优先级任务: {product} x{quantity}")
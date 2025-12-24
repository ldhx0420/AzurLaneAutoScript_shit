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
        self.name_to_config = {}
        self.posts = {}
        self.post_check_meal = {}  # 岗位生产中的产品
        self.post_products = {}
        self.warehouse_counts = {}  # 仓库识别到的产品
        self.to_post_products = {}
        self.current_totals = {}

        # 特殊材料（子类可覆盖）
        self.special_materials = {}

        # 套餐组成（子类可覆盖）
        self.meal_compositions = {}

        # 配置前缀（子类可覆盖）
        self.config_meal_prefix = "Island_Meal"
        self.config_number_prefix = "Island_MealNumber"
        self.config_away_cook = "IslandNextTask_AwayCook"
        self.config_post_number = "Island_PostNumber"

        # 滑动配置（子类可覆盖）
        self.post_manage_swipe_count = 1  # 默认滑动1次450

    def setup_config(self, config_meal_prefix, config_number_prefix,
                     config_away_cook, config_post_number):
        """从配置中读取餐品需求"""
        # 设置配置前缀
        self.config_meal_prefix = config_meal_prefix
        self.config_number_prefix = config_number_prefix
        self.config_away_cook = config_away_cook
        self.config_post_number = config_post_number

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
            return self.select_character()  # 默认WorkerJuu
        elif self.chef_config == "a":
            return self.select_character_a()
        elif self.chef_config == "b":
            return self.select_character_b()
        elif self.chef_config == "YingSwei":
            return self.select_character(character_name="YingSwei")
        else:
            return self.select_character()

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
        self.ui_goto(page_island_warehouse_filter,get_ship=False)
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
                if self.select_character_for_shop():
                    self.appear_then_click(SELECT_UI_CONFIRM)
                continue
            if self.appear(ISLAND_SELECT_PRODUCT_CHECK, offset=1):
                if self.select_product(selection, selection_check):
                    for _ in range(number - 1):
                        self.device.click(POST_ADD_ONE)
                    self.device.sleep(0.3)
                    self.device.click(POST_ADD_ORDER)
                    break
                continue
        self.wait_until_appear(ISLAND_POSTMANAGE_CHECK)
        self.device.sleep(0.3)
        self.post_manage_swipe(self.post_manage_swipe_count)
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
        """运行店铺逻辑（简化版本）- 只保留基础模式和常驻餐品"""
        self.goto_postmanage()
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.post_close()
        self.post_manage_swipe(self.post_manage_swipe_count)
        # 检查岗位状态
        post_count = getattr(self.config, self.config_post_number, 2)
        time_vars = []
        for i in range(post_count):
            time_var_name = f'{self.time_prefix}{i + 1}'
            time_vars.append(time_var_name)
            setattr(self, time_var_name, None)
            post_id = f'ISLAND_{self.shop_type.upper()}_POST{i + 1}'
            self.post_check(post_id, time_var_name)
        if self.get_idle_posts():
            self.get_warehouse_counts()
            self.goto_postmanage()
            self.post_manage_mode(POST_MANAGE_PRODUCTION)
            self.post_close()
            self.post_manage_swipe(self.post_manage_swipe_count)

            # 计算当前总库存
            total_subtract = Counter(self.post_check_meal)
            total_subtract.update(self.warehouse_counts)
            self.current_totals = {}
            for item in set(self.post_products.keys()) | set(total_subtract.keys()):
                self.current_totals[item] = total_subtract.get(item, 0)

            # ============ 调试信息 ============
            print(f"=== 调试信息 ===")
            print(f"仓库库存: {self.warehouse_counts}")
            print(f"生产中库存: {self.post_check_meal}")
            print(f"当前总库存: {self.current_totals}")
            print(f"基础需求配置: {self.post_products}")
            print("===============")

            # 清空待生产列表
            self.to_post_products = {}

            # ============ 基础需求计算 ============
            print("阶段：基础需求")
            # 计算基础需求
            for item, target in self.post_products.items():
                current = self.current_totals.get(item, 0)
                if current < target:
                    self.to_post_products[item] = target - current

            # ============ 处理套餐分解 ============
            if self.to_post_products:
                self.to_post_products = self.process_meal_requirements(self.to_post_products)
                print(f"基础需求生产计划: {self.to_post_products}")

            # ============ 安排生产 ============
            if self.to_post_products:
                self.schedule_production()
            else:
                # 如果生产列表为空，检查是否有常驻餐品
                print("基础需求已满足，检查常驻餐品")
                self.process_away_cook()

                # 如果有常驻餐品，安排生产
                if self.to_post_products:
                    self.schedule_production()
                else:
                    print("没有常驻餐品设置，保持空闲状态")

        # ============ 设置任务延迟 ============
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
        """处理套餐需求（修正版）"""
        print(f"=== 进入process_meal_requirements ===")
        print(f"传入的需求: {source_products}")

        result = {}

        # 1. 将需求分为套餐需求和基础餐品需求
        meal_demands = {}
        base_demands = {}

        for product, quantity in source_products.items():
            if quantity <= 0:
                continue
            if product in self.meal_compositions:
                meal_demands[product] = quantity
                print(f"  识别为套餐: {product} x{quantity}")
            else:
                base_demands[product] = quantity
                print(f"  识别为基础餐品: {product} x{quantity}")

        print(f"套餐需求: {meal_demands}")
        print(f"基础需求: {base_demands}")

        # 2. 处理套餐需求 - 直接加入结果（套餐可以直接生产）
        # 注意：这里传入的已经是净需求，不需要再扣除库存
        for meal, meal_quantity in meal_demands.items():
            if meal_quantity > 0:
                result[meal] = meal_quantity
                print(f"  套餐直接生产: {meal} x{meal_quantity}")

        # 3. 处理基础需求（这些可能是套餐的原材料）
        material_needs = {}

        # 计算所有套餐需要的原材料总量
        for meal, meal_quantity in meal_demands.items():
            if meal_quantity > 0 and meal in self.meal_compositions:
                composition = self.meal_compositions[meal]
                for material in composition['required']:
                    needed = meal_quantity * composition.get('quantity_per', 1)
                    material_needs[material] = material_needs.get(material, 0) + needed
                    print(f"  套餐 {meal} 需要原材料: {material} x{needed}")

        print(f"原材料总需求: {material_needs}")

        # 4. 处理基础需求，并考虑原材料需求
        for base_product, base_quantity in base_demands.items():
            print(f"  处理基础餐品 {base_product}: 基础需求={base_quantity}")

            # 总需求 = 基础需求 + 套餐原材料需求
            total_needed = base_quantity
            if base_product in material_needs:
                total_needed += material_needs[base_product]
                print(f"    合并原材料需求: +{material_needs[base_product]} = {total_needed}")
                # 从material_needs中移除，避免重复计算
                del material_needs[base_product]

            # 检查当前库存（包括生产中的）
            current_stock = self.current_totals.get(base_product, 0)
            print(f"    当前总库存: {current_stock}")

            # 计算净需求
            net_needed = max(0, total_needed - current_stock)
            if net_needed > 0:
                result[base_product] = net_needed
                print(f"    添加到生产计划: {base_product} x{net_needed}")
            else:
                print(f"    库存充足，不需要生产")

        # 5. 处理剩余的原材料需求（这些基础餐品不在基础需求列表中）
        for material, material_quantity in material_needs.items():
            print(f"  处理剩余原材料 {material}: 需求={material_quantity}")

            current_stock = self.current_totals.get(material, 0)
            print(f"    当前总库存: {current_stock}")

            net_needed = max(0, material_quantity - current_stock)
            if net_needed > 0:
                result[material] = net_needed
                print(f"    添加到生产计划: {material} x{net_needed}")
            else:
                print(f"    库存充足，不需要生产")

        # 6. 考虑特殊材料限制
        result = self.apply_special_material_constraints(result)

        print(f"最终生产计划: {result}")
        print(f"=== 离开process_meal_requirements ===")

        return result

    def get_max_producible(self, product, requested_quantity):
        """获取最大可生产数量（修正版）"""
        max_producible = requested_quantity

        # 1. 如果是套餐，检查原材料库存
        if product in self.meal_compositions:
            composition = self.meal_compositions[product]
            for material in composition['required']:
                # 使用仓库实际库存（生产会消耗仓库库存）
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

    def process_away_cook(self):
        """处理常驻餐品"""
        away_cook = getattr(self.config, self.config_away_cook, None)

        # 检查 away_cook 是否有效
        if away_cook and away_cook != "None" and away_cook in self.name_to_config:
            self.to_post_products = {away_cook: 9999}
            print(f"常驻餐品模式：生产 {away_cook}")
        else:
            self.to_post_products = {}
            if away_cook is None or away_cook == "None":
                print("未设置常驻餐品，保持空闲")
            elif away_cook not in self.name_to_config:
                print(f"常驻餐品 '{away_cook}' 不在商品列表中，保持空闲")

    def schedule_production(self):
        """安排生产，利用所有空闲岗位"""
        if not self.to_post_products:
            print("没有需要生产的餐品")
            return

        # 获取空闲岗位
        idle_posts = self.get_idle_posts()
        if not idle_posts:
            print("没有空闲的岗位")
            return

        # 检查是否为常驻餐品模式（无限数量生产）
        is_away_cook_mode = False
        away_cook_product = None
        for product, quantity in self.to_post_products.items():
            if quantity == 9999:  # 常驻餐品模式的标识
                is_away_cook_mode = True
                away_cook_product = product
                break

        if is_away_cook_mode:
            print(f"常驻餐品模式：为所有空闲岗位安排生产 {away_cook_product}")
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

            print("常驻餐品模式：已为所有空闲岗位安排生产")
            return

        # 非常驻餐品模式：处理所有产品需求
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

    def check_special_materials(self, product, batch_size):
        """检查特殊材料（子类可覆盖）"""
        # 默认实现不检查特殊材料
        return batch_size
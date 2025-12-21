from module.island_teahouse.assets import *
from module.island.island_shop_base import IslandShopBase
from module.island.assets import *
from module.ui.page import *
from collections import Counter
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)



class IslandTeahouse(IslandShopBase):
    def __init__(self, config, device=None, task=None):
        super().__init__(config=config, device=device, task=task)

        # 设置店铺类型
        self.shop_type = "teahouse"
        self.time_prefix = "time_tea"
        self.chef_config = self.config.IslandTeahouse_Chef

        # 设置商品列表
        self.shop_items = [
            {'name': 'apple_juice', 'template': TEMPLATE_APPLE_JUICE, 'var_name': 'apple_juice',
             'selection': SELECT_APPLE_JUICE, 'selection_check': SELECT_APPLE_JUICE_CHECK,
             'post_action': POST_APPLE_JUICE},
            {'name': 'banana_mango', 'template': TEMPLATE_BANANA_MANGO, 'var_name': 'banana_mango',
             'selection': SELECT_BANANA_MANGO, 'selection_check': SELECT_BANANA_MANGO_CHECK,
             'post_action': POST_BANANA_MANGO},
            {'name': 'honey_lemon', 'template': TEMPLATE_HONEY_LEMON, 'var_name': 'honey_lemon',
             'selection': SELECT_HONEY_LEMON, 'selection_check': SELECT_HONEY_LEMON_CHECK,
             'post_action': POST_HONEY_LEMON},
            {'name': 'strawberry_lemon', 'template': TEMPLATE_STRAWBERRY_LEMON, 'var_name': 'strawberry_lemon',
             'selection': SELECT_STRAWBERRY_LEMON, 'selection_check': SELECT_STRAWBERRY_LEMON_CHECK,
             'post_action': POST_STRAWBERRY_LEMON},
            {'name': 'strawberry_honey', 'template': TEMPLATE_STRAWBERRY_HONEY, 'var_name': 'strawberry_honey',
             'selection': SELECT_STRAWBERRY_HONEY, 'selection_check': SELECT_STRAWBERRY_HONEY_CHECK,
             'post_action': POST_STRAWBERRY_HONEY},
            {'name': 'floral_fruity', 'template': TEMPLATE_FLORAL_FRUITY, 'var_name': 'floral_fruity',
             'selection': SELECT_FLORAL_FRUITY, 'selection_check': SELECT_FLORAL_FRUITY_CHECK,
             'post_action': POST_FLORAL_FRUITY},
            {'name': 'fruit_paradise', 'template': TEMPLATE_FRUIT_PARADISE, 'var_name': 'fruit_paradise',
             'selection': SELECT_FRUIT_PARADISE, 'selection_check': SELECT_FRUIT_PARADISE_CHECK,
             'post_action': POST_FRUIT_PARADISE},
            {'name': 'lavender_tea', 'template': TEMPLATE_LAVENDER_TEA, 'var_name': 'lavender_tea',
             'selection': SELECT_LAVENDER_TEA, 'selection_check': SELECT_LAVENDER_TEA_CHECK,
             'post_action': POST_LAVENDER_TEA},
            {'name': 'sunny_honey', 'template': TEMPLATE_SUNNY_HONEY, 'var_name': 'sunny_honey',
             'selection': SELECT_SUNNY_HONEY, 'selection_check': SELECT_SUNNY_HONEY_CHECK,
             'post_action': POST_SUNNY_HONEY},
        ]

        # 设置套餐组成
        self.meal_compositions = {
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

        # 设置岗位按钮
        self.post_buttons = {
            'ISLAND_TEAHOUSE_POST1': ISLAND_TEAHOUSE_POST1,
            'ISLAND_TEAHOUSE_POST2': ISLAND_TEAHOUSE_POST2
        }

        # 设置筛选资产
        self.filter_asset = FILTER_ISLAND_TEAHOUSE

        # 设置配置前缀
        self.setup_config(
            config_meal_prefix="IslandTeahouse_Meal",
            config_number_prefix="IslandTeahouse_MealNumber",
            config_task_prefix="IslandTeahouseNextTask_MealTask",
            config_task_number_prefix="IslandTeahouseNextTask_MealTaskNumber",
            config_post_number="IslandTeahouse_PostNumber",
            config_away_cook="IslandTeahouseNextTask_AwayCook"
        )

        # 特殊材料：蜂蜜
        self.fresh_honey = 0
        self.initialize_shop()

    def get_warehouse_counts(self):
        """覆盖：获取仓库数量，包括蜂蜜"""
        # 先调用父类方法获取基础库存
        super().get_warehouse_counts()

        # 额外获取蜂蜜数量
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_BASIC)
        self.appear_then_click(FILTER_OTHER)
        self.appear_then_click(FILTER_CONFIRM)
        self.device.sleep(0.3)
        image = self.device.screenshot()
        self.fresh_honey = self.ocr_item_quantity(image, TEMPLATE_FRESH_HONEY)
        print(f"蜂蜜数量: {self.fresh_honey}")

        # 将蜂蜜库存存入warehouse_counts，便于统一处理
        self.warehouse_counts['fresh_honey'] = self.fresh_honey

        return self.warehouse_counts

    def check_special_materials(self, product, batch_size):
        """覆盖：检查特殊材料（蜂蜜）限制"""
        if batch_size <= 0:
            return 0

        # 蜂蜜柠檬需要检查蜂蜜
        if product == 'honey_lemon':
            max_by_honey = min(batch_size, self.fresh_honey)
            return max_by_honey

        # sunny_honey需要检查蜂蜜（通过honey_lemon）
        if product == 'sunny_honey':
            # sunny_honey需要honey_lemon，每个需要1个蜂蜜
            max_by_honey = min(batch_size, self.fresh_honey)
            return max_by_honey

        return batch_size

    def deduct_materials(self, product, number):
        """覆盖：扣除前置材料，包括蜂蜜和套餐原材料"""
        # 先调用父类方法扣除套餐原材料
        super().deduct_materials(product, number)

        # 蜂蜜柠檬需要扣除蜂蜜
        if product == 'honey_lemon':
            honey_needed = number
            self.fresh_honey = max(0, self.fresh_honey - honey_needed)
            if 'fresh_honey' in self.warehouse_counts:
                self.warehouse_counts['fresh_honey'] = self.fresh_honey
            print(f"扣除蜂蜜：fresh_honey -{honey_needed}")

        # sunny_honey套餐中的honey_lemon也需要扣除蜂蜜
        if product == 'sunny_honey':
            # sunny_honey需要honey_lemon，每个需要1个蜂蜜
            honey_needed = number
            self.fresh_honey = max(0, self.fresh_honey - honey_needed)
            if 'fresh_honey' in self.warehouse_counts:
                self.warehouse_counts['fresh_honey'] = self.fresh_honey
            print(f"扣除蜂蜜（用于sunny_honey）：fresh_honey -{honey_needed}")

    def apply_special_material_constraints(self, requirements):
        """覆盖：根据蜂蜜库存调整需求"""
        result = requirements.copy()

        # 首先处理honey_lemon的需求
        if 'honey_lemon' in result and result['honey_lemon'] > 0:
            honey_lemon_needed = result['honey_lemon']
            max_honey_lemon = min(honey_lemon_needed, self.fresh_honey)

            if max_honey_lemon < honey_lemon_needed:
                print(f"蜂蜜不足：honey_lemon需求从{honey_lemon_needed}调整为{max_honey_lemon}")

            result['honey_lemon'] = max_honey_lemon

        # 处理sunny_honey的需求
        if 'sunny_honey' in result and result['sunny_honey'] > 0:
            sunny_honey_needed = result['sunny_honey']

            # sunny_honey需要honey_lemon，每个需要1个蜂蜜
            # 但honey_lemon的需求可能已经在上面调整过
            honey_lemon_for_sunny = sunny_honey_needed

            # 计算可用于sunny_honey的蜂蜜
            # 减去已经分配给honey_lemon的蜂蜜
            honey_allocated = result.get('honey_lemon', 0)
            honey_remaining = max(0, self.fresh_honey - honey_allocated)

            max_sunny_honey = min(sunny_honey_needed, honey_remaining)

            if max_sunny_honey < sunny_honey_needed:
                print(f"蜂蜜不足：sunny_honey需求从{sunny_honey_needed}调整为{max_sunny_honey}")

            result['sunny_honey'] = max_sunny_honey

        return result

    # ============ 新增方法：处理蜂蜜任务 ============
    def process_honey_task(self):
        """处理蜂蜜任务 - 强制生产消耗strawberry_lemon"""
        if not (self.config.IslandTeahouse_SunnyHoney and self.fresh_honey > 0):
            return

        print("=== 检测到蜂蜜任务 ===")

        # 获取库存
        strawberry_lemon_stock = self.warehouse_counts.get('strawberry_lemon', 0)
        honey_lemon_stock = self.warehouse_counts.get('honey_lemon', 0)
        current_sunny_honey = self.warehouse_counts.get('sunny_honey', 0)

        print(
            f"当前库存: sunny_honey={current_sunny_honey}, strawberry_lemon={strawberry_lemon_stock}, honey_lemon={honey_lemon_stock}, honey={self.fresh_honey}")

        # 计算需要生产的数量（强制生产，不考虑现有sunny_honey库存）
        # 1. 蜂蜜限制
        max_by_honey = self.fresh_honey

        # 2. 原材料限制
        max_by_strawberry = strawberry_lemon_stock
        max_by_honey_lemon = honey_lemon_stock

        # 3. 目标库存控制 - 避免过多生产strawberry_lemon
        strawberry_lemon_target = 20  # strawberry_lemon的目标库存
        if strawberry_lemon_stock > strawberry_lemon_target:
            max_to_consume = strawberry_lemon_stock - strawberry_lemon_target
            max_by_strawberry_target = max_to_consume
        else:
            max_by_strawberry_target = 9999

        # 4. 计算最大可生产数量
        max_producible = min(
            max_by_honey,
            max_by_strawberry,
            max_by_honey_lemon,
            max_by_strawberry_target,
            10  # 2个岗位，每个最多5个
        )

        if max_producible > 0:
            # 强制生产，不考虑现有sunny_honey库存
            # 但需要检查实际需求：如果库存已经很多，可以少生产一些
            # 这里设置一个上限：最多生产5个
            actual_production = min(max_producible, 5)

            # 添加到高优先级任务
            self.add_high_priority_product('sunny_honey', actual_production)
            print(f"蜂蜜任务：安排生产sunny_honey x{actual_production}来消耗strawberry_lemon")
            print(f"  当前sunny_honey库存: {current_sunny_honey}")
            print(f"  最大可生产: {max_producible}")
            print(f"  实际安排生产: {actual_production}")
        else:
            print("蜂蜜任务：无法生产sunny_honey（材料不足）")

    # 重写process_meal_requirements，修复套餐需求计算
    def process_meal_requirements(self, source_products):
        """覆盖：处理套餐需求，修复库存计算"""
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
            # 对于高优先级任务（蜂蜜任务），不扣除现有库存，强制生产
            if meal == 'sunny_honey' and meal_quantity > 0:
                # 强制生产指定的数量，不扣除库存
                net_meal_needed = meal_quantity
            else:
                # 正常计算净需求
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

        # 3. 处理基础需求，并合并原材料需求
        for base_product, base_quantity in base_demands.items():
            # 使用仓库实际库存计算基础餐品净需求
            base_stock = self.warehouse_counts.get(base_product, 0)
            net_base_needed = max(0, base_quantity - base_stock)

            # 如果基础餐品也是套餐的原材料，需要合并需求
            if base_product in material_needs:
                # 总需求 = 基础需求 + 套餐原材料需求
                total_needed = net_base_needed + material_needs[base_product]
                # 重新计算净需求（减去仓库库存）
                net_total_needed = max(0, total_needed - base_stock)
                if net_total_needed > 0:
                    result[base_product] = net_total_needed
                # 从material_needs中移除，避免重复计算
                del material_needs[base_product]
            elif net_base_needed > 0:
                result[base_product] = net_base_needed

        # 4. 处理剩余的原材料需求
        for material, material_quantity in material_needs.items():
            # 使用仓库实际库存计算原材料净需求
            material_stock = self.warehouse_counts.get(material, 0)
            net_material_needed = max(0, material_quantity - material_stock)
            if net_material_needed > 0:
                result[material] = net_material_needed

        # 5. 考虑特殊材料限制（蜂蜜）
        result = self.apply_special_material_constraints(result)

        print(f"需求处理结果:")
        print(f"  原始需求: {source_products}")
        print(f"  生产计划: {result}")

        return result

    # 重写run方法，修复执行流程
    def run(self):
        self.island_error = False
        """运行店铺逻辑（通用）- 修复版本"""
        # 第一步：检查岗位状态
        self.goto_postmanage()
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.post_close()
        self.post_manage_down_swipe(450)
        self.post_manage_down_swipe(450)

        # 滑动以看到岗位
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

        # 第二步：获取仓库数量（包括蜂蜜）
        self.get_warehouse_counts()

        # 第三步：计算当前总库存
        total_subtract = Counter(self.post_check_meal)
        total_subtract.update(self.warehouse_counts)
        self.current_totals = {}
        for item in set(self.post_products.keys()) | set(total_subtract.keys()):
            self.current_totals[item] = total_subtract.get(item, 0)

        # 第四步：处理蜂蜜任务（必须在这里处理，否则库存数据不完整）
        self.process_honey_task()

        # 第五步：回到岗位管理界面，准备安排生产
        self.goto_postmanage()
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.post_close()
        self.post_manage_down_swipe(450)
        self.post_manage_down_swipe(450)

        # 滑动以看到岗位
        for _ in range(self.post_manage_swipe_count):
            self.post_manage_up_swipe(450)

        # 清空待生产列表
        self.to_post_products = {}

        # ============ 处理高优先级任务 ============
        if self.high_priority_products:
            print("=== 处理高优先级任务 ===")

            # 直接使用高优先级需求
            for product, required_quantity in self.high_priority_products.items():
                self.to_post_products[product] = required_quantity

            # 清空高优先级任务
            self.high_priority_products = {}

            if self.to_post_products:
                # 处理套餐需求
                self.to_post_products = self.process_meal_requirements(self.to_post_products)
                print(f"高优先级生产计划: {self.to_post_products}")

                # 安排高优先级任务的生产
                self.schedule_production()

                # 检查是否所有高优先级任务都已完成
                if not self.to_post_products:
                    print("所有高优先级任务已完成")
                else:
                    print(f"高优先级任务未完成，剩余需求: {self.to_post_products}")

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

        # 第六步：根据状态进入不同阶段
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

        # 第七步：处理套餐分解
        if self.to_post_products:
            self.to_post_products = self.process_meal_requirements(self.to_post_products)

        # 第八步：安排生产
        if self.to_post_products:
            self.schedule_production()

        # 第九步：设置任务延迟
        finish_times = []
        for var in time_vars:
            time_value = getattr(self, var)
            if time_value is not None:
                finish_times.append(time_value)
        if finish_times:
            finish_times.sort()
            self.config.task_delay(target=finish_times)
        else:
            from datetime import timedelta
            next_check = datetime.now() + timedelta(hours=12)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'没有任务需要安排，下次检查时间：{next_check.strftime("%H:%M")}')
            self.config.task_delay(target=[next_check])

        if self.island_error:
            from module.exception import GameBugError
            raise GameBugError("检测到岛屿ERROR1，需要重启")


if __name__ == "__main__":
    az = IslandTeahouse('alas', task='Alas')
    az.device.screenshot()
    az.run()
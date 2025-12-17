from module.island_juu_eatery.assets import *
from module.island.island_shop_base import IslandShopBase
from module.island.assets import *
from module.ui.page import *

class IslandJuuEatery(IslandShopBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置店铺类型
        self.shop_type = "juu_eatery"
        self.time_prefix = "time_eatery"
        self.chef_config = self.config.IslandJuuEatery_Chef
        # 设置商品列表
        self.shop_items = [
            {'name': 'apple_pie', 'template': TEMPLATE_APPLE_PIE, 'var_name': 'apple_pie',
             'selection': SELECT_APPLE_PIE, 'selection_check': SELECT_APPLE_PIE_CHECK,
             'post_action': POST_APPLE_PIE},
            {'name': 'corn_cup', 'template': TEMPLATE_CORN_CUP, 'var_name': 'corn_cup',
             'selection': SELECT_CORN_CUP, 'selection_check': SELECT_CORN_CUP_CHECK,
             'post_action': POST_CORN_CUP},
            {'name': 'orange_pie', 'template': TEMPLATE_ORANGE_PIE, 'var_name': 'orange_pie',
             'selection': SELECT_ORANGE_PIE, 'selection_check': SELECT_ORANGE_PIE_CHECK,
             'post_action': POST_ORANGE_PIE},
            {'name': 'banana_crepe', 'template': TEMPLATE_BANANA_CREPE, 'var_name': 'banana_crepe',
             'selection': SELECT_BANANA_CREPE, 'selection_check': SELECT_BANANA_CREPE_CHECK,
             'post_action': POST_BANANA_CREPE},
            {'name': 'orchard_duo', 'template': TEMPLATE_ORCHARD_DUO, 'var_name': 'orchard_duo',
             'selection': SELECT_ORCHARD_DUO, 'selection_check': SELECT_ORCHARD_DUO_CHECK,
             'post_action': POST_ORCHARD_DUO},
            {'name': 'rice_mango', 'template': TEMPLATE_RICE_MANGO, 'var_name': 'rice_mango',
             'selection': SELECT_RICE_MANGO, 'selection_check': SELECT_RICE_MANGO_CHECK,
             'post_action': POST_RICE_MANGO},
            {'name': 'succulently_sweet', 'template': TEMPLATE_SUCCULENTLY_SWEET, 'var_name': 'succulently_sweet',
             'selection': SELECT_SUCCULENTLY_SWEET, 'selection_check': SELECT_SUCCULENTLY_SWEET_CHECK,
             'post_action': POST_SUCCULENTLY_SWEET},
            {'name': 'berry_orange', 'template': TEMPLATE_BERRY_ORANGE, 'var_name': 'berry_orange',
             'selection': SELECT_BERRY_ORANGE, 'selection_check': SELECT_BERRY_ORANGE_CHECK,
             'post_action': POST_BERRY_ORANGE},
            {'name': 'strawberry_charlotte', 'template': TEMPLATE_STRAWBERRY_CHARLOTTE,
             'var_name': 'strawberry_charlotte',
             'selection': SELECT_STRAWBERRY_CHARLOTTE, 'selection_check': SELECT_STRAWBERRY_CHARLOTTE_CHECK,
             'post_action': POST_STRAWBERRY_CHARLOTTE},
        ]

        # 设置套餐组成和特殊餐品需求
        self.meal_compositions = {
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

        # 特殊餐品需求（strawberry_charlotte需要2个cheese）
        self.special_meal_requirements = {
            'strawberry_charlotte': {
                'required': ['cheese'],
                'quantity_per': 2
            }
        }

        # 设置岗位按钮
        self.post_buttons = {
            'ISLAND_JUU_EATERY_POST1': ISLAND_JUU_EATERY_POST1,
            'ISLAND_JUU_EATERY_POST2': ISLAND_JUU_EATERY_POST2
        }

        # 设置筛选资产
        self.filter_asset = FILTER_ISLAND_JUU_EATERY

        # 设置配置前缀
        self.setup_config(
            config_meal_prefix="IslandJuuEatery_Meal",
            config_number_prefix="IslandJuuEatery_MealNumber",
            config_task_prefix="IslandJuuEateryNextTask_MealTask",
            config_task_number_prefix="IslandJuuEateryNextTask_MealTaskNumber",
            config_post_number="IslandJuuEatery_PostNumber",
            config_away_cook="IslandJuuEateryNextTask_AwayCook"
        )

        # 特殊材料：cheese
        self.cheese_stock = 0

        # 初始化店铺
        self.initialize_shop()

    def get_warehouse_counts(self):
        """覆盖：获取仓库数量，包括cheese"""
        super().get_warehouse_counts()

        # 额外获取cheese数量
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_ISLAND_JUU_COFFEE)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()
        self.cheese_stock = self.ocr_item_quantity(image, TEMPLATE_CHEESE)
        print(f"芝士数量: {self.cheese_stock}")

        return self.warehouse_counts

    def process_meal_requirements(self, source_products):
        """覆盖：处理套餐分解和特殊餐品需求"""
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

        # 处理特殊餐品需求
        for meal, quantity in source_products.items():
            if meal in self.special_meal_requirements:
                requirement = self.special_meal_requirements[meal]
                required_materials = requirement['required']
                required_quantity = requirement['quantity_per'] * quantity
                for req_material in required_materials:
                    if req_material in result:
                        result[req_material] += required_quantity
                    else:
                        result[req_material] = required_quantity

        # 添加非套餐需求
        for meal, quantity in source_products.items():
            if meal not in self.meal_compositions and meal not in self.special_meal_requirements:
                if meal in result:
                    result[meal] += quantity
                else:
                    result[meal] = quantity

        # 考虑芝士限制：strawberry_charlotte需求不能超过可用芝士
        if 'strawberry_charlotte' in result and result['strawberry_charlotte'] > 0:
            strawberry_needed = result['strawberry_charlotte']
            cheese_needed = strawberry_needed * 2  # 每个需要2个芝士
            cheese_available = self.cheese_stock

            if cheese_needed > cheese_available:
                print(f"警告：芝士不足！需要{cheese_needed}个芝士，但只有{cheese_available}个芝士")
                max_strawberry = cheese_available // 2
                result['strawberry_charlotte'] = max_strawberry
                print(f"调整strawberry_charlotte需求为: {max_strawberry}")

        self.to_post_products = result
        print(f"转换完成：source_products -> to_post_products")
        print(f"原始需求: {source_products}")
        print(f"生产计划: {self.to_post_products}")

    def check_material_limits(self, product, batch_size):
        """覆盖：检查材料限制，包括芝士"""
        batch_size = super().check_material_limits(product, batch_size)

        # 处理strawberry_charlotte的芝士需求
        if product == 'strawberry_charlotte':
            cheese_needed_per_batch = 2
            possible_batch = min(batch_size, self.cheese_stock // cheese_needed_per_batch)
            if possible_batch <= 0:
                print(f"生产 {product} 的芝士不足")
                return 0
            batch_size = possible_batch

        return batch_size

    def deduct_materials(self, product, number):
        """覆盖：扣除前置材料"""
        super().deduct_materials(product, number)

        # 处理strawberry_charlotte的芝士扣除
        if product == 'strawberry_charlotte':
            cheese_needed = number * 2
            self.cheese_stock -= cheese_needed
            print(f"扣除芝士：cheese -{cheese_needed} (用于制作 {product})")


if __name__ == "__main__":
    az = IslandJuuEatery('alas', task='Alas')
    az.device.screenshot()
    az.run()
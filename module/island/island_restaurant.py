# island_restaurant.py
from module.island_restaurant.assets import *
from module.island.island_shop_base import IslandShopBase
from module.island.assets import *


class IslandRestaurant(IslandShopBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置店铺类型
        self.shop_type = "restaurant"
        self.time_prefix = "time_restaurant"

        # 设置商品列表
        self.shop_items = [
            {'name': 'tofu', 'template': TEMPLATE_TOFU, 'var_name': 'tofu',
             'selection': SELECT_TOFU, 'selection_check': SELECT_TOFU_CHECK,
             'post_action': POST_TOFU},
            {'name': 'omurice', 'template': TEMPLATE_OMURICE, 'var_name': 'omurice',
             'selection': SELECT_OMURICE, 'selection_check': SELECT_OMURICE_CHECK,
             'post_action': POST_OMURICE},
            {'name': 'cabbage_tofu', 'template': TEMPLATE_CABBAGE_TOFU, 'var_name': 'cabbage_tofu',
             'selection': SELECT_CABBAGE_TOFU, 'selection_check': SELECT_CABBAGE_TOFU_CHECK,
             'post_action': POST_CABBAGE_TOFU},
            {'name': 'salad', 'template': TEMPLATE_SALAD, 'var_name': 'salad',
             'selection': SELECT_SALAD, 'selection_check': SELECT_SALAD_CHECK,
             'post_action': POST_SALAD},
            {'name': 'tofu_meat', 'template': TEMPLATE_TOFU_MEAT, 'var_name': 'tofu_meat',
             'selection': SELECT_TOFU_MEAT, 'selection_check': SELECT_TOFU_MEAT_CHECK,
             'post_action': POST_TOFU_MEAT},
            {'name': 'tofu_combo', 'template': TEMPLATE_TOFU_COMBO, 'var_name': 'tofu_combo',
             'selection': SELECT_TOFU_COMBO, 'selection_check': SELECT_TOFU_COMBO_CHECK,
             'post_action': POST_TOFU_COMBO},
            {'name': 'hearty_meal', 'template': TEMPLATE_HEARTY_MEAL, 'var_name': 'hearty_meal',
             'selection': SELECT_HEARTY_MEAL, 'selection_check': SELECT_HEARTY_MEAL_CHECK,
             'post_action': POST_HEARTY_MEAL},
        ]

        # 设置套餐组成和特殊餐品需求
        self.meal_compositions = {
            'hearty_meal': {
                'required': ['tofu', 'omurice'],
                'quantity_per': 1
            },
            'tofu_combo': {
                'required': ['cabbage_tofu', 'tofu_meat'],
                'quantity_per': 1
            }
        }

        # 特殊餐品需求（需要豆腐）
        self.special_meal_requirements = {
            'cabbage_tofu': {
                'required': ['tofu'],
                'quantity_per': 1
            },
            'tofu_meat': {
                'required': ['tofu'],
                'quantity_per': 2
            }
        }

        # 设置岗位按钮
        self.post_buttons = {
            'ISLAND_RESTAURANT_POST1': ISLAND_RESTAURANT_POST1,
            'ISLAND_RESTAURANT_POST2': ISLAND_RESTAURANT_POST2
        }

        # 设置筛选资产
        self.filter_asset = FILTER_ISLAND_RESTAURANT

        # 设置配置前缀
        self.setup_config(
            config_meal_prefix="IslandRestaurant_Meal",
            config_number_prefix="IslandRestaurant_MealNumber",
            config_task_prefix="IslandRestaurantNextTask_MealTask",
            config_task_number_prefix="IslandRestaurantNextTask_MealTaskNumber",
            config_post_number="IslandRestaurant_PostNumber",
            config_away_cook="IslandRestaurantNextTask_AwayCook"
        )

        # 初始化店铺
        self.initialize_shop()

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

        self.to_post_products = result
        print(f"转换完成：source_products -> to_post_products")
        print(f"原始需求: {source_products}")
        print(f"生产计划: {self.to_post_products}")

    def check_material_limits(self, product, batch_size):
        """覆盖：检查材料限制，包括豆腐需求"""
        batch_size = super().check_material_limits(product, batch_size)

        # 处理特殊餐品的豆腐需求
        if product in self.special_meal_requirements:
            requirement = self.special_meal_requirements[product]
            tofu_needed_per_batch = requirement['quantity_per']
            tofu_stock = self.warehouse_counts.get('tofu', 0)
            possible_batch = min(batch_size, tofu_stock // tofu_needed_per_batch)
            if possible_batch <= 0:
                print(f"生产 {product} 的豆腐不足")
                return 0
            batch_size = possible_batch

        return batch_size

    def deduct_materials(self, product, number):
        """覆盖：扣除前置材料"""
        super().deduct_materials(product, number)

        # 处理特殊餐品的豆腐扣除
        if product in self.special_meal_requirements:
            requirement = self.special_meal_requirements[product]
            tofu_needed = number * requirement['quantity_per']
            if 'tofu' in self.warehouse_counts:
                self.warehouse_counts['tofu'] -= tofu_needed
                print(f"扣除豆腐：tofu -{tofu_needed} (用于制作 {product})")


if __name__ == "__main__":
    az = IslandRestaurant('alas', task='Alas')
    az.device.screenshot()
    az.run()
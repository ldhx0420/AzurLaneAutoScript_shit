from module.island_restaurant.assets import *
from module.island.island_shop_base import IslandShopBase
from module.island.assets import *


class IslandRestaurant(IslandShopBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置店铺类型
        self.shop_type = "restaurant"
        self.time_prefix = "time_restaurant"
        self.chef_config = self.config.IslandRestaurant_Chef

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

        # 设置套餐组成
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

        # 特殊材料：豆腐（用于特殊餐品制作）
        self.special_materials = {}

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

    def check_special_materials(self, product, batch_size):
        """覆盖：检查特殊材料（豆腐）限制"""
        if batch_size <= 0:
            return 0

        # cabbage_tofu需要1个豆腐
        if product == 'cabbage_tofu':
            tofu_needed_per_batch = 1
            tofu_available = self.warehouse_counts.get('tofu', 0)
            max_by_tofu = tofu_available // tofu_needed_per_batch
            return min(batch_size, max_by_tofu)

        # tofu_meat需要2个豆腐
        if product == 'tofu_meat':
            tofu_needed_per_batch = 2
            tofu_available = self.warehouse_counts.get('tofu', 0)
            max_by_tofu = tofu_available // tofu_needed_per_batch
            return min(batch_size, max_by_tofu)

        return batch_size

    def deduct_materials(self, product, number):
        """覆盖：扣除前置材料，包括豆腐"""
        # 先调用父类方法扣除套餐原材料
        super().deduct_materials(product, number)

        # cabbage_tofu需要扣除豆腐
        if product == 'cabbage_tofu':
            tofu_needed = number * 1
            if 'tofu' in self.warehouse_counts:
                self.warehouse_counts['tofu'] -= tofu_needed
                print(f"扣除豆腐：tofu -{tofu_needed} (用于制作 {product})")

        # tofu_meat需要扣除豆腐
        if product == 'tofu_meat':
            tofu_needed = number * 2
            if 'tofu' in self.warehouse_counts:
                self.warehouse_counts['tofu'] -= tofu_needed
                print(f"扣除豆腐：tofu -{tofu_needed} (用于制作 {product})")

    def apply_special_material_constraints(self, requirements):
        """覆盖：根据豆腐库存调整需求"""
        result = requirements.copy()

        # 获取豆腐库存
        tofu_stock = self.warehouse_counts.get('tofu', 0)

        # 处理cabbage_tofu的需求
        if 'cabbage_tofu' in result and result['cabbage_tofu'] > 0:
            cabbage_needed = result['cabbage_tofu']
            tofu_needed = cabbage_needed * 1  # 每个cabbage_tofu需要1个豆腐

            if tofu_stock < tofu_needed:
                # 调整需求
                max_cabbage = tofu_stock // 1
                result['cabbage_tofu'] = max_cabbage
                print(f"豆腐不足：cabbage_tofu需求从{cabbage_needed}调整为{max_cabbage}")
                tofu_stock -= max_cabbage  # 更新剩余豆腐

        # 处理tofu_meat的需求
        if 'tofu_meat' in result and result['tofu_meat'] > 0:
            tofu_meat_needed = result['tofu_meat']
            tofu_needed = tofu_meat_needed * 2  # 每个tofu_meat需要2个豆腐

            if tofu_stock < tofu_needed:
                # 调整需求
                max_tofu_meat = tofu_stock // 2
                result['tofu_meat'] = max_tofu_meat
                print(f"豆腐不足：tofu_meat需求从{tofu_meat_needed}调整为{max_tofu_meat}")

        return result

    def test(self):
        chef_config = getattr(self.config, "IslandRestaurant_Chef", "WorkerJuu")
        print(chef_config)


if __name__ == "__main__":
    az = IslandRestaurant('alas', task='Alas')
    az.device.screenshot()
    az.test()
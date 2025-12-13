from module.island_teahouse.assets import *
from module.island.island_shop_base import IslandShopBase
from module.island.assets import *
from module.ui.page import *


class IslandTeahouse(IslandShopBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置店铺类型
        self.shop_type = "teahouse"
        self.time_prefix = "time_tea"

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

        # 初始化店铺
        self.initialize_shop()

    def get_warehouse_counts(self):
        """覆盖：获取仓库数量，包括蜂蜜"""
        super().get_warehouse_counts()

        # 额外获取蜂蜜数量
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_BASIC)
        self.appear_then_click(FILTER_OTHER)
        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()
        self.fresh_honey = self.ocr_item_quantity(image, TEMPLATE_FRESH_HONEY)
        print(f"蜂蜜数量: {self.fresh_honey}")

        return self.warehouse_counts

    def deduct_materials(self, product, number):
        """覆盖：扣除前置材料，包括蜂蜜"""
        super().deduct_materials(product, number)

        # 蜂蜜柠檬需要扣除蜂蜜
        if product == 'honey_lemon':
            self.fresh_honey -= number
            print(f"扣除蜂蜜：fresh_honey -{number}")

    def process_meal_requirements(self, source_products):
        """覆盖：处理套餐分解，考虑蜂蜜限制"""
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

        # 考虑蜂蜜限制
        if 'honey_lemon' in result and result['honey_lemon'] > 0:
            honey_needed = result['honey_lemon']
            honey_available = self.fresh_honey

            # 检查是否有sunny_honey需求
            if 'sunny_honey' in source_products:
                sunny_honey_needs_honey_lemon = source_products['sunny_honey']
                honey_lemon_for_sunny = sunny_honey_needs_honey_lemon
                honey_lemon_needed = max(0, honey_needed - honey_lemon_for_sunny)

                if honey_lemon_needed > honey_available:
                    print(f"警告：蜂蜜不足！需要{honey_lemon_needed}个蜂蜜柠檬，但只有{honey_available}个蜂蜜")
                    result['honey_lemon'] = honey_available + honey_lemon_for_sunny
                else:
                    result['honey_lemon'] = honey_needed
            else:
                if honey_needed > honey_available:
                    print(f"警告：蜂蜜不足！需要{honey_needed}个蜂蜜柠檬，但只有{honey_available}个蜂蜜")
                    result['honey_lemon'] = honey_available
                else:
                    result['honey_lemon'] = honey_needed

        self.to_post_products = result
        print(f"转换完成：source_products -> to_post_products")
        print(f"原始需求: {source_products}")
        print(f"生产计划: {self.to_post_products}")

    def check_material_limits(self, product, batch_size):
        """覆盖：检查材料限制，包括蜂蜜"""
        batch_size = super().check_material_limits(product, batch_size)

        # 蜂蜜柠檬需要检查蜂蜜
        if product == 'honey_lemon':
            possible_batch = min(batch_size, self.fresh_honey)
            if possible_batch <= 0:
                print(f"生产 {product} 的蜂蜜不足")
                return 0
            batch_size = possible_batch

        return batch_size


if __name__ == "__main__":
    az = IslandTeahouse('alas', task='Alas')
    az.device.screenshot()
    az.run()
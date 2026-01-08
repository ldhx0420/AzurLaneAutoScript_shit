from module.island_teahouse.assets import *
from module.island.island_shop_base import IslandShopBase
from module.island.assets import *
from module.ui.page import *
from collections import Counter
from datetime import datetime, timedelta
from module.logger import logger


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

        # 设置配置前缀（更新为4个参数，删除任务相关配置）
        self.setup_config(
            config_meal_prefix="IslandTeahouse_Meal",
            config_number_prefix="IslandTeahouse_MealNumber",
            config_away_cook="IslandTeahouseNextTask_AwayCook",
            config_post_number="IslandTeahouse_PostNumber"
        )

        # 特殊材料：蜂蜜（仅用于库存检查和限制，不再有强制消耗任务）
        self.fresh_honey = 0
        self.initialize_shop()

    def get_warehouse_counts(self):
        """覆盖：获取仓库数量，包括蜂蜜"""
        # 先调用父类方法获取基础库存
        super().get_warehouse_counts()

        # 额外获取蜂蜜数量（用于库存限制）
        self.ui_goto(page_island_warehouse_filter,get_ship=False)
        self.appear_then_click(FILTER_RESET)
        self.appear_then_click(FILTER_BASIC)
        self.appear_then_click(FILTER_OTHER)
        self.appear_then_click(FILTER_CONFIRM)
        self.device.sleep(0.3)
        image = self.device.screenshot()
        self.fresh_honey = self.ocr_item_quantity(image, TEMPLATE_FRESH_HONEY)
        logger.info(f"蜂蜜数量: {self.fresh_honey}")

        # 将蜂蜜库存存入warehouse_counts，便于统一处理
        self.warehouse_counts['fresh_honey'] = self.fresh_honey

        return self.warehouse_counts

    def check_special_materials(self, product, batch_size):
        """覆盖：检查特殊材料（蜂蜜）限制"""
        if batch_size <= 0:
            return 0

        # sunny_honey需要honey_lemon或蜂蜜
        if product == 'sunny_honey':
            # 计算可用原材料：蜂蜜 + honey_lemon库存
            honey_available = self.fresh_honey
            honey_lemon_available = self.warehouse_counts.get('honey_lemon', 0)
            total_available = honey_available + honey_lemon_available

            max_by_material = min(batch_size, total_available)
            return max_by_material

        # honey_lemon需要蜂蜜
        if product == 'honey_lemon':
            max_by_honey = min(batch_size, self.fresh_honey)
            return max_by_honey

        return batch_size

    def deduct_materials(self, product, number):
        """覆盖：扣除前置材料，包括蜂蜜和套餐原材料"""
        # 先调用父类方法扣除套餐原材料
        super().deduct_materials(product, number)

        # sunny_honey套餐需要扣除原材料
        if product == 'sunny_honey':
            # sunny_honey需要honey_lemon和strawberry_lemon各1个
            # honey_lemon可以通过蜂蜜制作，所以优先扣除蜂蜜，不够再扣除honey_lemon

            honey_needed = number
            honey_lemon_needed = number

            # 优先扣除蜂蜜
            if self.fresh_honey >= honey_needed:
                self.fresh_honey -= honey_needed
                logger.info(f"扣除蜂蜜：fresh_honey -{honey_needed} (用于制作sunny_honey)")
            else:
                # 蜂蜜不足，扣除honey_lemon
                remaining_needed = honey_needed - self.fresh_honey
                if self.fresh_honey > 0:
                    logger.info(f"扣除蜂蜜：fresh_honey -{self.fresh_honey} (用于制作sunny_honey)")
                    self.fresh_honey = 0

                # 扣除honey_lemon库存
                if 'honey_lemon' in self.warehouse_counts:
                    available_honey_lemon = min(remaining_needed, self.warehouse_counts['honey_lemon'])
                    if available_honey_lemon > 0:
                        self.warehouse_counts['honey_lemon'] -= available_honey_lemon
                        logger.info(f"扣除honey_lemon：honey_lemon -{available_honey_lemon} (用于制作sunny_honey)")

    def apply_special_material_constraints(self, requirements):
        """覆盖：根据蜂蜜库存调整需求"""
        result = requirements.copy()

        # 首先处理honey_lemon的需求
        if 'honey_lemon' in result and result['honey_lemon'] > 0:
            honey_lemon_needed = result['honey_lemon']
            max_honey_lemon = min(honey_lemon_needed, self.fresh_honey)

            if max_honey_lemon < honey_lemon_needed:
                logger.info(f"蜂蜜不足：honey_lemon需求从{honey_lemon_needed}调整为{max_honey_lemon}")

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
                logger.info(f"蜂蜜不足：sunny_honey需求从{sunny_honey_needed}调整为{max_sunny_honey}")

            result['sunny_honey'] = max_sunny_honey

        return result


if __name__ == "__main__":
    az = IslandTeahouse('alas', task='Alas')
    az.device.screenshot()
    az.run()
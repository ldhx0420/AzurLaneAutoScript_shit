from module.island_juu_coffee.assets import *
from module.island.island_shop_base import IslandShopBase
from module.island.assets import *


class IslandJuuCoffee(IslandShopBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置店铺类型
        self.shop_type = "juu_coffee"
        self.time_prefix = "time_coffee"
        self.chef_config = self.config.IslandJuuCoffee_Chef

        # 设置商品列表
        self.shop_items = [
            {'name': 'iced_coffee', 'template': TEMPLATE_ICED_COFFEE, 'var_name': 'iced_coffee',
             'selection': SELECT_ICED_COFFEE, 'selection_check': SELECT_ICED_COFFEE_CHECK,
             'post_action': POST_ICED_COFFEE},
            {'name': 'omelette', 'template': TEMPLATE_OMELETTE, 'var_name': 'omelette',
             'selection': SELECT_OMELETTE, 'selection_check': SELECT_OMELETTE_CHECK,
             'post_action': POST_OMELETTE},
            {'name': 'cheese', 'template': TEMPLATE_CHEESE, 'var_name': 'cheese',
             'selection': SELECT_CHEESE, 'selection_check': SELECT_CHEESE_CHECK,
             'post_action': POST_CHEESE},
            {'name': 'latte', 'template': TEMPLATE_LATTE, 'var_name': 'latte',
             'selection': SELECT_LATTE, 'selection_check': SELECT_LATTE_CHECK,
             'post_action': POST_LATTE},
            {'name': 'citrus_coffee', 'template': TEMPLATE_CITRUS_COFFEE, 'var_name': 'citrus_coffee',
             'selection': SELECT_CITRUS_COFFEE, 'selection_check': SELECT_CITRUS_COFFEE_CHECK,
             'post_action': POST_CITRUS_COFFEE},
            {'name': 'strawberry_milkshake', 'template': TEMPLATE_STRAWBERRY_MILKSHAKE,
             'var_name': 'strawberry_milkshake',
             'selection': SELECT_STRAWBERRY_MILKSHAKE, 'selection_check': SELECT_STRAWBERRY_MILKSHAKE_CHECK,
             'post_action': POST_STRAWBERRY_MILKSHAKE},
            {'name': 'morning_light', 'template': TEMPLATE_MORNING_LIGHT, 'var_name': 'morning_light',
             'selection': SELECT_MORNING_LIGHT, 'selection_check': SELECT_MORNING_LIGHT_CHECK,
             'post_action': POST_MORNING_LIGHT},
            {'name': 'wake_up_call', 'template': TEMPLATE_WAKE_UP_CALL, 'var_name': 'wake_up_call',
             'selection': SELECT_WAKE_UP_CALL, 'selection_check': SELECT_WAKE_UP_CALL_CHECK,
             'post_action': POST_WAKE_UP_CALL},
            {'name': 'fruity_fruitier', 'template': TEMPLATE_FRUITY_FRUITIER, 'var_name': 'fruity_fruitier',
             'selection': SELECT_FRUITY_FRUITIER, 'selection_check': SELECT_FRUITY_FRUITIER_CHECK,
             'post_action': POST_FRUITY_FRUITIER},
        ]

        # 设置套餐组成
        self.meal_compositions = {
            'morning_light': {
                'required': ['latte', 'omelette'],
                'quantity_per': 1
            },
            'wake_up_call': {
                'required': ['cheese', 'iced_coffee'],
                'quantity_per': 1
            },
            'fruity_fruitier': {
                'required': ['citrus_coffee', 'strawberry_milkshake'],
                'quantity_per': 1
            }
        }

        # 设置岗位按钮
        self.post_buttons = {
            'ISLAND_JUU_COFFEE_POST1': ISLAND_JUU_COFFEE_POST1,
            'ISLAND_JUU_COFFEE_POST2': ISLAND_JUU_COFFEE_POST2
        }

        # 设置筛选资产
        self.filter_asset = FILTER_ISLAND_JUU_COFFEE

        # 设置配置前缀
        self.setup_config(
            config_meal_prefix="IslandJuuCoffee_Meal",
            config_number_prefix="IslandJuuCoffee_MealNumber",
            config_task_prefix="IslandJuuCoffeeNextTask_MealTask",
            config_task_number_prefix="IslandJuuCoffeeNextTask_MealTaskNumber",
            config_post_number="IslandJuuCoffee_PostNumber",
            config_away_cook="IslandJuuCoffeeNextTask_AwayCook"
        )

        # 设置滑动次数（JuuCoffee需要滑动两次）
        self.post_manage_swipe_count = 2  # run方法中滑动2次450
        self.post_produce_swipe_count = 2  # post_produce方法中滑动2次450

        # 初始化店铺
        self.initialize_shop()


if __name__ == "__main__":
    az = IslandJuuCoffee('alas', task='Alas')
    az.device.screenshot()
    az.run()
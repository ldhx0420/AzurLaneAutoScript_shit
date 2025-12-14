from module.island.island import *
from module.island_manufacture.assets import *
from module.island.island_shop_base import IslandShopBase
from module.island.assets import *
from module.ui.page import *

class IslandManufacture(IslandShopBase):
    def __init__(self, *args, **kwargs):
        # 初始化父类
        Island.__init__(self, *args, **kwargs)
        WarehouseOCR.__init__(self)

        # 设置店铺类型
        self.shop_type = "manufacture"
        self.time_prefix = "time_manufacture"

        # 设置滑动配置（岗位管理界面需要两次滑动）
        self.post_manage_swipe_count = 2
        self.post_produce_swipe_count = 2

        # 设置筛选资产
        self.filter_asset = FILTER_FACTORY

        # 制造业产品配置
        self.manufacture = {
            'wood_processing': {
                'items': [
                    {'name': 'file_cabinet', 'template': TEMPLATE_FILE_CABINET,
                     'var_name': 'file_cabinet', 'selection': SELECT_FILE_CABINET,
                     'selection_check': SELECT_FILE_CABINET_CHECK, 'post_action': POST_FILE_CABINET},
                ]
            },
            'industrial_production': {
                'items': [
                    {'name': 'iron_nail', 'template': TEMPLATE_IRON_NAIL,
                     'var_name': 'iron_nail', 'selection': SELECT_IRON_NAIL,
                     'selection_check': SELECT_IRON_NAIL_CHECK, 'post_action': POST_IRON_NAIL},
                    {'name': 'cutlery', 'template': TEMPLATE_CUTLERY,
                     'var_name': 'cutlery', 'selection': SELECT_CUTLERY,
                     'selection_check': SELECT_CUTLERY_CHECK, 'post_action': POST_CUTLERY},
                ]
            },
            'handmade': {
                'items': [
                    {'name': 'leather', 'template': TEMPLATE_LEATHER,
                     'var_name': 'leather', 'selection': SELECT_LEATHER,
                     'selection_check': SELECT_LEATHER_CHECK, 'post_action': POST_LEATHER},
                    {'name': 'peanut_oil', 'template': TEMPLATE_PEANUT_OIL,
                     'var_name': 'peanut_oil', 'selection': SELECT_PEANUT_OIL,
                     'selection_check': SELECT_PEANUT_OIL_CHECK, 'post_action': POST_PEANUT_OIL},
                    {'name': 'boot', 'template': TEMPLATE_BOOT,
                     'var_name': 'boot', 'selection': SELECT_BOOT,
                     'selection_check': SELECT_BOOT_CHECK, 'post_action': POST_BOOT},
                ]
            }
        }

        # 设置岗位按钮
        self.post_buttons = {
            'ISLAND_WOOD_PROCESSING_POST1': ISLAND_WOOD_PROCESSING_POST1,
            'ISLAND_WOOD_PROCESSING_POST2': ISLAND_WOOD_PROCESSING_POST2,
            'ISLAND_INDUSTRIAL_POST1': ISLAND_INDUSTRIAL_POST1,
            'ISLAND_INDUSTRIAL_POST2': ISLAND_INDUSTRIAL_POST2,
            'ISLAND_HANDMADE_POST1': ISLAND_HANDMADE_POST1,
            'ISLAND_HANDMADE_POST2': ISLAND_HANDMADE_POST2,
        }

        # 将所有产品展平到一个列表中，供基类使用
        self.shop_items = []
        for category in self.manufacture.values():
            self.shop_items.extend(category['items'])

        # 初始化店铺
        self.initialize_shop()

        # 初始化需求列表（制造业不需要外部配置的需求）
        self.post_products = {}
        self.post_products_task = {}

        # 设置任务标志
        self.task_completed = False

    def get_warehouse_counts(self):
        """获取仓库数量（覆盖基类方法）"""
        self.ui_goto(page_island_warehouse_filter)
        self.appear_then_click(FILTER_RESET)

        # 点击筛选资产
        for asset in self.filter_asset:
            self.device.click(asset)

        self.appear_then_click(FILTER_CONFIRM)
        self.wait_until_appear(ISLAND_WAREHOUSE_GOTO_WAREHOUSE_FILTER)
        image = self.device.screenshot()

        for dish in self.shop_items:
            self.warehouse_counts[dish['name']] = self.ocr_item_quantity(image, dish['template'])
            if self.warehouse_counts[dish['name']]:
                print(f"{dish['name']}", self.warehouse_counts[dish['name']])

        return self.warehouse_counts

    def get_idle_posts_by_category(self, category):
        """获取指定类别的空闲岗位ID列表"""
        category_posts = []
        if category == 'wood_processing':
            category_posts = ['ISLAND_WOOD_PROCESSING_POST1', 'ISLAND_WOOD_PROCESSING_POST2']
        elif category == 'industrial_production':
            category_posts = ['ISLAND_INDUSTRIAL_POST1', 'ISLAND_INDUSTRIAL_POST2']
        elif category == 'handmade':
            category_posts = ['ISLAND_HANDMADE_POST1', 'ISLAND_HANDMADE_POST2']

        return [post_id for post_id in category_posts
                if post_id in self.posts and self.posts[post_id]['status'] == 'idle']

    def select_product_with_material_check(self, post_id, product_list):
        """选择产品并检查材料是否充足"""
        post_button = self.posts[post_id]['button']

        for product_info in product_list:
            selection = product_info['selection']
            selection_check = product_info['selection_check']

            # 选择产品
            self.select_product(selection, selection_check)

            # 等待界面更新
            self.device.sleep(0.5)

            # 截图检查按钮区域颜色
            image = self.device.screenshot()

            # 定义材料不足时的颜色检测区域（这里需要根据实际情况调整）
            # 假设材料不足时按钮区域会变灰
            area = (493, 597, 621, 643)
            color = get_color(image, area)

            # 检查颜色是否与材料不足的颜色相似
            # (18.0, 211.0, 186.0) 是材料不足的颜色示例，80是相似度阈值
            if color_similar(color, (18.0, 211.0, 186.0), 80):
                print(f"材料不足，跳过产品: {product_info['name']}")
                # 点击返回按钮重置界面
                self.device.click(SELECT_UI_BACK)
                # 重新打开岗位
                self.post_open(post_button)
                continue
            else:
                # 材料充足，返回选中的产品信息
                return product_info

        # 所有产品都材料不足
        print("所有产品材料不足，保持空闲")
        return None

    def schedule_manufacture(self):
        """安排制造业生产（覆盖基类的schedule_production方法）"""
        # 1. 木料加工：只生产file_cabinet
        self.schedule_wood_processing()

        # 2. 工业生产
        self.schedule_industrial_production()

        # 3. 手工生产
        self.schedule_handmade()

    def schedule_wood_processing(self):
        """安排木料加工生产"""
        idle_posts = self.get_idle_posts_by_category('wood_processing')
        if not idle_posts:
            return

        # 木料加工只生产file_cabinet
        product_list = self.manufacture['wood_processing']['items']

        for post_id in idle_posts:
            if not self.to_post_products:  # 如果没有需求，则生产1个
                product_info = self.select_product_with_material_check(post_id, product_list)
                if product_info:
                    post_num = post_id[-1]
                    time_var_name = f'{self.time_prefix}{post_num}'
                    self.post_produce(post_id, product_info['name'], 1, time_var_name)
                break  # 只安排一个空闲岗位

    def schedule_industrial_production(self):
        """安排工业生产"""
        idle_posts = self.get_idle_posts_by_category('industrial_production')
        if not idle_posts:
            return

        # 检查库存iron_nail
        iron_nail_stock = self.warehouse_counts.get('iron_nail', 0)

        # 根据规则选择产品
        if iron_nail_stock >= 15:
            product_list = [item for item in self.manufacture['industrial_production']['items']
                            if item['name'] == 'cutlery']
        else:
            product_list = [item for item in self.manufacture['industrial_production']['items']
                            if item['name'] == 'iron_nail']

        for post_id in idle_posts:
            product_info = self.select_product_with_material_check(post_id, product_list)
            if product_info:
                post_num = post_id[-1]
                time_var_name = f'{self.time_prefix}{post_num}'
                self.post_produce(post_id, product_info['name'], 1, time_var_name)
                break  # 只安排一个空闲岗位

    def schedule_handmade(self):
        """安排手工生产"""
        idle_posts = self.get_idle_posts_by_category('handmade')
        if not idle_posts:
            return

        # 检查库存leather
        leather_stock = self.warehouse_counts.get('leather', 0)

        # 构建产品选择列表（按优先级）
        product_list = []

        # 优先生产peanut_oil
        peanut_oil_item = [item for item in self.manufacture['handmade']['items']
                           if item['name'] == 'peanut_oil'][0]
        product_list.append(peanut_oil_item)

        # 如果leather库存>=15，则生产boot
        if leather_stock >= 15:
            boot_item = [item for item in self.manufacture['handmade']['items']
                         if item['name'] == 'boot'][0]
            product_list.append(boot_item)

        # 最后生产leather
        leather_item = [item for item in self.manufacture['handmade']['items']
                        if item['name'] == 'leather'][0]
        product_list.append(leather_item)

        for post_id in idle_posts:
            product_info = self.select_product_with_material_check(post_id, product_list)
            if product_info:
                post_num = post_id[-1]
                time_var_name = f'{self.time_prefix}{post_num}'
                self.post_produce(post_id, product_info['name'], 1, time_var_name)
                break  # 只安排一个空闲岗位

    def run(self):
        """运行制造业逻辑"""
        self.goto_management()
        self.ui_goto(page_island_postmanage)
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)

        # 滑动以看到岗位（需要两次滑动）
        for _ in range(self.post_manage_swipe_count):
            self.post_manage_up_swipe(450)

        # 检查岗位状态
        post_count = len(self.post_buttons)
        time_vars = []
        for i, post_id in enumerate(self.post_buttons.keys()):
            time_var_name = f'{self.time_prefix}{i + 1}'
            time_vars.append(time_var_name)
            setattr(self, time_var_name, None)
            self.post_check(post_id, time_var_name)

        # 获取仓库数量
        self.get_warehouse_counts()

        # 清空待生产列表（制造业不需要）
        self.to_post_products = {}

        # 安排生产
        self.schedule_manufacture()

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




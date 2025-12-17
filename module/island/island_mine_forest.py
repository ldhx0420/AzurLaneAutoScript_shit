from module.island.island import *
from module.island_mine_forest.assets import *
from module.ui.page import *
from module.handler.login import LoginHandler
from module.config.utils import *
from module.island.warehouse import *


class IslandMineForest(Island,LoginHandler):
    def __init__(self, *args, **kwargs):
        Island.__init__(self, *args, **kwargs)

    PRODUCT_CONFIGS = {
        "Copper": (SELECT_COPPER, SELECT_COPPER_CHECK, POST_COPPER),
        "Aluminium": (SELECT_ALUMINIUM, SELECT_ALUMINIUM_CHECK, POST_ALUMINIUM),
        "Iron": (SELECT_IRON, SELECT_IRON_CHECK, POST_IRON),
        "Sulphur": (SELECT_SULPHUR, SELECT_SULPHUR_CHECK, POST_SULPHUR),
        "Silver": (SELECT_SILVER, SELECT_SILVER_CHECK, POST_SILVER),
        "Elegant": (SELECT_ELEGANT, SELECT_ELEGANT_CHECK, POST_ELEGANT),
        "Practical": (SELECT_PRACTICAL, SELECT_PRACTICAL_CHECK, POST_PRACTICAL),
        "Selected": (SELECT_SELECTED, SELECT_SELECTED_CHECK, POST_SELECTED),
        "Natural": (SELECT_NATURAL, SELECT_NATURAL_CHECK, POST_NATURAL),
    }

    def get_product_config(self, product_name):
        """获取产品配置"""
        return self.PRODUCT_CONFIGS.get(product_name, (None, None, None))

    def is_product_available(self, product_name):
        """检查产品是否可用"""
        config = self.get_product_config(product_name)
        return config[2] is not None and self.appear(config[2])

    def _handle_max_check(self):
        """处理最大数量检查的通用逻辑"""
        while True:
            self.device.screenshot()
            if self.appear(POST_MAX_CHECK):
                self.device.click(POST_ADD_ORDER)
                break
            if self.appear(ERROR1):
                self.device.app_stop()
                self.device.app_start()
                self.handle_app_login()
                break
            if self.appear_then_click(POST_MAX):
                continue
            if self.appear_then_click(POST_GET):
                continue
            if self.device.click(POST_ADD):
                continue

    def _select_product(self, selection_buttons):
        """选择产品的通用流程"""
        self.wait_until_appear(ISLAND_SELECT_CHARACTER_CHECK)
        self.select_character()
        self.appear_then_click(SELECT_UI_CONFIRM)
        product_selection, product_selection_check, _ = selection_buttons
        self.select_product(product_selection, product_selection_check)
        self._handle_max_check()

    def _process_post_state(self, post_id, product_name, time_var_name):
        """处理岗位状态的通用逻辑"""
        config = self.get_product_config(product_name)
        if not all(config[:2]):  # 检查选择按钮是否存在
            return

        time_work = Duration(ISLAND_WORKING_TIME)

        # 按优先级处理状态
        if self.appear(ISLAND_WORKING):
            if self.is_product_available(product_name):
                if self.appear(POST_GET):
                    self._handle_max_check()
                    self.post_open(post_id)
                    self._update_time_and_close(time_work, post_id, time_var_name)
                else:
                    self._update_time_and_close(time_work, post_id, time_var_name)
            else:
                self.device.click(POST_CLOSE)

        elif self.appear(ISLAND_WORK_COMPLETE):
            while not self.appear(ISLAND_POST_SELECT):
                self.device.screenshot()
                if self.appear_then_click(POST_GET):
                    continue

            if self.appear_then_click(ISLAND_POST_SELECT):
                self._select_product(config)

            self._update_time_and_close(time_work, post_id, time_var_name)

        elif self.appear_then_click(ISLAND_POST_SELECT):
            self._select_product(config)
            self._update_time_and_close(time_work, post_id, time_var_name)

    def _update_time_and_close(self, time_work, post_id, time_var_name):
        """更新完成时间并关闭岗位"""
        time_value = time_work.ocr(self.device.image)
        setattr(self, time_var_name, datetime.now() + time_value)
        self.device.click(POST_CLOSE)

    def run_single_post(self, post_id, product_config, time_var_name):
        """运行单个岗位"""
        self.device.click(POST_CLOSE)
        self.post_open(post_id)
        self.device.screenshot()
        self._process_post_state(post_id, product_config, time_var_name)

    def run(self):
        """运行所有岗位"""
        # 初始化时间变量
        time_vars = ['time_Mining1', 'time_Mining2', 'time_Mining3', 'time_Mining4',
                     'time_Felling1', 'time_Felling2', 'time_Felling3', 'time_Felling4']
        for var in time_vars:
            setattr(self, var, None)

        # 配置所有岗位
        all_configs = [
            (ISLAND_MINE_POST1, self.config.IslandMine_Mining1, 'time_Mining1'),
            (ISLAND_MINE_POST2, self.config.IslandMine_Mining2, 'time_Mining2'),
            (ISLAND_MINE_POST3, self.config.IslandMine_Mining3, 'time_Mining3'),
            (ISLAND_MINE_POST4, self.config.IslandMine_Mining4, 'time_Mining4'),
            (ISLAND_FOREST_POST1, self.config.IslandForest_Felling1, 'time_Felling1'),
            (ISLAND_FOREST_POST2, self.config.IslandForest_Felling2, 'time_Felling2'),
            (ISLAND_FOREST_POST3, self.config.IslandForest_Felling3, 'time_Felling3'),
            (ISLAND_FOREST_POST4, self.config.IslandForest_Felling4, 'time_Felling4')
        ]

        # 通用设置
        self.goto_postmanage()
        self.post_manage_mode(POST_MANAGE_PRODUCTION)
        self.device.click(POST_CLOSE)
        self.post_manage_down_swipe(450)
        self.post_manage_down_swipe(450)

        # 运行所有岗位
        for post_id, product_config, time_var_name in all_configs:
            if product_config is not None:
                self.run_single_post(post_id, product_config, time_var_name)

        # 收集并处理完成时间
        self._process_finish_times(time_vars)
    def _process_finish_times(self, time_vars):
        """处理完成时间"""
        finish_times = [getattr(self, var) for var in time_vars if getattr(self, var) is not None]
        finish_times.sort()

        logger.info(f'Island post finish times: {[str(f) for f in finish_times]}')

        if finish_times:
            self.config.task_delay(target=finish_times)
            logger.info(f'Found {len(finish_times)} post timers, next run at {finish_times[0]}')
        else:
            logger.info('No post timers found')
            self.config.task_delay(success=True)

if __name__ == "__main__":
    az =IslandMineForest('alas', task='Alas')
    az.device.screenshot()
    az.run()

from module.island_select_character.assets import *
from module.base.button import *
from module.ui.ui import UI


class SelectCharacter(UI):
    def __init__(self, *args, **kwargs):
        UI.__init__(self, *args, **kwargs)
        self.select_character_grid = ButtonGrid(
            origin=(58, 141),
            delta=(140, 180),
            button_shape=(120, 160),
            grid_shape=(6, 2),
            name="SELECT_CHARACTER_GRID"
        )

        # 定义状态检测区域（相对于每个角色按钮）
        self.character_area_relative = (32, 14, 118, 65)
        self.working_area_relative = (15, 65, 105, 95)
        self.stamina_area_relative = (56, 139, 63, 152)
        self.selected_area_relative = (86, 1, 119, 12)

        # 角色模板映射
        self.character_templates = {
            "WorkerJuu": TEMPLATE_WORKERJUU,
            "NewJersey": TEMPLATE_NEWJERSEY,
            "Tashkent": TEMPLATE_TASHKENT,
            "YingSwei": TEMPLATE_YINGSWEI,
            "Saratoga": TEMPLATE_SARATOGA,
            "Akashi": TEMPLATE_AKASHI,
            "LeMalin": TEMPLATE_LEMALIN,
            "Shimakaze": TEMPLATE_SHIMAKAZE,
            "Amagi_chan": TEMPLATE_AMAGI_CHAN,
            "Cheshire": TEMPLATE_CHESHIRE,
            "Unicorn": TEMPLATE_UNICORN
        }

    def recognize_all_characters(self, screenshot):
        """识别网格中所有角色的状态"""
        results = []

        for row, col, button in self.select_character_grid.generate():
            # 获取角色按钮区域
            character_status = self._recognize_character_status(screenshot, button)
            if character_status:
                results.append({
                    "grid_position": (row, col),
                    "button_area": button.area,
                    **character_status
                })

        return results

    def _recognize_character_status(self, screenshot, button):
        """识别单个角色的状态"""
        # 1. 识别角色身份
        character_name = self._recognize_character_identity(screenshot, button)
        if not character_name:
            return None  # 该位置没有角色

        # 2. 识别是否工作中
        is_working = self._check_working_status(screenshot, button)

        # 3. 识别体力是否充沛
        has_stamina = self._check_stamina_status(screenshot, button)

        # 4. 识别是否已选中
        is_selected = self._check_selected_status(screenshot, button)

        return {
            "character_name": character_name,
            "is_working": is_working,
            "has_stamina": has_stamina,
            "is_selected": is_selected
        }

    def _recognize_character_identity(self, screenshot, button):
        """识别角色身份"""
        # 获取角色识别区域
        char_area = self._get_absolute_area(button, self.character_area_relative)
        char_image = crop(screenshot, char_area)

        # 遍历所有角色模板进行匹配
        best_match = None
        best_similarity = 0.0

        for char_name, template in self.character_templates.items():
            similarity = template.match(char_image, similarity=0.8)
            if similarity > best_similarity and similarity >= 0.8:
                best_similarity = similarity
                best_match = char_name

        return best_match

    def _check_working_status(self, screenshot, button):
        """检查是否工作中"""
        working_area = self._get_absolute_area(button, self.working_area_relative)
        working_image = crop(screenshot, working_area)

        # 匹配工作中模板
        similarity = TEMPLATE_CHARACTER_WORKING.match(working_image, similarity=0.85)
        return similarity >= 0.85

    def _check_stamina_status(self, screenshot, button):
        """检查体力是否充沛"""
        stamina_area = self._get_absolute_area(button, self.stamina_area_relative)
        stamina_color = get_color(screenshot, stamina_area)
        return color_similar(stamina_color, (18.0, 211.0, 186.0),80)

    def _check_selected_status(self, screenshot, button):
        """检查是否已选中"""
        selected_area = self._get_absolute_area(button, self.selected_area_relative)
        selected_color = get_color(screenshot, selected_area)
        return color_similar(selected_color, (19.0, 182.0, 234.0),80)

    def _get_absolute_area(self, button, relative_area):
        """将相对坐标转换为绝对坐标"""
        x1 = button.area[0] + relative_area[0]
        y1 = button.area[1] + relative_area[1]
        x2 = button.area[0] + relative_area[2]
        y2 = button.area[1] + relative_area[3]
        return (x1, y1, x2, y2)

    def find_available_characters(self, screenshot):
        """查找可用的角色（非工作中、体力充沛）"""
        all_characters = self.recognize_all_characters(screenshot)
        available = []

        for char_info in all_characters:
            if not char_info["is_working"] and char_info["has_stamina"]:
                available.append(char_info)

        return available

    def find_specific_character(self, screenshot, character_name="WorkerJuu"):
        """查找指定角色的位置信息"""
        all_characters = self.recognize_all_characters(screenshot)
        for char_info in all_characters:
            if char_info["character_name"] == character_name:
                return char_info["grid_position"]
        return None

    def find_working_characters(self, screenshot):
        """查找工作中的角色"""
        all_characters = self.recognize_all_characters(screenshot)
        working = []

        for char_info in all_characters:
            if char_info["is_working"]:
                working.append(char_info)

        return working

    def get_character_by_position(self, screenshot, row, col):
        """获取指定网格位置的字符状态"""
        for char_info in self.recognize_all_characters(screenshot):
            if char_info["grid_position"] == (row, col):
                return char_info
        return None

    def select_character(self, character_name="WorkerJuu"):
        """选择指定角色，如果不可用则选择WorkerJuu"""
        screenshot = self.device.screenshot()
        all_status = self.recognize_all_characters(screenshot)
        target_row, target_col = None, None
        if character_name != "WorkerJuu":
            for char_info in all_status:
                if char_info["character_name"] == character_name:
                    if not char_info["is_working"] and char_info["has_stamina"]:
                        target_row, target_col = char_info["grid_position"]
                        break
        if target_row is None:
            for char_info in all_status:
                if char_info["character_name"] == "WorkerJuu":
                    target_row, target_col = char_info["grid_position"]
                    break
        if target_row is not None and target_col is not None:
            button = self.select_character_grid[target_row, target_col]
            while True:
                screenshot = self.device.screenshot()
                current_char_info = self.get_character_by_position(screenshot, target_row, target_col)
                if current_char_info and current_char_info["is_selected"]:
                    break
                else:
                    self.device.click(button)
                self.device.sleep(0.3)

    def _is_character_available_by_config(self, character_name):
        """
        根据玩家配置判断角色是否可用于选择
        返回True表示角色可用于选择，False表示不可用
        """
        if character_name == "WorkerJuu":
            return True
        # 特殊角色配置检查
        if character_name == "YingSwei" and self.config.IslandRestaurant_Chef == "YingSwei":
            return False  # 不可用
        if character_name == "Amagi_chan" and self.config.PersonnelManagement_AmagiChanRubber:
            return False  # 不可用
        # 获取营业状态
        business_status = self.config.PersonnelManagement_BusinessStatus
        # 检查角色是否在店铺配置中以及对应的波次
        business_configs = [
            "IslandRestaurantBusiness",
            "IslandTeahouseBusiness",
            "IslandGrillBusiness",
            "IslandJuuEateryBusiness",
            "IslandJuuCoffeeBusiness"
        ]
        # 记录角色出现在哪个波次的店铺中
        appears_in_wave1 = False
        appears_in_wave2 = False
        for business in business_configs:
            # 检查该角色是否是此店铺的店员
            waiter1 = getattr(self.config, f"{business}_Waiter1", None)
            waiter2 = getattr(self.config, f"{business}_Waiter2", None)

            if waiter1 == character_name or waiter2 == character_name:
                # 获取店铺波次
                time_attr = getattr(self.config, f"{business}_time", 0)
                if time_attr == 1:
                    appears_in_wave1 = True
                elif time_attr == 2:
                    appears_in_wave2 = True
        # 根据营业状态判断
        if business_status == 0:  # 所有店铺角色不可选
            # 如果角色出现在任何店铺中，都不可选
            if appears_in_wave1 or appears_in_wave2:
                return False
            # 不在任何店铺中，可用
            return True
        elif business_status == 1:  # 只有波次为1且不在波次2的店铺角色可选
            # 如果出现在波次2中，不可选
            if appears_in_wave2:
                return False
            # 如果只出现在波次1中，可选
            if appears_in_wave1:
                return True
            # 不出现在任何店铺中，可用
            return True
        elif business_status == 2:  # 所有店铺角色可选
            # 无论出现在哪个波次，都可用
            return True
        # 默认情况
        return True

    def _select_first_available_character(self, screenshot, character_list):
        """
        从指定角色列表中选择第一个空闲且体力充沛的角色
        如果无可选角色则选择WorkerJuu
        """
        all_characters = self.recognize_all_characters(screenshot)

        # 构建角色名到状态的映射
        character_dict = {}
        for char_info in all_characters:
            character_dict[char_info["character_name"]] = char_info
        # 优先按列表顺序检查指定角色
        for char_name in character_list:
            if char_name in character_dict:
                char_info = character_dict[char_name]
                # 检查角色状态和配置可用性
                if (not char_info["is_working"] and
                        char_info["has_stamina"] and
                        self._is_character_available_by_config(char_name)):
                    return char_info["grid_position"]
        # 如果没有找到可用角色，查找WorkerJuu
        if "WorkerJuu" in character_dict:
            worker_info = character_dict["WorkerJuu"]
            return worker_info["grid_position"]
        return None

    def select_character_a(self):
        """
        选择第一个可用的A类角色，否则选择WorkerJuu
        角色列表: "Amagi_chan", "NewJersey", "Unicorn", "LeMalin"
        """
        character_list = ["LeMalin", "Unicorn", "NewJersey", "Amagi_chan"]

        screenshot = self.device.screenshot()
        position = self._select_first_available_character(screenshot, character_list)


        row, col = position
        button = self.select_character_grid[row, col]
        while True:
            screenshot = self.device.screenshot()
            current_char_info = self.get_character_by_position(screenshot, row, col)
            if current_char_info and current_char_info["is_selected"]:
                break
            else:
                self.device.click(button)
            self.device.sleep(0.3)

    def select_character_b(self):
        """
        选择第一个可用的B类角色，否则选择WorkerJuu
        合并了原来的B类和C类角色
        角色列表: "Cheshire", "YingSwei", "Shimakaze", "Saratoga", "Tashkent", "Akashi"
        """
        character_list = ["Cheshire", "YingSwei", "Shimakaze", "Saratoga", "Tashkent", "Akashi"]
        screenshot = self.device.screenshot()
        position = self._select_first_available_character(screenshot, character_list)
        row, col = position
        button = self.select_character_grid[row, col]
        while True:
            screenshot = self.device.screenshot()
            current_char_info = self.get_character_by_position(screenshot, row, col)
            if current_char_info and current_char_info["is_selected"]:
                break
            else:
                self.device.click(button)
            self.device.sleep(0.3)





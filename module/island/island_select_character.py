from module.island_select_character.assets import *
from module.base.button import *
from module.island.island import *


class SelectCharacter(UI):
    def __init__(self, *args, **kwargs):
        UI.__init__(self, *args, **kwargs)
        self.grid = ButtonGrid(
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

        for row, col, button in self.grid.generate():
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
            button = self.grid[target_row, target_col]
            while True:
                screenshot = self.device.screenshot()
                current_char_info = self.get_character_by_position(screenshot, target_row, target_col)
                if current_char_info and current_char_info["is_selected"]:
                    break
                else:
                    self.device.click(button)
                self.device.sleep(0.3)


    def select_character_b(self,screenshot):
        all_status = self.recognize_all_characters(screenshot)
        for status in all_status:
            print(f"位置: {status['grid_position']}")
            print(f"角色: {status['character_name']}")
            print(f"工作中: {status['is_working']}")
            print(f"体力充沛: {status['has_stamina']}")
            print(f"已选中: {status['is_selected']}")
            print("-" * 30)

        available_chars = self.find_available_characters(screenshot)
        print(f"可用角色数量: {len(available_chars)}")
        # 查找工作中的角色
        working_chars = self.find_working_characters(screenshot)
        print(f"工作中的角色数量: {len(working_chars)}")




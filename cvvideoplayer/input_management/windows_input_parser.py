from .base_input_parser import BaseInputParser
from ..utils.windows_os_utils import VK_CODE_MAP


class WindowsInputParser(BaseInputParser):
    @staticmethod
    def _vk_code_mapper(vk_code):
        return VK_CODE_MAP[vk_code]

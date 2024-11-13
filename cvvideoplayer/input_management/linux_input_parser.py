from .base_input_parser import BaseInputParser


class LinuxInputParser(BaseInputParser):
    @staticmethod
    def _vk_code_mapper(vk_code):
        return chr(vk_code)

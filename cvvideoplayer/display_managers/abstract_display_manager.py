import abc


class DisplayManager(abc.ABC):
    @abc.abstractmethod
    def get_in_focus_window_id(self):
        ...

    @abc.abstractmethod
    def get_player_window_id(self, window_name):
        ...

    @abc.abstractmethod
    def get_screen_size(self):
        ...

    @abc.abstractmethod
    def set_icon(self, window_id, window_name):
        ...

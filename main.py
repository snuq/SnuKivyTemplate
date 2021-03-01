import os
from snu.app import *
from snu.button import *
from snu.label import *
from snu.layouts import *
from snu.popup import *
from snu.scrollview import *
from snu.slider import *
from snu.stencilview import *
from snu.textinput import *
from snu.filebrowser import *
from snu.recycleview import *
from snu.songplayer import *
from snu.smoothsetting import *
from kivy.base import EventLoop
from kivy.core.window import Window
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
app = None

Window.size = (800, 600)


class RecycleItemButton(RecycleItem, NormalButton):
    pass


class MainScreen(Screen):
    """Example Screen Widget"""

    menu = ObjectProperty()
    recycle_data_1 = ListProperty()
    recycle_data_2 = ListProperty()

    def filebrowser_popup(self):
        if app.popup:
            app.popup.dismiss()
        content = FileBrowser()
        #content = FileBrowser(file_select=False, folder_select=True, show_files=False, show_filename=False)
        #content = FileBrowser(edit_filename=True, clear_filename=False, file_select=False, default_filename='default.txt')
        content.bind(on_select=self.filebrowser_select)
        content.bind(on_cancel=self.filebrowser_cancel)
        app.popup = NormalPopup(title='Select A File', content=content, size_hint=(1, 1))
        app.popup.open()

    def filebrowser_select(self, browser):
        app.message('Selected: '+';'.join(browser.selected))
        #app.message('Selected: '+browser.edited_selected)
        app.popup.dismiss()

    def filebrowser_cancel(self, browser):
        app.message('Cancelled file selection')
        app.popup.dismiss()

    def input_popup(self):
        if app.popup:
            app.popup.dismiss()
        content = InputPopupContent(text='Input A Value')
        content.bind(on_answer=self.answer_popup)
        app.popup = NormalPopup(title='Input Popup', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 5))
        app.popup.open()

    def question_popup(self):
        if app.popup:
            app.popup.dismiss()
        content = ConfirmPopupContent(text='Are You Sure?', warn_yes=True)
        content.bind(on_answer=self.answer_popup)
        app.popup = NormalPopup(title='Question Popup', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
        app.popup.open()

    def answer_popup(self, instance, answer):
        app.popup.dismiss()
        app.message('Popup Gave Answer: '+answer)

    def message(self, instance):
        self.menu.dismiss()
        app.message('Called Menu Item: ' + instance.text)

    def on_enter(self):
        self.recycle_data_1 = [{'text': 'First'}, {'text': 'Second'}, {'text': 'Third'}, {'text': 'Fourth'}, {'text': 'Fifth'}, {'text': 'Sixth'}, {'text': 'Seventh'}]
        self.recycle_data_2 = self.recycle_data_1
        self.menu = NormalDropDown()
        for menu_button_text in ['First', 'Second', 'Third', 'Fourth']:
            menu_button = MenuButton(text=menu_button_text)
            menu_button.bind(on_release=self.message)
            self.menu.add_widget(menu_button)


class Test(NormalApp):
    screen_manager = ObjectProperty()

    def build(self):
        """Called when app is initialized, kv files are not loaded, but other data is"""

        global app
        app = self
        self.screen_manager = ScreenManager()
        self.main()
        return self.screen_manager

    def on_start(self):
        """Called when the app is started, after kv files are loaded"""

        self.set_window_size()
        self.start_keyboard_navigation()
        self.start_joystick_navigation()
        self.load_theme(1)
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def on_pause(self):
        """Called when the app is suspended or paused, need to make sure things are saved because it might not come back"""

        self.config.write()
        return True

    def on_stop(self):
        """Called when the app is about to be ended"""

        self.config.write()

    def hook_keyboard(self, window, key, *_):
        """This function receives keyboard events, such as the 'back' or 'escape' key."""

        del window
        if key == 27:  #Escape/Back key
            if Window.keyboard_height > 0:
                Window.release_all_keyboards()
                return True
            elif not self.screen_manager.current_screen:
                return False
            elif self.screen_manager.current != 'main':
                self.main()
                return True

    def main(self):
        """Switches the screen manager to the 'main' screen layout.
        Uses 'lazy' loading to ensure first startup is as quick as possible."""

        if 'main' not in self.screen_manager.screen_names:
            self.screen_manager.add_widget(MainScreen(name='main'))
        self.screen_manager.current = 'main'


if __name__ == '__main__':
    theme = {
        "name": "White",
        "button_down": [1, 1, 1, 0],
        "button_up": [1, 1, 1, 0],
        "button_text": [1, 1, 1, 0],
        "button_warn_down": [1, 1, 1, 0],
        "button_warn_up": [1, 1, 1, 0],
        "button_toggle_true": [1, 1, 1, 0],
        "button_toggle_false": [1, 1, 1, 0],
        "button_menu_up": [1, 1, 1, 0],
        "button_menu_down": [1, 1, 1, 0],
        "button_disabled": [1, 1, 1, 0],
        "button_disabled_text": [1, 1, 1, 0],
        "header_background": [1, 1, 1, 0],
        "header_text": [1, 1, 1, 0],
        "info_text": [1, 1, 1, 0],
        "info_background": [1, 1, 1, 0],
        "input_background": [1, 1, 1, 0],
        "scroller": [1, 1, 1, 0],
        "scroller_selected": [1, 1, 1, 0],
        "sidebar_resizer": [1, 1, 1, 0],
        "slider_grabber": [1, 1, 1, 0],
        "slider_background": [1, 1, 1, 0],
        "main_background": [1, 1, 1, 0],
        "menu_background": [1, 1, 1, 0],
        "area_background": [1, 1, 1, 0],
        "text": [1, 1, 1, 0],
        "disabled_text": [1, 1, 1, 0],
        "selected": [1, 1, 1, 0],
        "background": [1, 1, 1, 1],
        "selected_overlay": [1, 1, 1, 0],
    }
    themes.insert(0, theme)
    try:
        Test().run()
    except Exception as e:
        try:
            Test().save_crashlog()
        except:
            print(e)
        os._exit(-1)

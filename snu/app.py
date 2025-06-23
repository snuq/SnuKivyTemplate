import os
import time
import json
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.logger import Logger, LoggerHistory
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, StringProperty, BooleanProperty, OptionProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.dropdown import DropDown
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.settings import Settings
from kivy.utils import platform
from .navigation import Navigation
from .textinput import InputMenu
from .popup import MessagePopupContent, NormalPopup
from .button import ClickFade
from .settings import *

desktop = platform in ['win', 'linux', 'macosx', 'unknown']

themes = [
    {
        "name": "Clean And Bright",
        "button_down": [0.651, 0.651, 0.678, 1.0],
        "button_up": [0.8, 0.8, 0.8, 1.0],
        "button_text": [0.0, 0.0, 0.0, 1.0],
        "button_warn_down": [0.78, 0.33, 0.33, 1.0],
        "button_warn_up": [1.0, 0.493, 0.502, 1.0],
        "button_toggle_true": [0.31, 0.68, 0.46, 1.0],
        "button_toggle_false": [0.678, 0.651, 0.678, 1.0],
        "button_menu_up": [0.686, 0.686, 0.686, 1.0],
        "button_menu_down": [0.511, 0.52, 0.52, 1.0],
        "button_disabled": [0.686, 0.695, 0.721, 0.669],
        "button_disabled_text": [1.0, 1.0, 1.0, 0.748],
        "header_background": [1.0, 1.0, 1.0, 0.397],
        "header_text": [0.107, 0.099, 0.099, 1.0],
        "info_text": [0.0, 0.0, 0.0, 1.0],
        "info_background": [1.0, 1.0, 0.0, 0.75],
        "input_background": [1.0, 1.0, 1.0, 0.651],
        "scroller": [0.7, 0.7, 0.7, 0.388],
        "scroller_selected": [0.7, 0.7, 0.7, 0.9],
        "sidebar_resizer": [0.862, 1.0, 0.897, 1.0],
        "slider_grabber": [0.45, 0.45, 0.458, 1.0],
        "slider_background": [1.0, 1.0, 1.0, 1.0],
        "main_background": [0.616, 0.616, 0.616, 0.32],
        "menu_background": [0.529, 0.537, 0.537, 1.0],
        "text": [0.0, 0.011, 0.0, 1.0],
        "disabled_text": [0.0, 0.0, 0.0, 0.572],
        "selected": [0.239, 1.0, 0.344, 0.634],
        "active": [1.0, 0.239, 0.344, 0.5],
        "background": [1.0, 1.0, 1.0, 1.0],
        "selected_overlay": [.8, 1, .8, .33],
    },
    {
        "name": "Blue And Green",
        "button_down": [0.48, 0.59, 0.62, 1.0],
        "button_up": [0.35, 0.49, 0.53, 1.0],
        "button_text": [1.0, 1.0, 1.0, 0.9],
        "button_warn_down": [0.78, 0.33, 0.33, 1.0],
        "button_warn_up": [0.8, 0.08, 0.08, 1.0],
        "button_toggle_true": [0.31, 0.68, 0.46, 1.0],
        "button_toggle_false": [0.38, 0.38, 0.38, 1.0],
        "button_menu_up": [0.14, 0.42, 0.35, 1.0],
        "button_menu_down": [0.15, 0.84, 0.67, 1.0],
        "button_disabled": [0.28, 0.28, 0.28, 1.0],
        "button_disabled_text": [1.0, 1.0, 1.0, 0.5],
        "header_background": [0.739, 0.739, 0.8, 1.0],
        "header_text": [1.0, 1.0, 1.0, 1.0],
        "info_text": [0.0, 0.0, 0.0, 1.0],
        "info_background": [1.0, 1.0, 0.0, 0.75],
        "input_background": [0.18, 0.18, 0.27, 1.0],
        "scroller": [0.7, 0.7, 0.7, 0.4],
        "scroller_selected": [0.7, 0.7, 0.7, 0.9],
        "slider_grabber": [0.5098, 0.8745, 0.6588, 1.0],
        "slider_background": [0.546, 0.59, 0.616, 1.0],
        "main_background": [0.5, 0.5, 0.634, 0.292],
        "menu_background": [0.26, 0.29, 0.31, 1.0],
        "text": [1.0, 1.0, 1.0, 0.9],
        "disabled_text": [1.0, 1.0, 1.0, 0.5],
        "selected": [0.5098, 0.8745, 0.6588, 0.5],
        "active": [1.0, 0.239, 0.344, 0.5],
        "background": [0.0, 0.0, 0.0, 1.0],
        "selected_overlay": [.8, 1, .8, .33],
    }
]


class Theme(Widget):
    """Theme class that stores all the colors used in the interface."""

    button_down = ListProperty()
    button_up = ListProperty()
    button_text = ListProperty()
    button_warn_down = ListProperty()
    button_warn_up = ListProperty()
    button_toggle_true = ListProperty()
    button_toggle_false = ListProperty()
    button_menu_up = ListProperty()
    button_menu_down = ListProperty()
    button_disabled = ListProperty()
    button_disabled_text = ListProperty()

    header_background = ListProperty()
    header_text = ListProperty()
    info_text = ListProperty()
    info_background = ListProperty()

    input_background = ListProperty()
    scroller = ListProperty()
    scroller_selected = ListProperty()
    slider_grabber = ListProperty()
    slider_background = ListProperty()

    main_background = ListProperty()
    menu_background = ListProperty()
    text = ListProperty()
    disabled_text = ListProperty()
    selected = ListProperty()
    active = ListProperty()
    background = ListProperty()
    selected_overlay = ListProperty()

    def data_to_theme(self, data):
        """Converts a theme dictionary into the theme object that is used for displaying colors"""

        for color in data:
            if hasattr(self, color):
                new_color = data[color]
                r = float(new_color[0])
                g = float(new_color[1])
                b = float(new_color[2])
                a = float(new_color[3])
                new_color = [r, g, b, a]
                setattr(self, color, new_color)


class SimpleTheme(Theme):
    button_down = ListProperty()
    button_up = ListProperty()
    text = ListProperty()
    selected = ListProperty()
    active = ListProperty()
    background = ListProperty()

    def on_background(self, *_):
        self.header_background = self.background[:3]+[0.4]
        self.info_background = self.background[:3]+[0.7]
        self.main_background = self.background[:3]+[0.3]
        self.menu_background = self.background
        self.slider_background = self.background

    def on_text(self, *_):
        self.button_text = self.text
        self.info_text = self.text
        self.header_text = self.text
        self.button_disabled_text = self.text[:3]+[0.5]
        self.disabled_text = self.text[:3]+[0.5]

    def on_button_up(self, *_):
        self.input_background = self.button_up
        self.button_menu_up = self.button_up
        self.button_toggle_false = self.button_up
        self.slider_grabber = self.button_up

    def on_button_down(self, *_):
        self.button_disabled = self.button_down
        self.button_menu_down = self.button_down
        self.scroller = self.button_down[:3]+[0.4]
        self.button_warn_down = self.button_down

    def on_selected(self, *_):
        self.selected = self.selected[:3]+[0.7]
        self.scroller_selected = self.selected[:3]+[0.9]
        self.button_toggle_true = self.selected[:3]+[1]
        self.selected_overlay = self.selected[:3]+[0.33]

    def on_active(self, *_):
        self.active = self.active[:3]+[0.5]
        self.button_warn_up = self.active[:3]+[1]


class NormalApp(App):
    theme_index = NumericProperty(0)  #Override this to create an app with a different theme index
    popup_x = NumericProperty(640)  #Override this to set the default width of popups
    popup_size_hint_x = NumericProperty(None, allownone=True)
    about_title = "About This App"  #Title that will appear in the about popup
    about_text = 'About'  #Override this to change the text that appears in the the about popup in the settings screen
    animations = BooleanProperty(True)  #Set this to disable animations in the app
    animation_length = NumericProperty(0.2)  #Set this to change the length in seconds that animations will take
    scaling_mode = OptionProperty("divisions", options=["divisions", "pixels"])
    scale_amount = NumericProperty(15)

    list_background_odd = ListProperty([0, 0, 0, 0])
    list_background_even = ListProperty([0, 0, 0, .1])
    button_scale = NumericProperty(100)
    scrollbar_scale = NumericProperty(50)
    text_scale = NumericProperty(100)
    display_padding = NumericProperty(8)
    display_border = NumericProperty(16)
    settings_cls = AppSettings

    window_top = None
    window_left = None
    window_width = None
    window_height = None
    window_maximized = BooleanProperty(False)

    bubble = ObjectProperty(allownone=True)

    clickfade_object = ObjectProperty()
    infotext = StringProperty('')
    infotext_setter = ObjectProperty()
    popup = ObjectProperty(allownone=True)
    theme = ObjectProperty()
    button_update = BooleanProperty(False)

    navigation_enabled = BooleanProperty(True)
    selected_object = ObjectProperty(allownone=True)
    last_joystick_axis = NumericProperty(0)
    joystick_deadzone = NumericProperty(.25)
    navigation_next = [274, 12, -12]
    navigation_prev = [273, 11, -11]
    navigation_activate = [13, 0, 21]
    navigation_left = [276, 13, -13]
    navigation_right = [275, 14, -14]
    navigation_jump = [9]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme = Theme()
        self.load_theme(self.theme_index)
        Window.bind(on_resize=self.window_on_size)
        Window.bind(on_draw=self.window_on_draw)
        Window.bind(on_maximize=self.set_maximized)
        Window.bind(on_restore=self.unset_maximized)

    def on_popup(self, *_):
        self.selected_overlay_set(None)

    def start_keyboard_navigation(self):
        Window.bind(on_key_down=self.nav_key_down)
        Window.bind(on_key_up=self.nav_key_up)

    def start_joystick_navigation(self):
        Window.bind(on_joy_button_down=self.nav_joy_down)
        Window.bind(on_joy_button_up=self.nav_joy_up)
        Window.bind(on_joy_axis=self.nav_joy_axis)
        Window.bind(on_joy_hat=self.nav_joy_hat)

    def nav_joy_down(self, window, padindex, button):
        self.nav_key_down(window, scancode=(0 - button))

    def nav_joy_up(self, window, padindex, button):
        self.nav_key_up(window, scancode=(0 - button))

    def nav_joy_axis(self, window, stickid, axisid, axis):
        axis = axis / 32768
        if axis == 0:
            self.last_joystick_axis = 0
        current_time = time.time()
        if current_time - self.last_joystick_axis > 1:
            if axisid == 0:
                if axis < (0 - self.joystick_deadzone):
                    self.nav_key_down(window, scancode=276)
                    self.last_joystick_axis = current_time
                elif axis > self.joystick_deadzone:
                    self.nav_key_down(window, scancode=275)
                    self.last_joystick_axis = current_time
                else:
                    self.nav_key_up(window, scancode=276)
                    self.nav_key_up(window, scancode=275)
            elif axisid == 1:
                if axis < (0 - self.joystick_deadzone):
                    self.nav_key_down(window, scancode=273)
                    self.last_joystick_axis = current_time
                elif axis > self.joystick_deadzone:
                    self.nav_key_down(window, scancode=274)
                    self.last_joystick_axis = current_time
                else:
                    self.nav_key_up(window, scancode=273)
                    self.nav_key_up(window, scancode=274)

    def nav_joy_hat(self, window, stickid, axisid, axis):
        axis_x, axis_y = axis

        if axis_x < 0:
            self.nav_key_down(window, scancode=276)
        elif axis_x > 0:
            self.nav_key_down(window, scancode=275)
        elif axis_x == 0:
            self.nav_key_up(window, scancode=276)
            self.nav_key_up(window, scancode=275)
        if axis_y > 0:
            self.nav_key_down(window, scancode=273)
        elif axis_y < 0:
            self.nav_key_down(window, scancode=274)
        elif axis_x == 0:
            self.nav_key_up(window, scancode=273)
            self.nav_key_up(window, scancode=274)

    def nav_key_down(self, window, scancode=None, *_):
        """Detects navigation-based key presses"""

        if not self.navigation_enabled:
            return False
        if scancode in self.navigation_activate:
            self.selected_activate()
            return True
        elif scancode in self.navigation_next:
            self.selected_next()
            return True
        elif scancode in self.navigation_prev:
            self.selected_prev()
            return True
        elif scancode in self.navigation_left:
            self.selected_left()
            return True
        elif scancode in self.navigation_right:
            self.selected_right()
            return True
        elif scancode in self.navigation_jump:
            self.selected_skip()
            return True

    def nav_key_up(self, window, scancode=None, *_):
        pass

    def selected_activate(self):
        #Attempts to activate the current selected_object.
        if self.selected_object:
            self.selected_object.on_navigation_activate()

    def selected_next(self, lookin=None):
        #Convenience function for selecting the next widget in the tree
        if self.selected_object:
            if self.selected_object.on_navigation_next():
                return
        self.selected_item(lookin, True)

    def selected_prev(self, lookin=None):
        #Convenience function for selecting the previous widget in the tree
        if self.selected_object:
            if self.selected_object.on_navigation_prev():
                return
        self.selected_item(lookin, False)

    def selected_left(self):
        if self.selected_object:
            self.selected_object.on_navigation_decrease()

    def selected_right(self):
        if self.selected_object:
            self.selected_object.on_navigation_increase()

    def selected_skip(self, lookin=None):
        self.selected_item(lookin, True, skip=True)

    def selected_can_select(self, widget):
        if isinstance(widget, Navigation) and widget.navigation_selectable:
            return True
        return False

    def selected_find_active(self, root_widget, forward, found, skip=False):
        if root_widget == self.selected_object and not found:
            #The root widget is the current active! If True is returned when recursively searching, the next recursion level up will try to find the next available widget in the tree
            return True

        is_recycle = False
        recycle_layout = None
        if isinstance(root_widget, DropDown):
            pass

        if isinstance(root_widget, RecycleView):
            #Recycleview, need to do special stuff to account for some children not currently existing
            is_recycle = True
            recycle_layout = root_widget.children[0]
            children = sorted(recycle_layout.children, key=lambda x: (-x.x, x.y))
        elif isinstance(root_widget, ScreenManager):
            #Screen manager widget, we only want to iterate through the current displayed screen
            children = [root_widget.current_screen]
        else:
            #Other types of layouts, just iterate through the child list
            children = list(root_widget.children)
        if forward:
            children.reverse()
        for index, child in enumerate(children):
            is_selectable = self.selected_can_select(child)
            if is_recycle and is_selectable and found:
                self.selected_scroll_to_item(root_widget)
            if found and not child.disabled and is_selectable:
                #last widget in the tree was the old active, now this child becomes the current active
                return child
            found_active = self.selected_find_active(child, forward, found, skip=skip)
            if found_active is True:
                #This child or one of its children is selected, need to find the next possible
                found = True
                if is_recycle and is_selectable:
                    #self.selected_scroll_to_item(root_widget)
                    if skip:
                        #Skip out of this recycleview and go to the next selected
                        return True
                    if index + 1 >= len(children):
                        #This recycleview has no more children to switch to, it could be on the last child, or it may need to be scrolled
                        scrollable_x = recycle_layout.width - root_widget.width  #how many pixels of scrolling is available in the x direction
                        scrollable_y = recycle_layout.height - root_widget.height
                        if root_widget.do_scroll_x and scrollable_x > 0:  #root can scroll in horizontal
                            if forward and root_widget.scroll_x > 0:  #root can and should scroll forward
                                root_widget.scroll_x = max(root_widget.scroll_x - (self.selected_object.width / scrollable_x), 0)
                                return self.selected_object
                            elif not forward and root_widget.scroll_x < 1:  #root can and should scroll backward
                                root_widget.scroll_x = min(root_widget.scroll_x + (self.selected_object.width / scrollable_x), 1)
                                return self.selected_object
                        elif root_widget.do_scroll_y and scrollable_y > 0:  #root can scroll in vertical
                            if forward and root_widget.scroll_y > 0:  #root can and should scroll forward
                                root_widget.scroll_y = max(root_widget.scroll_y - (self.selected_object.height / scrollable_y), 0)
                                return self.selected_object
                            elif not forward and root_widget.scroll_y < 1:  #root can and should scroll backward
                                root_widget.scroll_y = min(root_widget.scroll_y + (self.selected_object.height / scrollable_y), 1)
                                return self.selected_object

            elif found_active is None:
                #active not found in this child or its children, move on to the next child
                continue
            else:
                #the next active was found, return it to go up one recursion level
                return found_active

        if found:
            #Tried to find the next active but couldnt, continue search in the next tree up
            return True
        return None  #The active was not found in this tree at all

    def selected_get_root(self):
        #determine the best root widget to look for items to navigate

        root_window = self.root.get_parent_window()
        if len(root_window.children) == 1:
            return root_window.children[0]
        for item in reversed(root_window.children):
            if isinstance(item, DropDown):
                return item
        for item in reversed(root_window.children):
            if isinstance(item, ModalView):
                return item
        for item in reversed(root_window.children):
            if isinstance(item, Settings):
                return item
        return root_window

    def selected_item(self, lookin, forward, skip=None):
        if lookin is None:
            lookin = self.selected_get_root()
        active = self.selected_find_active(lookin, forward, False, skip=skip)
        if active is True or active is None:
            active = self.selected_find_active(lookin, forward, True, skip=skip)
        self.selected_overlay_set(active)

    def selected_clear(self):
        self.selected_overlay_set(None)

    def selected_overlay_set(self, widget):
        #This function will actually set the given widget as the current selected, also ensures it is scrolled to if in a Scroller

        if self.selected_object is not None:
            self.selected_object.on_navigation_deselect()
        self.selected_object = widget
        if widget is None:
            return
        self.selected_object.on_navigation_select()
        self.selected_scroll_to_item(widget)

    def selected_scroll_to_item(self, widget):
        parent = widget.parent
        while parent is not None:
            if parent.parent == parent:
                break
            if hasattr(parent, 'scroll_y'):
                try:
                    if parent.children[0].height < parent.height:
                        parent.scroll_y = 1
                    else:
                        parent.scroll_to(widget, animate=False, padding=20)
                except:
                    pass
                break
            parent = parent.parent

    def clickfade(self, widget, mode='opacity'):
        try:
            Window.remove_widget(self.clickfade_object)
        except:
            pass
        if self.clickfade_object is None:
            self.clickfade_object = ClickFade()
        self.clickfade_object.size = widget.size
        self.clickfade_object.pos = widget.to_window(*widget.pos)
        self.clickfade_object.begin(mode)
        Window.add_widget(self.clickfade_object)

    def load_theme(self, theme):
        """Load and display a theme from the current presets"""

        try:
            data = themes[theme]
        except:
            data = theme
        self.theme.data_to_theme(data)
        self.button_update = not self.button_update

    def set_maximized(self, *_):
        self.window_maximized = True

    def unset_maximized(self, *_):
        self.window_maximized = False

    def window_init_position(self, *_):
        #Set window position from saved settings
        self.window_top = int(self.config.get('Settings', 'window_top'))
        self.window_left = int(self.config.get('Settings', 'window_left'))
        Window.left = self.window_left
        Window.top = self.window_top

    @mainthread
    def window_on_size(self, *_):
        #called when Window.on_resize happens

        if self.window_height is None:
            #app just started, window is uninitialized, load in stored size if enabled
            if self.config.getboolean("Settings", "remember_window") and desktop:
                self.window_maximized = self.config.getboolean('Settings', 'window_maximized')
                self.window_width = int(self.config.get('Settings', 'window_width'))
                self.window_height = int(self.config.get('Settings', 'window_height'))
                Window.size = (self.window_width, self.window_height)
                if self.window_maximized:
                    Window.maximize()
                else:
                    Clock.schedule_once(self.window_init_position)  #Need to delay this to ensure window has time to resize first
            else:
                self.window_width = Window.size[0]
                self.window_height = Window.size[1]
            self.rescale_interface(height=self.window_height)  #Need to pass in actual window height because Window.size isnt always showing correct size yet
        else:
            #Window is resized by user
            self.config.set("Settings", "window_maximized", 1 if self.window_maximized else 0)
            self.check_window()

    def check_window(self, *_):
        if Window.left != self.window_left and self.window_left is not None:  #Left changed
            if not self.window_maximized:
                self.window_left = Window.left
                self.config.set('Settings', 'window_left', self.window_left)
        if Window.top != self.window_top and self.window_top is not None:  #Top changed
            if not self.window_maximized:
                self.window_top = Window.top
                self.config.set('Settings', 'window_top', self.window_top)
        self.popup_x = Window.width
        if Window.width != self.window_width and self.window_width is not None:  #Width changed
            if not self.window_maximized:
                self.window_width = Window.width
                self.config.set('Settings', 'window_width', self.window_width)
        if Window.height != self.window_height and self.window_height is not None:  #Height changed
            if not self.window_maximized:
                self.window_height = Window.height
                self.config.set('Settings', 'window_height', self.window_height)
            self.rescale_interface()

    @mainthread
    def window_on_draw(self, *_):
        #need to have this because kivy on windows will not trigger Window.on_resize on startup...
        if self.window_height is None:
            #trigger this just in case window hasnt triggered the on resize event
            self.window_on_size()

    def rescale_interface(self, height=None):
        """Updates variables dependent on screen height"""
        if height is None:
            height = Window.size[1]
        if self.scaling_mode == 'divisions':
            self.button_scale = int((height / self.scale_amount) * int(self.config.get("Settings", "buttonsize")) / 100)
        elif self.scaling_mode == 'pixels':
            self.button_scale = int(self.scale_amount * (int(self.config.get("Settings", "buttonsize")) / 100))
        self.text_scale = int((self.button_scale / 3) * int(self.config.get("Settings", "textsize")) / 100)
        self.scrollbar_scale = int(((self.button_scale / 2) * (int(self.config.get("Settings", "scrollersize")) / 100)))
        self.display_border = self.button_scale / 3
        self.display_padding = self.button_scale / 4

    def popup_bubble(self, text_input, pos):
        """Calls the text input right-click popup menu"""

        self.close_bubble()
        text_input.unfocus_on_touch = False
        self.bubble = InputMenu(owner=text_input)
        window = self.root_window
        window.add_widget(self.bubble)
        posx = pos[0]
        posy = pos[1]
        #check position to ensure its not off screen
        if posx + self.bubble.width > window.width:
            posx = window.width - self.bubble.width
        if posy + self.bubble.height > window.height:
            posy = window.height - self.bubble.height
        self.bubble.pos = [posx, posy]

    def close_bubble(self, *_):
        """Closes the text input right-click popup menu"""

        if self.bubble:
            self.bubble.owner.unfocus_on_touch = True
            window = self.root_window
            window.remove_widget(self.bubble)
            self.bubble = None

    def message(self, text, timeout=20):
        """Sets the app.infotext variable to a specific message, and clears it after a set amount of time."""

        self.infotext = text
        if self.infotext_setter:
            self.infotext_setter.cancel()
        self.infotext_setter = Clock.schedule_once(self.clear_message, timeout)

    def clear_message(self, *_):
        """Clear the app.infotext variable"""

        self.infotext = ''

    def about(self):
        """Opens a special message popup with the app's about text in it"""

        if self.popup:
            self.popup.dismiss()
        self.popup = AboutPopup(size_hint=(self.popup_size_hint_x, None), width=self.popup_x)
        self.popup.open()
        #self.message_popup(text, title=title)

    def message_popup(self, text, title='Notification'):
        """Opens a basic message popup with an ok button"""

        if self.popup:
            self.popup.dismiss()
        content = MessagePopupContent(text=text)
        self.popup = NormalPopup(title=title, content=content, size_hint=(self.popup_size_hint_x, None), size=(self.popup_x, self.button_scale * 4))
        self.popup.open()

    def build_config(self, config):
        """Setup config file if it is not found"""

        config.setdefaults(
            'Settings', {
                'remember_window': 1,
                'buttonsize': 100,
                'textsize': 100,
                'scrollersize': 100,
                'window_maximized': 0,
                'window_top': 50,
                'window_left': 100,
                'window_width': 800,
                'window_height': 600,
            })

    def build_settings(self, settings):
        """Kivy settings dialog panel
        settings types: title, bool, numeric, options, string, path"""

        settingspanel = []
        settingspanel.append({
            "type": "aboutbutton",
            "title": "",
            "section": "Settings",
            "key": "buttonsize"
        })
        settingspanel.append({
            "type": "title",
            "title": "General Settings"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Button Scale",
            "desc": "Scale percentage for interface elements",
            "section": "Settings",
            "key": "buttonsize"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Text Scale",
            "desc": "Scale percentage for text in the interface",
            "section": "Settings",
            "key": "textsize"
        })
        settingspanel.append({
            "type": "numeric",
            "title": "Scrollbar Scale",
            "desc": "Scale percentage for scrollbars, 100% is half the button size",
            "section": "Settings",
            "key": "scrollersize"
        })
        if desktop:
            settingspanel.append({
                "type": "bool",
                "title": "Remember Window",
                "desc": "Recall the last used window size and position on startup",
                "section": "Settings",
                "key": "remember_window"
            })
        settings.add_json_panel('Settings', self.config, data=json.dumps(settingspanel))

    def on_config_change(self, config, section, key, value):
        """Called when the configuration file is changed"""

        self.rescale_interface()

    def get_crashlog_file(self):
        """Returns the crashlog file path and name"""

        savefolder_loc = os.path.split(self.get_application_config())[0]
        crashlog = os.path.join(savefolder_loc, 'testapp_crashlog.txt')
        return crashlog

    def save_crashlog(self):
        """Saves the just-generated crashlog to the current default location"""

        import traceback
        crashlog = self.get_crashlog_file()
        log_history = reversed(LoggerHistory.history)
        crashlog_file = open(crashlog, 'w')
        for log_line in log_history:
            log_line = log_line.msg
            crashlog_file.write(log_line+'\n')
        traceback_text = traceback.format_exc()
        print(traceback_text)
        crashlog_file.write(traceback_text)
        crashlog_file.close()

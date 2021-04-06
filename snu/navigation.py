from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.graphics import Color, Rectangle


class Navigation(Widget):
    """Mixin class that adds keyboard/joystick navigation functionality to the mixed widget, when paired with the NormalApp class"""

    navigation_selectable = BooleanProperty(True)
    navigation_overlay_color = None
    navigation_overlay_box = None

    def on_navigation_activate(self):
        #Override this function for custom functionality of the 'enter' function of the keyboard navigation.
        try:
            self.trigger_action()
        except:
            pass
        try:
            self.focus = not self.focus
        except:
            pass

    def on_navigation_next(self):
        #Override this function and return True to 'lock' the next navigation function to this widget
        return False

    def on_navigation_prev(self):
        #Override this function and return True to 'lock' the previous navigation function to this widget
        return False

    def on_navigation_increase(self):
        #Override this function to allow the keyboard navigation 'right' to control this widget.
        pass

    def on_navigation_decrease(self):
        #Override this function to allow the keyboard navigation 'left' to control this widget.
        pass

    def on_navigation_select(self):
        app = App.get_running_app()
        self.navigation_overlay_color = Color(rgba=app.theme.selected_overlay)
        app.theme.bind(selected_overlay=self.set_navigation_overlay_color)
        self.navigation_overlay_box = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.set_navigation_overlay_size)
        self.bind(pos=self.set_navigation_overlay_pos)
        self.canvas.after.add(self.navigation_overlay_color)
        self.canvas.after.add(self.navigation_overlay_box)

    def on_navigation_deselect(self):
        self.canvas.after.remove(self.navigation_overlay_color)
        self.canvas.after.remove(self.navigation_overlay_box)
        self.unbind(size=self.set_navigation_overlay_size)
        self.unbind(pos=self.set_navigation_overlay_pos)
        app = App.get_running_app()
        app.theme.unbind(selected_overlay=self.set_navigation_overlay_color)
        self.navigation_overlay_color = None
        self.navigation_overlay_box = None

    def set_navigation_overlay_size(self, instance, value):
        self.navigation_overlay_box.size = value

    def set_navigation_overlay_pos(self, instance, value):
        self.navigation_overlay_box.pos = value

    def set_navigation_overlay_color(self, instance, value):
        if self.navigation_overlay_color:
            self.navigation_overlay_color.rgba = value

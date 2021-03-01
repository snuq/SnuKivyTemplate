from kivy.graphics.transformation import Matrix
from kivy.properties import BooleanProperty
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from kivy.lang.builder import Builder
Builder.load_string("""
<SmallSpacer>:
    size_hint: None, None
    height: int(app.button_scale / 4)
    width: int(app.button_scale / 4)

<MediumSpacer>:
    size_hint: None, None
    height: int(app.button_scale / 2)
    width: int(app.button_scale / 2)

<LargeSpacer>:
    size_hint: None, None
    height: app.button_scale
    width: app.button_scale

<HeaderBase>:
    size_hint_y: None
    orientation: 'horizontal'

<Holder>:
    orientation: 'horizontal'
    size_hint_y: None
    height: app.button_scale

<Header>:
    canvas.before:
        Color:
            rgba: app.theme.header_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/headerbg.png'
    height: app.button_scale

<MainArea>:
    canvas.before:
        Color:
            rgba: app.theme.main_background
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'data/mainbg.png'
    size_hint: 1, 1
    orientation: 'vertical'
""")


class SmallSpacer(Widget):
    pass


class MediumSpacer(Widget):
    pass


class LargeSpacer(Widget):
    pass


class HeaderBase(BoxLayout):
    pass


class Header(HeaderBase):
    pass


class Holder(BoxLayout):
    pass


class MainArea(BoxLayout):
    pass


class LimitedScatterLayout(ScatterLayout):
    """Custom ScatterLayout that won't allow sub-widgets to be moved out of the visible area,
    and will not respond to touches outside of the visible area.
    """

    bypass = BooleanProperty(False)

    def on_bypass(self, instance, bypass):
        if bypass:
            self.transform = Matrix()

    def on_transform_with_touch(self, touch):
        """Modified to not allow widgets to be moved out of the visible area."""

        width = self.bbox[1][0]
        height = self.bbox[1][1]
        scale = self.scale

        local_bottom = self.bbox[0][1]
        local_left = self.bbox[0][0]
        local_top = local_bottom+height
        local_right = local_left+width

        local_xmax = width/scale
        local_xmin = 0
        local_ymax = height/scale
        local_ymin = 0

        if local_right < local_xmax:
            self.transform[12] = local_xmin - (width - local_xmax)
        if local_left > local_xmin:
            self.transform[12] = local_xmin
        if local_top < local_ymax:
            self.transform[13] = local_ymin - (height - local_ymax)
        if local_bottom > local_ymin:
            self.transform[13] = local_ymin

    def on_touch_down(self, touch):
        """Modified to only register touches in visible area."""

        if self.bypass:
            for child in self.children[:]:
                if child.dispatch('on_touch_down', touch):
                    return True
        else:
            if self.collide_point(*touch.pos):
                super(LimitedScatterLayout, self).on_touch_down(touch)

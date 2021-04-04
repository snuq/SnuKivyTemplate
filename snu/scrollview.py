from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty

from kivy.lang.builder import Builder
Builder.load_string("""
<Scroller>:
    always_overscroll: False
    scroll_distance: 10
    scroll_timeout: 100
    bar_width: app.scrollbar_scale
    bar_color: app.theme.scroller_selected
    bar_inactive_color: app.theme.scroller
    scroll_type: ['bars', 'content']
""")


class Scroller(ScrollView):
    """Generic scroller container widget."""
    pass


class ScrollViewCentered(ScrollView):
    """Special ScrollView that begins centered"""

    def __init__(self, **kwargs):
        self.scroll_x = 0.5
        self.scroll_y = 0.5
        super(ScrollViewCentered, self).__init__(**kwargs)

    def window_to_parent(self, x, y, relative=False):
        return self.to_parent(*self.to_widget(x, y))


class ScrollWrapper(Scroller):
    """Special ScrollView that allows ScrollViews inside it to respond to touches.
    The internal ScrollViews must be added to the 'masks' list"""

    masks = ListProperty()

    def on_touch_down(self, touch):
        for mask in self.masks:
            coords = mask.to_parent(*mask.to_widget(*touch.pos))
            collide = mask.collide_point(*coords)
            if collide:
                touch.apply_transform_2d(mask.to_widget)
                touch.apply_transform_2d(mask.to_parent)
                mask.on_touch_down(touch)
                return True
        super(ScrollWrapper, self).on_touch_down(touch)

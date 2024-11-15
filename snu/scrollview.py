from kivy.uix.scrollview import ScrollView
from kivy.animation import Animation
from kivy.properties import ListProperty, AliasProperty, NumericProperty, ObjectProperty, BooleanProperty, ColorProperty
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.stencilview import StencilView
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

<ScrollBarX>:
    _handle_x_pos: self.x + self.width * self.hbar[0], self.y
    _handle_x_size: self.width * self.hbar[1], self.height
    canvas:
        Color:
            rgba: self._bar_color if (self.viewport_size[0] > self.scroller_size[0]) else [0, 0, 0, 0]
        RoundedRectangle:
            radius: [self.rounding]
            pos: root._handle_x_pos or (0, 0)
            size: root._handle_x_size or (0, 0)
    is_active: not self.viewport_size[0] <= self.scroller_size[0]
    bar_color: app.theme.scroller_selected
    bar_inactive_color: app.theme.scroller
    size_hint_y: None
    orientation: 'horizontal'
    height: 0 if (not self.is_active and self.autohide) else app.scrollbar_scale
    opacity: 0 if (not self.is_active and self.autohide) else 1

<ScrollBarY>:
    _handle_y_pos: self.x, self.y + self.height * self.vbar[0]
    _handle_y_size: self.width, self.height * self.vbar[1]
    canvas:
        Color:
            rgba: self._bar_color if (self.viewport_size[1] > self.scroller_size[1]) else [0, 0, 0, 0]
        RoundedRectangle:
            radius: [self.rounding]
            pos: root._handle_y_pos or (0, 0)
            size: root._handle_y_size or (0, 0)
    is_active: not self.viewport_size[1] <= self.scroller_size[1]
    bar_color: app.theme.scroller_selected
    bar_inactive_color: app.theme.scroller
    size_hint_x: None
    orientation: 'vertical'
    width: 0 if (not self.is_active and self.autohide) else app.scrollbar_scale
    opacity: 0 if (not self.is_active and self.autohide) else 1
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


class ScrollBar(BoxLayout):
    """
    Base class for a basic scrollbar widget that can control a set ScrollView.
    This class itself should not be used, use ScrollBarX or ScrollBarY for horizontal or vertical scrolling.
    The 'scroller' variable must be set to the ScrollView widget that should be controlled.
    'bar_color' and 'bar_inactive_color' can be set to a rgba color.
    """

    scroll = NumericProperty()
    scroller = ObjectProperty(allownone=True)
    scroll_wheel_distance = NumericProperty('20sp')
    bar_color = ColorProperty([.7, .7, .7, .9])
    bar_inactive_color = ColorProperty([.7, .7, .7, .2])
    viewport_size = ListProperty([0, 0])
    scroller_size = ListProperty([0, 0])
    rounding = NumericProperty(0)
    is_active = BooleanProperty(True)
    autohide = BooleanProperty(True)

    _bar_color = ListProperty([0, 0, 0, 0])
    _bind_inactive_bar_color_ev = None

    def _set_scroller_size(self, instance, value):
        self.scroller_size = value

    def _set_viewport_size(self, instance, value):
        self.viewport_size = value

    def _set_scroll(self, instance, value):
        self.scroll = value

    def _bind_inactive_bar_color(self, *l):
        self.funbind('bar_color', self._change_bar_color)
        self.fbind('bar_inactive_color', self._change_bar_color)
        Animation(_bar_color=self.bar_inactive_color, d=.5, t='out_quart').start(self)

    def _change_bar_color(self, inst, value):
        self._bar_color = value

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_bar_color()

    def jump_bar(self, pos):
        pass

    def on_touch_down(self, touch):
        if not self.disabled and self.collide_point(*touch.pos):
            self.jump_bar(touch.pos)
            touch.grab(self)
            if 'button' in touch.profile and touch.button.startswith('scroll'):
                btn = touch.button
                scroll_direction = ''
                if btn in ('scrollup', 'scrollright'):
                    scroll_direction = 'up'
                elif btn in ('scrolldown', 'scrollleft'):
                    scroll_direction = 'down'
                return self.wheel_scroll(scroll_direction)

            self.do_touch_scroll(touch)
            return True

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self.do_touch_scroll(touch)

    def do_touch_scroll(self, touch):
        pass

    def on_scroller(self, instance, value):
        if value:
            value.bind(size=self._set_scroller_size)
            value.bind(viewport_size=self._set_viewport_size)
            self.scroller_size = value.size
            self.viewport_size = value.viewport_size

    def update_bar_color(self):
        ev = self._bind_inactive_bar_color_ev
        if ev is None:
            ev = self._bind_inactive_bar_color_ev = Clock.create_trigger(
                self._bind_inactive_bar_color, .5)
        self.funbind('bar_inactive_color', self._change_bar_color)
        Animation.stop_all(self, '_bar_color')
        self.fbind('bar_color', self._change_bar_color)
        self._bar_color = self.bar_color
        ev()

    def wheel_scroll(self, direction):
        return False


class ScrollBarX(ScrollBar):
    """Horizontal scrollbar widget.  See 'ScrollBar' for more information."""

    scroll = NumericProperty(0.)
    def _get_hbar(self):
        if self.width > 0:
            min_width = self.height / self.width  #prevent scroller size from being too small
        else:
            min_width = 0
        vw = self.viewport_size[0]
        w = self.scroller_size[0]
        if vw < w or vw == 0:
            return 0, 1.
        pw = max(min_width, w / float(vw))
        sx = min(1.0, max(0.0, self.scroll))
        px = (1. - pw) * sx
        return px, pw
    hbar = AliasProperty(_get_hbar, bind=('scroller_size', 'scroll', 'viewport_size', 'width'), cache=True)

    def in_hbar(self, pos_x):
        local_x = pos_x - self.x
        local_per = local_x / self.width
        hbar = self.hbar
        hbar_top = hbar[0] + hbar[1]
        hbar_bottom = hbar[0]
        half_hbar_height = hbar[1] / 2
        if local_per > hbar_top:
            return local_per - hbar_top + half_hbar_height
        elif local_per < hbar_bottom:
            return local_per - hbar_bottom - half_hbar_height
        else:  #hbar_top > local_per > hbar_bottom:
            return 0

    def jump_bar(self, pos):
        position = self.in_hbar(pos[0])
        self.scroller.scroll_x += position

    def on_scroller(self, instance, value):
        super().on_scroller(instance, value)
        if value:
            value.bind(scroll_x=self._set_scroll)
            self.scroll = value.scroll_x

    def on_scroll(self, instance, value):
        if self.scroller is not None:
            self.scroller.scroll_x = value

    def do_touch_scroll(self, touch):
        self.update_bar_color()
        scroll_scale = (self.width - self.width * self.hbar[1])
        if scroll_scale == 0:
            return
        scroll_amount = touch.dx / scroll_scale
        self.scroll = min(max(self.scroll + scroll_amount, 0.), 1.)

    def wheel_scroll(self, direction):
        if (direction == 'up' and self.scroll >= 1) or (direction == 'down' and self.scroll <= 0):
            return False

        if self.viewport_size[0] > self.scroller_size[0]:
            scroll_percent = self.scroll_wheel_distance / self.viewport_size[0]
            if direction == 'up':
                new_scroll = self.scroll - scroll_percent
            else:
                new_scroll = self.scroll + scroll_percent
            self.scroll = min(max(new_scroll, 0), 1)
            return True
        return False


class ScrollBarY(ScrollBar):
    """Vertical scrollbar widget.  See 'ScrollBar' for more information."""

    scroll = NumericProperty(1.)
    def _get_vbar(self):
        if self.height > 0:
            min_height = self.width / self.height  #prevent scroller size from being too small
        else:
            min_height = 0
        vh = self.viewport_size[1]
        h = self.scroller_size[1]
        if vh < h or vh == 0:
            return 0, 1.
        ph = max(min_height, h / float(vh))
        sy = min(1.0, max(0.0, self.scroll))
        py = (1. - ph) * sy
        return py, ph
    vbar = AliasProperty(_get_vbar, bind=('scroller_size', 'scroll', 'viewport_size', 'height'), cache=True)

    def in_vbar(self, pos_y):
        local_y = pos_y - self.y
        local_per = local_y / self.height
        vbar = self.vbar
        vbar_top = vbar[0] + vbar[1]
        vbar_bottom = vbar[0]
        half_vbar_height = vbar[1] / 2
        if local_per > vbar_top:
            return local_per - vbar_top + half_vbar_height
        elif local_per < vbar_bottom:
            return local_per - vbar_bottom - half_vbar_height
        else:  #vbar_top > local_per > vbar_bottom:
            return 0

    def jump_bar(self, pos):
        position = self.in_vbar(pos[1])
        self.scroller.scroll_y += position

    def on_scroller(self, instance, value):
        super().on_scroller(instance, value)
        if value:
            value.bind(scroll_y=self._set_scroll)
            self.scroll = value.scroll_y

    def on_scroll(self, instance, value):
        if self.scroller is not None:
            self.scroller.scroll_y = value

    def do_touch_scroll(self, touch):
        self.update_bar_color()
        scroll_scale = (self.height - self.height * self.vbar[1])
        if scroll_scale == 0:
            return
        scroll_amount = touch.dy / scroll_scale
        self.scroll = min(max(self.scroll + scroll_amount, 0.), 1.)

    def wheel_scroll(self, direction):
        if (direction == 'up' and self.scroll >= 1) or (direction == 'down' and self.scroll <= 0):
            return False

        if self.viewport_size[1] > self.scroller_size[1]:
            scroll_percent = self.scroll_wheel_distance / self.viewport_size[1]
            if direction == 'up':
                new_scroll = self.scroll - scroll_percent
            else:
                new_scroll = self.scroll + scroll_percent
            self.scroll = min(max(new_scroll, 0), 1)
            return True
        return False


class TouchScroller(ScrollView):
    """
    Modified version of Kivy's ScrollView widget, removes scrollbars and allows for finer control over touch events.
    allow_middle_mouse: set this to True to enable scrolling with the middle mouse button (blocks middle mouse clicks on child widgets).
    allow_flick: set this to True to enable touch 'flicks' to scroll the view.
    allow_drag: Set this to True to enable click-n-drag scrolling within the scrollview itself.
    allow_wheel: set this to True to enable scrolling via the mouse wheel.
    masks: ListProperty, add any child widgets to this, and they will receive all touches on them, blocking any touch controlls of this widget within their bounds.
    """

    bar_width = NumericProperty(0)
    scroll_distance = NumericProperty(10)
    scroll_timeout = NumericProperty(100)
    scroll_wheel_distance = NumericProperty('20sp')

    allow_middle_mouse = BooleanProperty(True)
    allow_flick = BooleanProperty(True)
    allow_drag = BooleanProperty(True)
    allow_wheel = BooleanProperty(True)
    masks = ListProperty()

    _touch_moves = 0
    _touch_delay = None
    _start_scroll_x = 0
    _start_scroll_y = 0

    def transformed_touch(self, touch, touch_type='down'):
        touch.push()
        touch.apply_transform_2d(self.to_local)
        #touch.apply_transform_2d(self.to_widget)
        if touch_type == 'down':
            ret = StencilView.on_touch_down(self, touch)
        elif touch_type == 'up':
            ret = StencilView.on_touch_up(self, touch)
        else: #touch_type == 'move'
            ret = StencilView.on_touch_move(self, touch)
        touch.pop()
        return ret

    def scroll_to_point(self, per_x, per_y, animate=True):
        sxp = min(1, max(0, per_x))
        syp = min(1, max(0, per_y))
        Animation.stop_all(self, 'scroll_x', 'scroll_y')
        if animate:
            if animate is True:
                animate = {'d': 0.2, 't': 'out_quad'}
            Animation(scroll_x=sxp, scroll_y=syp, **animate).start(self)
        else:
            self.scroll_x = sxp
            self.scroll_y = syp

    def scroll_by(self, per_x, per_y, animate=True):
        self.scroll_to_point(self.scroll_x + per_x, self.scroll_y + per_y, animate=animate)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            for widget in self.masks:
                touch.push()
                #touch.apply_transform_2d(self.to_local)
                touch.apply_transform_2d(self.to_widget)
                if widget.collide_point(*touch.pos):
                    return widget.on_touch_down(touch)
                touch.pop()

            #delay touch to check if scroll is initiated
            if 'button' in touch.profile and touch.button.startswith('scroll'):
                if self.allow_wheel:
                    touch.grab(self)
                    btn = touch.button
                    return self.wheel_scroll(btn)
                else:
                    return self.transformed_touch(touch)

            touch.grab(self)
            self._touch_delay = None
            self._touch_moves = 0

            self._start_scroll_x = self.scroll_x
            self._start_scroll_y = self.scroll_y
            if self.allow_middle_mouse and 'button' in touch.profile and touch.button == 'middle':
                return True
            if self.allow_drag or self.allow_flick:
                self._touch_delay = Clock.schedule_once(partial(self._on_touch_down_delay, touch), (self.scroll_timeout / 1000))
            else:
                return self.transformed_touch(touch)
            return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
        if self.allow_middle_mouse and 'button' in touch.profile and touch.button == 'middle':
            return True
        if self._touch_delay:
            self._touch_delay.cancel()
            self._touch_delay = None
            dx, dy = self.touch_moved_distance(touch)
            if self.allow_flick and (dx or dy):
                per_x = self.scroll_x - ((dx * 2) / self.width)
                per_y = self.scroll_y - ((dy * 2) / self.height)
                self.scroll_to_point(per_x, per_y)
                self._touch_delay = None
                return True
            else:
                self.transformed_touch(touch)
        return self.transformed_touch(touch, 'up')

    def _on_touch_down_delay(self, touch, *largs):
        self._touch_delay = None
        dx, dy = self.touch_moved_distance(touch)
        if self.allow_drag and (dx or dy):
            #user has satisfied the requirements for scrolling
            return True
        else:
            touch.ungrab(self)
            #Need to fix the touch position since it has been translated by this widget's position somehow...
            touch.push()
            touch.apply_transform_2d(self.to_widget)
            touch.apply_transform_2d(self.to_parent)
            return self.transformed_touch(touch)

    def on_touch_move(self, touch):
        middle_button = 'button' in touch.profile and touch.button == 'middle'
        if not self.allow_drag and not middle_button:
            return
        if self._touch_delay:
            always = False
        else:
            always = True
        if touch.grab_current == self:
            self._touch_moves += 1
            if self._touch_moves == 1 and not middle_button:
                animate = True
            else:
                animate = False
            dx, dy = self.touch_moved_distance(touch, always=always)
            if self.viewport_size[0] != self.width:
                per_x = self._start_scroll_x + (dx / (self.width - self.viewport_size[0]))
            else:
                per_x = self._start_scroll_x
            if self.viewport_size[1] != self.height:
                per_y = self._start_scroll_y + (dy / (self.height - self.viewport_size[1]))
            else:
                per_y = self._start_scroll_y
            self.scroll_to_point(per_x, per_y, animate=animate)

    def touch_moved_distance(self, touch, always=False):
        #determines if the touch has moved the required distance to allow for scrolling
        can_move_x = self.viewport_size[0] > self.width
        can_move_y = self.viewport_size[1] > self.height
        dx = touch.pos[0] - touch.opos[0]
        dy = touch.pos[1] - touch.opos[1]
        if can_move_x and (always or abs(dx) >= self.scroll_distance):
            pass
        else:
            dx = 0
        if can_move_y and (always or abs(dy) >= self.scroll_distance):
            pass
        else:
            dy = 0

        return dx, dy

    def wheel_scroll(self, btn):
        can_move_x = self.viewport_size[0] > self.width
        can_move_y = self.viewport_size[1] > self.height
        scroll_percent_x = self.scroll_wheel_distance / self.viewport_size[0]
        scroll_percent_y = self.scroll_wheel_distance / self.viewport_size[1]

        if can_move_x and can_move_y:
            if btn == 'scrollup':
                self.scroll_by(0, scroll_percent_y, animate=False)
            elif btn == 'scrolldown':
                self.scroll_by(0, 0 - scroll_percent_y, animate=False)
            elif btn == 'scrollleft':
                self.scroll_by(scroll_percent_x, 0, animate=False)
            elif btn == 'scrollright':
                self.scroll_by(0 - scroll_percent_x, 0, animate=False)
        elif can_move_x:
            if btn in ['scrolldown', 'scrollleft']:
                self.scroll_by(scroll_percent_x, 0, animate=False)
            elif btn in ['scrollup', 'scrollright']:
                self.scroll_by(0 - scroll_percent_x, 0, animate=False)
        elif can_move_y:
            if btn in ['scrolldown', 'scrollright']:
                self.scroll_by(0, scroll_percent_y, animate=False)
            elif btn in ['scrollup', 'scrollleft']:
                self.scroll_by(0, 0 - scroll_percent_y, animate=False)
        return True

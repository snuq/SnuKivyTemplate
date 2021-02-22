'''
RouletteScrollEffect
===================

This is a subclass of :class:`kivy.effects.ScrollEffect` that simulates the 
motion of a roulette, or a notched wheel (think Wheel of Fortune). It is
primarily designed for emulating the effect of the iOS and android date pickers.

Usage
-----

Here's an example of using :class:`RouletteScrollEffect` for a 
:class:`kivy.uix.scrollview.ScrollView`:: 

    if __name__ == '__main__':
        # example modified from the scrollview example
    
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.button import Button
        from kivy.uix.scrollview import ScrollView
    
        # preparing a gridlayout inside a scrollview
        layout = GridLayout(cols=1, padding=10,
                size_hint=(None, None), width=500)
    
        layout.bind(minimum_height=layout.setter('height'))
    
        for i in range(30):
            btn = Button(text=str(i), size=(480, 40),
                         size_hint=(None, None))
            layout.add_widget(btn)
    
        root = ScrollView(size_hint=(None, None), size=(500, 320),
                pos_hint={'center_x': .5, 'center_y': .5}
                , do_scroll_x=False)
        root.add_widget(layout)
        
        # preparation complete. Now add the new scroll effect!
        root.effect_y = RouletteScrollEffect(anchor=20, interval=40)

        runTouchApp(root)
        
Here the :class:`ScrollView` scrolls through a series of buttons with height
40. We then attached a :class:`RouletteScrollEffect` with interval 40, 
corresponding to the button heights. This allows the scrolling to stop at
the same offset no matter where it stops. The :attr:`RouletteScrollEffect.anchor`
adjusts this offset. 

Customizations
--------------

Other settings that can be played with include 
:attr:`RouletteScrollEffect.pull_duration`, 
:attr:`RouletteScrollEffect.coasting_alpha`,
:attr:`RouletteScrollEffect.pull_back_velocity`, and
:attr:`RouletteScrollEffect.terminal_velocity`. See their module documentations
for details.

:class:`RouletteScrollEffect` has one event ``on_coasted_to_stop`` that
is fired when the roulette stops, "making a selection". It can be listened to
for handling or cleaning up choice making.
'''

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.effects.scroll import ScrollEffect
from kivy.properties import NumericProperty, AliasProperty, ObjectProperty
from math import ceil, floor, exp

class RouletteScrollEffect(ScrollEffect):
    __events__ = ('on_coasted_to_stop',)
    
    drag_threshold = NumericProperty(0)
    '''overrides :attr:`ScrollEffect.drag_threshold` to abolish drag threshold.
    
    .. note::
        If using this with a :class:`Roulette` or other :class:`Tickline`
        subclasses, what matters is :attr:`Tickline.drag_threshold`, which
        is passed to this attribute in the end.
    '''
    
    min = NumericProperty(-float('inf'))
    max = NumericProperty(float('inf'))

    interval = NumericProperty(50)
    '''the interval of the values of the "roulette".'''
    
    anchor = NumericProperty(0)
    '''one of the valid stopping values.'''

    pull_duration = NumericProperty(.2)
    '''when movement slows around a stopping value, an animation is used
    to pull it toward the nearest value. :attr:`pull_duration` is the duration
    used for such an animation.'''
    
    coasting_alpha = NumericProperty(.5)
    '''When within :attr:`coasting_alpha` * :attr:`interval` of the
    next notch and velocity is below :attr:`terminal_velocity`, 
    coasting begins and will end on the next notch.'''

    pull_back_velocity = NumericProperty('50sp')
    '''the velocity below which the scroll value will be drawn to the 
    *nearest* notch instead of the *next* notch in the direction travelled.'''

    _anim = ObjectProperty(None)
    
    def get_term_vel(self):
        return (exp(self.friction) * self.interval * 
                self.coasting_alpha / self.pull_duration)
    def set_term_vel(self, val):
        self.pull_duration = (exp(self.friction) * self.interval * 
                              self.coasting_alpha / val)
    terminal_velocity = AliasProperty(get_term_vel, set_term_vel, 
                                      bind=['interval',
                                            'coasting_alpha',
                                            'pull_duration',
                                            'friction'],
                                      cache=True)
    '''if velocity falls between :attr:`pull_back_velocity` and 
    :attr:`terminal velocity` then the movement will start to coast
    to the next coming stopping value.
    
    :attr:`terminal_velocity` is computed from a set formula given
    :attr:`interval`, :attr:`coasting_alpha`, :attr:`pull_duration`,
    and :attr:`friction`. Setting :attr:`terminal_velocity` has the
    effect of setting :attr:`pull_duration`.
    '''

    def start(self, val, t=None):
        if self._anim:
            self._anim.stop(self)
        return ScrollEffect.start(self, val, t=t)
    
    def on_notch(self, *args):
        return (self.scroll - self.anchor) % self.interval == 0
    
    def nearest_notch(self, *args):
        interval = float(self.interval)
        anchor = self.anchor
        n = round((self.scroll - anchor) / interval)
        return anchor + n * interval
    
    def next_notch(self, *args):
        interval = float(self.interval)
        anchor = self.anchor
        round_ = ceil if self.velocity > 0 else floor
        n = round_((self.scroll - anchor) / interval)
        return anchor + n * interval
        
    def near_notch(self, d=0.01):
        nearest = self.nearest_notch()
        if abs((nearest - self.scroll) / self.interval) % 1 < d:
            return nearest
        else:
            return None
        
    def near_next_notch(self, d=None):
        d = d or self.coasting_alpha
        next_ = self.next_notch()
        if abs((next_ - self.scroll) / self.interval) % 1 < d:
            return next_
        else:
            return None
        
    def update_velocity(self, dt):
        if self.is_manual:
            return
        velocity = self.velocity
        t_velocity = self.terminal_velocity
        next_ = self.near_next_notch()
        pull_back_velocity = self.pull_back_velocity
        if pull_back_velocity < abs(velocity) < t_velocity and next_:
            duration = abs((next_ - self.scroll) / self.velocity)
            anim = Animation(scroll=next_, 
                             duration=duration,
                             )
            self._anim = anim
            anim.on_complete = self._coasted_to_stop
            anim.start(self)
            return
        if abs(velocity) < pull_back_velocity and not self.on_notch():
            anim = Animation(scroll=self.nearest_notch(), 
                             duration=self.pull_duration,
                             t='in_out_circ')
            self._anim = anim
            anim.on_complete = self._coasted_to_stop
            anim.start(self)
        else:
            self.velocity -= self.velocity * self.friction
            self.apply_distance(self.velocity * dt)
            self.trigger_velocity_update()
            
    def on_coasted_to_stop(self, *args):
        '''this event fires when the roulette has stopped, "making a selection".
        '''
        pass
        
    def _coasted_to_stop(self, *args):
        self.velocity = 0
        self.dispatch('on_coasted_to_stop')
        
     
if __name__ == '__main__':
    # example modified from the scrollview example

    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.base import runTouchApp

    layout = GridLayout(cols=1, padding=10,
            size_hint=(None, None), width=500)

    layout.bind(minimum_height=layout.setter('height'))

    for i in range(30):
        btn = Button(text=str(i), size=(480, 40),
                     size_hint=(None, None))
        layout.add_widget(btn)

    root = ScrollView(size_hint=(None, None), size=(500, 320),
            pos_hint={'center_x': .5, 'center_y': .5}
            , do_scroll_x=False)
    root.add_widget(layout)

    root.effect_y = RouletteScrollEffect(anchor=20, interval=40)
    runTouchApp(root)
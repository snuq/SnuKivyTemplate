import os
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, OptionProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.lang.builder import Builder
Builder.load_string("""
<SongPlayer>:
    canvas.after:
        Color:
            rgba: 0, 0, 0, .5 if self.disabled else 0
        Rectangle:
            size: self.size
            pos: self.pos
    rows: 1
    size_hint_y: None
    height: '44dp'
    disabled: not root._song

    SongPlayerStop:
        size_hint_x: None
        song: root
        width: '44dp'
        source: root.image_stop
        fit_mode: 'contain'

    SongPlayerPlayPause:
        size_hint_x: None
        song: root
        width: '44dp'
        source: root.image_pause if root.state == 'play' else root.image_play
        fit_mode: 'contain'

    SongPlayerVolume:
        song: root
        size_hint_x: None
        width: '44dp'
        source: root.image_volumehigh if root.volume > 0.8 else (root.image_volumemedium if root.volume > 0.4 else (root.image_volumelow if root.volume > 0 else root.image_volumemuted))
        fit_mode: 'contain'

    Widget:
        size_hint_x: None
        width: 5

    SongPlayerProgressBar:
        song: root
        max: 1
        value: root.position

    Widget:
        size_hint_x: None
        width: 10
""")


class SongPlayerVolume(Image):
    song = ObjectProperty(None)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        touch.grab(self)
        # save the current volume and delta to it
        touch.ud[self.uid] = [self.song.volume, 0]
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        # calculate delta
        dy = abs(touch.y - touch.oy)
        if dy > 10:
            dy = min(dy - 10, 100)
            touch.ud[self.uid][1] = dy
            self.song.volume = dy / 100.
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        dy = abs(touch.y - touch.oy)
        if dy < 10:
            if self.song.volume > 0:
                self.song.volume = 0
            else:
                self.song.volume = 1.


class SongPlayerPlayPause(Image):
    song = ObjectProperty(None)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.song.state == 'play':
                self.song.state = 'pause'
            else:
                self.song.state = 'play'
            return True


class SongPlayerStop(Image):
    song = ObjectProperty(None)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.song.state = 'stop'
            return True


class SongPlayerProgressBar(ProgressBar):
    song = ObjectProperty(None)
    seek = NumericProperty(None, allownone=True)
    scrub = BooleanProperty(True)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        self._update_seek(touch.x)
        if self.song.state != 'play':
            self.song.state = 'play'
        self.song.seek(self.seek)
        self.seek = None
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        if self.scrub:
            self._update_seek(touch.x)
            self.song.seek(self.seek)
            self.seek = None
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        if self.seek is not None:
            self.song.seek(self.seek)
        self.seek = None
        return True

    def _update_seek(self, x):
        if self.width == 0:
            return
        x = max(self.x, min(self.right, x)) - self.x
        self.seek = x / float(self.width)


class SongPlayer(GridLayout):
    source = StringProperty('')
    duration = NumericProperty(-1)
    position = NumericProperty(0)
    volume = NumericProperty(1.0)
    state = OptionProperty('stop', options=('play', 'pause', 'stop'))
    image_play = StringProperty('atlas://data/images/defaulttheme/media-playback-start')
    image_stop = StringProperty('atlas://data/images/defaulttheme/media-playback-stop')
    image_pause = StringProperty('atlas://data/images/defaulttheme/media-playback-pause')
    image_volumehigh = StringProperty('atlas://data/images/defaulttheme/audio-volume-high')
    image_volumemedium = StringProperty('atlas://data/images/defaulttheme/audio-volume-medium')
    image_volumelow = StringProperty('atlas://data/images/defaulttheme/audio-volume-low')
    image_volumemuted = StringProperty('atlas://data/images/defaulttheme/audio-volume-muted')
    _song = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        self._song = None
        super(SongPlayer, self).__init__(**kwargs)

    def on_source(self, instance, value):
        if self._song is not None:
            self._song.unload()
            self._song = None
        if os.path.exists(self.source):
            self._song = SoundLoader.load(self.source)
            if self._song is None:
                return
            self._song.volume = self.volume
            self._song.state = self.state
            self.duration = self._song.length

    def _update_position(self, *_):
        if self._song is None:
            return
        if self.state == 'play':
            self.position = (self._song.get_pos() / self.duration)
            Clock.schedule_once(self._update_position)

    def on_state(self, instance, value):
        if self._song is not None:
            if value == 'play':
                self._song.play()
                self.seek(self.position)
                self._update_position()
            elif value == 'pause':
                self._song.stop()
            else:
                self._song.stop()
                self.position = 0

    def on_volume(self, instance, value):
        if not self._song:
            return
        self._song.volume = value

    def seek(self, percent):
        if not self._song:
            return
        self._song.seek(percent * self.duration)

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty, DictProperty
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.widget import Widget
from .label import NormalLabel
from kivy.lang.builder import Builder
Builder.load_string("""
<RecycleItemLabel>:
    canvas.before:
        Color:
            rgba: self.bgcolor
        Rectangle:
            size: self.size
            pos: self.pos

<SelectableRecycleBoxLayout>:
    default_size_hint: 1, None
    default_size: self.width, app.button_scale
    size_hint_x: 1
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height

<SelectableRecycleGridLayout>:
    cols: max(1, int(self.width / ((app.button_scale * 4 * self.scale) + (app.button_scale / 2))))
    focus: False
    default_size: app.button_scale * 4 * self.scale, app.button_scale * 4 * self.scale
    default_size_hint: None, None
    height: self.minimum_height
    size_hint_y: None

<NormalRecycleView>:
    size_hint: 1, 1
    do_scroll_x: False
    do_scroll_y: True
    scroll_distance: 10
    scroll_timeout: 300
    bar_width: app.scrollbar_scale
    bar_color: app.theme.scroller_selected
    bar_inactive_color: app.theme.scroller
    scroll_type: ['bars', 'content']
""")


class RecycleItem(RecycleDataViewBehavior):
    bgcolor = ListProperty([0, 0, 0, 0])
    owner = ObjectProperty()
    text = StringProperty()
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    index = NumericProperty(0)
    data = {}
    remove_length = NumericProperty(.25)
    animation = ObjectProperty(allownone=True)
    o_pos = ListProperty()
    o_opacity = NumericProperty()

    def on_selected(self, *_):
        self.set_color()

    def set_color(self):
        app = App.get_running_app()

        if self.selected:
            self.bgcolor = app.theme.selected
        else:
            if self.index % 2 == 0:
                self.bgcolor = app.list_background_even
            else:
                self.bgcolor = app.list_background_odd

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.data = data
        if 'selected' not in self.data:
            self.data['selected'] = False
        if 'selectable' not in self.data:
            self.data['selectable'] = True
        self.set_color()
        return super(RecycleItem, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(RecycleItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            touch.grab(self)

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            if self.collide_point(*touch.pos):
                touch.ungrab(self)
                self.parent.click_node(self)
                if 'shift' in Window.modifiers:
                    self.parent.select_range(self.index, touch)
                return True

    def remove(self):
        if not self.animation:
            self.o_pos = self.pos
            self.o_opacity = self.opacity
            self.animation = Animation(opacity=0, duration=self.remove_length, pos=(self.pos[0]-self.width, self.pos[1]))
            self.animation.start(self)
            self.animation.bind(on_complete=self.remove_finish)

    def remove_finish(self, *_):
        self.animation = None
        self.opacity = self.o_opacity
        self.pos = self.o_pos
        if self.parent:
            self.parent.remove_node(self)


class RecycleItemLabel(RecycleItem, NormalLabel):
    pass


class SelectableRecycleLayout(Widget):
    """Adds selection and focus behavior to the view."""
    owner = ObjectProperty()
    selected = DictProperty()
    selects = ListProperty()
    multiselect = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_click_node')

    def clear_selects(self):
        self.selects = []

    def refresh_selection(self):
        for node in self.children:
            try:  #possible for nodes to not be synched with data
                data = self.parent.data[node.index]
                node.selected = data['selected']
            except:
                pass

    def deselect_all(self):
        for data in self.parent.data:
            data['selected'] = False
        self.refresh_selection()
        self.selects = []
        self.selected = {}

    def select_all(self):
        self.selects = []
        selects = []
        for data in self.parent.data:
            if data['selectable']:
                data['selected'] = True
                selects.append(data)
        self.selects = selects
        if selects:
            self.selected = selects[-1]
        else:
            self.selected = {}
        self.refresh_selection()

    def select_node(self, node):
        if not self.multiselect:
            self.deselect_all()
        node.selected = True
        self.selects.append(node.data)
        if node.data not in self.parent.data:
            return
        self.parent.data[self.parent.data.index(node.data)]['selected'] = True
        node.data['selected'] = True
        self.selected = node.data

    def deselect_node(self, node):
        if node.data in self.selects:
            self.selects.remove(node.data)
        if self.selected == node.data:
            if self.selects:
                self.selected = self.selects[-1]
            else:
                self.selected = {}
        if node.data in self.parent.data:
            parent_index = self.parent.data.index(node.data)
            parent_data = self.parent.data[parent_index]
            parent_data['selected'] = False
        node.selected = False
        node.data['selected'] = False

    def click_node(self, node):
        #Called by a child widget when it is clicked on
        if node.selected:
            if self.multiselect:
                self.deselect_node(node)
            else:
                if self.selected != node.data:
                    self.selected = node.data
                #self.deselect_all()
        else:
            if not self.multiselect:
                self.deselect_all()
            self.select_node(node)
            self.selected = node.data
        self.dispatch('on_click_node', node)

    def on_click_node(self, node):
        pass

    def remove_node(self, node):
        self.parent.data.pop(node.index)

    def select_range(self, *_):
        if self.multiselect and self.selected and self.selected['selectable']:
            select_index = self.parent.data.index(self.selected)
            selected_nodes = []
            if self.selects:
                for select in self.selects:
                    if select['selectable']:
                        if select not in self.parent.data:
                            continue
                        index = self.parent.data.index(select)
                        if index != select_index:
                            selected_nodes.append(index)
            else:
                selected_nodes = [0, len(self.parent.data)]
            if not selected_nodes:
                return
            closest_node = min(selected_nodes, key=lambda x: abs(x-select_index))
            for index in range(min(select_index, closest_node), max(select_index, closest_node)):
                selected = self.parent.data[index]
                selected['selected'] = True
                if selected not in self.selects:
                    self.selects.append(selected)
            self.parent.refresh_from_data()

    def toggle_select(self, *_):
        if self.multiselect:
            if self.selects:
                self.deselect_all()
            else:
                self.select_all()
        else:
            if self.selected:
                self.selected = {}


class SelectableRecycleBoxLayout(SelectableRecycleLayout, RecycleBoxLayout):
    pass


class SelectableRecycleGridLayout(SelectableRecycleLayout, RecycleGridLayout):
    scale = NumericProperty(1)


class NormalRecycleView(RecycleView):
    pass

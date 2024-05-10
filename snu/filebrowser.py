import os
import re
import datetime
import fnmatch
import string
from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.filechooser import FileSystemLocal
from .popup import NormalPopup, InputPopupContent, ConfirmPopupContent
from .layouts import Holder
from .recycleview import NormalRecycleView, SelectableRecycleBoxLayout, RecycleItem
from .button import NormalButton, WideButton
from .textinput import NormalInput
from .label import NormalLabel, LeftNormalLabel
from .navigation import Navigation
from kivy.lang.builder import Builder
if platform == 'win':
    from ctypes import windll, create_unicode_buffer

Builder.load_string("""
<FileBrowserItem>:
    canvas.before:
        Color:
            rgba: self.bgcolor
        Rectangle:
            pos: self.pos
            size: self.size
    canvas.after:
        Color:
            rgba: app.theme.selected if root.selected == self else (1, 1, 1, 0)
        Rectangle:
            size: self.size
            pos: self.pos
    height: app.button_scale
    Image:
        size_hint_x: None
        width: app.button_scale
        source: 'atlas://data/images/defaulttheme/filechooser_%s' % ('folder' if root.type == 'folder' else 'file')
    NormalLabel:
        size_hint_y: None
        height: app.button_scale
        text_size: (self.width - 20, None)
        text: root.text
        halign: 'left'
        valign: 'center'
    NormalLabel:
        size_hint_x: 0 if root.is_folder else 0.25
        text: root.file_size
    NormalLabel:
        size_hint_x: 0 if root.is_folder else 0.333
        text: root.modified

<FileBrowser>:
    orientation: 'horizontal' if self.width > self.height else 'vertical'
    BoxLayout:
        orientation: 'vertical'
        Holder:
            NormalButton:
                text: 'Go Up'
                on_release: root.go_up()
            TickerLabel:
                text: root.folder
            NormalButton:
                text: 'New Folder...'
                disabled: not root.show_folder_edit
                opacity: 0 if self.disabled else 1
                width: 0 if self.disabled else self.texture_size[0] + app.button_scale
                on_release: root.new_folder()
            NormalButton:
                text: 'Delete Folder'
                disabled: not root.show_folder_edit or not root.can_delete_folder
                opacity: 1 if root.show_folder_edit else 0
                width: self.texture_size[0] + app.button_scale if root.show_folder_edit else 0
                on_release: root.delete_folder()
        NormalRecycleView:
            viewclass: 'FileBrowserItem'
            id: fileList
            data: root.file_list_data
            SelectableRecycleBoxLayout:
                id: files
                multiselect: root.multi_select
        NormalInput:
            id: fileInputArea
            disabled: not root.show_filename or not root.edit_filename
            opacity: 1 if root.show_filename else 0
            height: app.button_scale if root.show_filename else 0
            text: ';'.join(root.selected)
            on_text: root.set_edit(self.text)
    Widget:
        size_hint: None, None
        size: app.button_scale * 0.1, app.button_scale * 0.5
    BoxLayout:
        size_hint_x: root.shortcuts_size if root.width > root.height else 1
        size_hint_y: 1
        orientation: 'vertical'
        NormalLabel:
            text: 'Locations:'
        NormalRecycleView:
            viewclass: 'FileBrowserItem'
            id: locationsList
            data: root.shortcuts_data
            SelectableRecycleBoxLayout:
        WideButton:
            text: root.cancel_text
            disabled: not root.show_cancel
            opacity: 0 if self.disabled else 1
            height: 0 if self.disabled else app.button_scale
            on_release: root.dispatch('on_cancel')
        WideButton:
            text: root.select_text
            disabled: not root.show_select or not (len(root.selected) > 0 or root.edited_selected)
            opacity: 1 if root.show_select else 0
            height: app.button_scale if root.show_select else 0
            on_release: root.dispatch('on_select')
""")

def format_size(size):
    """Formats a file size in bytes to human-readable format.
    Accepts a numerical value, returns a string.
    """

    if size >= 1024:
        size = size/1024
        if size >= 1024:
            size = size/1024
            if size >= 1024:
                size = size/1024
                return str(round(size, 2))+' GB'
            else:
                return str(round(size, 2))+' MB'
        else:
            return str(round(size, 2))+' KB'
    else:
        return str(round(size, 2))+' Bytes'

def get_drives():
    drives = []
    if platform == 'win':
        for path in ['Desktop', 'Documents', 'Pictures']:
            drives.append((os.path.expanduser(u'~') + os.path.sep + path + os.path.sep, path))
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                name = create_unicode_buffer(64)
                # get name of the drive
                drive = letter + u':'
                windll.kernel32.GetVolumeInformationW(drive + os.path.sep, name, 64, None, None, None, None, 0)
                drive_name = drive
                if name.value:
                    drive_name = drive_name + '(' + name.value + ')'
                drives.append((drive + os.path.sep, drive_name))
            bitmask >>= 1
    elif platform == 'linux':
        drives.append((os.path.sep, os.path.sep))
        drives.append((os.path.expanduser(u'~') + os.path.sep, 'Home'))
        drives.append((os.path.sep + u'mnt' + os.path.sep, os.path.sep + u'mnt'))
        places = (os.path.sep + u'mnt' + os.path.sep, os.path.sep + u'media')
        for place in places:
            if os.path.isdir(place):
                for directory in next(os.walk(place))[1]:
                    drives.append((place + os.path.sep + directory + os.path.sep, directory))
    elif platform == 'macosx' or platform == 'ios':
        drives.append((os.path.expanduser(u'~') + os.path.sep, 'Home'))
        vol = os.path.sep + u'Volume'
        if os.path.isdir(vol):
            for drive in next(os.walk(vol))[1]:
                drives.append((vol + os.path.sep + drive + os.path.sep, drive))
    elif platform == 'android':
        paths = [
            ('/', 'Root'),
            ('/storage', 'Mounted Storage')
        ]
        from android.storage import primary_external_storage_path
        primary_ext_storage = primary_external_storage_path()
        if primary_ext_storage:
            paths.append((primary_ext_storage, 'Primary Storage'))

        from android.storage import secondary_external_storage_path
        secondary_ext_storage = secondary_external_storage_path()
        if secondary_ext_storage:
            paths.append((secondary_ext_storage, 'Secondary Storage'))

        for path in paths:
            realpath = os.path.realpath(path[0]) + os.path.sep
            if os.path.exists(realpath):
                drives.append((realpath, path[1]))

    return drives

def tryint(s):
    try:
        return int(s)
    except ValueError:
        return s

def alphanum_key(s):
    return [tryint(c) for c in re.split('([0-9]+)', s.lower())]

def sort_nicely(l):
    return sorted(l, key=alphanum_key)


class FileBrowserItem(RecycleItem, BoxLayout, Navigation):
    text = StringProperty()
    fullpath = StringProperty()
    type = StringProperty()
    file = StringProperty()
    owner = ObjectProperty(allownone=True)
    is_folder = BooleanProperty()
    selected = BooleanProperty(False)
    multi_select = BooleanProperty(False)
    selectable = BooleanProperty(False)
    file_size = StringProperty()
    modified = StringProperty()

    def on_navigation_activate(self):
        if self.selectable:
            self.parent.click_node(self)
            self.owner.single_click(self)

    def on_selected(self, *_):
        if self.type == 'folder' and self.multi_select and self.selected:
            self.selected = False
        if self.type == 'shortcut' and self.selected:
            self.selected = False
        self.set_color()

    def on_touch_down(self, touch):
        if not self.selectable:
            return
        super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            if not self.multi_select and touch.is_double_tap:
                self.owner.double_click(self)
            else:
                self.owner.single_click(self)


class FileBrowser(BoxLayout):
    __events__ = ('on_cancel', 'on_select')
    selected = ListProperty()  #List of currently selected filenames and folders in the dialog
    folder = StringProperty('\\')  #Current opened folder in the dialog
    filetypes_filter = ListProperty()  #Display only files with the given file extensions
    edited_selected = StringProperty('')
    default_filename = StringProperty('')

    #Theme variables:
    cancel_text = StringProperty('Cancel')
    select_text = StringProperty('Select')
    shortcuts_size = NumericProperty(0.5)  #Size hint of shortcuts area
    show_cancel = BooleanProperty(True)  #Show the cancel button
    show_select = BooleanProperty(True)  #Show the select button
    show_folder_edit = BooleanProperty(True)  #Display the folder creation/delete buttons
    show_filename = BooleanProperty(True)  #Shows the selected filename(s) in a text field

    #Behavior settings:
    file_select = BooleanProperty(True)  #Allows the dialog to select a filename
    folder_select = BooleanProperty(False)  #Allows the dialog to select a folder
    multi_select = BooleanProperty(False)  #Select multiple files or folders
    show_files = BooleanProperty(True)  #Display files in the browser
    show_hidden = BooleanProperty(True)  #Display hidden files in the browser
    require_filename = BooleanProperty(True)  #If true, the ok button cannot be clicked in file select mode if no filename is given.
    edit_filename = BooleanProperty(False)  #Allows the user to edit the filename(s) that are selected
    autoselect_files = BooleanProperty(False)  #Automatically selects all files when a folder is entered
    clear_filename = BooleanProperty(True)  #Automatically clear the filename(s) when a folder is changed

    #Internal variables:
    popup = ObjectProperty(allownone=True)
    shortcuts_data = ListProperty()
    file_list_data = ListProperty()
    folder_files = ListProperty()
    can_delete_folder = BooleanProperty(False)
    root_path = StringProperty()

    def __init__(self, **kwargs):
        Clock.schedule_once(self.refresh_all)
        super().__init__(**kwargs)
        if self.folder_select:
            self.selected = [self.folder]

    def on_select(self):
        pass

    def on_cancel(self):
        pass

    def on_default_filename(self, *_):
        Clock.schedule_once(lambda x: self.update_text_input(self.default_filename))

    def update_text_input(self, text):
        self.ids['fileInputArea'].text = text

    def set_edit(self, text):
        if self.edit_filename and not self.multi_select:
            if self.edited_selected != text:
                self.edited_selected = text

    def single_click(self, clickedon):
        app = App.get_running_app()
        app.clickfade(clickedon)
        if clickedon.type == 'shortcut':
            self.folder = clickedon.fullpath
            self.refresh_folder()
            if self.folder_select:
                self.selected = [clickedon.fullpath]
            elif self.clear_filename:
                self.selected = []
        elif clickedon.type == 'folder':
            self.folder = clickedon.fullpath
            self.refresh_folder()
            if self.folder_select:
                self.selected = [clickedon.fullpath]
            elif self.clear_filename:
                self.selected = []
        else:
            #clickedon.type == 'file'
            if self.file_select:
                self.update_selected_files()

    def double_click(self, clickedon):
        app = App.get_running_app()
        app.clickfade(clickedon)
        if clickedon.type == 'file' and self.file_select:
            self.update_selected_files()
            self.dispatch('on_select')

    def update_selected_files(self, *_):
        #Reads the current selected files in the fileview and updates self.selected
        self.selected = []
        file_data = []
        fileslayout = self.ids['files']
        for file in fileslayout.selects:
            if file['type'] == 'file':
                file_data.append(file['file'])
        self.selected = sort_nicely(file_data)

    def go_up(self):
        up_path = os.path.realpath(os.path.join(self.folder, '..'))
        if not up_path.endswith(os.path.sep):
            up_path += os.path.sep
        if up_path == self.folder:
            up_path = self.root_path
        self.folder = up_path
        if self.folder_select:
            self.selected = []
            self.selected = [self.folder]
        elif self.clear_filename:
            self.selected = []
        self.refresh_folder()

    def dismiss_popup(self, *_):
        """If this dialog has a popup, closes it and removes it."""

        if self.popup:
            self.popup.dismiss()
            self.popup = None

    def new_folder(self):
        """Starts the add folder process, creates an input text popup."""

        self.dismiss_popup()
        content = InputPopupContent(hint='Folder Name', text='Enter A Folder Name:')
        app = App.get_running_app()
        content.bind(on_answer=self.new_folder_answer)
        self.popup = NormalPopup(title='Create Folder', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 5), auto_dismiss=False)
        self.popup.open()

    def new_folder_answer(self, instance, answer):
        """Tells the app to rename the folder if the dialog is confirmed.
        Arguments:
            instance: The dialog that called this function.
            answer: String, if 'yes', the folder will be created, all other answers will just close the dialog.
        """

        if answer == 'yes':
            text = instance.ids['input'].text.strip(' ')
            if text:
                app = App.get_running_app()
                folder = os.path.join(self.folder, text)
                created = False
                try:
                    if not os.path.isdir(folder):
                        os.makedirs(folder)
                        created = True
                except:
                    pass
                if created:
                    app.message("Created the folder '" + folder + "'")
                    self.folder = folder
                    self.refresh_folder()
                else:
                    app.message("Could Not Create Folder.")
        self.dismiss_popup()

    def delete_folder(self):
        """Starts the delete folder process, creates the confirmation popup."""

        app = App.get_running_app()
        text = "Delete The Selected Folder?"
        content = ConfirmPopupContent(text=text, yes_text='Delete', no_text="Don't Delete", warn_yes=True)
        content.bind(on_answer=self.delete_folder_answer)
        self.popup = NormalPopup(title='Confirm Delete', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
        self.popup.open()

    def delete_folder_answer(self, instance, answer):
        """Tells the app to delete the folder if the dialog is confirmed.
        Arguments:
            instance: The dialog that called this function.
            answer: String, if 'yes', the folder will be deleted, all other answers will just close the dialog.
        """

        del instance
        if answer == 'yes':
            app = App.get_running_app()
            try:
                os.rmdir(self.folder)
                app.message("Deleted Folder: \"" + self.folder + "\"")
                self.go_up()
            except:
                app.message("Could Not Delete Folder...")
        self.dismiss_popup()

    def refresh_all(self, *_):
        self.refresh_shortcuts()
        self.refresh_folder()

    def refresh_shortcuts(self, *_):
        locations = get_drives()
        self.root_path = locations[0][0]
        data = []
        for location in locations:
            data.append({
                'text': location[1],
                'fullpath': location[0],
                'type': 'shortcut',
                'is_folder': True,
                'owner': self,
                'selectable': True,
                'selected': False
            })
        self.shortcuts_data = []
        self.shortcuts_data = data

    def refresh_folder(self, *_):
        fileslayout = self.ids['files']
        fileslayout.selects = []
        fileslayout.selected = {}

        data = []
        files = []
        dirs = []

        walk = os.walk
        for root, list_dirs, list_files in walk(self.folder, topdown=True):
            dirs = list_dirs[:]
            list_dirs.clear()
            files = list_files
        self.folder_files = files
        if dirs or files:
            self.can_delete_folder = False
        else:
            self.can_delete_folder = True
        dirs = sorted(dirs, key=lambda s: s.lower())

        #Sort directory list
        for directory in dirs:
            fullpath = os.path.join(self.folder, directory)
            data.append({
                'text': directory,
                'fullpath': fullpath,
                'type': 'folder',
                'file': '',
                'owner': self,
                'is_folder': True,
                'selected': False,
                'multi_select': self.multi_select,
                'selectable': True,
                'file_size': '',
                'modified': ''
            })
        #Sort file list
        if self.show_files:
            if self.filetypes_filter:
                filtered_files = []
                for item in self.filetypes_filter:
                    filtered_files += fnmatch.filter(files, item)
                files = filtered_files
            #files = sorted(files, key=lambda s: s.lower())
            files = sort_nicely(files)
            if self.autoselect_files and self.multi_select:
                file_selected = True
            else:
                file_selected = False
            filesystem = FileSystemLocal()
            for file in files:
                fullpath = os.path.join(self.folder, file)
                if not self.show_hidden:
                    if filesystem.is_hidden(fullpath):
                        continue
                file_size = int(os.path.getsize(fullpath))
                modified = int(os.path.getmtime(fullpath))
                file_data = {
                    'text': file,
                    'fullpath': fullpath,
                    'type': 'file',
                    'file': file,
                    'owner': self,
                    'is_folder': False,
                    'selected': file_selected,
                    'multi_select': self.multi_select,
                    'selectable': self.file_select,
                    'file_size': format_size(file_size),
                    'modified': datetime.datetime.fromtimestamp(modified).strftime('%Y-%m-%d, %I:%M%p')
                }
                data.append(file_data)
                if file_selected:
                    fileslayout.selects.append(file_data)
            if file_selected:
                Clock.schedule_once(self.update_selected_files)

        self.file_list_data = data
        self.reset_folder_scroll()

    def reset_folder_scroll(self, *_):
        filelist = self.ids['fileList']
        filelist.scroll_y = 1

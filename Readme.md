# General Info
Snu Kivy Template is a collection of classes and widgets that make it easier to create theme-able, clean, and a bit flashy apps in Kivy.  Please note that this depends entirely on Kivy, and will not be usable without Kivy installed first.  

This is a gift to the Kivy community, a culmination of what I have learned over the years when developing several kivy-based apps.  Use these classes as a basis for your own, or just use them directly, I impose no limitations on the code or images enclosed in this archive.

To use this template, copy the 'snu' folder to your app directory, and start importing stuff.  See the main.py and test.kv files for examples on how to use the various widgets.  

These widgets mostly depend on the 'NormalApp' class found in 'snu.app.NormalApp'. To use the various widgets, you must make your app a subclass of this, not the basic kivy App class.

Here is a demo of some of the features implemented:
![Demo](demo.gif)  

# snu.app.NormalApp Functionality

This class is a subclass of the 'kivy.app.App' class, it also implements the following features:
## Themes
Two default themes are included in the 'themes' variable, this is simply a list of dictionaries with a specific set of keys.  Copy one of the theme variables and modify the color values to create your own.  

* ### NormalApp.button_scale
Numeric Property, this controlls the overall scale of interface, sane values should be between 50 and 150.  
This value is loaded from the app config file, 'buttonscale'.  
When the config is changed, or when this value is changed, the app will automatically adjust scale.

* ### NormalApp.text_scale
Relative scaling of text, sane values are between 50 and 150.  
This value is loaded from the app config file, 'textscale'.  
When the config is changed, or when this value is changed, the app will automatically adjust scale.

* ### NormalApp.theme_index
Numeric Property, this defines the index of the theme from the 'themes' variable to be loaded on app creation.  Override this variable in your app to set a different theme index to start with.  

* ### NormalApp.load_theme(Integer)
Load a specific theme index from the themes variable.  This will cause the theme to 'fade' from the current theme.

Tip: Try creating a fully black or fully white theme as the default, then loading your default theme in your on_start for a nice fade-in!

* ### NormalApp.data_to_theme(Dictionary)
Load a theme dictionary as the theme for this app.  Note that if any variables are missing from the dictionary, the current variables will not be changed.  

* ### NormalApp.popup_x
Numeric property that sets the default width in pixels of auto-generated popups. Defaults to 640.

* ### NormalApp.animations
Boolean Property, defaults to True.  Setting this to False will disable all animations in the custom widgets.

* ### NormalApp.animation_length
Numeric Property, defaults to 0.2.  This will define the length of the animations in all custom widgets.

* ### NormalApp.clickfade(Widget, mode='opacity')
This function will create a quick colored overlay in the shape and size of the passed-in widget.  This can be used to bring the user's attention to an important widget, or to show that something has been clicked on.  
The 'mode' argument can be set to 'height' to cause the clickfade to fade out by shrinking in height instead of fading out (default behavior).

* ### NormalApp.message(String, timeout=20)
This function will create a user feedback message that will automatically be displayed by all snu.label.InfoLabel widgets.  
This message will blink for a few seconds then vanish.  
Pass in a Float to the timeout variable to change the time this text is displayed.  

* ### NormalApp.clear_message()
This function will instantly clear the app message shown in the InfoLabel widgets.

* ### NormalApp.about()
This function will open a popup that shows the about this app message.  

* ### NormalApp.about_text
String Property, this is the text that will be shown in the popup generated by the about() function shown above.  

* ### NormalApp.message_popup(String, title='Notification')
This function will open a simple message popup that displays the passed in String along with a basic 'OK' button.


# snu.button Classes

* ### Theme Colors
This button will automatically use the current theme's colors for background and text, and will animate between them for nice smooth button presses.  

* ### Theme Sizes
All buttons will default to being app.button_scale height.  
All button text will default to being the app.text_scale size.

* ### ButtonBase.warn
Boolean Property, setting this to True will cause this button to be the theme's button_warn colors instead of the standard colors.

## snu.button.ButtonBase
All buttons are based on this class.  

## snu.button.NormalButton
Based on the ButtonBase class, this button will only be as wide as it needs to be to include the shown text.

## snu.button.WideButton
Based on the ButtonBase class, this button has a size_hint_x of 1.

## snu.button.NormalMenuStarter
Similar to the NormalButton above, but also shows a double-arrow graphic to show that this is a dropdown menu.

## snu.button.WideMenuStarter
Similar to the WideButton above, but also shows the double-arrow graphic to indicate that this is a dropdown menu.

## snu.button.MenuButton
Similar to the WideButton above, but using the menu button colors from the theme.

## snu.button.NormalToggle
Similar to the NormalButton, but using the toggle button colors from the theme, and implementing toggle button functionality.

## snu.button.WideToggle
Like NormalToggle, but with a size_hint_x of 1

## snu.button.SettingsButton
Special button with the 'hamburger' icon and square-shaped.  Clicking this button will open the app settings.

## snu.button.NormalDropDown
Themed widget for DropDown menus, use instead of the standard DropDown class



# snu.image Classes

## snu.image.FillImage
Custom subclass of kivy.uix.image.Image that keeps the source in proper aspect ratio and scales it to completely fill the widget.  



# snu.label Classes

* ### Theme Colors
All labels will use the theme colors for text color

* ### Theme Sizes
All labels will default to being app.button_scale height.  
All labels' text will default to the app.text_scale size.

## snu.label.NormalLabel
Standard label class, label is full width and text will be horizontally centered.

## snu.label.ShortLabel
This label will only be as wide as the text is.

## snu.label.LeftNormalLabel
Full width label, text will be aligned to the left side.

## snu.label.HeaderLabel
Larger font size and colored using theme's header_text value for the color.  

## snu.label.InfoLabel
Special label that is filled with the app.infotext text, will also flash when the text changes.



# snu.layouts Classes
Special classes that help with layouting.

## snu.layouts.SpallSpacer
Empty widget that is 1/4 the button size in both width and height.

## snu.layouts.MediumSpacer
Empty widget that is 1/2 the button size in both width and height.

## snu.layouts.LargeSpacer
Empty widget that is the button size in both width and height.

## snu.layouts.Header
Horizontal BoxLayout that is the button height, uses the headerbg image from the data folder as its background, and is colored based on the theme main_background color.  

## snu.layouts.Holder
Similar to the Header class, but with no background or coloring.  

## snu.layouts.MainArea
Vertical BoxLayout that uses the mainbg image from the data directory as a background, and is colored based on the theme main_background variable.  



# snu.popup Classes

## snu.popup.NormalPopup
Themed popup class using the panelbg image from the data directory and theme's menu_background color.  

## snu.popup.MessagePopupContent
Basic popup content that has a message and a close button.

## snu.popup.InputPopupContent
Basic popup content that has a labeled textinput and ok/cancel buttons.

## snu.popup.ConfirmPopupContent
Basic popup content that has a message and ok and cancel buttons.



# snu.recycleview Classes

## snu.recycleview.NormalRecycleView
Themed RecycleView class using theme settings for scrollbar size and colors.  

## snu.recycleview.SelectableRecycleBoxLayout
Subclass of RecycleBoxLayout that implements selection behavior when paired with RecycleItem subclasses.  
Warning: not using a RecycleItem subclass for the viewclass will not allow for selection behavior.    
Set the 'multiselect' variable to True to enable multi select mode: Shift-click to select a range of items, Ctrl-click to select multiple items.  

## snu.recycleview.SelectableRecycleGridLayout
Same as SelectableRecycleBoxLayout, but in a gridlayout.  By default it will attempt to reflow the number of columns based on a width of 4 times the button scale.  

## snu.recycleview.RecycleItem
Specialized class that is designed to be mixed with other classes and placed in a recycleview.  
This class allows recycleview items to be selected, removed in an animated fashion, and have alternating colors to make rows easier to see.  

## snu.recycleview.RecycleItemLabel
Subclass of RecycleItem that includes a NormalLabel class, shown as an example for mixing other classes with RecycleItem, and provided for convenience.  



# snu.scrollview Classes

## snu.scrollview.Scroller
Themed subclass of ScrollView, scrollbar will be sized and colored based on theme settings.  

## snu.scrollview.ScrollViewCentered
Subclass of Scroller, begins in a centered position.  

## snu.scrollview.ScrollWrapper
Subclass of Scroller, allows ScrollView clasess to be placed inside of it and still respond to touches.  Internal ScrollViews must be added to the 'masks' property, for example:

    <ScrollWrapper>:
        masks: [subscroller]
        Scroller:
            id: subscroller


# snu.slider Classes

## snu.slider.SpecialSlider
Custom subclass of kivy.uix.slider.Slider, implements a double-click reset function.
A function must be bound to the 'reset_value()' function to allow this to work.  
For example, in kvlang:

    SpecialSlider:
        reset_value: root.reset_function


## snu.slider.NormalSlider
Themed slider based on SpecialSlider.  Uses colors from the theme and the sliderbg image from the data directory.


# snu.stencilview Classes

## snu.stencilview.StencilViewTouch
Subclass of kivy.uix.stencilview that limits touches to the stenciled area only.



# snu.textinput Classes
All text inputs default to being the standard button height, and are themed based on the theme colors.  

## snu.textinput.NormalInput
Themed TextInput with some standard convenience settings.  No limitations on text to be entered, implements a right-click/long-press context menu for standard clipboard operations.  

* ### NormalInput.press_enter(String)
This function is called when the 'Enter' key is pressed in the text input field.  This function will be passed the textinput widget, and the current text in the widget.   You can overwrite the function in your own subclass, or bind it to another function like so:

    NormalInput:
        press_enter: root.search

## snu.textinput.FloatInput
Themed TextInput widget that limits inputted text to only numbers and a single period.

## snu.textinput.IntegerInput
Themed TextInput widget that limits inputted toxt to numbers only.



# snu.settings
Fully themed settings screen that follows the colors of the rest of the app.
Implements an 'aboutbutton' settings item that shows a button that opens the app's about popup.
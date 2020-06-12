from kivy.uix.stencilview import StencilView


class StencilViewTouch(StencilView):
    """Custom StencilView that stencils touches as well as visual elements."""

    def on_touch_down(self, touch):
        """Modified to only register touch down events when inside stencil area."""
        if self.collide_point(*touch.pos):
            super(StencilViewTouch, self).on_touch_down(touch)

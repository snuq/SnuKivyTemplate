from kivy.uix.image import Image
from kivy.properties import AliasProperty


class FillImage(Image):
    def get_filled_image_size(self):
        ratio = self.image_ratio
        w, h = self.size

        widget_ratio = w / h
        iw = (h * ratio) if ratio > widget_ratio else w
        ih = (w / ratio) if ratio <= widget_ratio else h
        return iw, ih

    norm_image_size = AliasProperty(get_filled_image_size, bind=('texture', 'size', 'allow_stretch', 'image_ratio', 'keep_ratio'), cache=True)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from compressor import compress_and_encrypt, extract_archive
import os

# Detect if running on Android
try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
except ImportError:
    ANDROID = False

# Safe cross-platform base directory fallback
if ANDROID:
    BASE_DIR = "/storage/emulated/0/Download"
else:
    BASE_DIR = os.path.expanduser("~")


class SecureCompressor(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='vertical', padding=20, spacing=12, **kw)
        self.selected = []

        # Request storage permissions on Android startup
        if ANDROID:
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        self.add_widget(Label(text="Secure Compressor", font_size=22, size_hint=(1, 0.12)))
        self.file_label = Label(text="No files selected", size_hint=(1, 0.08))
        self.add_widget(self.file_label)

        b1 = Button(text="Select Files", size_hint=(1, 0.12))
        b1.bind(on_release=self.pick_files)
        self.add_widget(b1)

        self.pwd_input = TextInput(hint_text="Password (optional)",
                                   password=True, multiline=False,
                                   size_hint=(1, 0.1))
        self.add_widget(self.pwd_input)

        b2 = Button(text="Compress Files", size_hint=(1, 0.12))
        b2.bind(on_release=self.do_compress)
        self.add_widget(b2)

        b3 = Button(text="Extract Archive", size_hint=(1, 0.12))
        b3.bind(on_release=self.pick_archive)
        self.add_widget(b3)

        self.status = Label(text="Ready", size_hint=(1, 0.1))
        self.add_widget(self.status)

    def pick_files(self, instance):
        fc = FileChooserListView(path=BASE_DIR, multiselect=True)
        popup = Popup(title="Select Files", content=fc, size_hint=(0.95, 0.95))

        def choose(_):
            self.selected = list(fc.selection)
            self.file_label.text = f"{len(self.selected)} file(s) selected"
            popup.dismiss()

        btn = Button(text="Confirm", size_hint=(1, 0.15))
        btn.bind(on_release=choose)
        box = BoxLayout(orientation='vertical')
        box.add_widget(fc)
        box.add_widget(btn)
        popup.content = box
        popup.open()

    def do_compress(self, instance):
        if not self.selected:
            self.status.text = "Select files first"
            return
        out = os.path.join(BASE_DIR, "secure_archive.zip")
        pwd = self.pwd_input.text or None
        try:
            compress_and_encrypt(self.selected, out, password=pwd)
            size = os.path.getsize(out) / 1e6
            self.status.text = f"Saved: secure_archive.zip ({size:.1f} MB)"
        except Exception as e:
            self.status.text = f"Error: {e}"

    def pick_archive(self, instance):
        fc = FileChooserListView(path=BASE_DIR, filters=["*.zip"])
        popup = Popup(title="Select .zip Archive", content=fc, size_hint=(0.95, 0.95))

        def choose(_):
            if not fc.selection:
                return
            arc = fc.selection[0]
            popup.dismiss()
            outdir = os.path.join(BASE_DIR, "extracted_files")
            os.makedirs(outdir, exist_ok=True)
            pwd = self.pwd_input.text or None
            ok, msg = extract_archive(arc, outdir, password=pwd)
            self.status.text = msg

        btn = Button(text="Extract Here", size_hint=(1, 0.15))
        btn.bind(on_release=choose)
        box = BoxLayout(orientation='vertical')
        box.add_widget(fc)
        box.add_widget(btn)
        popup.content = box
        popup.open()


class MyApp(App):
    def build(self):
        return SecureCompressor()


if __name__ == "__main__":
    MyApp().run()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from compressor import compress_and_encrypt, extract_archive
import os

# Detect if running on Android
try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    ANDROID = True
except ImportError:
    ANDROID = False

if ANDROID:
    BASE_DIR = "/storage/emulated/0/Download"
else:
    BASE_DIR = os.path.expanduser("~")


class ProfessionalButton(Button):
    def __init__(self, bg_color=(0.18, 0.22, 0.28, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        self.font_size = '14sp'
        self.bold = True
        self.color = (0.95, 0.96, 0.98, 1)

        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            self.col = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[4])
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class SecureCompressor(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='vertical', padding=24, spacing=14, **kw)
        self.selected = []

        if ANDROID:
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        # Title
        title_label = Label(
            text="Secure Archive Management",
            font_size='20sp',
            bold=True,
            color=(0.9, 0.92, 0.95, 1),
            size_hint=(1, 0.1),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)

        # Status Tracker / File Info
        self.file_label = Label(
            text="Target: No files selected",
            font_size='13sp',
            color=(0.55, 0.60, 0.68, 1),
            size_hint=(1, 0.08),
            halign='left',
            valign='middle'
        )
        self.file_label.bind(size=self.file_label.setter('text_size'))
        self.add_widget(self.file_label)

        # File Selection Button
        b1 = ProfessionalButton(text="Select Files from Downloads", bg_color=(0.22, 0.28, 0.36, 1), size_hint=(1, 0.11))
        b1.bind(on_release=self.pick_files)
        self.add_widget(b1)

        # Password Input Field
        self.pwd_input = TextInput(
            hint_text="Archive Password (Optional)",
            password=True,
            multiline=False,
            size_hint=(1, 0.1),
            font_size='14sp',
            padding_x=12,
            padding_y=12,
            background_color=(0.14, 0.16, 0.20, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            cursor_color=(0.3, 0.6, 1, 1),
            hint_text_color=(0.4, 0.45, 0.5, 1)
        )
        self.add_widget(self.pwd_input)

        # Compression Action Button
        b2 = ProfessionalButton(text="Compress and Encrypt", bg_color=(0.12, 0.48, 0.32, 1), size_hint=(1, 0.11))
        b2.bind(on_release=self.do_compress)
        self.add_widget(b2)

        # Extraction Action Button
        b3 = ProfessionalButton(text="Extract Archive", bg_color=(0.20, 0.38, 0.58, 1), size_hint=(1, 0.11))
        b3.bind(on_release=self.pick_archive)
        self.add_widget(b3)

        # System Status Log
        self.status = Label(
            text="Status: Ready",
            font_size='13sp',
            color=(0.6, 0.65, 0.72, 1),
            size_hint=(1, 0.1),
            halign='left',
            valign='middle'
        )
        self.status.bind(size=self.status.setter('text_size'))
        self.add_widget(self.status)

    def show_alert(self, title, message):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text=message, font_size='14sp', color=(0.9, 0.9, 0.9, 1)))
        
        btn = ProfessionalButton(text="Dismiss", bg_color=(0.22, 0.28, 0.36, 1), size_hint=(1, 0.4))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def pick_files(self, instance):
        if ANDROID:
            # Safely grab files directly from phone Download directory to avoid URI crashes
            try:
                if os.path.exists(BASE_DIR):
                    files = [os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) if os.path.isfile(os.path.join(BASE_DIR, f))]
                    if files:
                        # Automatically select the latest file or list them
                        self.selected = [files[-1]]
                        filename = os.path.basename(self.selected[0])
                        self.file_label.text = f"Target: {filename}"
                        self.status.text = "Status: File loaded from Downloads"
                        self.show_alert("File Loaded", f"Successfully loaded:\n{filename}")
                        return
                self.show_alert("Notice", "No files found in your Download folder.")
            except Exception as e:
                self.show_alert("Error", str(e))
        else:
            # PC fallback using plyer or direct dialog
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_file_selection, multiple=True)

    def handle_file_selection(self, selection):
        if selection:
            self.selected = selection
            self.file_label.text = f"Target: {len(self.selected)} file(s) selected"
            self.status.text = "Status: Files loaded successfully"

    def do_compress(self, instance):
        if not self.selected:
            self.show_alert("Action Required", "Please select files before compressing.")
            return
        
        out = os.path.join(BASE_DIR, "secure_archive.zip")
        pwd = self.pwd_input.text or None
        try:
            compress_and_encrypt(self.selected, out, password=pwd)
            size = os.path.getsize(out) / 1e6
            self.status.text = f"Status: Complete ({size:.1f} MB)"
            self.show_alert("Success", f"Archive successfully created at:\n{out}")
        except Exception as e:
            self.status.text = "Status: Compression failed"
            self.show_alert("Compression Error", str(e))

    def pick_archive(self, instance):
        if ANDROID:
            try:
                if os.path.exists(BASE_DIR):
                    zips = [os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) if f.endswith('.zip')]
                    if zips:
                        arc = zips[-1]
                        outdir = os.path.join(BASE_DIR, "extracted_files")
                        os.makedirs(outdir, exist_ok=True)
                        pwd = self.pwd_input.text or None
                        ok, msg = extract_archive(arc, outdir, password=pwd)
                        self.status.text = "Status: Extraction complete"
                        self.show_alert("Extraction Result", f"{msg}\nSaved to: {outdir}")
                        return
                self.show_alert("Notice", "No .zip archives found in Download folder.")
            except Exception as e:
                self.show_alert("Error", str(e))
        else:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_archive_selection, filters=[("ZIP Archives", "*.zip")])

    def handle_archive_selection(self, selection):
        if not selection:
            return
        arc = selection[0]
        outdir = os.path.join(BASE_DIR, "extracted_files")
        os.makedirs(outdir, exist_ok=True)
        pwd = self.pwd_input.text or None
        try:
            ok, msg = extract_archive(arc, outdir, password=pwd)
            self.status.text = "Status: Extraction complete"
            self.show_alert("Extraction Result", f"{msg}\nSaved to: {outdir}")
        except Exception as e:
            self.status.text = "Status: Extraction failed"
            self.show_alert("Extraction Error", str(e))


class MyApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = (0.07, 0.08, 0.10, 1)
        return SecureCompressor()


if __name__ == "__main__":
    MyApp().run()

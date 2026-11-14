from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Line
from compressor import compress_and_encrypt, extract_archive
import os

# Detect if running on Android
try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
except ImportError:
    ANDROID = False

if ANDROID:
    BASE_DIR = "/storage/emulated/0/Download"
else:
    BASE_DIR = os.path.expanduser("~")


class ModernButton(Button):
    """A sleek button with smooth rounded corners and press feedback."""
    def __init__(self, bg_color=(0.23, 0.33, 0.53, 1), press_color=(0.18, 0.26, 0.42, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.normal_bg = bg_color
        self.press_bg = press_color
        self.current_bg = bg_color
        self.font_size = '14sp'
        self.bold = True
        self.color = (0.95, 0.97, 1, 1)

        with self.canvas.before:
            self.col = Color(*self.current_bg)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(state=self.update_state)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_state(self, instance, state):
        if state == 'down':
            self.col.rgba = self.press_bg
        else:
            self.col.rgba = self.normal_bg


class SecureCompressorUI(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='vertical', padding=20, spacing=16, **kw)
        self.selected = []

        if ANDROID:
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        # --- Header Section ---
        header_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=4)
        
        title_label = Label(
            text="🔒 SecureVault Archive",
            font_size='22sp',
            bold=True,
            color=(0.95, 0.97, 1, 1),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        header_layout.add_widget(title_label)

        subtitle_label = Label(
            text="Encrypt and secure your files for safe transmission",
            font_size='13sp',
            color=(0.55, 0.62, 0.73, 1),
            halign='left',
            valign='middle'
        )
        subtitle_label.bind(size=subtitle_label.setter('text_size'))
        header_layout.add_widget(subtitle_label)
        
        self.add_widget(header_layout)

        # --- Status Card ---
        status_card = BoxLayout(orientation='vertical', padding=14, size_hint=(1, 0.15))
        with status_card.canvas.before:
            Color(0.12, 0.16, 0.24, 1)  # Card background
            self.card_rect = RoundedRectangle(pos=status_card.pos, size=status_card.size, radius=[10])
            Color(0.20, 0.27, 0.38, 1)  # Subtle border outline
            self.card_line = Line(rounded_rectangle=(status_card.x, status_card.y, status_card.width, status_card.height, 10), width=1)
        status_card.bind(pos=self.update_card, size=self.update_card)

        self.file_label = Label(
            text="📂 Target: No files selected",
            font_size='13sp',
            color=(0.8, 0.85, 0.92, 1),
            halign='left',
            valign='middle'
        )
        self.file_label.bind(size=self.file_label.setter('text_size'))
        status_card.add_widget(self.file_label)
        
        self.add_widget(status_card)

        # --- File Selection Button ---
        b1 = ModernButton(
            text="📁 Select Files from Downloads", 
            bg_color=(0.18, 0.25, 0.38, 1), 
            press_color=(0.14, 0.20, 0.31, 1),
            size_hint=(1, 0.11)
        )
        b1.bind(on_release=self.pick_files)
        self.add_widget(b1)

        # --- Password Input Field ---
        self.pwd_input = TextInput(
            hint_text="🔑 Enter Encryption Password",
            password=True,
            multiline=False,
            size_hint=(1, 0.1),
            font_size='14sp',
            padding_x=14,
            padding_y=14,
            background_color=(0.09, 0.12, 0.18, 1),
            foreground_color=(0.95, 0.97, 1, 1),
            cursor_color=(0.35, 0.6, 1, 1),
            hint_text_color=(0.4, 0.46, 0.55, 1)
        )
        self.add_widget(self.pwd_input)

        # --- Action Buttons (Encrypt / Extract) ---
        actions_layout = BoxLayout(orientation='horizontal', spacing=12, size_hint=(1, 0.11))
        
        b2 = ModernButton(
            text="🔒 Compress & Encrypt", 
            bg_color=(0.08, 0.52, 0.35, 1), 
            press_color=(0.06, 0.42, 0.28, 1)
        )
        b2.bind(on_release=self.do_compress)
        actions_layout.add_widget(b2)

        b3 = ModernButton(
            text="📂 Extract Archive", 
            bg_color=(0.15, 0.42, 0.68, 1), 
            press_color=(0.12, 0.34, 0.55, 1)
        )
        b3.bind(on_release=self.pick_archive)
        actions_layout.add_widget(b3)

        self.add_widget(actions_layout)

        # --- System Status Footer ---
        self.status = Label(
            text="⚡ Status: Ready",
            font_size='13sp',
            color=(0.5, 0.58, 0.68, 1),
            size_hint=(1, 0.08),
            halign='left',
            valign='middle'
        )
        self.status.bind(size=self.status.setter('text_size'))
        self.add_widget(self.status)

    def update_card(self, instance, *args):
        self.card_rect.pos = instance.pos
        self.card_rect.size = instance.size
        self.card_line.rounded_rectangle = (instance.x, instance.y, instance.width, instance.height, 10)

    def show_alert(self, title, message):
        content = BoxLayout(orientation='vertical', padding=16, spacing=16)
        content.add_widget(Label(text=message, font_size='14sp', color=(0.9, 0.92, 0.95, 1), halign='center'))
        
        btn = ModernButton(text="Dismiss", bg_color=(0.22, 0.29, 0.4, 1), size_hint=(1, 0.4))
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.38))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def pick_files(self, instance):
        if ANDROID:
            try:
                if os.path.exists(BASE_DIR):
                    files = [os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR) if os.path.isfile(os.path.join(BASE_DIR, f))]
                    if files:
                        self.selected = [files[-1]]
                        filename = os.path.basename(self.selected[0])
                        self.file_label.text = f"📂 Target: {filename}"
                        self.status.text = "⚡ Status: File loaded from Downloads"
                        self.show_alert("File Loaded", f"Successfully loaded:\n{filename}")
                        return
                self.show_alert("Notice", "No files found in your Download folder.")
            except Exception as e:
                self.show_alert("Error", str(e))
        else:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_file_selection, multiple=True)

    def handle_file_selection(self, selection):
        if selection:
            self.selected = selection
            self.file_label.text = f"📂 Target: {len(self.selected)} file(s) selected"
            self.status.text = "⚡ Status: Files loaded successfully"

    def do_compress(self, instance):
        if not self.selected:
            self.show_alert("Action Required", "Please select files before compressing.")
            return
        
        out = os.path.join(BASE_DIR, "secure_archive.zip")
        pwd = self.pwd_input.text or None
        try:
            compress_and_encrypt(self.selected, out, password=pwd)
            size = os.path.getsize(out) / 1e6
            self.status.text = f"⚡ Status: Complete ({size:.1f} MB)"
            self.show_alert("Success", f"Archive successfully created at:\n{out}")
        except Exception as e:
            self.status.text = "⚡ Status: Compression failed"
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
                        self.status.text = "⚡ Status: Extraction complete"
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
            self.status.text = "⚡ Status: Extraction complete"
            self.show_alert("Extraction Result", f"{msg}\nSaved to: {outdir}")
        except Exception as e:
            self.status.text = "⚡ Status: Extraction failed"
            self.show_alert("Extraction Error", str(e))


class MyApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = (0.05, 0.07, 0.11, 1)  # Deep dark slate background
        return SecureCompressorUI()


if __name__ == "__main__":
    MyApp().run()

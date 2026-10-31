[app]

title = Secure Compressor
package.name = securecompressor
package.domain = org.secure

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1

requirements = python3,kivy

# Force python-for-android to use a stable branch compatible with Python 3.11/3.12 standard wheels
p4a.branch = master

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a

android.accept_sdk_license = True
android.allow_backup = True

[buildozer]

log_level = 2
warn_on_root = 1

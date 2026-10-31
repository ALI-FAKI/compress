[app]

title = Secure Compressor
package.name = securecompressor
package.domain = org.secure

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1

# Stable Python version + Kivy (using built-in zipfile for compression)
requirements = python3==3.11.9,kivy

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

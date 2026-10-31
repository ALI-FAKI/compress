[app]

title = Secure Compressor
package.name = securecompressor
package.domain = org.secure

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1

requirements = python3,kivy

# Pin to stable p4a release (v2024.01.21) to avoid Python 3.14 Android wheel incompatibility on master
p4a.branch = v2024.01.21

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

[app]

title = Secure Compressor
package.name = securecompressor
package.domain = org.secure

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_patterns = assets/*,images/*

version = 0.1

requirements = python3==3.10.12,kivy,py7zr,pycryptodome,charset_normalizer==3.3.2

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

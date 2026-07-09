[app]

title = Studex
package.name = studex
package.domain = org.studex

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 0.1

requirements = python3,kivy==2.3.0,requests,urllib3,certifi,charset_normalizer,idna,plyer

orientation = portrait
fullscreen = 0

# icon.filename = %(source.dir)s/icon.png
# Yuqoridagi qatorni ochib, o'z 512x512 icon.png faylingizni shu papkaga
# qo'yib, package.name papkasiga qo'shsangiz, ilova ikonkasi almashadi.

android.permissions = INTERNET

android.api = 34
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

log_level = 2
warn_on_root = 1

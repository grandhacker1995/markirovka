[app]
title = Markirovka
package.name = markirovka
package.domain = uz.evos
source.dir = .
source.include_exts = py,png,jpg,json
version = 1.2

requirements = python3,kivy,pyjnius,android

orientation = portrait
fullscreen = 0

# Android sozlamalari
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,INTERNET
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

# Icon (agar icon.png qo'shsangiz)
# icon.filename = icon.png

[buildozer]
log_level = 2
warn_on_root = 1

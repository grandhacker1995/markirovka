[app]
title = Markirovka
package.name = markirovka
package.domain = uz.evos
source.dir = .
source.include_exts = py,png,jpg,json
version = 1.2

requirements = python3,kivy==2.3.0,pyjnius==1.6.1,android

orientation = portrait
fullscreen = 0

# Android sozlamalari
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

# python-for-android barqaror versiyasi (NDK 25b bilan mos)
p4a.branch = v2024.01.21

# Icon (agar icon.png qo'shsangiz)
# icon.filename = icon.png

[buildozer]
log_level = 2
warn_on_root = 1

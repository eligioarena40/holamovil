[app]
title = Reproductor Kivy
package.name = reproductoraudio
package.domain = org.eligio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3
version = 0.1

requirements = python3, kivy==2.3.0, ffpyplayer, sdl2, sdl2_image, sdl2_mixer, sdl2_ttf

orientation = portrait
fullscreen = 1

android.archs = armeabi-v7a, arm64-v8a
android.allow_backup = True
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 1
warn_on_root = 1

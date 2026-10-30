[app]
title = GameNews
package.name = gamenews
package.domain = org.gamenews
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xml

# Исключаем серверные папки, чтобы они не попали в APK
source.exclude_dirs = api, database, migrations, __pycache__, tests, .git, .buildozer

version = 1.0
requirements = python3==3.10.12,hostpython3==3.10.12,setuptools,wheel,kivy==2.3.1,requests,deep-translator,certifi,urllib3,chardet,idna
orientation = portrait
android.archs = arm64-v8a
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.no_compile_pyo = True
android.release_artifact = apk

# ОБХОД ОШИБКИ libthorvg
p4a.branch = develop

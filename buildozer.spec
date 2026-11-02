[app]
title = GameNews
package.name = gamenews
package.domain = org.gamenews
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xml

# Исключаем серверные папки и тесты
source.exclude_dirs = api, database, migrations, __pycache__, tests, .git, .buildozer
source.exclude_patterns = create_test_users.py, test_*.py, setup_db.py, check_news.py, fix*.py, requirements.txt, alembic.ini

version = 1.0
# Только клиентские библиотеки (БЕЗ PILLOW)
requirements = python3==3.10.12,hostpython3==3.10.12,setuptools,wheel,kivy==2.2.1,requests,deep-translator,certifi,urllib3,chardet,idna

orientation = portrait
android.archs = arm64-v8a
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.no_compile_pyo = True
android.release_artifact = apk

p4a.branch = master

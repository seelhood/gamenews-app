[app]

# Название приложения
title = GameNews

# Уникальное имя пакета и домен
package.name = gamenews
package.domain = org.gamenews

# Где лежат исходники
source.dir = .

# Какие файлы включать в сборку (только нужные расширения)
source.include_exts = py,png,jpg,kv,atlas,xml,db

# Исключаем серверные папки, чтобы они не попали в APK
source.exclude_dirs = api, database, migrations, __pycache__, tests, .git, .buildozer

# Версия приложения
version = 1.0

# --- КРИТИЧЕСКИ ВАЖНЫЕ НАСТРОЙКИ ---
# Библиотеки: только клиентские. Никаких sqlalchemy, bcrypt и psycopg2!
requirements = python3==3.10.12,hostpython3==3.10.12,setuptools,wheel,kivy==2.3.1,requests,deep-translator,certifi,urllib3,chardet,idna

# Ориентация экрана
orientation = portrait

# Собираем только под 64-битную архитектуру (экономит память и время)
android.archs = arm64-v8a

# Разрешение только на интернет (для работы с API)
android.permissions = INTERNET

# Версии API и NDK
android.api = 33
android.minapi = 21
android.ndk = 25b

# Автоматически принимаем лицензии SDK
android.accept_sdk_license = True

# Отключаем лишнюю оптимизацию Python
android.no_compile_pyo = True

# Формат артефакта (APK)
android.release_artifact = apk

# Обход ошибки libthorvg в сборщике
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1

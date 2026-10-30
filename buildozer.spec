[app]

# Название приложения
title = GameNews

# Уникальное имя пакета
package.name = gamenews

# Домен
package.domain = org.gamenews

# Где лежат исходники
source.dir = .

# Какие файлы включать в сборку
source.include_exts = py,png,jpg,kv,atlas,xml

# Версия приложения
version = 1.0

# --- КРИТИЧЕСКИ ВАЖНЫЕ НАСТРОЙКИ ---
# Только те библиотеки, которые нужны мобильному клиенту (API через requests)
requirements = python3==3.10.12,hostpython3==3.10.12,setuptools,wheel,kivy==2.3.1,requests,deep-translator,pillow,certifi,urllib3,chardet,idna

# Ориентация экрана
orientation = portrait

# Собираем под ДВЕ архитектуры, чтобы запустилось на любом телефоне
android.archs = armeabi-v7a, arm64-v8a

# Разрешение на интернет (критически важно для работы API)
android.permissions = INTERNET

# Версии API и NDK
android.api = 33
android.minapi = 21
android.ndk = 25b

# Автоматически принимаем лицензии SDK
android.accept_sdk_license = True

# Отключаем лишнюю оптимизацию Python (экономит время и память)
android.no_compile_pyo = True

# --- НАСТРОЙКА ДЛЯ РЕЛИЗНОЙ СБОРКИ ---
android.release_artifact = apk
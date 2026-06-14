import locale

LANGUAGES = {
    "en": "English",
    "ru": "Русский",
    "uk": "Українська"
}

TRANSLATIONS = {
    "en": {
        "new_fence": "New Fence",
        "search_placeholder": "Search...",
        "manage_fences": "Manage Fences",
        "delete_fence": "Delete this fence",
        "lock_fence": "Lock fence",
        "unlock_fence": "Unlock fence",
        "auto_fit": "Auto-fit free space",
        "search_icons": "Search icons",
        "color_this_window": "Color of this window",
        "color_all_windows": "Color of all windows",
        "create_custom_preset": "Create custom preset...",
        "delete_all_fences": "Delete Fence",
        "open": "Open",
        "open_count": "Open ({count})",
        "run_as_admin": "Run as admin",
        "rename": "Rename",
        "show_in_folder": "Show in folder",
        "properties": "Properties",
        "delete_file": "Delete file",
        "delete_files": "Delete selected ({count})",
        "confirm_delete_files": "Are you sure you want to delete {count} items?",
        "confirm_delete_file": "Are you sure you want to delete '{name}'?",
        "confirm_delete_title": "Confirm Deletion",
        "delete": "delete",
        "tray_settings": "Settings",
        "tray_profiles": "Profiles",
        "tray_create": "Create new fence",
        "tray_exit": "Exit",
        "settings_title": "Nestly Settings",
        "autostart": "Launch with Windows",
        "language": "Language",
        "opacity": "Window Opacity",
        "save": "Save",
        "cancel": "Cancel",
        "export": "Export Config",
        "import": "Import Config",
        "profile_home": "Home",
        "profile_work": "Work",
        "create_profile": "Create Profile...",
    },
    "ru": {
        "new_fence": "Новая Сетка",
        "search_placeholder": "Поиск...",
        "manage_fences": "Управление сетками",
        "delete_fence": "Удалить эту сетку",
        "lock_fence": "Закрепить сетку",
        "unlock_fence": "Открепить сетку",
        "auto_fit": "Заполнить свободное место",
        "search_icons": "Поиск иконок",
        "color_this_window": "Цвет этого окна",
        "color_all_windows": "Цвет всех окон",
        "create_custom_preset": "Создать свой пресет...",
        "delete_all_fences": "Удалить сетку",
        "open": "Открыть",
        "open_count": "Открыть ({count})",
        "run_as_admin": "Запуск от имени администратора",
        "rename": "Переименовать",
        "show_in_folder": "Показать в папке",
        "properties": "Свойства",
        "delete_file": "Удалить файл",
        "delete_files": "Удалить выбранные ({count})",
        "confirm_delete_files": "Вы уверены, что хотите удалить выбранные файлы ({count} шт.)?",
        "confirm_delete_file": "Вы уверены, что хотите удалить '{name}'?",
        "confirm_delete_title": "Подтверждение удаления",
        "delete": "удалить",
        "tray_settings": "Настройки",
        "tray_profiles": "Профили",
        "tray_create": "Создать новую сетку",
        "tray_exit": "Выход",
        "settings_title": "Настройки Nestly",
        "autostart": "Запускать вместе с Windows",
        "language": "Язык",
        "opacity": "Прозрачность окна",
        "save": "Сохранить",
        "cancel": "Отмена",
        "export": "Экспорт настроек",
        "import": "Импорт настроек",
        "profile_home": "Дом",
        "profile_work": "Работа",
        "create_profile": "Создать профиль...",
    },
    "uk": {
        "new_fence": "Нова Сітка",
        "search_placeholder": "Пошук...",
        "manage_fences": "Керування сітками",
        "delete_fence": "Видалити цю сітку",
        "lock_fence": "Закріпити сітку",
        "unlock_fence": "Відкріпити сітку",
        "auto_fit": "Заповнити вільний простір",
        "search_icons": "Пошук іконок",
        "color_this_window": "Колір цього вікна",
        "color_all_windows": "Колір усіх вікон",
        "create_custom_preset": "Створити власний пресет...",
        "delete_all_fences": "Видалити сітку",
        "open": "Відкрити",
        "open_count": "Відкрити ({count})",
        "run_as_admin": "Запуск від імені адміністратора",
        "rename": "Перейменувати",
        "show_in_folder": "Показати в папці",
        "properties": "Властивості",
        "delete_file": "Видалити файл",
        "delete_files": "Видалити вибрані ({count})",
        "confirm_delete_files": "Ви впевнені, що хочете видалити вибрані файли ({count} шт.)?",
        "confirm_delete_file": "Ви впевнені, що хочете видалити '{name}'?",
        "confirm_delete_title": "Підтвердження видалення",
        "delete": "видалити",
        "tray_settings": "Налаштування",
        "tray_profiles": "Профілі",
        "tray_create": "Створити нову сітку",
        "tray_exit": "Вихід",
        "settings_title": "Налаштування Nestly",
        "autostart": "Запускати разом з Windows",
        "language": "Мова",
        "opacity": "Прозорість вікна",
        "save": "Зберегти",
        "cancel": "Скасувати",
        "export": "Експорт налаштувань",
        "import": "Імпорт налаштувань",
        "profile_home": "Дім",
        "profile_work": "Робота",
        "create_profile": "Створити профіль...",
    }
}

class I18nManager:
    def __init__(self, config_manager):
        self.config = config_manager
        
        sys_lang = locale.getdefaultlocale()[0]
        default_lang = "en"
        if sys_lang:
            if sys_lang.startswith("ru"):
                default_lang = "ru"
            elif sys_lang.startswith("uk"):
                default_lang = "uk"
                
        self.current_lang = self.config.config_data.get("language", default_lang)
        if self.current_lang not in TRANSLATIONS:
            self.current_lang = "en"

    def set_language(self, lang_code):
        if lang_code in TRANSLATIONS:
            self.current_lang = lang_code
            self.config.config_data["language"] = lang_code
            self.config.save_config()

    def tr(self, key, **kwargs):
        text = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"]).get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

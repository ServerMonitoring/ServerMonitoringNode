import logging

# Создаём корневой логгер
logger = logging.getLogger("agent")
logger.setLevel(logging.DEBUG)  # захватываем ВСЕ уровни

#  DEBUG + INFO + WARNING ->  debug.log
debug_handler = logging.FileHandler("debug.log", encoding="utf-8")
debug_handler.setLevel(logging.DEBUG)

# INFO + WARNING + ERROR + CRITICAL ->  error.log
error_handler = logging.FileHandler("error.log", encoding="utf-8")
error_handler.setLevel(logging.INFO)

#  Вывод в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

#  Формат логов
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
debug_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Подключаем обработчики
logger.addHandler(debug_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

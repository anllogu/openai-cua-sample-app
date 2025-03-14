from .computer import Computer
from .browserbase import BrowserbaseBrowser
from .local_playwright import LocalPlaywrightComputer
from .docker import DockerComputer
from .scrapybara import ScrapybaraBrowser, ScrapybaraUbuntu

# Importamos la clase Windows11Computer con verificación de plataforma
import platform
if platform.system() == "Windows":
    from .windows import Windows11Computer

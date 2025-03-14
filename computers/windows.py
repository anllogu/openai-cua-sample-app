import base64
import io
import time
from typing import List, Dict, Literal
from PIL import ImageGrab, Image

# PyAutoGUI para controlar teclado y ratón
import pyautogui

# Para capturar pulsaciones de teclas especiales
import platform
if platform.system() == "Windows":
    import win32api
    import win32con
    import win32gui
    import win32ui


class Windows11Computer:
    """
    Implementación para controlar el escritorio de Windows 11 utilizando PyAutoGUI
    y bibliotecas específicas de Windows.
    """
    environment: Literal["windows"] = "windows"
    dimensions = (1920, 1080)  # Resolución predeterminada, se actualizará en __enter__

    def __init__(self):
        # Configuración recomendada para PyAutoGUI
        pyautogui.FAILSAFE = True  # Moviendo el ratón a (0,0) detiene la ejecución
        pyautogui.PAUSE = 0.1      # Pequeña pausa entre acciones

    def __enter__(self):
        # Obtener la resolución real de la pantalla
        width, height = pyautogui.size()
        self.dimensions = (width, height)
        print(f"Windows11Computer: pantalla detectada {width}x{height}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def screenshot(self) -> str:
        """Captura la pantalla y devuelve una imagen codificada en base64."""
        screenshot = ImageGrab.grab()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def click(self, x: int, y: int, button: str = "left") -> None:
        """Hace clic en las coordenadas especificadas."""
        button_map = {"left": "left", "right": "right", "middle": "middle"}
        pyautogui.click(x, y, button=button_map.get(button, "left"))

    def double_click(self, x: int, y: int) -> None:
        """Hace doble clic en las coordenadas especificadas."""
        pyautogui.doubleClick(x, y)

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        """Desplaza la pantalla en las coordenadas especificadas."""
        pyautogui.moveTo(x, y)
        # PyAutoGUI usa valores positivos para desplazarse hacia abajo,
        # mientras que la API de CUA usa valores negativos
        pyautogui.scroll(-scroll_y)  # Invertimos el valor para mantener la convención

    def type(self, text: str) -> None:
        """Escribe el texto especificado."""
        pyautogui.typewrite(text)

    def wait(self, ms: int = 1000) -> None:
        """Espera el tiempo especificado en milisegundos."""
        time.sleep(ms / 1000)

    def move(self, x: int, y: int) -> None:
        """Mueve el ratón a las coordenadas especificadas."""
        pyautogui.moveTo(x, y)

    def keypress(self, keys: List[str]) -> None:
        """Presiona las teclas especificadas."""
        # Mapeo de teclas de CUA a PyAutoGUI
        key_mapping = {
            "CTRL": "ctrl",
            "ALT": "alt",
            "SHIFT": "shift",
            "META": "win",
            "ENTER": "enter",
            "BACKSPACE": "backspace",
            "ESC": "esc",
            "TAB": "tab",
            "UP": "up",
            "DOWN": "down",
            "LEFT": "left",
            "RIGHT": "right",
            "F1": "f1",
            "F2": "f2",
            "F3": "f3",
            "F4": "f4",
            "F5": "f5",
            "F6": "f6",
            "F7": "f7",
            "F8": "f8",
            "F9": "f9",
            "F10": "f10",
            "F11": "f11",
            "F12": "f12",
            "PAGEUP": "pageup",
            "PAGEDOWN": "pagedown",
            "HOME": "home",
            "END": "end",
            "INSERT": "insert",
            "DELETE": "delete",
            "SPACE": "space",
        }
        
        # Si hay múltiples teclas, usamos hotkey
        if len(keys) > 1:
            mapped_keys = [key_mapping.get(key.upper(), key.lower()) for key in keys]
            pyautogui.hotkey(*mapped_keys)
        # Si hay una sola tecla, usamos press
        elif len(keys) == 1:
            key = keys[0]
            mapped_key = key_mapping.get(key.upper(), key.lower())
            pyautogui.press(mapped_key)

    def drag(self, path: List[Dict[str, int]]) -> None:
        """Arrastra el ratón a lo largo de una ruta especificada."""
        if not path:
            return
        
        # Mover a la primera posición
        start_x, start_y = path[0]["x"], path[0]["y"]
        pyautogui.moveTo(start_x, start_y)
        
        # Presionar el botón del ratón
        pyautogui.mouseDown()
        
        # Seguir la ruta
        for point in path[1:]:
            pyautogui.moveTo(point["x"], point["y"])
        
        # Soltar el botón del ratón
        pyautogui.mouseUp()

    def get_current_url(self) -> str:
        """
        Este método es requerido por la interfaz Computer, pero no es aplicable
        a un entorno de escritorio completo. Devolvemos una cadena vacía.
        """
        return ""
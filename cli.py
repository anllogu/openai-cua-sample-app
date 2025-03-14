import argparse
import platform
from agent.agent import Agent
from computers import (
    BrowserbaseBrowser,
    ScrapybaraBrowser,
    ScrapybaraUbuntu,
    LocalPlaywrightComputer,
    DockerComputer,
)

# Importamos Windows11Computer si estamos en Windows
if platform.system() == "Windows":
    from computers import Windows11Computer


def acknowledge_safety_check_callback(message: str) -> bool:
    response = input(
        f"Safety Check Warning: {message}\nDo you want to acknowledge and proceed? (y/n): "
    ).lower()
    return response.lower().strip() == "y"


def main():
    parser = argparse.ArgumentParser(
        description="Select a computer environment from the available options."
    )
    
    # Lista de opciones de entorno de computadora
    computer_choices = [
        "local-playwright",
        "docker",
        "browserbase",
        "scrapybara-browser",
        "scrapybara-ubuntu",
    ]
    
    # Agregar la opción de Windows 11 si estamos en Windows
    if platform.system() == "Windows":
        computer_choices.append("windows11")
    
    parser.add_argument(
        "--computer",
        choices=computer_choices,
        help="Choose the computer environment to use.",
        default="local-playwright",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Initial input to use instead of asking the user.",
        default=None,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed output.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show images during the execution.",
    )
    parser.add_argument(
        "--start-url",
        type=str,
        help="Start the browsing session with a specific URL (only for browser environments).",
        default="https://bing.com",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["claude-3-opus-20240229", "claude-3-sonnet-20240229", "computer-use-preview"],
        help="Choose the model to use for the agent.",
        default="claude-3-opus-20240229",
    )
    args = parser.parse_args()

    computer_mapping = {
        "local-playwright": LocalPlaywrightComputer,
        "docker": DockerComputer,
        "browserbase": BrowserbaseBrowser,
        "scrapybara-browser": ScrapybaraBrowser,
        "scrapybara-ubuntu": ScrapybaraUbuntu,
    }
    
    # Agregar Windows11Computer al mapeo si estamos en Windows
    if platform.system() == "Windows":
        computer_mapping["windows11"] = Windows11Computer

    ComputerClass = computer_mapping[args.computer]

    with ComputerClass() as computer:
        agent = Agent(
            model=args.model,
            computer=computer,
            acknowledge_safety_check_callback=acknowledge_safety_check_callback,
        )
        items = []

        while True:
            user_input = args.input or input("> ")
            items.append({"role": "user", "content": user_input})
            output_items = agent.run_full_turn(
                items,
                print_steps=True,
                show_images=args.show,
                debug=args.debug,
            )
            items += output_items
            args.input = None


if __name__ == "__main__":
    main()

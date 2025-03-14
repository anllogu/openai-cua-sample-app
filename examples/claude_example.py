"""
Example of using Claude to control a computer.
This example demonstrates how to use Claude with the computer environment.
"""

from agent.agent import Agent
from computers import LocalPlaywrightComputer
import os


def acknowledge_safety_check_callback(message: str) -> bool:
    response = input(
        f"Safety Check Warning: {message}\nDo you want to acknowledge and proceed? (y/n): "
    ).lower()
    return response.strip() == "y"


def main():
    """Simple example of Claude controlling a computer."""
    with LocalPlaywrightComputer(start_url="https://bing.com") as computer:
        # Create agent with Claude model
        agent = Agent(
            model="claude-3-opus-20240229",
            computer=computer,
            acknowledge_safety_check_callback=acknowledge_safety_check_callback,
        )

        # Run the agent with an initial user request
        initial_request = "Find the current weather in San Francisco"

        # Run a full turn of the agent
        items = [{"role": "user", "content": initial_request}]

        # This will run all of the computer actions and return when the agent is done
        responses = agent.run_full_turn(items, print_steps=True, debug=True, show_images=True)

        # Print the final response
        final_response = [item for item in responses if item.get("role") == "assistant"]
        if final_response:
            print("\nFinal response:")
            print(final_response[-1]["content"])


if __name__ == "__main__":
    main()
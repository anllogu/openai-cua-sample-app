import os
import requests
from dotenv import load_dotenv
import json
import base64
from PIL import Image
from io import BytesIO
import io
from urllib.parse import urlparse
from typing import Dict, Any, List, Union, Optional

load_dotenv(override=True)

BLOCKED_DOMAINS = [
    "maliciousbook.com",
    "evilvideos.com",
    "darkwebforum.com",
    "shadytok.com",
    "suspiciouspins.com",
    "ilanbigio.com",
]


def pp(obj):
    print(json.dumps(obj, indent=4))


def show_image(base_64_image):
    image_data = base64.b64decode(base_64_image)
    image = Image.open(BytesIO(image_data))
    image.show()


def calculate_image_dimensions(base_64_image):
    image_data = base64.b64decode(base_64_image)
    image = Image.open(io.BytesIO(image_data))
    return image.size


def sanitize_message(msg: dict) -> dict:
    """Return a copy of the message with image_url omitted for computer_call_output messages."""
    if msg.get("type") == "computer_call_output":
        output = msg.get("output", {})
        if isinstance(output, dict):
            sanitized = msg.copy()
            sanitized["output"] = {**output, "image_url": "[omitted]"}
            return sanitized
    return msg


def create_response(**kwargs):
    # Determine which API to use based on the model
    model = kwargs.get("model", "")
    
    if model.startswith("claude-"):
        return create_claude_response(**kwargs)
    else:
        return create_openai_response(**kwargs)


def create_openai_response(**kwargs):
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json",
        # TODO: remove for launch
        "Openai-beta": "responses=v1",
    }

    openai_org = os.getenv("OPENAI_ORG")
    if openai_org:
        headers["Openai-Organization"] = openai_org

    response = requests.post(url, headers=headers, json=kwargs)

    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")

    return response.json()


def create_claude_response(**kwargs):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    # Convert OpenAI format to Claude format
    claude_request = convert_to_claude_format(kwargs)
    
    response = requests.post(url, headers=headers, json=claude_request)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.text}")
        return {"error": response.text}
    
    # Convert Claude response to OpenAI format
    return convert_from_claude_format(response.json(), kwargs.get("tools", []))


def convert_to_claude_format(openai_request: Dict[str, Any]) -> Dict[str, Any]:
    """Convert OpenAI request format to Claude format."""
    model = openai_request.get("model", "claude-3-sonnet-20240229")
    input_messages = openai_request.get("input", [])
    tools = openai_request.get("tools", [])
    
    # Convert messages to Claude format
    messages = []
    for msg in input_messages:
        if msg.get("role") == "user":
            role = "user"
            content = convert_content_to_claude(msg.get("content", ""))
            messages.append({"role": role, "content": content})
        elif msg.get("role") == "assistant":
            role = "assistant"
            content = convert_content_to_claude(msg.get("content", ""))
            messages.append({"role": role, "content": content})
        elif msg.get("type") == "computer_call_output":
            # Handle computer screenshots as user messages with images
            output = msg.get("output", {})
            if output.get("type") == "input_image" and "image_url" in output:
                image_url = output["image_url"]
                if image_url.startswith("data:image/png;base64,"):
                    base64_image = image_url.split(",")[1]
                    content = [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_image}}
                    ]
                    if "current_url" in output:
                        content.append({"type": "text", "text": f"Current URL: {output['current_url']}"})
                    messages.append({"role": "user", "content": content})
    
    # Convert tools to Claude tool format
    claude_tools = []
    computer_tool = None
    
    for tool in tools:
        if tool.get("type") == "computer-preview":
            computer_tool = {
                "name": "computer",
                "description": "Perform actions on a computer",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                            },
                            "additionalProperties": True
                        }
                    }
                }
            }
            claude_tools.append(computer_tool)
    
    # Create system prompt for Claude
    system_prompt = "You are Claude, an AI assistant that can control a computer. "
    system_prompt += "You can see screenshots of the computer and perform actions on it. "
    
    if computer_tool:
        display_width = computer_tool.get("display_width", 1280)
        display_height = computer_tool.get("display_height", 720)
        environment = computer_tool.get("environment", "browser")
        system_prompt += f"The computer has a display of {display_width}x{display_height} pixels. "
        system_prompt += f"You are working in a {environment} environment. "
    
    system_prompt += "Analyze what you see and help the user accomplish their tasks."
    
    # Build final Claude request
    claude_request = {
        "model": model,
        "messages": messages,
        "system": system_prompt,
        "max_tokens": 4096
    }
    
    if claude_tools:
        claude_request["tools"] = claude_tools
    
    return claude_request


def convert_content_to_claude(content):
    """Convert OpenAI content format to Claude content format."""
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    elif isinstance(content, list):
        claude_content = []
        for item in content:
            if item.get("type") == "text":
                claude_content.append({"type": "text", "text": item.get("text", "")})
            elif item.get("type") == "image_url":
                url = item.get("image_url", "")
                if url.startswith("data:image/"):
                    media_type = url.split(";")[0].replace("data:", "")
                    base64_data = url.split(",")[1]
                    claude_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_data
                        }
                    })
        return claude_content
    return [{"type": "text", "text": str(content)}]


def convert_from_claude_format(claude_response: Dict[str, Any], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert Claude response format to OpenAI format."""
    content = claude_response.get("content", [])
    tool_calls = claude_response.get("tool_calls", [])
    
    output_items = []
    
    # Handle text content
    text_parts = []
    for item in content:
        if item.get("type") == "text":
            text_parts.append(item.get("text", ""))
    
    if text_parts:
        output_items.append({
            "role": "assistant",
            "content": "".join(text_parts)
        })
    
    # Handle tool calls
    for tool_call in tool_calls:
        if tool_call.get("name") == "computer":
            input_data = tool_call.get("input", {})
            action = input_data.get("action", {})
            
            output_items.append({
                "type": "computer_call",
                "call_id": tool_call.get("id", ""),
                "action": action,
                "pending_safety_checks": []
            })
    
    return {"output": output_items}


def check_blocklisted_url(url: str) -> None:
    """Raise ValueError if the given URL (including subdomains) is in the blocklist."""
    hostname = urlparse(url).hostname or ""
    if any(
        hostname == blocked or hostname.endswith(f".{blocked}")
        for blocked in BLOCKED_DOMAINS
    ):
        raise ValueError(f"Blocked URL: {url}")

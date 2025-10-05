#!/usr/bin/env python3
"""
CortexAI CLI - Modern command-line interface for CortexAI
Mimics Gemini-style CLI with rich UI, settings, and chat history
"""

import requests
import json
import sys
import argparse
import os
import time
import threading
import subprocess
import readline
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path
import uuid


# Rich UI components
class CortexCompleter:
    """Custom completer for CortexAI CLI commands"""

    def __init__(self):
        self.commands = [
            "help",
            "models",
            "settings",
            "history",
            "clear",
            "status",
            "save",
            "quit",
            "exit",
            "pwd",
            "whereami",
            "ls",
            "list",
            "read",
            "cat",
        ]
        self.file_extensions = [
            ".py",
            ".js",
            ".ts",
            ".html",
            ".css",
            ".md",
            ".txt",
            ".json",
            ".yaml",
            ".yml",
        ]

    def complete(self, text, state):
        """Provide tab completion"""
        if state == 0:
            # First time called
            self.matches = []

            # Check if we're completing a command
            for cmd in self.commands:
                if cmd.startswith(text):
                    self.matches.append(cmd)

            # Check if we're completing a file (for read/cat commands)
            if any(cmd.startswith(text) for cmd in ["read ", "cat "]):
                # Try to complete filenames
                try:
                    for item in os.listdir("."):
                        if item.startswith(text.split()[-1] if " " in text else text):
                            self.matches.append(item)
                except:
                    pass

        # Return the next match
        try:
            return self.matches[state]
        except IndexError:
            return None


class Colors:
    """ANSI color codes for terminal output"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"

    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class CLIDisplay:
    """Handles rich terminal display and formatting"""

    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def print_header():
        """Print the application header"""
        # Create a properly aligned header with exact spacing
        box_width = 58  # Total width of the box
        title = "🤖 CortexAI CLI"
        subtitle = "Modern AI Assistant Interface"

        # Calculate padding for centering
        title_padding = (box_width - len(title)) // 2
        subtitle_padding = (box_width - len(subtitle)) // 2

        print(f"{Colors.BOLD}{Colors.BLUE}╔{'═' * box_width}╗{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BLUE}║{Colors.RESET}{' ' * title_padding}{Colors.BOLD}{title}{Colors.RESET}{' ' * (box_width - len(title) - title_padding)}{Colors.BOLD}{Colors.BLUE}║{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BLUE}║{Colors.RESET}{' ' * subtitle_padding}{Colors.DIM}{subtitle}{Colors.RESET}{' ' * (box_width - len(subtitle) - subtitle_padding)}{Colors.BOLD}{Colors.BLUE}║{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.BLUE}╚{'═' * box_width}╝{Colors.RESET}")
        print()

    @staticmethod
    def print_status(status: str, status_type: str = "info"):
        """Print a status message with appropriate styling"""
        icons = {
            "success": f"{Colors.GREEN}✅{Colors.RESET}",
            "error": f"{Colors.RED}❌{Colors.RESET}",
            "warning": f"{Colors.YELLOW}⚠️{Colors.RESET}",
            "info": f"{Colors.BLUE}ℹ️{Colors.RESET}",
            "loading": f"{Colors.CYAN}⏳{Colors.RESET}",
        }
        print(f"{icons.get(status_type, icons['info'])} {status}")

    @staticmethod
    def print_message(
        content: str,
        sender: str = "assistant",
        timestamp: bool = True,
        model_name: str = None,
    ):
        """Print a chat message with rich formatting"""
        if sender == "user":
            avatar = f"{Colors.CYAN}👤{Colors.RESET}"
            prefix = f"{Colors.BOLD}{Colors.BLUE}You:{Colors.RESET}"
        else:
            avatar = f"{Colors.GREEN}🤖{Colors.RESET}"
            # Use model name if provided, otherwise fall back to "Assistant"
            display_name = model_name if model_name else "Assistant"
            prefix = f"{Colors.BOLD}{Colors.GREEN}{display_name}:{Colors.RESET}"

        time_str = (
            f" {Colors.DIM}[{datetime.now().strftime('%H:%M:%S')}]{Colors.RESET}"
            if timestamp
            else ""
        )
        print(f"\n{avatar} {prefix}{time_str}")
        print(f"{Colors.WHITE}{content}{Colors.RESET}")

    @staticmethod
    def print_usage_info(usage: Dict[str, int]):
        """Print token usage information"""
        print(
            f"\n{Colors.DIM}📊 Usage: {usage['total_tokens']} tokens "
            f"({usage['input_tokens']} input, {usage['output_tokens']} output){Colors.RESET}"
        )

    @staticmethod
    def print_typing_indicator():
        """Print a typing indicator"""
        print(
            f"\n{Colors.CYAN}🤖 Assistant is typing...{Colors.RESET}",
            end="",
            flush=True,
        )

    @staticmethod
    def clear_typing_indicator():
        """Clear the typing indicator line"""
        print("\r" + " " * 50 + "\r", end="", flush=True)


class SettingsManager:
    """Manages CLI settings with persistent storage"""

    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            config_dir = Path.home() / ".cortexai"
        self.config_dir = config_dir
        self.config_file = config_dir / "settings.json"
        self.config_dir.mkdir(exist_ok=True)
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        default_settings = {
            "server_url": "http://localhost:8000",
            "default_model": "gpt-4o-mini",
            "temperature": 0.7,
            "system_prompt": "",
            "max_history": 50,
            "show_timestamps": True,
            "show_usage": True,
            "auto_save": True,
            "streaming": True,
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
            except (json.JSONDecodeError, IOError):
                CLIDisplay.print_status(
                    "Failed to load settings, using defaults", "warning"
                )

        return default_settings

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.settings, f, indent=2)
            CLIDisplay.print_status("Settings saved successfully", "success")
        except IOError:
            CLIDisplay.print_status("Failed to save settings", "error")

    def get(self, key: str, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value"""
        self.settings[key] = value

    def update(self, updates: Dict[str, Any]):
        """Update multiple settings"""
        self.settings.update(updates)


class ChatHistory:
    """Manages chat history and conversations"""

    def __init__(self, history_dir: Path = None):
        if history_dir is None:
            history_dir = Path.home() / ".cortexai" / "history"
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.current_conversation = []
        self.current_conversation_id = None

    def start_new_conversation(self) -> str:
        """Start a new conversation and return its ID"""
        self.current_conversation_id = str(uuid.uuid4())
        self.current_conversation = []
        return self.current_conversation_id

    def add_message(self, message: str, sender: str, usage: Dict[str, int] = None):
        """Add a message to the current conversation"""
        message_data = {
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "content": message,
            "usage": usage or {},
        }
        self.current_conversation.append(message_data)

    def save_conversation(self):
        """Save the current conversation to disk"""
        if not self.current_conversation_id or not self.current_conversation:
            return

        conversation_file = self.history_dir / f"{self.current_conversation_id}.json"
        try:
            with open(conversation_file, "w") as f:
                json.dump(
                    {
                        "id": self.current_conversation_id,
                        "created_at": (
                            self.current_conversation[0]["timestamp"]
                            if self.current_conversation
                            else datetime.now().isoformat()
                        ),
                        "messages": self.current_conversation,
                    },
                    f,
                    indent=2,
                )
        except IOError:
            CLIDisplay.print_status("Failed to save conversation", "error")

    def load_conversation(self, conversation_id: str) -> bool:
        """Load a conversation by ID"""
        conversation_file = self.history_dir / f"{conversation_id}.json"
        if not conversation_file.exists():
            return False

        try:
            with open(conversation_file, "r") as f:
                data = json.load(f)
                self.current_conversation_id = data["id"]
                self.current_conversation = data["messages"]
                return True
        except (json.JSONDecodeError, IOError):
            CLIDisplay.print_status("Failed to load conversation", "error")
            return False

    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all saved conversations"""
        conversations = []
        for file_path in self.history_dir.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    conversations.append(
                        {
                            "id": data["id"],
                            "created_at": data["created_at"],
                            "message_count": len(data.get("messages", [])),
                            "first_message": (
                                data.get("messages", [{}])[0].get("content", "")[:50]
                                + "..."
                                if data.get("messages")
                                else ""
                            ),
                        }
                    )
            except (json.JSONDecodeError, IOError):
                continue

        return sorted(conversations, key=lambda x: x["created_at"], reverse=True)

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        conversation_file = self.history_dir / f"{conversation_id}.json"
        try:
            if conversation_file.exists():
                conversation_file.unlink()
                return True
        except IOError:
            pass
        return False


class CortexCLI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.settings = SettingsManager()
        self.history = ChatHistory()
        self.is_connected = False
        self.last_context = None  # Store context from commands for AI

        # Setup readline for better input handling
        self.setup_readline()

    def setup_readline(self):
        """Setup readline for enhanced input with history and editing"""
        try:
            # Enable history and editing
            readline.parse_and_bind("tab: complete")
            readline.parse_and_bind("set editing-mode emacs")

            # Set up custom completer
            completer = CortexCompleter()
            readline.set_completer(completer.complete)

            # Set up history file with better error handling
            history_file = os.path.expanduser("~/.cortexai/input_history")

            try:
                # Try to create directory
                os.makedirs(os.path.dirname(history_file), exist_ok=True)

                # Try to read history file
                readline.read_history_file(history_file)
            except (FileNotFoundError, PermissionError, OSError):
                # If we can't read/write to the file, just continue without history
                pass

            # Limit history size
            readline.set_history_length(1000)

        except Exception:
            # If readline setup fails entirely, continue without enhanced features
            pass

    def save_history(self):
        """Save readline history to file"""
        try:
            history_file = os.path.expanduser("~/.cortexai/input_history")
            readline.write_history_file(history_file)
        except (PermissionError, OSError):
            # If we can't save history, just continue
            pass

    def get_user_input(self, prompt: str) -> str:
        """Get user input with readline support"""
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            return ""

    def health_check(self) -> bool:
        """Check if the server is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                CLIDisplay.print_status("Server is healthy and connected", "success")
                return True
            else:
                self.is_connected = False
                CLIDisplay.print_status(
                    f"Server health check failed: {response.status_code}", "error"
                )
                return False
        except requests.exceptions.ConnectionError:
            self.is_connected = False
            CLIDisplay.print_status("Cannot connect to server. Is it running?", "error")
            return False
        except requests.exceptions.Timeout:
            self.is_connected = False
            CLIDisplay.print_status("Server connection timeout", "error")
            return False

    def list_models(self):
        """List available models with rich formatting"""
        CLIDisplay.print_status("Fetching available models...", "loading")
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                print(f"\n{Colors.BOLD}🤖 Available Models{Colors.RESET}")
                print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.RESET}")

                # Provider icons mapping
                provider_icons = {
                    "openai": "🔵",
                    "google": "🟡",
                    "cohere": "🟣",
                    "anthropic": "🟠",
                }

                for provider, model_list in models.items():
                    icon = provider_icons.get(provider.lower(), "🤖")
                    provider_name = provider.capitalize()
                    print(f"\n{icon} {Colors.BOLD}{provider_name}{Colors.RESET}")
                    print(f"{Colors.DIM}{'-' * (len(provider_name) + 2)}{Colors.RESET}")

                    for model in model_list:
                        # Highlight the default model
                        if model == self.settings.get("default_model"):
                            print(
                                f"  {Colors.GREEN}★{Colors.RESET} {Colors.BOLD}{model}{Colors.RESET} {Colors.DIM}(default){Colors.RESET}"
                            )
                        else:
                            print(f"  • {Colors.WHITE}{model}{Colors.RESET}")
            else:
                CLIDisplay.print_status(
                    f"Failed to get models: {response.status_code}", "error"
                )
        except requests.exceptions.ConnectionError:
            CLIDisplay.print_status("Cannot connect to server", "error")
        except requests.exceptions.Timeout:
            CLIDisplay.print_status("Request timeout while fetching models", "error")

    def chat(
        self,
        message: str,
        model: str = None,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        show_user_message: bool = True,
    ) -> Optional[str]:
        """Send a chat message with enhanced UI"""
        # Use settings defaults if not provided
        if model is None:
            model = self.settings.get("default_model", "gpt-4o-mini")
        if temperature is None:
            temperature = self.settings.get("temperature", 0.7)
        if system_prompt is None:
            system_prompt = self.settings.get("system_prompt", "")

        # Include context if available
        full_message = message
        if self.last_context:
            full_message = f"Context: {self.last_context}\n\nUser message: {message}"
            self.last_context = None  # Clear context after use

        payload = {"message": full_message, "model": model, "temperature": temperature}

        # Only include conversation_id if it's a valid response ID from the server
        # Don't send our internal UUID conversation IDs
        if conversation_id and conversation_id.startswith("resp_"):
            payload["conversation_id"] = conversation_id
        if system_prompt:
            payload["system_prompt"] = system_prompt

        # Add user message to history
        if not self.history.current_conversation_id:
            self.history.start_new_conversation()

        self.history.add_message(message, "user")

        # Show user message if requested (not shown in interactive mode)
        if show_user_message:
            CLIDisplay.print_message(
                message, "user", self.settings.get("show_timestamps", True)
            )

        # Show typing indicator only for non-streaming to avoid extra lines
        if not self.settings.get("streaming", True):
            CLIDisplay.print_typing_indicator()

        try:
            if self.settings.get("streaming", True):
                conv_id = self._chat_stream(payload, model)
                return conv_id
            else:
                response = requests.post(
                    f"{self.base_url}/chat", json=payload, timeout=60
                )
                CLIDisplay.clear_typing_indicator()

                if response.status_code == 200:
                    result = response.json()

                    # Show assistant response with model name
                    model_name = result.get("model", model)
                    CLIDisplay.print_message(
                        result["message"],
                        "assistant",
                        self.settings.get("show_timestamps", True),
                        model_name,
                    )

                    # Show usage info if enabled
                    if self.settings.get("show_usage", True):
                        CLIDisplay.print_usage_info(result["usage"])

                    # Add assistant message to history
                    self.history.add_message(
                        result["message"], "assistant", result["usage"]
                    )

                    # Save conversation if auto-save is enabled
                    if self.settings.get("auto_save", True):
                        self.history.save_conversation()

                    # Update conversation ID
                    self.history.current_conversation_id = result["conversation_id"]

                    return result["conversation_id"]
                else:
                    CLIDisplay.clear_typing_indicator()
                    error_msg = f"Chat failed: {response.status_code}"
                    if hasattr(response, "text"):
                        try:
                            error_data = response.json()
                            error_msg += f" - {error_data.get('detail', response.text)}"
                        except:
                            error_msg += f" - {response.text}"

                    CLIDisplay.print_message(error_msg, "assistant")
                    return None

        except requests.exceptions.ConnectionError:
            CLIDisplay.clear_typing_indicator()
            CLIDisplay.print_message("Cannot connect to server", "assistant")
            return None
        except requests.exceptions.Timeout:
            CLIDisplay.clear_typing_indicator()
            CLIDisplay.print_message(
                "Request timeout - server may be overloaded", "assistant"
            )
            return None

    def _chat_stream(
        self, payload: Dict[str, Any], requested_model: str
    ) -> Optional[str]:
        """Stream assistant reply from /chat/stream (SSE)."""
        import sys

        try:
            with requests.post(
                f"{self.base_url}/chat/stream", json=payload, stream=True, timeout=120
            ) as resp:
                if resp.status_code != 200:
                    CLIDisplay.clear_typing_indicator()
                    try:
                        err = resp.json()
                        CLIDisplay.print_message(
                            f"Streaming failed: {resp.status_code} - {err.get('detail', '')}",
                            "assistant",
                        )
                    except Exception:
                        CLIDisplay.print_message(
                            f"Streaming failed: HTTP {resp.status_code}", "assistant"
                        )
                    return None

                # Clear typing indicator and print header line
                CLIDisplay.clear_typing_indicator()

                show_ts = self.settings.get("show_timestamps", True)
                display_name = requested_model
                timestamp = (
                    f" {Colors.DIM}[{datetime.now().strftime('%H:%M:%S')}]"
                    + Colors.RESET
                    if show_ts
                    else ""
                )
                header = f"\n{Colors.GREEN}🤖{Colors.RESET} {Colors.BOLD}{Colors.GREEN}{display_name}:{Colors.RESET}{timestamp}\n"
                sys.stdout.write(header)
                sys.stdout.flush()

                # Parse SSE frames
                event = None
                data_buf = []
                full_text = []
                final_usage = None
                final_conv_id = None
                model_name = requested_model
                approx_out_tokens = 0
                delta_count = 0

                try:
                    for raw_line in resp.iter_lines(decode_unicode=True):
                        if raw_line is None:
                            continue
                        line = raw_line.strip("\r")
                        if line == "":
                            # End of one SSE event
                            if event and data_buf:
                                data_str = "\n".join(data_buf)
                                try:
                                    payload_obj = json.loads(data_str)
                                except Exception:
                                    payload_obj = None

                                if event == "start" and isinstance(payload_obj, dict):
                                    model_name = payload_obj.get("model", model_name)
                                elif event == "delta" and isinstance(payload_obj, dict):
                                    delta = payload_obj.get("text", "")
                                    if delta:
                                        full_text.append(delta)
                                        sys.stdout.write(Colors.WHITE + delta + Colors.RESET)
                                        sys.stdout.flush()
                                        # Incremental approx tokens (roughly 1 per 4 chars)
                                        approx_out_tokens += max(1, len(delta) // 4)
                                        delta_count += 1
                                        if delta_count % 20 == 0 and self.settings.get("show_usage", True):
                                            sys.stdout.write(
                                                f"\n{Colors.DIM}… tokens ~ {approx_out_tokens}{Colors.RESET}\n"
                                            )
                                            sys.stdout.flush()
                                elif event == "end" and isinstance(payload_obj, dict):
                                    final_usage = payload_obj.get("usage")
                                    final_conv_id = payload_obj.get("conversation_id")
                                    # End of stream
                                    break

                            # Reset for next event
                            event = None
                            data_buf = []
                            continue

                        if line.startswith("event:"):
                            event = line[len("event:") :].strip()
                        elif line.startswith("data:"):
                            data_buf.append(line[len("data:") :].strip())
                except KeyboardInterrupt:
                    try:
                        resp.close()
                    except Exception:
                        pass
                    sys.stdout.write(f"\n{Colors.DIM}[stream aborted]{Colors.RESET}\n")
                    sys.stdout.flush()

                # Finish the line
                sys.stdout.write("\n")
                sys.stdout.flush()

                content = "".join(full_text)

                # Show usage if enabled
                if self.settings.get("show_usage", True):
                    if final_usage:
                        CLIDisplay.print_usage_info(final_usage)
                    elif approx_out_tokens:
                        CLIDisplay.print_usage_info(
                            {
                                "total_tokens": approx_out_tokens,
                                "input_tokens": 0,
                                "output_tokens": approx_out_tokens,
                            }
                        )

                # Record in history and save
                self.history.add_message(content, "assistant", final_usage or {})
                if self.settings.get("auto_save", True):
                    self.history.save_conversation()

                # Update conversation id if provided
                if final_conv_id:
                    self.history.current_conversation_id = final_conv_id
                    return final_conv_id
                return self.history.current_conversation_id
        except requests.exceptions.Timeout:
            CLIDisplay.clear_typing_indicator()
            CLIDisplay.print_message(
                "Streaming timeout - server may be overloaded", "assistant"
            )
            return None
        except requests.exceptions.ConnectionError:
            CLIDisplay.clear_typing_indicator()
            CLIDisplay.print_message("Cannot connect to server", "assistant")
            return None

    def show_settings_menu(self):
        """Display and manage settings"""
        while True:
            CLIDisplay.clear_screen()
            CLIDisplay.print_header()

            print(f"{Colors.BOLD}⚙️  Settings{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.RESET}")

            # Current settings display
            print(f"\n{Colors.BOLD}Current Settings:{Colors.RESET}")
            print(
                f"  Server URL: {Colors.CYAN}{self.settings.get('server_url')}{Colors.RESET}"
            )
            print(
                f"  Default Model: {Colors.CYAN}{self.settings.get('default_model')}{Colors.RESET}"
            )
            print(
                f"  Temperature: {Colors.CYAN}{self.settings.get('temperature')}{Colors.RESET}"
            )
            print(
                f"  System Prompt: {Colors.CYAN}{self.settings.get('system_prompt', 'None')}{Colors.RESET}"
            )
            print(
                f"  Show Timestamps: {Colors.CYAN}{self.settings.get('show_timestamps')}{Colors.RESET}"
            )
            print(
                f"  Show Usage: {Colors.CYAN}{self.settings.get('show_usage')}{Colors.RESET}"
            )
            print(
                f"  Auto Save: {Colors.CYAN}{self.settings.get('auto_save')}{Colors.RESET}"
            )
            print(
                f"  Streaming (SSE): {Colors.CYAN}{self.settings.get('streaming')}{Colors.RESET}"
            )

            print(f"\n{Colors.BOLD}Settings Menu:{Colors.RESET}")
            print(f"  {Colors.GREEN}1{Colors.RESET} - Change Server URL")
            print(f"  {Colors.GREEN}2{Colors.RESET} - Change Default Model")
            print(f"  {Colors.GREEN}3{Colors.RESET} - Change Temperature")
            print(f"  {Colors.GREEN}4{Colors.RESET} - Set System Prompt")
            print(f"  {Colors.GREEN}5{Colors.RESET} - Toggle Timestamps")
            print(f"  {Colors.GREEN}6{Colors.RESET} - Toggle Usage Display")
            print(f"  {Colors.GREEN}7{Colors.RESET} - Toggle Auto Save")
            print(f"  {Colors.GREEN}8{Colors.RESET} - Test Connection")
            print(f"  {Colors.GREEN}9{Colors.RESET} - Reset to Defaults")
            print(f"  {Colors.GREEN}10{Colors.RESET} - Toggle Streaming (SSE)")
            print(f"  {Colors.YELLOW}0{Colors.RESET} - Back to Chat")

            try:
                choice = input(f"\n{Colors.BOLD}Select option:{Colors.RESET} ").strip()

                if choice == "0":
                    break
                elif choice == "1":
                    new_url = input(
                        f"Enter new server URL [{self.settings.get('server_url')}]: "
                    ).strip()
                    if new_url:
                        self.settings.set("server_url", new_url)
                        self.base_url = new_url.rstrip("/")
                        self.settings.save_settings()
                elif choice == "2":
                    self.list_models()
                    new_model = input(
                        f"Enter model name [{self.settings.get('default_model')}]: "
                    ).strip()
                    if new_model:
                        self.settings.set("default_model", new_model)
                        self.settings.save_settings()
                elif choice == "3":
                    try:
                        new_temp = float(
                            input(
                                f"Enter temperature (0.0-2.0) [{self.settings.get('temperature')}]: "
                            ).strip()
                        )
                        if 0.0 <= new_temp <= 2.0:
                            self.settings.set("temperature", new_temp)
                            self.settings.save_settings()
                        else:
                            CLIDisplay.print_status(
                                "Temperature must be between 0.0 and 2.0", "error"
                            )
                            input("Press Enter to continue...")
                    except ValueError:
                        CLIDisplay.print_status("Invalid temperature value", "error")
                        input("Press Enter to continue...")
                elif choice == "4":
                    new_prompt = input(
                        f"Enter system prompt (or empty to clear): "
                    ).strip()
                    self.settings.set("system_prompt", new_prompt)
                    self.settings.save_settings()
                elif choice == "5":
                    current = self.settings.get("show_timestamps")
                    self.settings.set("show_timestamps", not current)
                    self.settings.save_settings()
                elif choice == "6":
                    current = self.settings.get("show_usage")
                    self.settings.set("show_usage", not current)
                    self.settings.save_settings()
                elif choice == "7":
                    current = self.settings.get("auto_save")
                    self.settings.set("auto_save", not current)
                    self.settings.save_settings()
                elif choice == "8":
                    self.health_check()
                    input("Press Enter to continue...")
                elif choice == "9":
                    confirm = (
                        input("Reset all settings to defaults? (y/N): ").strip().lower()
                    )
                    if confirm == "y":
                        # Reset to defaults
                        default_settings = {
                            "server_url": "http://localhost:8000",
                            "default_model": "gpt-4o-mini",
                            "temperature": 0.7,
                            "system_prompt": "",
                            "show_timestamps": True,
                            "show_usage": True,
                            "auto_save": True,
                            "streaming": True,
                        }
                        self.settings.update(default_settings)
                        self.base_url = default_settings["server_url"]
                        self.settings.save_settings()
                elif choice == "10":
                    current = self.settings.get("streaming", True)
                    self.settings.set("streaming", not current)
                    self.settings.save_settings()

            except KeyboardInterrupt:
                break
            except EOFError:
                break

    def show_conversation_history(self):
        """Display and manage conversation history"""
        while True:
            CLIDisplay.clear_screen()
            CLIDisplay.print_header()

            print(f"{Colors.BOLD}📚 Conversation History{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.RESET}")

            conversations = self.history.list_conversations()

            if not conversations:
                print(f"\n{Colors.DIM}No saved conversations found.{Colors.RESET}")
            else:
                print(f"\n{Colors.BOLD}Recent Conversations:{Colors.RESET}")
                for i, conv in enumerate(conversations[:10], 1):
                    date_str = datetime.fromisoformat(conv["created_at"]).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    print(
                        f"  {Colors.GREEN}{i}{Colors.RESET} - {Colors.DIM}{date_str}{Colors.RESET} "
                        f"({conv['message_count']} messages)"
                    )
                    print(f"      {Colors.WHITE}{conv['first_message']}{Colors.RESET}")
                    print(f"      {Colors.DIM}ID: {conv['id'][:8]}...{Colors.RESET}")

            print(f"\n{Colors.BOLD}History Menu:{Colors.RESET}")
            print(f"  {Colors.GREEN}1-10{Colors.RESET} - Load conversation")
            print(f"  {Colors.YELLOW}0{Colors.RESET} - Back to Chat")

            try:
                choice = input(
                    f"\n{Colors.BOLD}Select conversation or option:{Colors.RESET} "
                ).strip()

                if choice == "0":
                    break
                elif choice.isdigit() and 1 <= int(choice) <= len(conversations):
                    conv_index = int(choice) - 1
                    conv_id = conversations[conv_index]["id"]

                    if self.history.load_conversation(conv_id):
                        CLIDisplay.print_status(
                            f"Loaded conversation with {conversations[conv_index]['message_count']} messages",
                            "success",
                        )

                        # Display conversation history
                        print(f"\n{Colors.BOLD}Conversation History:{Colors.RESET}")
                        for msg in self.history.current_conversation:
                            timestamp = datetime.fromisoformat(
                                msg["timestamp"]
                            ).strftime("%H:%M:%S")
                            sender = (
                                "👤 You" if msg["sender"] == "user" else "🤖 Assistant"
                            )
                            print(f"\n{Colors.DIM}[{timestamp}]{Colors.RESET} {sender}")
                            print(f"{Colors.WHITE}{msg['content']}{Colors.RESET}")

                        input("\nPress Enter to continue with this conversation...")
                    break

            except KeyboardInterrupt:
                break
            except EOFError:
                break

    def interactive_chat(self, model: str = None):
        """Start an enhanced interactive chat session"""
        if model is None:
            model = self.settings.get("default_model", "gpt-4o-mini")

        # Update base URL from settings
        self.base_url = self.settings.get("server_url", "http://localhost:8000").rstrip(
            "/"
        )

        CLIDisplay.clear_screen()
        CLIDisplay.print_header()

        # Initial health check
        CLIDisplay.print_status("Checking server connection...", "loading")
        if not self.health_check():
            CLIDisplay.print_status(
                "Server not available. Some features may not work.", "warning"
            )

        print(f"\n{Colors.BOLD}🚀 Starting interactive chat with {model}{Colors.RESET}")
        print(f"{Colors.DIM}Type 'help' for commands, 'quit' to exit{Colors.RESET}")

        # Start new conversation if none exists
        if not self.history.current_conversation_id:
            self.history.start_new_conversation()

        while True:
            try:
                # Show conversation status
                conv_status = f"{Colors.DIM}[{len(self.history.current_conversation)} messages]{Colors.RESET}"
                user_input = self.get_user_input(
                    f"\n{Colors.BOLD}💬 You{conv_status}:{Colors.RESET} "
                ).strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    if (
                        self.settings.get("auto_save", True)
                        and self.history.current_conversation
                    ):
                        self.history.save_conversation()
                    self.save_history()
                    CLIDisplay.print_status("Goodbye! 👋", "success")
                    break
                elif user_input.lower() == "help":
                    self.show_help()
                    continue
                elif user_input.lower() == "models":
                    self.list_models()
                    continue
                elif user_input.lower() == "settings":
                    self.show_settings_menu()
                    CLIDisplay.clear_screen()
                    CLIDisplay.print_header()
                    continue
                elif user_input.lower() == "history":
                    self.show_conversation_history()
                    CLIDisplay.clear_screen()
                    CLIDisplay.print_header()
                    continue
                elif user_input.lower() == "clear":
                    self.history.start_new_conversation()
                    CLIDisplay.print_status("Started new conversation", "success")
                    continue
                elif user_input.lower() == "status":
                    self.show_status()
                    continue
                elif user_input.lower() == "pwd" or user_input.lower() == "whereami":
                    context_info = self.get_current_directory_info()
                    self.show_current_directory()
                    # Store context for next AI interaction
                    self.last_context = context_info
                    continue
                elif user_input.lower().startswith(
                    "ls"
                ) or user_input.lower().startswith("list"):
                    directory_info = self.get_directory_info(user_input)
                    self.list_directory(user_input)
                    # Store context for next AI interaction
                    self.last_context = directory_info
                    continue
                elif user_input.lower().startswith(
                    "read "
                ) or user_input.lower().startswith("cat "):
                    file_content = self.get_file_content(user_input)
                    self.read_file(user_input)
                    # Store context for next AI interaction
                    self.last_context = file_content
                    continue
                elif user_input.lower() == "save":
                    if self.history.current_conversation:
                        self.history.save_conversation()
                        CLIDisplay.print_status("Conversation saved", "success")
                    else:
                        CLIDisplay.print_status("No conversation to save", "warning")
                    continue
                elif not user_input:
                    continue

                # Check if user is asking about current location/environment
                location_keywords = [
                    "where am i",
                    "what directory",
                    "current directory",
                    "working directory",
                    "pwd",
                    "location",
                    "path",
                ]
                if any(keyword in user_input.lower() for keyword in location_keywords):
                    # Automatically provide location context
                    location_info = self.get_current_directory_info()
                    self.last_context = location_info

                # Check if user is asking about files or code in current directory
                file_keywords = [
                    "what files",
                    "list files",
                    "show files",
                    "files here",
                    "code here",
                    "project structure",
                ]
                if any(keyword in user_input.lower() for keyword in file_keywords):
                    # Automatically provide directory listing context
                    directory_info = self.get_directory_info("ls")
                    self.last_context = directory_info

                # Send message (don't show user message in interactive mode since it's already shown in prompt)
                self.chat(
                    user_input,
                    model,
                    self.history.current_conversation_id,
                    show_user_message=False,
                )

            except KeyboardInterrupt:
                if (
                    self.settings.get("auto_save", True)
                    and self.history.current_conversation
                ):
                    self.history.save_conversation()
                self.save_history()
                CLIDisplay.print_status("Goodbye! 👋", "success")
                break
            except EOFError:
                if (
                    self.settings.get("auto_save", True)
                    and self.history.current_conversation
                ):
                    self.history.save_conversation()
                self.save_history()
                CLIDisplay.print_status("Goodbye! 👋", "success")
                break

    def get_current_directory_info(self):
        """Get current directory info as string for AI context"""
        try:
            cwd = os.getcwd()
            git_info = self.get_git_info()
            python_info = f"Python {sys.version.split()[0]}"

            info_parts = [f"Working Directory: {cwd}"]

            if git_info:
                info_parts.append(f"Git Branch: {git_info.get('branch', 'unknown')}")
                info_parts.append(f"Git Remote: {git_info.get('remote', 'none')}")

            info_parts.append(f"Python Version: {python_info}")

            recent_files = self.get_recent_files()
            if recent_files:
                info_parts.append(f"Recent Files: {', '.join(recent_files[:5])}")

            return "; ".join(info_parts)
        except Exception as e:
            return f"Error getting directory info: {e}"

    def show_current_directory(self):
        """Show current working directory and environment info"""
        try:
            cwd = os.getcwd()
            git_info = self.get_git_info()
            python_info = f"Python {sys.version.split()[0]}"

            CLIDisplay.print_status("Current Environment", "info")
            print(f"\n{Colors.CYAN}📁 Working Directory:{Colors.RESET}")
            print(f"   {cwd}")

            if git_info:
                print(f"\n{Colors.GREEN}🌿 Git Repository:{Colors.RESET}")
                print(f"   Branch: {git_info.get('branch', 'unknown')}")
                print(f"   Remote: {git_info.get('remote', 'none')}")

            print(f"\n{Colors.BLUE}🐍 Runtime:{Colors.RESET}")
            print(f"   {python_info}")

            # Show recent files
            recent_files = self.get_recent_files()
            if recent_files:
                print(f"\n{Colors.YELLOW}📄 Recent Files:{Colors.RESET}")
                for file in recent_files[:5]:
                    print(f"   {file}")

        except Exception as e:
            CLIDisplay.print_status(f"Error getting directory info: {e}", "error")

    def get_git_info(self):
        """Get git repository information"""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
            branch = result.stdout.strip() if result.returncode == 0 else None

            # Get remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
            remote = result.stdout.strip() if result.returncode == 0 else None

            return {"branch": branch, "remote": remote}
        except:
            return None

    def get_recent_files(self):
        """Get recently modified files"""
        try:
            cwd = os.getcwd()
            files = []
            for root, dirs, filenames in os.walk(cwd):
                # Skip hidden directories and common build directories
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".")
                    and d not in ["node_modules", "__pycache__", "build", "dist"]
                ]

                for filename in filenames:
                    if not filename.startswith(".") and filename.endswith(
                        (".py", ".js", ".ts", ".html", ".css", ".md", ".txt", ".json")
                    ):
                        filepath = os.path.join(root, filename)
                        try:
                            mtime = os.path.getmtime(filepath)
                            files.append((mtime, os.path.relpath(filepath, cwd)))
                        except:
                            continue

            # Sort by modification time (newest first) and return just the filenames
            files.sort(reverse=True)
            return [file[1] for file in files]
        except:
            return []

    def get_directory_info(self, command):
        """Get directory listing as string for AI context"""
        try:
            parts = command.split()
            path = parts[1] if len(parts) > 1 else "."

            if not os.path.exists(path):
                return f"Path not found: {path}"

            items = os.listdir(path)
            items.sort()

            item_list = []
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    item_list.append(f"{item}/")
                else:
                    item_list.append(item)

            return f"Contents of {path}: {', '.join(item_list)}"

        except Exception as e:
            return f"Error listing directory: {e}"

    def list_directory(self, command):
        """List directory contents"""
        try:
            parts = command.split()
            path = parts[1] if len(parts) > 1 else "."

            if not os.path.exists(path):
                CLIDisplay.print_status(f"Path not found: {path}", "error")
                return

            CLIDisplay.print_status(f"Contents of {path}", "info")

            items = os.listdir(path)
            items.sort()

            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    print(f"  {Colors.BLUE}📁 {item}/{Colors.RESET}")
                else:
                    # Color code by file extension
                    ext = os.path.splitext(item)[1]
                    if ext in [".py"]:
                        color = Colors.GREEN
                        icon = "🐍"
                    elif ext in [".js", ".ts", ".html", ".css"]:
                        color = Colors.YELLOW
                        icon = "🌐"
                    elif ext in [".md", ".txt"]:
                        color = Colors.WHITE
                        icon = "📄"
                    elif ext in [".json", ".yaml", ".yml"]:
                        color = Colors.CYAN
                        icon = "⚙️"
                    else:
                        color = Colors.WHITE
                        icon = "📄"

                    print(f"  {color}{icon} {item}{Colors.RESET}")

        except Exception as e:
            CLIDisplay.print_status(f"Error listing directory: {e}", "error")

    def get_file_content(self, command):
        """Get file content as string for AI context"""
        try:
            parts = command.split()
            if len(parts) < 2:
                return "Usage: read <filename>"

            filename = parts[1]
            if not os.path.exists(filename):
                return f"File not found: {filename}"

            # Check file size
            file_size = os.path.getsize(filename)
            if file_size > 10000:  # 10KB limit
                return f"File too large ({file_size} bytes) - truncated for AI context"

            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            return f"File: {filename}\nContent:\n{content}"

        except Exception as e:
            return f"Error reading file: {e}"

    def read_file(self, command):
        """Read and display file contents"""
        try:
            parts = command.split()
            if len(parts) < 2:
                CLIDisplay.print_status("Usage: read <filename>", "error")
                return

            filename = parts[1]
            if not os.path.exists(filename):
                CLIDisplay.print_status(f"File not found: {filename}", "error")
                return

            # Check file size
            file_size = os.path.getsize(filename)
            if file_size > 10000:  # 10KB limit
                CLIDisplay.print_status(
                    f"File too large ({file_size} bytes). Use a smaller file.",
                    "warning",
                )
                return

            CLIDisplay.print_status(f"Reading {filename}", "info")

            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            print(f"\n{Colors.CYAN}📄 {filename}:{Colors.RESET}")
            print(f"{Colors.DIM}{'='*50}{Colors.RESET}")
            print(content)
            print(f"{Colors.DIM}{'='*50}{Colors.RESET}")

        except Exception as e:
            CLIDisplay.print_status(f"Error reading file: {e}", "error")

    def show_help(self):
        """Display help information"""
        print(f"\n{Colors.BOLD}🤖 CortexAI CLI Help{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.RESET}")

        print(f"\n{Colors.BOLD}Chat Commands:{Colors.RESET}")
        print(f"  {Colors.GREEN}help{Colors.RESET}     - Show this help message")
        print(f"  {Colors.GREEN}models{Colors.RESET}   - List available AI models")
        print(f"  {Colors.GREEN}settings{Colors.RESET} - Open settings menu")
        print(
            f"  {Colors.GREEN}history{Colors.RESET}  - View and load conversation history"
        )
        print(f"  {Colors.GREEN}clear{Colors.RESET}    - Start a new conversation")
        print(f"  {Colors.GREEN}status{Colors.RESET}   - Show current status")
        print(
            f"  {Colors.GREEN}save{Colors.RESET}     - Manually save current conversation"
        )
        print(f"  {Colors.GREEN}quit{Colors.RESET}     - Exit the application")

        print(f"\n{Colors.BOLD}Context Commands:{Colors.RESET}")
        print(
            f"  {Colors.GREEN}pwd{Colors.RESET}      - Show current directory and environment"
        )
        print(
            f"  {Colors.GREEN}whereami{Colors.RESET} - Show current directory and environment"
        )
        print(f"  {Colors.GREEN}ls [path]{Colors.RESET} - List directory contents")
        print(f"  {Colors.GREEN}list [path]{Colors.RESET} - List directory contents")
        print(f"  {Colors.GREEN}read <file>{Colors.RESET} - Read file contents")
        print(f"  {Colors.GREEN}cat <file>{Colors.RESET} - Read file contents")

        print(f"\n{Colors.BOLD}Features:{Colors.RESET}")
        print(f"  • Rich terminal UI with colors and formatting")
        print(f"  • Persistent settings and conversation history")
        print(f"  • Multiple AI model support")
        print(f"  • Typing indicators and usage statistics")
        print(f"  • Auto-save conversations")

        print(f"\n{Colors.DIM}Just type your message to start chatting!{Colors.RESET}")

    def show_status(self):
        """Show current application status"""
        print(f"\n{Colors.BOLD}📊 Current Status{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 50}{Colors.RESET}")

        # Connection status
        status_icon = "🟢" if self.is_connected else "🔴"
        status_text = "Connected" if self.is_connected else "Disconnected"
        status_color = Colors.GREEN if self.is_connected else Colors.RED
        print(
            f"\n{status_icon} Server: {status_color}{status_text}{Colors.RESET} ({self.base_url})"
        )

        # Current conversation
        conv_id = self.history.current_conversation_id
        if conv_id:
            print(
                f"💬 Conversation: {Colors.CYAN}{conv_id[:8]}...{Colors.RESET} ({len(self.history.current_conversation)} messages)"
            )
        else:
            print(f"💬 Conversation: {Colors.DIM}None{Colors.RESET}")

        # Current settings
        print(
            f"🤖 Model: {Colors.CYAN}{self.settings.get('default_model')}{Colors.RESET}"
        )
        print(
            f"🌡️  Temperature: {Colors.CYAN}{self.settings.get('temperature')}{Colors.RESET}"
        )
        print(
            f"💾 Auto-save: {Colors.CYAN}{self.settings.get('auto_save')}{Colors.RESET}"
        )

        # History stats
        conversations = self.history.list_conversations()
        print(
            f"📚 Saved conversations: {Colors.CYAN}{len(conversations)}{Colors.RESET}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="CortexAI CLI - Modern AI Assistant Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cortex_cli                          # Start interactive chat
  cortex_cli interactive              # Start interactive chat
  cortex_cli chat "Hello, AI!"        # Send single message
  cortex_cli models                   # List available models
  cortex_cli health                   # Check server health
  cortex_cli settings                 # Open settings menu
        """,
    )
    parser.add_argument("--url", help="Server URL (overrides settings)")
    parser.add_argument("--model", help="Default model to use (overrides settings)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Health check
    subparsers.add_parser("health", help="Check server health")

    # List models
    subparsers.add_parser("models", help="List available models")

    # Settings
    subparsers.add_parser("settings", help="Open settings menu")

    # Chat
    chat_parser = subparsers.add_parser("chat", help="Send a chat message")
    chat_parser.add_argument("message", help="Message to send")
    chat_parser.add_argument("--model", help="Model to use")
    chat_parser.add_argument("--conversation-id", help="Continue conversation")
    chat_parser.add_argument("--system-prompt", help="System prompt")
    chat_parser.add_argument("--temperature", type=float, help="Temperature (0.0-2.0)")

    # Interactive chat
    interactive_parser = subparsers.add_parser(
        "interactive", help="Start interactive chat"
    )
    interactive_parser.add_argument("--model", help="Model to use")

    # History
    history_parser = subparsers.add_parser("history", help="View conversation history")

    # Status
    subparsers.add_parser("status", help="Show current status")

    args = parser.parse_args()

    # Initialize CLI with settings
    cli = CortexCLI()

    # Override settings with command line arguments
    if args.url:
        cli.settings.set("server_url", args.url)
        cli.base_url = args.url.rstrip("/")

    if args.model:
        cli.settings.set("default_model", args.model)

    # Execute command
    if args.command == "health":
        cli.health_check()
    elif args.command == "models":
        cli.list_models()
    elif args.command == "settings":
        cli.show_settings_menu()
    elif args.command == "chat":
        model = args.model or cli.settings.get("default_model", "gpt-4o-mini")
        cli.chat(
            args.message,
            model,
            args.conversation_id,
            args.system_prompt,
            args.temperature,
        )
    elif args.command == "interactive":
        model = args.model or cli.settings.get("default_model", "gpt-4o-mini")
        cli.interactive_chat(model)
    elif args.command == "history":
        cli.show_conversation_history()
    elif args.command == "status":
        cli.show_status()
    else:
        # Default: start interactive chat
        model = args.model or cli.settings.get("default_model", "gpt-4o-mini")
        cli.interactive_chat(model)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)

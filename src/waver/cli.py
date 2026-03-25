import os
import sys
import io
import ctypes

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def setup_colors():
    try:
        import colorama

        colorama.init()
        return {
            "RED": "\033[91m",
            "GREEN": "\033[92m",
            "YELLOW": "\033[93m",
            "BLUE": "\033[94m",
            "MAGENTA": "\033[95m",
            "CYAN": "\033[96m",
            "RESET": "\033[0m",
        }
    except ImportError:
        pass

    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            return {
                "RED": "\033[91m",
                "GREEN": "\033[92m",
                "YELLOW": "\033[93m",
                "BLUE": "\033[94m",
                "MAGENTA": "\033[95m",
                "CYAN": "\033[96m",
                "RESET": "\033[0m",
            }
        except Exception:
            return {
                "RED": "",
                "GREEN": "",
                "YELLOW": "",
                "BLUE": "",
                "MAGENTA": "",
                "CYAN": "",
                "RESET": "",
            }
    else:
        return {
            "RED": "\033[91m",
            "GREEN": "\033[92m",
            "YELLOW": "\033[93m",
            "BLUE": "\033[94m",
            "MAGENTA": "\033[95m",
            "CYAN": "\033[96m",
            "RESET": "\033[0m",
        }


_colors = setup_colors()


class Style:
    RED = _colors["RED"]
    GREEN = _colors["GREEN"]
    YELLOW = _colors["YELLOW"]
    BLUE = _colors["BLUE"]
    MAGENTA = _colors["MAGENTA"]
    CYAN = _colors["CYAN"]
    RESET = _colors["RESET"]

    TEXT_HIGHLIGHT = "\033[96m"
    TEXT_HIGHLIGHT_BOLD = "\033[96m\033[1m"
    TEXT_DIM = "\033[90m"
    TEXT_DIM_BOLD = "\033[90m\033[1m"
    TEXT_NORMAL = "\033[0m"
    TEXT_NORMAL_BOLD = "\033[1m"
    TEXT_WARNING = "\033[93m"
    TEXT_WARNING_BOLD = "\033[93m\033[1m"
    TEXT_DANGER = "\033[91m"
    TEXT_DANGER_BOLD = "\033[91m\033[1m"
    TEXT_SUCCESS = "\033[92m"
    TEXT_SUCCESS_BOLD = "\033[92m\033[1m"
    TEXT_INFO = "\033[94m"
    TEXT_INFO_BOLD = "\033[94m\033[1m"


style = Style()

RED = style.RED
GREEN = style.GREEN
YELLOW = style.YELLOW
BLUE = style.BLUE
MAGENTA = style.MAGENTA
CYAN = style.CYAN
RESET = style.RESET
DIM = style.TEXT_DIM


class UI:
    @staticmethod
    def println(*messages):
        print(" ".join(messages))

    @staticmethod
    def print(*messages):
        sys.stdout.write(" ".join(messages))
        sys.stdout.flush()

    @staticmethod
    def error(message):
        if RICH_AVAILABLE:
            console.print(f"[bold red]Error: [/bold red]{message}")
        else:
            print(f"{style.TEXT_DANGER_BOLD}Error: {style.TEXT_NORMAL}{message}")

    @staticmethod
    def warning(message):
        if RICH_AVAILABLE:
            console.print(f"[bold yellow]Warning: [/bold yellow]{message}")
        else:
            print(f"{style.TEXT_WARNING_BOLD}Warning: {style.TEXT_NORMAL}{message}")

    @staticmethod
    def success(message):
        if RICH_AVAILABLE:
            console.print(f"[bold green]OK: [/bold green]{message}")
        else:
            print(f"{style.TEXT_SUCCESS_BOLD}OK: {style.TEXT_NORMAL}{message}")

    @staticmethod
    def info(message):
        if RICH_AVAILABLE:
            console.print(f"[bold blue]Info: [/bold blue]{message}")
        else:
            print(f"{style.TEXT_INFO_BOLD}Info: {style.TEXT_NORMAL}{message}")


try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.style import Style
    from rich.theme import Theme
    import rich

    custom_theme = Theme(
        {
            "info": "dim cyan",
            "warning": "magenta",
            "danger": "bold red",
            "user": "bold green",
            "ai": "bold blue",
            "command": "yellow",
        }
    )
    console = Console(theme=custom_theme)
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a file and write content to it",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path (absolute or relative)",
                    },
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file content",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path to read",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a system command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute"},
                    "workdir": {
                        "type": "string",
                        "description": "Working directory (optional)",
                    },
                },
                "required": ["command"],
            },
        },
    },
]

from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


PROVIDERS = {
    "nvidia": {
        "name": "NVIDIA",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "default_model": "meta/llama-3.1-70b-instruct",
        "api_type": "openai",
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "api_type": "openai",
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "api_type": "openai",
    },
    "kimi": {
        "name": "Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "api_type": "openai",
    },
    "glm": {
        "name": "GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4-flash",
        "api_type": "openai",
    },
    "claude": {
        "name": "Claude",
        "api_type": "anthropic",
    },
    "google": {
        "name": "Google AI",
        "api_type": "google",
    },
}

current_provider = "nvidia"

CONFIG_FILE = "waver_config.json"
ENV_FILE = ".env"


def load_env():
    """从 .env 文件加载环境变量"""
    env_vars = {}
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    return env_vars


def get_api_key_from_env(provider):
    """从环境变量获取 API Key"""
    env_vars = load_env()
    key_name = f"{provider.upper()}_API_KEY"
    return env_vars.get(key_name)


def select_option(options, title="Select", default=0):
    """交互式选择菜单"""
    if RICH_AVAILABLE:
        from rich.console import Console
        from rich.prompt import Prompt

        console = Console()
        prompt = Prompt()

    while True:
        if RICH_AVAILABLE:
            console.clear()
            from rich import print as rprint

            rprint(f"\n[bold cyan]{title}[/bold cyan]\n")

            for i, opt in enumerate(options):
                if i == default:
                    rprint(f"  [green]▶ {opt}[/green]")
                else:
                    rprint(f"    {opt}")

            rprint(f"\n[dim]输入编号 (1-{len(options)}):[/dim]")
            choice = console.input("> ").strip()
        else:
            print(f"\n{title}\n")
            for i, opt in enumerate(options):
                marker = "▶" if i == default else " "
                print(f"  {marker} {i + 1}. {opt}")
            print(f"\n输入编号 (1-{len(options)}):")
            choice = input("> ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        elif choice == "":
            return options[default] if options else None


def load_settings():
    import json

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def persist_settings(settings):
    import json

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def get_saved_api_keys():
    settings = load_settings()
    keys = settings.get("api_keys", {})

    # 合并环境变量中的 API Key（优先级更高）
    env_vars = load_env()
    for provider in PROVIDERS.keys():
        env_key = f"{provider.upper()}_API_KEY"
        if env_key in env_vars and env_vars[env_key]:
            keys[provider] = env_vars[env_key]

    return keys


def save_api_key(provider, api_key):
    settings = load_settings()
    if "api_keys" not in settings:
        settings["api_keys"] = {}
    settings["api_keys"][provider] = api_key
    persist_settings(settings)


def display_reply(reply):
    """显示带语法高亮的回复"""
    if RICH_AVAILABLE:
        from rich.markdown import Markdown
        from rich.panel import Panel
        from rich.syntax import Syntax

        # 检查是否包含代码块
        if "```" in reply:
            console.print(
                Panel.fit(
                    "[dim]Thinking...[/dim]",
                    title="[cyan]WAVER[/cyan]",
                    border_style="blue",
                )
            )
            # 使用 Markdown 渲染
            md = Markdown(reply)
            console.print(md)
        else:
            console.print(
                Panel.fit(
                    reply,
                    title="[cyan]WAVER[/cyan]",
                    border_style="blue",
                )
            )
    else:
        print(f"\n\033[94m>\033[0m {reply}\n")


PROVIDER_URLS = {
    "nvidia": "https://build.nvidia.com/",
    "openai": "https://platform.openai.com/api-keys",
    "claude": "https://console.anthropic.com/",
    "google": "https://aistudio.google.com/app/apikey",
    "deepseek": "https://platform.deepseek.com/",
    "kimi": "https://platform.moonshot.cn/",
    "glm": "https://open.bigmodel.cn/",
}


def ask_for_api_key(provider):
    provider_info = PROVIDERS[provider]
    if RICH_AVAILABLE:
        api_key = console.input(f"{DIM}Key: {RESET}").strip()
    else:
        api_key = input("Key: ").strip()
    return api_key


def ensure_provider_key(provider):
    saved_keys = get_saved_api_keys()
    api_key = saved_keys.get(provider)

    if not api_key:
        api_key = ask_for_api_key(provider)
        if not api_key:
            return None
        save_api_key(provider, api_key)

    return api_key


def execute_tool(tool_call):
    import json
    import subprocess

    function_name = tool_call.function.name
    try:
        arguments = json.loads(tool_call.function.arguments, strict=False)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON: {e}"
    except UnicodeDecodeError as e:
        return f"Error: Encoding error: {e}"

    if function_name == "create_file":
        file_path = arguments.get("file_path")
        content = arguments.get("content")
        if not file_path:
            return "Error: missing file_path"
        try:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File created: {file_path}"
        except Exception as e:
            return f"Error creating file: {e}"

    elif function_name == "read_file":
        file_path = arguments.get("file_path")
        if not file_path:
            return "Error: missing file_path"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if len(content) > 2000:
                content = content[:2000] + "\n... (truncated)"
            return f"Content:\n{content}"
        except FileNotFoundError:
            return f"Error: file not found {file_path}"
        except Exception as e:
            return f"Error reading file: {e}"

    elif function_name == "run_command":
        command = arguments.get("command")
        workdir = arguments.get("workdir")
        if not command:
            return "Error: missing command"
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=workdir,
                timeout=10,
            )
            output = result.stdout + result.stderr
            if len(output) > 2000:
                output = output[:2000] + "\n... (output truncated)"
            return f"Output:\n{output}"
        except subprocess.TimeoutExpired:
            return "Error: command timed out (10s)"
        except Exception as e:
            return f"Error: {e}"

    else:
        return f"Error: unknown tool {function_name}"


def get_available_models(client, provider="nvidia"):
    default_models = {
        "nvidia": [
            "meta/llama-3.1-70b-instruct",
            "meta/llama-3.1-405b-instruct",
            "microsoft/phi-3-medium-128k-instruct",
            "mistralai/mixtral-8x22b-instruct-v0.1",
        ],
        "openai": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        "anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
    }
    try:
        models_response = client.models.list()
        model_list = []
        for m in models_response.data:
            if hasattr(m, "id"):
                model_list.append(m.id)
        model_list = sorted(set(model_list))
        return model_list if model_list else default_models.get(provider, [])
    except Exception:
        return default_models.get(provider, [])


def _show_boot_animation():
    import os
    import sys

    os.system("cls" if os.name == "nt" else "clear")

    ascii_art = """
\033[96m    ██╗    ██╗ █████╗ ██╗   ██╗███████╗██████╗\033[0m
\033[96m    ██║    ██║██╔══██╗██║   ██║██╔════╝██╔══██╗\033[0m
\033[96m    ██║ █╗ ██║███████║██║   ██║█████╗  ██████╔╝\033[0m
\033[96m    ██║███╗██║██╔══██║╚██╗ ██╔╝██╔══╝  ██╔══██╗\033[0m
\033[96m    ╚███╔███╔╝██║  ██║ ╚████╔╝ ███████╗██║  ██║\033[0m
\033[96m     ╚══╝╚══╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝\033[0m
    """

    print(ascii_art)
    print("\033[90m┌─────────────────────────────────────────────┐\033[0m")
    print(
        "\033[90m│\033[0m  \033[1mv1.0.3\033[0m                                    \033[90m│\033[0m"
    )
    print(
        "\033[90m│\033[0m  \033[90mnow or never\033[0m                              \033[90m│\033[0m"
    )
    print("\033[90m└─────────────────────────────────────────────┘\033[0m")
    sys.stdout.flush()


def chat():
    _show_boot_animation()

    settings = load_settings()
    current_provider = settings.get("provider", "nvidia")
    # Default to provider's default model if not set
    default_model = PROVIDERS.get(current_provider, {}).get("default_model", "gpt-4o")
    model = settings.get("model", default_model)

    rules_content = ""
    try:
        with open("rules.txt", "r", encoding="utf-8") as f:
            rules_content = f.read().strip()
    except FileNotFoundError:
        pass

    system_content = (
        "Reply in Chinese. You can use tools to create files, read files, run commands."
    )
    if rules_content:
        system_content += f"\n\nGlobal rules:\n{rules_content}"

    history = [
        {
            "role": "system",
            "content": system_content,
        }
    ]
    stream = False

    saved_keys = get_saved_api_keys()
    if not saved_keys:
        # 首次运行，显示交互式选择菜单
        provider_options = [f"{k} - {v['name']}" for k, v in PROVIDERS.items()]
        selected = select_option(provider_options, "Select Provider")
        if selected:
            current_provider = selected.split(" - ")[0]
        else:
            current_provider = "nvidia"
        settings["provider"] = current_provider
        persist_settings(settings)
    else:
        current_provider = settings.get("provider", list(saved_keys.keys())[0])
        if current_provider not in PROVIDERS:
            current_provider = list(saved_keys.keys())[0]

    api_key = ensure_provider_key(current_provider)
    if not api_key:
        return

    provider_config = PROVIDERS[current_provider]
    api_type = provider_config.get("api_type", "openai")

    if api_type == "anthropic":
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            client_type = "anthropic"
        except ImportError:
            print(f"{RED}Please install anthropic: pip install anthropic{RESET}")
            return
    elif api_type == "google":
        try:
            import google.genai as genai

            client = genai.Client(api_key=api_key)
            client_type = "google"
        except ImportError:
            print(f"{RED}Please install google-genai: pip install google-genai{RESET}")
            return
    else:
        extra_headers = provider_config.get("extra_headers", {})
        if extra_headers:
            client = OpenAI(
                api_key=api_key,
                base_url=provider_config["base_url"],
                default_headers=extra_headers,
            )
        else:
            client = OpenAI(api_key=api_key, base_url=provider_config["base_url"])
        client_type = "openai"

    while True:
        try:
            cwd = os.getcwd()
            prompt = f"\033[90m[{current_provider} {model}]\033[0m > "
            text = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not text:
            continue

        if text.startswith("\\"):
            text = "/" + text[1:]

        if text == "/quit":
            break
        elif text == "/clear":
            history.clear()
            history.append({"role": "system", "content": "Reply in Chinese"})
            print(f"{YELLOW}Cleared{RESET}")
            continue
        elif text == "/model":
            provider_config = PROVIDERS.get(current_provider, {})
            default_model = provider_config.get("default_model", "")
            print(f"{YELLOW}Current: {model}{RESET}")
            print(f"{YELLOW}Default: {default_model}{RESET}")
            c = input(f"{YELLOW}Enter model (or enter for default): {RESET}").strip()
            if c:
                model = c
                settings = load_settings()
                settings["model"] = model
                settings["provider"] = current_provider
                persist_settings(settings)
                print(f"{YELLOW}Set to: {model}{RESET}")
            continue
        elif text == "/provider":
            print(f"{YELLOW}Available:{RESET}")
            saved_keys = get_saved_api_keys()
            for k, v in PROVIDERS.items():
                marker = ">" if k == current_provider else " "
                key_status = "+" if saved_keys.get(k) else "-"
                print(f"  {marker} {k} - {v['name']} [{key_status}]")
            c = input(f"{YELLOW}Choose: {RESET}").strip()
            if c in PROVIDERS:
                current_provider = c
                api_key = ensure_provider_key(c)
                if not api_key:
                    continue
                model = PROVIDERS[c]["default_model"]
                provider_config = PROVIDERS[c]
                api_type = provider_config.get("api_type", "openai")

                if api_type == "anthropic":
                    import anthropic

                    client = anthropic.Anthropic(api_key=api_key)
                elif api_type == "google":
                    import google.genai as genai

                    client = genai.Client(api_key=api_key)
                else:
                    extra_headers = provider_config.get("extra_headers", {})
                    if extra_headers:
                        client = OpenAI(
                            api_key=api_key,
                            base_url=provider_config["base_url"],
                            default_headers=extra_headers,
                        )
                    else:
                        client = OpenAI(
                            api_key=api_key, base_url=provider_config["base_url"]
                        )

                print(
                    f"{YELLOW}Switched to: {PROVIDERS[c]['name']}, model: {model}{RESET}"
                )
                settings = load_settings()
                settings["provider"] = current_provider
                settings["model"] = model
                persist_settings(settings)
            elif c:
                print(f"{RED}Invalid provider{RESET}")
            continue
        elif text == "/history":
            for msg in history:
                if msg["role"] == "user":
                    print(f"{GREEN}user: {msg['content']}{RESET}")
                elif msg["role"] == "assistant":
                    print(f"{BLUE}{msg['content']}{RESET}")
            continue
        elif text == "/save":
            try:
                with open("history.txt", "w", encoding="utf-8") as f:
                    for msg in history:
                        f.write(f"{msg['role']}: {msg['content']}\n")
                print(f"{YELLOW}Saved to history.txt{RESET}")
            except Exception as e:
                print(f"{RED}Save failed: {e}{RESET}")
            continue
        elif text == "/load":
            try:
                with open("history.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                history.clear()
                for line in lines:
                    line = line.strip()
                    if line.startswith("user: "):
                        history.append({"role": "user", "content": line[6:]})
                    elif line.startswith("assistant: "):
                        history.append({"role": "assistant", "content": line[11:]})
                    elif line.startswith("system: "):
                        history.append({"role": "system", "content": line[8:]})
                print(f"{YELLOW}Loaded{RESET}")
            except FileNotFoundError:
                print(f"{RED}File not found{RESET}")
            except Exception as e:
                print(f"{RED}Load failed: {e}{RESET}")
            continue
        elif text == "/stream":
            stream = not stream
            status = "on" if stream else "off"
            print(f"{YELLOW}Stream {status}{RESET}")
            continue
        elif text == "/key":
            print(f"{YELLOW}Current provider: {current_provider}{RESET}")
            new_key = input(f"{YELLOW}New key: {RESET}").strip()
            if new_key:
                save_api_key(current_provider, new_key)
                print(f"{YELLOW}Key updated for {current_provider}{RESET}")
            else:
                print(f"{RED}Key cannot be empty{RESET}")
            continue
        elif text == "/help":
            if RICH_AVAILABLE:
                help_table = Table(
                    title="Commands", show_header=True, header_style="bold magenta"
                )
                help_table.add_column("Command", style="cyan", width=12)
                help_table.add_column("Description", style="green")
                help_table.add_row("/clear", "Clear history")
                help_table.add_row("/model", "Switch model")
                help_table.add_row("/provider", "Switch provider")
                help_table.add_row("/history", "Show history")
                help_table.add_row("/save", "Save history")
                help_table.add_row("/load", "Load history")
                help_table.add_row("/stream", "Toggle stream")
                help_table.add_row("/key", "Update API key")
                help_table.add_row("/help", "Show this help")
                help_table.add_row("/quit", "Exit")
                console.print(help_table)
            else:
                print(f"{YELLOW}Commands:{RESET}")
                print(f"  /clear    Clear history")
                print(f"  /model   Switch model")
                print(f"  /provider Switch provider")
                print(f"  /history Show history")
                print(f"  /save    Save history")
                print(f"  /load    Load history")
                print(f"  /stream  Toggle stream")
                print(f"  /key     Update API key")
                print(f"  /help    Show help")
                print(f"  /quit    Exit")
            continue

        history.append({"role": "user", "content": text})

        try:
            if stream:
                resp = client.chat.completions.create(
                    model=model,
                    messages=history,
                    max_tokens=1024,
                    tools=TOOLS,
                    tool_choice="auto",
                )
                if RICH_AVAILABLE:
                    console.print("\n", end="")
                else:
                    sys.stdout.write(f"\n")
                    sys.stdout.flush()
                reply = ""
                for chunk in resp:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        sys.stdout.write(delta.content)
                        sys.stdout.flush()
                        reply += delta.content
                if RICH_AVAILABLE:
                    console.print()
                else:
                    sys.stdout.write(f"{RESET}\n")
                    sys.stdout.flush()
            else:
                resp = client.chat.completions.create(
                    model=model,
                    messages=history,
                    max_tokens=1024,
                    tools=TOOLS,
                    tool_choice="auto",
                )
                message = resp.choices[0].message

                if message.tool_calls:
                    history.append(message)

                    for tool_call in message.tool_calls:
                        if RICH_AVAILABLE:
                            console.print(
                                f"\n[yellow]Tool: {tool_call.function.name}[/yellow]"
                            )
                        else:
                            print(f"\n{YELLOW}Tool: {tool_call.function.name}{RESET}")

                        tool_result = execute_tool(tool_call)
                        history.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": tool_result,
                            }
                        )

                    resp = client.chat.completions.create(
                        model=model, messages=history, max_tokens=1024
                    )
                    reply = resp.choices[0].message.content
                else:
                    reply = message.content

                # 显示带语法高亮的回复
                display_reply(reply)
            history.append({"role": "assistant", "content": reply})
        except Exception as e:
            err_msg = str(e)
            if "Connection" in err_msg:
                msg = f"{RED}Connection error. Check network/proxy.{RESET}"
            elif "401" in err_msg or "Invalid Authentication" in err_msg:
                msg = f"{RED}Invalid API key. Use /key to update.{RESET}"
            else:
                msg = f"{RED}Error: {e}{RESET}"
            if RICH_AVAILABLE:
                console.print(msg)
            else:
                print(msg)


def main():
    chat()


if __name__ == "__main__":
    main()

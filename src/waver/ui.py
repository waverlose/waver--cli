"""
Waver CLI UI 模块 - 简洁的终端界面
"""

import sys
import time
import os
import io
import logging
from typing import Optional

# Windows CMD 编码支持
if sys.platform == "win32":
    os.system("chcp 65001")
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich import print as rprint
from rich.live import Live
from rich.progress import SpinnerColumn, TextColumn, Progress, BarColumn
from waver import constants

logger = logging.getLogger(__name__)

# 为 Windows 优化 Console
console = Console(
    force_terminal=True,
    force_jupyter=False,
    legacy_windows=True if sys.platform == "win32" else False,
    width=100
)


def show_banner():
    """启动横幅 - 带动画"""
    # Windows CMD 兼容的 ASCII art
    ascii_art = """
[cyan]╔════════════════════════════════════════╗[/cyan]
[cyan]║                                        ║[/cyan]
[cyan]║           [bold]WAVER v2.0.0[/bold]            ║[/cyan]
[cyan]║         now or never                  ║[/cyan]
[cyan]║                                        ║[/cyan]
[cyan]╚════════════════════════════════════════╝[/cyan]"""

    # 逐行显示
    for line in ascii_art.strip().split("\n"):
        console.print(line)
        time.sleep(0.05)

    console.print()
    console.print("[green]✓[/green] Ready to chat")
    console.print("[dim]Type [bold]/help[/bold] for commands[/dim]")
    console.print()


def show_provider_list(providers: dict, current: str = None):
    """显示提供商列表"""
    table = Table(
        title="Available Providers", show_header=True, header_style="bold cyan"
    )
    table.add_column("Provider", style="green")
    table.add_column("Name", style="blue")
    table.add_column("Default Model")

    for key, val in providers.items():
        marker = ">" if key == current else " "
        table.add_row(f"{marker} {key}", val["name"], val.get("default_model", "-"))

    console.print(table)


# Windows CMD 兼容的加载帧
WAVE_FRAMES = ["|", "/", "-", "\\"]


class ThinkingSpinner:
    """思考中的动态显示"""

    def __init__(self, message: str = "Thinking"):
        self.message = message
        self.live = None

    def __enter__(self):
        from rich.panel import Panel

        # 创建带边框的面板
        panel = Panel(
            f"[cyan]{self.message} {WAVE_FRAMES[0]}[/cyan]",
            border_style="cyan",
            title="[bold cyan]WAVER[/bold cyan]",
        )
        self.live = Live(panel, console=console, transient=True, refresh_per_second=10)
        self.live.start()
        self.frame_idx = 0
        return self

    def __exit__(self, *args):
        if self.live:
            self.live.stop()
            self.live = None

    def update(self):
        if self.live:
            from rich.panel import Panel

            self.frame_idx = (self.frame_idx + 1) % len(WAVE_FRAMES)
            panel = Panel(
                f"[cyan]{self.message} {WAVE_FRAMES[self.frame_idx]}[/cyan]",
                border_style="cyan",
                title="[bold cyan]WAVER[/bold cyan]",
            )
            self.live.update(panel)


def show_spinner(message: str = "Thinking"):
    """显示加载动画"""
    return ThinkingSpinner(message)


def show_progress(current: int, total: int, message: str = "Loading"):
    """显示像素进度条"""
    bar_length = 15
    filled = int(bar_length * current // total)
    bar = "█" * filled + "░" * (bar_length - filled)
    percent = current * 100 // total
    console.print(f"\r[cyan]{message} [{bar}] {percent}%[/cyan]", end="", flush=True)


def show_response(response: str):
    """显示回复 - 带框"""
    console.print()
    if "```" in response:
        md = Markdown(response)
        console.print(md)
    else:
        console.print(
            Panel(
                response, 
                border_style="cyan", 
                title="[bold cyan]WAVER[/bold cyan]",
                expand=False
            )
        )
    console.print()


def show_error(message: str):
    """显示错误"""
    logger.error(message)
    console.print(f"[bold red]{constants.UI_MESSAGES['error_prefix']}[/bold red] {message}")


def show_success(message: str):
    """显示成功"""
    logger.info(message)
    console.print(f"[bold green]{constants.UI_MESSAGES['success_prefix']}[/bold green] {message}")


def show_info(message: str):
    """显示信息"""
    logger.info(message)
    console.print(f"[bold blue]{constants.UI_MESSAGES['info_prefix']}[/bold blue] {message}")


def get_input(prompt: str = "> ") -> str:
    """获取用户输入"""
    try:
        return console.input(prompt)
    except EOFError:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        logger.error(f"Input error: {e}")
        show_error(f"Input error: {e}")
        return ""


def show_help():
    """显示帮助"""
    table = Table(title="Commands", show_header=True)
    table.add_column("Command", style="cyan", width=15)
    table.add_column("Description", style="green")

    for cmd, desc in constants.COMMANDS.items():
        table.add_row(cmd, desc)

    console.print(table)


def show_live_progress(total: int, description: str = "Processing"):
    """显示实时进度条"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description, total=total)
        return task, progress


def show_animated_response(response: str, delay: float = 0.02):
    """显示打字机效果的回复"""
    console.print()
    if "```" in response:
        md = Markdown(response)
        console.print(md)
    else:
        # 打字机效果
        panel_content = ""
        for char in response:
            panel_content += char
            console.print(
                Panel.fit(
                    panel_content,
                    border_style="cyan",
                    title="[bold cyan]WAVER[/bold cyan]",
                ),
                end="\r",
            )
            time.sleep(delay)
        console.print()


def show_status_table(status_data: dict):
    """显示状态表格"""
    table = Table(title="Status", show_header=True, header_style="bold cyan")
    table.add_column("Item", style="green")
    table.add_column("Value", style="blue")
    
    for key, value in status_data.items():
        table.add_row(key, str(value))
    
    console.print(table)


def show_loading_animation(message: str = "Loading", duration: int = 3):
    """显示加载动画（可自定义时长）"""
    # Windows CMD 兼容的帧
    frames = ["|", "/", "-", "\\"]
    start_time = time.time()
    frame_idx = 0
    
    while time.time() - start_time < duration:
        console.print(
            f"\r[bold cyan]{frames[frame_idx]} {message}[/bold cyan]", 
            end="", 
            flush=True
        )
        frame_idx = (frame_idx + 1) % len(frames)
        time.sleep(0.1)
    
    console.print("\r" + " " * 50 + "\r", end="")


def show_streaming_response(stream):
    """显示流式回复（实时输出）"""
    console.print()
    full_response = ""
    with console.pager():
        for chunk in stream:
            if isinstance(chunk, str):
                text = chunk
            else:
                text = str(chunk)
            full_response += text
            console.print(text, end="", flush=True)
    console.print()
    return full_response


def show_dialog(title: str, content: str, style: str = "cyan"):
    """显示对话框"""
    console.print()
    console.print(
        Panel(
            content,
            title=f"[bold {style}]{title}[/bold {style}]",
            border_style=style,
            expand=False,
        )
    )
    console.print()

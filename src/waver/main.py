"""Waver CLI - 主程序"""

import sys
import io
import os
import logging

# 设置 UTF-8 编码
if sys.platform == "win32":
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import typer
from typing import Optional, Dict, Any, List
from waver import config, providers, client, executor, ui, constants

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="waver",
    help="Modern AI CLI Tool",
    add_completion=False,
    pretty_exceptions_show_locals=False,
)


class ChatSession:
    """对话会话管理"""

    def __init__(
        self, provider: str, model: str, api_client: Any, stream: bool = False
    ):
        self.current_provider = provider
        self.current_model = model
        self.api_client = api_client
        self.stream = stream
        self.history = [
            {"role": "system", "content": constants.SYSTEM_PROMPTS["default"]}
        ]

    def run_chat_loop(self) -> None:
        """运行主对话循环"""
        ui.show_info(f"Using {self.current_provider} / {self.current_model}")

        while True:
            try:
                user_input = ui.get_input(
                    f"[{self.current_provider}:{self.current_model}] > "
                )
            except (KeyboardInterrupt, EOFError):
                logger.info("Chat session ended by user")
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                if self.handle_command(user_input):
                    continue
                break

            self.process_message(user_input)

    def handle_command(self, user_input: str) -> bool:
        """处理命令，返回True表示继续"""
        cmd = user_input.split()[0]

        if cmd in ["/quit", "/exit", "q"]:
            return False
        elif cmd == "/help":
            ui.show_help()
        elif cmd == "/provider":
            self.switch_provider()
        elif cmd == "/model":
            self.switch_model()
        elif cmd == "/key":
            self.update_api_key()
        elif cmd == "/proxy":
            self.update_proxy()
        elif cmd == "/clear":
            self.clear_history()
        else:
            ui.show_error(constants.ERROR_MESSAGES["unknown_command"].format(cmd=cmd))

        return True

    def switch_provider(self) -> None:
        """切换提供商"""
        ui.show_provider_list(providers.list_providers(), self.current_provider)
        new_provider = input("Select provider: ").strip() or self.current_provider
        if (
            new_provider != self.current_provider
            and new_provider in providers.list_providers()
        ):
            self.current_provider = new_provider
            self.current_model = client.get_model(new_provider)
            api_key = config.get_key(new_provider)
            if not api_key:
                api_key = input(f"Enter API key for {new_provider}: ").strip()
                config.set_key(new_provider, api_key)
            self.api_client = client.create_client(new_provider)
            config.set_default_provider(new_provider)

    def switch_model(self) -> None:
        """切换模型"""
        models = client.list_models(self.current_provider)
        if models:
            ui.show_info(f"Available models for {self.current_provider}:")
            for i, m in enumerate(models[:15], 1):
                marker = ">" if m == self.current_model else " "
                ui.show_info(f"  {marker} {i}. {m}")
            if len(models) > 15:
                ui.show_info(f"  ... and {len(models) - 15} more")

            choice = input("\nSelect: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(models):
                self.current_model = models[int(choice) - 1]
            elif choice and choice in models:
                self.current_model = choice
            elif choice:
                self.current_model = choice

            config.save_provider_config(self.current_provider, self.current_model)
            ui.show_success(f"Model: {self.current_model}")

    def update_api_key(self) -> None:
        """更新API密钥"""
        new_key = input(f"New API key for {self.current_provider}: ").strip()
        if new_key:
            config.set_key(self.current_provider, new_key)
            self.api_client = client.create_client(self.current_provider)
            ui.show_success("API key updated")

    def update_proxy(self) -> None:
        """更新代理"""
        proxy_input = input("Proxy: ").strip()
        if proxy_input:
            config.set_proxy(proxy_input)
            os.environ["http_proxy"] = proxy_input
            os.environ["https_proxy"] = proxy_input
        else:
            config.clear_proxy()
        ui.show_success("Proxy updated")

    def clear_history(self) -> None:
        """清除历史"""
        self.history = [
            {"role": "system", "content": constants.SYSTEM_PROMPTS["default"]}
        ]
        ui.show_success("History cleared")

    def process_message(self, user_input: str) -> None:
        """处理消息"""
        self.history.append({"role": "user", "content": user_input})
        try:
            if self.stream:
                self.handle_streaming_response()
            else:
                self.handle_normal_response()
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ui.show_error(str(e))

    def handle_streaming_response(self) -> None:
        """处理流式响应"""
        response = self.api_client.chat.completions.create(
            model=self.current_model,
            messages=self.history,
            stream=True,
            tools=executor.get_tools() if self.current_provider != "claude" else None,
        )
        console_output = []
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                console_output.append(delta.content)
        print()
        reply = "".join(console_output)
        ui.show_response(reply)
        self.history.append({"role": "assistant", "content": reply})

    def handle_normal_response(self) -> None:
        """处理非流式响应"""
        with ui.show_spinner():
            response = self.api_client.chat.completions.create(
                model=self.current_model,
                messages=self.history,
                max_tokens=constants.MAX_TOKENS,
                tools=executor.get_tools()
                if self.current_provider not in ["claude", "google"]
                else None,
            )
            message = response.choices[0].message

            if message.tool_calls:
                self.history.append(message)
                for tool_call in message.tool_calls:
                    ui.show_info(f"Tool: {tool_call.function.name}")
                    result = executor.execute_tool(tool_call)
                    self.history.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )
                response = self.api_client.chat.completions.create(
                    model=self.current_model,
                    messages=self.history,
                    max_tokens=constants.MAX_TOKENS,
                )
                reply = response.choices[0].message.content
            else:
                reply = message.content

        ui.show_response(reply)
        self.history.append({"role": "assistant", "content": reply})


def initialize_session(provider: Optional[str], model: Optional[str]) -> tuple:
    """初始化会话"""
    if provider and isinstance(provider, str):
        current_provider = provider
    else:
        current_provider = config.get_default_provider()
        if not current_provider:
            ui.show_provider_list(providers.list_providers())
            current_provider = input("Select provider: ").strip()
            if not current_provider:
                ui.show_error("No provider selected")
                raise typer.Exit(1)

        keys = config.get_all_keys()
        if current_provider not in keys or not config.get_key(current_provider):
            api_key = input(f"Enter API key for {current_provider}: ").strip()
            if api_key:
                config.set_key(current_provider, api_key)

    api_key = config.get_key(current_provider)

    if model:
        current_model = model
    else:
        current_model = client.get_model(current_provider)

    proxy = config.get_proxy()
    if proxy:
        os.environ["http_proxy"] = proxy
        os.environ["https_proxy"] = proxy

    try:
        api_client = client.create_client(current_provider)
    except Exception as e:
        ui.show_error(constants.ERROR_MESSAGES["failed_create_client"].format(error=e))
        logger.error(f"Client creation failed: {e}")
        raise typer.Exit(1)

    return current_provider, current_model, api_client


@app.command()
def chat(
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="AI provider"
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name"),
    stream: bool = typer.Option(False, "--stream", "-s", help="Enable streaming"),
):
    """Start interactive chat"""
    ui.show_banner()
    current_provider, current_model, api_client = initialize_session(provider, model)
    session = ChatSession(current_provider, current_model, api_client, stream)
    session.run_chat_loop()


@app.command()
def set_key(
    provider: str = typer.Argument(..., help="Provider name"),
    api_key: str = typer.Option(None, "--key", "-k", help="API key"),
):
    """Set API key"""
    if not api_key:
        api_key = typer.prompt(f"Enter API key for {provider}", hide_input=True)
    config.set_key(provider, api_key)
    ui.show_success(f"API key saved for {provider}")


@app.command()
def list_providers_cmd():
    """List all providers"""
    ui.show_provider_list(providers.list_providers(), config.get_default_provider())


@app.command()
def configure():
    """Configuration wizard"""
    ui.show_banner()
    ui.show_provider_list(providers.list_providers())

    provider = typer.prompt("Select provider", default=config.get_default_provider())
    if provider not in providers.list_providers():
        ui.show_error(f"Unknown provider: {provider}")
        raise typer.Exit(1)

    api_key = config.get_key(provider)
    if not api_key:
        api_key = typer.prompt(f"Enter API key for {provider}", hide_input=True)
        config.set_key(provider, api_key)

    config.set_default_provider(provider)
    ui.show_success(f"Configured: {provider}")


if __name__ == "__main__":
    app()

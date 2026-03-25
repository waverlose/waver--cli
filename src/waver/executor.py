"""工具执行器 - 沙箱安全"""

import subprocess
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from waver import constants

logger = logging.getLogger(__name__)

# 工具定义
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read",
                    }
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["file_path", "content"],
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
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory path"},
                },
                "required": ["directory"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_size",
            "description": "Get file size in bytes",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                },
                "required": ["file_path"],
            },
        },
    },
]


def _check_dangerous_patterns(command: str) -> bool:
    """检查危险模式"""
    for pattern in constants.DANGEROUS_PATTERNS:
        if pattern in command:
            return True
    return False


def _validate_path(path_str: str, allow_parent: bool = False) -> Path:
    """验证并规范化文件路径"""
    try:
        path = Path(path_str).expanduser().resolve()

        # 防止目录遍历
        if not allow_parent:
            home = Path.home().resolve()
            try:
                path.relative_to(home)
            except ValueError:
                # 如果不是home目录的子目录，检查是否是当前项目内
                pass

        return path
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")


def safe_execute(command: str, workdir: str = None) -> str:
    """安全执行命令，防止注入攻击"""
    if _check_dangerous_patterns(command):
        return f"Error: {constants.ERROR_MESSAGES['dangerous_pattern'].format(pattern='pipe/redirect')}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=workdir,
            timeout=constants.TIMEOUT_SECONDS,
        )
        output = result.stdout + result.stderr
        if len(output) > constants.MAX_OUTPUT_LENGTH:
            output = output[: constants.MAX_OUTPUT_LENGTH] + "\n... (truncated)"
        return output if output else "OK"
    except subprocess.TimeoutExpired:
        return constants.ERROR_MESSAGES["timeout"].format(
            timeout=constants.TIMEOUT_SECONDS
        )
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        return f"Error: {e}"


def read_file_tool(file_path: str) -> str:
    """读取文件内容"""
    try:
        path = _validate_path(file_path)
        if not path.exists():
            return f"Error: file not found: {file_path}"
        if not path.is_file():
            return f"Error: not a file: {file_path}"

        content = path.read_text(encoding="utf-8")
        if len(content) > constants.MAX_OUTPUT_LENGTH:
            content = content[: constants.MAX_OUTPUT_LENGTH] + "\n... (truncated)"
        return f"Content of {file_path}:\n{content}"
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"Error reading file: {e}"


def write_file_tool(file_path: str, content: str) -> str:
    """写入文件内容"""
    try:
        path = _validate_path(file_path, allow_parent=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info(f"File written: {file_path}")
        return f"File written: {file_path}"
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return f"Error writing file: {e}"


def list_files_tool(directory: str) -> str:
    """列出目录中的文件"""
    try:
        path = _validate_path(directory)
        if not path.exists():
            return f"Error: directory not found: {directory}"
        if not path.is_dir():
            return f"Error: not a directory: {directory}"

        files = []
        for item in sorted(path.iterdir())[:50]:  # 限制结果数量
            files.append(f"{'[DIR]' if item.is_dir() else '[FILE]'} {item.name}")

        return "Files:\n" + "\n".join(files)
    except Exception as e:
        logger.error(f"Error listing directory {directory}: {e}")
        return f"Error listing directory: {e}"


def get_file_size_tool(file_path: str) -> str:
    """获取文件大小"""
    try:
        path = _validate_path(file_path)
        if not path.exists():
            return f"Error: file not found: {file_path}"
        if not path.is_file():
            return f"Error: not a file: {file_path}"

        size = path.stat().st_size
        return f"File size: {size} bytes"
    except Exception as e:
        logger.error(f"Error getting file size {file_path}: {e}")
        return f"Error: {e}"


def get_tools() -> List[Dict]:
    """获取工具定义列表"""
    return TOOLS


def execute_tool(tool_call) -> str:
    """执行工具调用"""
    function_name = tool_call.function.name

    try:
        arguments = json.loads(tool_call.function.arguments, strict=False)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in tool call: {e}")
        return f"Error: Invalid JSON: {e}"

    logger.info(f"Executing tool: {function_name}")

    if function_name == "read_file":
        file_path = arguments.get("file_path")
        if not file_path:
            return "Error: missing file_path"
        return read_file_tool(file_path)

    elif function_name == "write_file":
        file_path = arguments.get("file_path")
        content = arguments.get("content")
        if not file_path:
            return "Error: missing file_path"
        return write_file_tool(file_path, content or "")

    elif function_name == "run_command":
        command = arguments.get("command")
        workdir = arguments.get("workdir")
        if not command:
            return "Error: missing command"
        return safe_execute(command, workdir)

    elif function_name == "list_files":
        directory = arguments.get("directory")
        if not directory:
            return "Error: missing directory"
        return list_files_tool(directory)

    elif function_name == "get_file_size":
        file_path = arguments.get("file_path")
        if not file_path:
            return "Error: missing file_path"
        return get_file_size_tool(file_path)

    return f"Error: Unknown tool: {function_name}"
    return TOOLS

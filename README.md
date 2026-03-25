# Waver CLI

just fun

AI CLI tool with multi-provider support.

## Install

```bash
pip install waver-cli
```

Or from source:

```bash
pip install -e .
```

## Usage

```bash
waver
```

## Features

- Multi-provider support: NVIDIA, OpenAI, DeepSeek, Kimi, GLM, Claude, Google AI
- Tool calling: create files, read files, run commands
- Config persistence
- Stream mode support

## Commands

- `/help` - Show help
- `/provider` - Switch AI provider
- `/model` - Switch model
- `/key` - Update API key
- `/stream` - Toggle streaming
- `/clear` - Clear history
- `/save` - Save history
- `/load` - Load history
- `/quit` - Exit

## Config

Config is saved to `waver_config.json` in current directory.

## License

MIT

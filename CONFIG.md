# Configuration Reference

Complete reference for nanobot configuration options.

## Configuration File

**Location:** `~/.nanobot/config.json`

**Format:** JSON

## Schema

### Root Structure

```json
{
  "agents": { ... },
  "channels": { ... },
  "providers": { ... },
  "gateway": { ... },
  "tools": { ... }
}
```

---

## Agents Configuration

Controls agent behavior and defaults.

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.nanobot/workspace",
      "model": "anthropic/claude-opus-4-5",
      "maxTokens": 8192,
      "temperature": 0.7,
      "maxToolIterations": 20
    }
  }
}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `workspace` | string | `~/.nanobot/workspace` | Directory for agent files and memory |
| `model` | string | `anthropic/claude-opus-4-5` | Default LLM model to use |
| `maxTokens` | integer | 8192 | Maximum tokens in LLM response |
| `temperature` | float | 0.7 | Sampling temperature (0.0-2.0) |
| `maxToolIterations` | integer | 20 | Maximum tool calls per conversation turn |

### Model Names

Model names follow the format `provider/model-name`:

- **OpenRouter:** `anthropic/claude-opus-4-5`, `openai/gpt-4`
- **Direct:** `gemini/gemini-2.0-flash-exp`, `deepseek/deepseek-chat`
- **Local (vLLM):** `meta-llama/Llama-3.1-8B-Instruct`

---

## Providers Configuration

LLM provider API keys and endpoints.

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-...",
      "apiBase": null
    },
    "anthropic": {
      "apiKey": "",
      "apiBase": null
    },
    "openai": {
      "apiKey": "",
      "apiBase": null
    },
    "deepseek": {
      "apiKey": "",
      "apiBase": null
    },
    "groq": {
      "apiKey": "",
      "apiBase": null
    },
    "gemini": {
      "apiKey": "",
      "apiBase": null
    },
    "zhipu": {
      "apiKey": "",
      "apiBase": null
    },
    "vllm": {
      "apiKey": "dummy",
      "apiBase": "http://localhost:8000/v1"
    }
  }
}
```

### Provider Options

| Provider | Get API Key | Notes |
|----------|-------------|-------|
| `openrouter` | [openrouter.ai](https://openrouter.ai) | Recommended: Access all models through one API |
| `anthropic` | [console.anthropic.com](https://console.anthropic.com) | Direct Claude access |
| `openai` | [platform.openai.com](https://platform.openai.com) | Direct GPT access |
| `deepseek` | [platform.deepseek.com](https://platform.deepseek.com) | Chinese LLM provider |
| `groq` | [console.groq.com](https://console.groq.com) | Fast inference + Whisper transcription |
| `gemini` | [aistudio.google.com](https://aistudio.google.com) | Google's Gemini models |
| `zhipu` | [open.bigmodel.cn](https://open.bigmodel.cn) | GLM models (Chinese) |
| `vllm` | N/A | Local models via vLLM server |

### Fields

- **`apiKey`** (string): Provider API key
- **`apiBase`** (string, optional): Custom API endpoint (for vLLM, proxies, etc.)

---

## Channels Configuration

Chat channel integrations (Telegram, WhatsApp, Feishu).

### Telegram

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "123456:ABC-DEF...",
      "allowFrom": ["123456789"],
      "proxy": null
    }
  }
}
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `enabled` | boolean | Yes | Enable Telegram channel |
| `token` | string | Yes | Bot token from [@BotFather](https://t.me/BotFather) |
| `allowFrom` | string[] | Recommended | User IDs allowed to use bot (get from [@userinfobot](https://t.me/userinfobot)) |
| `proxy` | string | No | HTTP/SOCKS5 proxy URL (e.g., `http://127.0.0.1:7890`) |

### WhatsApp

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "bridgeUrl": "ws://localhost:3001",
      "allowFrom": ["+1234567890"]
    }
  }
}
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `enabled` | boolean | Yes | Enable WhatsApp channel |
| `bridgeUrl` | string | Yes | WebSocket URL of WhatsApp bridge server |
| `allowFrom` | string[] | Recommended | Phone numbers allowed to message (E.164 format) |

**Note:** Requires Node.js ≥18 and running `nanobot channels login` first.

### Feishu (飞书/Lark)

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_...",
      "appSecret": "...",
      "encryptKey": "",
      "verificationToken": "",
      "allowFrom": []
    }
  }
}
```

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `enabled` | boolean | Yes | Enable Feishu channel |
| `appId` | string | Yes | App ID from [Feishu Open Platform](https://open.feishu.cn) |
| `appSecret` | string | Yes | App Secret from Feishu Open Platform |
| `encryptKey` | string | No | Event encryption key (optional for WebSocket mode) |
| `verificationToken` | string | No | Event verification token (optional for WebSocket mode) |
| `allowFrom` | string[] | Recommended | User open_ids allowed to message (empty = allow all) |

**Note:** Uses WebSocket long connection—no public IP required.

---

## Gateway Configuration

Server settings for the gateway.

```json
{
  "gateway": {
    "host": "0.0.0.0",
    "port": 18790
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | `0.0.0.0` | Host to bind (use `127.0.0.1` to restrict to localhost) |
| `port` | integer | 18790 | Port number |

---

## Tools Configuration

Configuration for built-in tools.

### Web Tools

```json
{
  "tools": {
    "web": {
      "search": {
        "apiKey": "BSA...",
        "maxResults": 5
      }
    }
  }
}
```

#### Web Search

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | "" | [Brave Search API](https://brave.com/search/api/) key |
| `maxResults` | integer | 5 | Default number of search results (1-10) |

### Shell Execution

```json
{
  "tools": {
    "exec": {
      "timeout": 60,
      "restrictToWorkspace": true
    }
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | integer | 60 | Command timeout in seconds |
| `restrictToWorkspace` | boolean | **true** | Block commands accessing paths outside workspace |

**Security:** Always keep `restrictToWorkspace: true` unless you have a specific reason. See [SECURITY.md](SECURITY.md) for details.

---

## Environment Variables

nanobot configuration can be partially overridden using environment variables:

```bash
export NANOBOT_AGENTS__DEFAULTS__MODEL="anthropic/claude-sonnet-4"
export NANOBOT_PROVIDERS__OPENROUTER__API_KEY="sk-or-v1-..."
export NANOBOT_GATEWAY__PORT=8080
```

**Format:** `NANOBOT_<SECTION>__<SUBSECTION>__<KEY>=<value>`

- Prefix: `NANOBOT_`
- Delimiter: `__` (double underscore)
- Case: UPPERCASE

---

## Minimal Configuration

The smallest working config:

```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-..."
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5"
    }
  }
}
```

All other options use sensible defaults.

---

## Full Example

See [`README.md`](README.md#configuration) for a complete configuration example.

---

## Validation

nanobot validates configuration at startup. Common issues:

- **Missing API key:** Set at least one provider's `apiKey`
- **Invalid model name:** Ensure model format matches provider
- **Port already in use:** Change `gateway.port` or stop conflicting service
- **Invalid JSON:** Use a JSON validator to check syntax

Run `nanobot status` to check configuration status.

---

## Configuration Changes

Changes to `~/.nanobot/config.json` require restarting the gateway:

```bash
# Stop gateway (Ctrl+C)
# Edit config
vim ~/.nanobot/config.json

# Restart
nanobot gateway
```

For `nanobot agent` commands, configuration is loaded fresh each time.

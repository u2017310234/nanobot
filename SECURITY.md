# Security Guidelines

## Overview

This document outlines security best practices and considerations when using nanobot.

## API Key Management

### Secure Storage

- **Never commit API keys** to version control
- Store API keys in `~/.nanobot/config.json` (outside the project directory)
- Ensure config file has restricted permissions: `chmod 600 ~/.nanobot/config.json`

### Environment Variables

The nanobot provider system temporarily sets environment variables during LLM API calls and cleans them up afterwards to minimize exposure. However, for additional security:

- Don't run untrusted code in the same process
- Avoid logging at DEBUG level in production
- Use separate API keys for development and production

## Shell Command Execution

### Workspace Restriction

The shell execution tool (`exec`) has a `restrict_to_workspace` option:

```json
{
  "tools": {
    "exec": {
      "restrict_to_workspace": true,  // Recommended: prevents access outside workspace
      "timeout": 60
    }
  }
}
```

**Default:** `true` (since version 0.1.4)

### Command Safety Guards

The shell tool includes built-in safety guards that block:
- Destructive commands (`rm -rf`, `format`, `mkfs`)
- System operations (`shutdown`, `reboot`)
- Fork bombs
- Direct disk writes

However, these guards are **best-effort** and not foolproof. For production:

1. **Use allowlist mode**: Define `allow_patterns` to restrict to specific command patterns
2. **Run in container**: Use Docker to isolate the workspace
3. **Principle of least privilege**: Don't run nanobot as root

### Example: Restricted Configuration

```json
{
  "tools": {
    "exec": {
      "restrict_to_workspace": true,
      "allow_patterns": [
        "^(ls|cat|echo|grep|find|pwd)",  // Read-only commands
        "^(python|node|npm|pip).*"        // Development tools
      ],
      "timeout": 30
    }
  }
}
```

## Web Tools Security

### SSRF Protection

The web fetch tool (`web_fetch`) includes protections against Server-Side Request Forgery (SSRF):

- Blocks access to private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Blocks localhost access (127.0.0.1, ::1)
- Validates URL schemes (only http/https allowed)

### Rate Limiting

Currently, nanobot **does not enforce rate limiting** on tool calls. Consider:

- Setting low `max_tool_iterations` in config
- Monitoring API usage
- Using provider rate limits (OpenRouter, etc.)

## Chat Channels Security

### Telegram

- **Always** set `allowFrom` to restrict bot access:
  ```json
  {
    "channels": {
      "telegram": {
        "enabled": true,
        "token": "YOUR_BOT_TOKEN",
        "allowFrom": ["123456789"]  // Your Telegram user ID
      }
    }
  }
  ```
- Get your user ID from `@userinfobot` on Telegram
- Keep your bot token secret

### WhatsApp

- The WhatsApp bridge runs locally and requires Node.js
- QR code authentication is session-based
- Set `allowFrom` to restrict which phone numbers can interact

### Feishu

- Uses WebSocket long connection (no public endpoint needed)
- Set `allowFrom` to restrict user open_ids
- Keep `appSecret` confidential

## Docker Security

When running in Docker:

```bash
# 1. Don't bind to 0.0.0.0 if not needed
# Instead of: -p 18790:18790
# Use: -p 127.0.0.1:18790:18790

# 2. Use read-only workspace if possible
docker run -v ~/.nanobot:/root/.nanobot:ro nanobot agent -m "..."

# 3. Run with limited capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nanobot gateway
```

## Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do not** open a public issue
2. Email the maintainers (see COMMUNICATION.md)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond within 48 hours and will credit reporters (unless they prefer to remain anonymous).

## Security Checklist

- [ ] API keys stored in `~/.nanobot/config.json` with restricted permissions
- [ ] `restrict_to_workspace: true` enabled in shell tool config
- [ ] Chat channels restricted with `allowFrom` lists
- [ ] Running in Docker container (optional but recommended)
- [ ] Not running as root user
- [ ] Regular updates to dependencies (`pip install --upgrade nanobot-ai`)
- [ ] Monitoring logs for suspicious activity

## Version Security

| Version | Security Status | Notes |
|---------|----------------|-------|
| 0.1.4+  | ✅ Recommended | SSRF protection, secure env var handling |
| 0.1.3   | ⚠️ Upgrade      | Missing SSRF protection |
| < 0.1.3 | ❌ Not supported | Multiple security issues |

Always use the latest version for best security.

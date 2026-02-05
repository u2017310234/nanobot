"""Security tests for nanobot tools."""

import pytest

from nanobot.agent.tools.shell import ExecTool
from nanobot.agent.tools.web import _validate_url, _is_private_ip


class TestShellToolSecurity:
    """Test shell execution tool security features."""
    
    def test_deny_patterns_block_dangerous_commands(self):
        """Test that dangerous commands are blocked by deny patterns."""
        tool = ExecTool(restrict_to_workspace=False)
        
        # Test various dangerous commands
        dangerous_commands = [
            "rm -rf /",
            "rm -fr /home",
            "format c:",
            "del /f important.txt",
            "shutdown -h now",
            "reboot",
            "dd if=/dev/zero of=/dev/sda",
            ":(){ :|:& };:",  # fork bomb
        ]
        
        for cmd in dangerous_commands:
            result = tool._guard_command(cmd, "/home/user")
            assert result is not None, f"Command should be blocked: {cmd}"
            assert "blocked by safety guard" in result.lower()
    
    def test_workspace_restriction_blocks_path_traversal(self):
        """Test that workspace restriction blocks path traversal."""
        tool = ExecTool(restrict_to_workspace=True)
        
        # Test path traversal attempts
        traversal_commands = [
            "cat ../../../etc/passwd",
            "ls ..\\..",
            "rm -f /etc/hosts",
        ]
        
        for cmd in traversal_commands:
            result = tool._guard_command(cmd, "/home/user/workspace")
            assert result is not None, f"Command should be blocked: {cmd}"
            assert "blocked by safety guard" in result.lower()
    
    def test_safe_commands_pass_guard(self):
        """Test that safe commands are allowed."""
        tool = ExecTool(restrict_to_workspace=False)
        
        safe_commands = [
            "ls -la",
            "echo 'hello world'",
            "python script.py",
            "git status",
        ]
        
        for cmd in safe_commands:
            result = tool._guard_command(cmd, "/home/user/workspace")
            assert result is None, f"Safe command should pass: {cmd}"
    
    def test_allowlist_mode_blocks_unlisted_commands(self):
        """Test that allowlist mode only allows whitelisted patterns."""
        tool = ExecTool(
            allow_patterns=[r"^(ls|echo|cat)\b"],
            restrict_to_workspace=False
        )
        
        # Allowed commands
        assert tool._guard_command("ls -la", "/tmp") is None
        assert tool._guard_command("echo test", "/tmp") is None
        assert tool._guard_command("cat file.txt", "/tmp") is None
        
        # Blocked commands
        assert tool._guard_command("python script.py", "/tmp") is not None
        assert tool._guard_command("rm file.txt", "/tmp") is not None


class TestWebToolSecurity:
    """Test web tool security features."""
    
    def test_ssrf_protection_blocks_private_ips(self):
        """Test that SSRF protection blocks private IP addresses."""
        # Private IPv4 ranges
        assert not _validate_url("http://127.0.0.1/admin")[0]
        assert not _validate_url("http://localhost/admin")[0]
        assert not _validate_url("http://10.0.0.1/internal")[0]
        assert not _validate_url("http://192.168.1.1/router")[0]
        assert not _validate_url("http://172.16.0.1/api")[0]
        
        # IPv6 loopback
        assert not _validate_url("http://[::1]/admin")[0]
    
    def test_ssrf_protection_allows_public_ips(self):
        """Test that public IPs are allowed."""
        valid, _ = _validate_url("http://8.8.8.8/")
        assert valid
        
        valid, _ = _validate_url("https://1.1.1.1/dns-query")
        assert valid
    
    def test_ssrf_protection_allows_public_domains(self):
        """Test that public domains are allowed."""
        valid, _ = _validate_url("https://example.com/page")
        assert valid
        
        valid, _ = _validate_url("https://api.github.com/users")
        assert valid
    
    def test_url_validation_blocks_invalid_schemes(self):
        """Test that non-http(s) schemes are blocked."""
        assert not _validate_url("file:///etc/passwd")[0]
        assert not _validate_url("ftp://ftp.example.com")[0]
        assert not _validate_url("javascript:alert(1)")[0]
        assert not _validate_url("data:text/html,<script>alert(1)</script>")[0]
    
    def test_url_validation_requires_netloc(self):
        """Test that URLs without domain are rejected."""
        assert not _validate_url("http://")[0]
        assert not _validate_url("https://")[0]
    
    def test_is_private_ip_detection(self):
        """Test private IP address detection."""
        # Private IPs
        assert _is_private_ip("127.0.0.1")
        assert _is_private_ip("localhost")
        assert _is_private_ip("10.0.0.1")
        assert _is_private_ip("192.168.1.1")
        assert _is_private_ip("172.16.0.1")
        assert _is_private_ip("::1")
        
        # Public IPs
        assert not _is_private_ip("8.8.8.8")
        assert not _is_private_ip("1.1.1.1")
        assert not _is_private_ip("example.com")


class TestConfigurationSecurity:
    """Test configuration security features."""
    
    def test_default_workspace_restriction_is_secure(self):
        """Test that default configuration has workspace restriction enabled."""
        from nanobot.config.schema import ExecToolConfig
        
        config = ExecToolConfig()
        assert config.restrict_to_workspace is True, \
            "Default should be secure (restrict_to_workspace=True)"
    
    def test_default_gateway_host_allows_external_access(self):
        """Test that default gateway configuration is documented."""
        from nanobot.config.schema import GatewayConfig
        
        config = GatewayConfig()
        # Note: This is 0.0.0.0 by default for ease of use
        # Users should change to 127.0.0.1 for local-only access
        assert config.host == "0.0.0.0"


@pytest.mark.asyncio
async def test_shell_tool_timeout():
    """Test that shell tool respects timeout."""
    tool = ExecTool(timeout=2)
    
    # This command should timeout
    result = await tool.execute("sleep 10")
    assert "timed out" in result.lower()


@pytest.mark.asyncio
async def test_shell_tool_output_truncation():
    """Test that shell tool truncates long output."""
    from nanobot.agent.tools.shell import MAX_OUTPUT_LENGTH
    
    tool = ExecTool()
    
    # Generate output longer than MAX_OUTPUT_LENGTH
    cmd = f"python -c \"print('x' * {MAX_OUTPUT_LENGTH + 1000})\""
    result = await tool.execute(cmd)
    
    assert "truncated" in result.lower()
    assert len(result) <= MAX_OUTPUT_LENGTH + 200  # Allow some overhead for truncation message

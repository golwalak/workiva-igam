# Configuration Files

This directory contains configuration templates and examples for the Workiva IGAM development workspace.

## MCP (Model Context Protocol) Configuration

### mcp-config.template.json
Basic MCP server configuration template for GitHub integration.

**Usage:**
1. Copy to your MCP client's configuration directory
2. Replace `your_github_token_here` with your actual GitHub personal access token
3. Configure your MCP client to use this server configuration

### mcp-config-enhanced.template.json
Enhanced MCP configuration with multiple servers:
- **filesystem**: File system access for workspace
- **brave_search**: Web search capabilities
- **github**: GitHub integration

**Setup:**
1. Copy template and rename (remove `.template` extension)
2. Update the filesystem path to your actual workspace path
3. Add your API keys:
   - `GITHUB_PERSONAL_ACCESS_TOKEN`: GitHub personal access token
   - `BRAVE_API_KEY`: Brave Search API key (optional)
4. Configure your MCP client to use this configuration

## Security Notes

- **Never commit files with actual API keys or tokens**
- Use environment variables for sensitive configuration in production
- Ensure proper file permissions on configuration files
- Regularly rotate API keys and tokens
- Review and validate all configuration before deployment

## MCP Client Setup

These configuration files are compatible with:
- **Claude Desktop**: Place in Claude's MCP configuration directory
- **VS Code with MCP Extension**: Use in VS Code MCP settings
- **Custom MCP Clients**: Adapt format as needed for your client

For detailed MCP setup instructions, see the main README.md file.

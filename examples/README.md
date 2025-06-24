# GitHub MCP Server Usage Examples

This directory contains examples of how to use the GitHub MCP Server with various clients.

## Claude Desktop Configuration

### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["C:\\absolute\\path\\to\\github-mcp-server\\build\\index.js"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

### macOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["/absolute/path/to/github-mcp-server/build/index.js"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

## Example Queries

Here are some example queries you can use with Claude Desktop once the GitHub MCP server is configured:

### Repository Management
- "List the repositories for the microsoft organization"
- "Get information about the microsoft/vscode repository"
- "Search for popular JavaScript repositories related to React"

### Issue Management
- "Show me all open issues in microsoft/typescript"
- "Create an issue titled 'Feature request: Add dark mode' in my repository"
- "Update issue #123 in myuser/myrepo to add the 'enhancement' label"

### Pull Request Management
- "List all open pull requests in facebook/react"
- "Create a pull request from feature-branch to main in myuser/myrepo"

### File Operations
- "Show me the README.md file from microsoft/vscode"
- "Get the contents of src/index.ts from my repository"

### Search Operations
- "Find issues related to 'typescript' across GitHub"
- "Search for repositories that use Python and have 'machine learning' in the name"

### User Information
- "Get information about the GitHub user 'torvalds'"
- "Show me details about the user 'gaearon'"

## Environment Setup

### Setting up GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select the appropriate scopes:
   - `repo` - Full control of private repositories
   - `public_repo` - Access to public repositories only
   - `read:user` - Read user profile information
   - `read:org` - Read organization information
4. Copy the generated token

### Environment Variables

**Windows Command Prompt:**
```cmd
set GITHUB_TOKEN=your_github_token_here
```

**Windows PowerShell:**
```powershell
$env:GITHUB_TOKEN="your_github_token_here"
```

**macOS/Linux:**
```bash
export GITHUB_TOKEN=your_github_token_here
```

## Testing the Server

You can test the server by running it directly:

```bash
# Set your GitHub token
export GITHUB_TOKEN=your_token_here

# Start the server
npm run start
```

The server will wait for MCP protocol messages on stdin/stdout.

## Common Issues

### Authentication Errors
- Ensure your GITHUB_TOKEN is set correctly
- Verify the token has the necessary scopes
- Check that the token hasn't expired

### Rate Limiting
- GitHub API has rate limits (5000 requests/hour for authenticated users)
- The server handles rate limiting gracefully
- Consider using a GitHub App for higher rate limits in production

### Network Issues
- Ensure you can access https://api.github.com
- Check firewall and proxy settings
- Verify SSL/TLS connectivity

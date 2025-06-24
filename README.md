# Workiva IGAM Development Workspace

This workspace contains both a **GitHub MCP Server** for GitHub integration and **Python scripts** for Workiva Identity, Governance, and Access Management (IGAM) reporting.

## Projects

### 1. GitHub MCP Server (TypeScript)
A Model Context Protocol (MCP) server that provides comprehensive GitHub integration capabilities. This server allows AI assistants and other MCP clients to interact with GitHub repositories, issues, pull requests, and more through a standardized interface.

### 2. Workiva IGAM Python Scripts
Python scripts for retrieving, processing, and reporting on Workiva user account data for compliance and analysis purposes.

---

## GitHub MCP Server

A Model Context Protocol (MCP) server that provides comprehensive GitHub integration capabilities. This server allows AI assistants and other MCP clients to interact with GitHub repositories, issues, pull requests, and more through a standardized interface.

## Features

### Repository Management
- **list-repositories**: List repositories for a user or organization
- **get-repository**: Get detailed information about a specific repository
- **search-repositories**: Search for repositories across GitHub

### Issue Management
- **list-issues**: List issues for a repository with filtering options
- **create-issue**: Create new issues with labels and assignees
- **update-issue**: Update existing issues (title, body, state, labels, assignees)
- **search-issues**: Search for issues and pull requests across GitHub

### Pull Request Management
- **list-pull-requests**: List pull requests for a repository
- **create-pull-request**: Create new pull requests with draft support

### File Operations
- **get-file-contents**: Retrieve file contents or directory listings from repositories

### User Information
- **get-user**: Get detailed information about GitHub users

## Prerequisites

- Node.js 16 or higher
- TypeScript
- A GitHub personal access token

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd github-mcp-server
```

2. Install dependencies:
```bash
npm install
```

3. Build the project:
```bash
npm run build
```

## Configuration

### GitHub Token

You need a GitHub personal access token to use this server. Create one at:
https://github.com/settings/tokens

The token needs the following scopes depending on your use case:
- `repo` - Full control of private repositories
- `public_repo` - Access to public repositories
- `read:user` - Read user profile information
- `read:org` - Read organization information

### Environment Variables

Set the `GITHUB_TOKEN` environment variable:

**Windows:**
```cmd
set GITHUB_TOKEN=your_github_token_here
```

**PowerShell:**
```powershell
$env:GITHUB_TOKEN="your_github_token_here"
```

**macOS/Linux:**
```bash
export GITHUB_TOKEN=your_github_token_here
```

## Usage

### Running the Server

```bash
npm run start
```

Or for development with auto-rebuild:
```bash
npm run dev
```

### Using with Claude Desktop

1. Update your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

2. Add the server configuration:
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

3. Restart Claude Desktop

### Using with VS Code

The project includes a `.vscode/mcp.json` configuration file. Update the `GITHUB_TOKEN` value and use the MCP extension for VS Code.

## Tool Reference

### Repository Tools

#### list-repositories
List repositories for a user or organization.

**Parameters:**
- `owner` (string): Username or organization name
- `type` (optional): Repository type filter ("all", "owner", "member")
- `sort` (optional): Sort by ("created", "updated", "pushed", "full_name")
- `per_page` (optional): Number of results per page (max 100)

#### get-repository
Get detailed information about a specific repository.

**Parameters:**
- `owner` (string): Repository owner
- `repo` (string): Repository name

#### search-repositories
Search for repositories on GitHub.

**Parameters:**
- `query` (string): Search query
- `sort` (optional): Sort field ("stars", "forks", "help-wanted-issues", "updated")
- `order` (optional): Sort order ("asc", "desc")
- `per_page` (optional): Number of results per page (max 100)

### Issue Tools

#### list-issues
List issues for a repository.

**Parameters:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `state` (optional): Issue state ("open", "closed", "all")
- `labels` (optional): Comma-separated list of labels
- `assignee` (optional): Username of assignee
- `per_page` (optional): Number of results per page (max 100)

#### create-issue
Create a new issue in a repository.

**Parameters:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `title` (string): Issue title
- `body` (optional): Issue body/description
- `labels` (optional): Array of label names
- `assignees` (optional): Array of usernames to assign

#### update-issue
Update an existing issue.

**Parameters:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `issue_number` (number): Issue number
- `title` (optional): New issue title
- `body` (optional): New issue body
- `state` (optional): New issue state ("open", "closed")
- `labels` (optional): Array of label names
- `assignees` (optional): Array of usernames to assign

### Pull Request Tools

#### list-pull-requests
List pull requests for a repository.

**Parameters:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `state` (optional): Pull request state ("open", "closed", "all")
- `head` (optional): Filter by head branch
- `base` (optional): Filter by base branch
- `per_page` (optional): Number of results per page (max 100)

#### create-pull-request
Create a new pull request.

**Parameters:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `title` (string): Pull request title
- `head` (string): Head branch name
- `base` (string): Base branch name
- `body` (optional): Pull request body/description
- `draft` (optional): Create as draft pull request

### File Tools

#### get-file-contents
Get the contents of a file from a repository.

**Parameters:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `path` (string): File path in the repository
- `ref` (optional): Branch, tag, or commit SHA

### Search Tools

#### search-issues
Search for issues and pull requests on GitHub.

**Parameters:**
- `query` (string): Search query
- `sort` (optional): Sort field
- `order` (optional): Sort order ("asc", "desc")
- `per_page` (optional): Number of results per page (max 100)

### User Tools

#### get-user
Get information about a GitHub user.

**Parameters:**
- `username` (string): GitHub username

## Example Usage

Here are some example queries you can use with the GitHub MCP server:

1. **List repositories**: "Show me the repositories for the microsoft organization"
2. **Create an issue**: "Create an issue in myrepo titled 'Bug fix needed' with the label 'bug'"
3. **Search repositories**: "Find popular Python repositories related to machine learning"
4. **Get file contents**: "Show me the README.md file from the main branch of microsoft/vscode"
5. **List issues**: "Show me all open issues in microsoft/typescript assigned to someone"

## Error Handling

The server implements comprehensive error handling:
- GitHub API errors are caught and returned with descriptive messages
- Rate limiting is handled gracefully
- Authentication errors provide clear guidance
- Validation errors for required parameters

## Security Considerations

- Never expose your GitHub token in logs or commit it to version control
- Use environment variables for token storage
- The server validates all inputs before making API calls
- Follow the principle of least privilege when setting token scopes

## Development

### Project Structure
```
src/
  index.ts          # Main MCP server implementation
.github/
  copilot-instructions.md  # Development guidelines
.vscode/
  mcp.json         # VS Code MCP configuration
build/             # Compiled JavaScript output
package.json       # Project configuration
tsconfig.json      # TypeScript configuration
```

### Contributing

1. Follow the coding guidelines in `.github/copilot-instructions.md`
2. Use TypeScript for all code
3. Implement proper error handling for new tools
4. Add comprehensive documentation for new features
5. Test with various GitHub repositories and scenarios

### Testing

Test the server by running it and using various tools:

```bash
# Set your GitHub token
export GITHUB_TOKEN=your_token_here

# Start the server
npm run start

# The server will listen on stdio for MCP protocol messages
```

## License

ISC License

---

## Workiva IGAM Python Scripts

The `python/` directory contains Python scripts for Workiva Identity, Governance, and Access Management (IGAM) reporting.

### Key Features
- **OAuth 2.0 Authentication**: Secure API access using client credentials flow
- **User Data Processing**: Retrieve and filter Workiva user account information
- **CSV Report Generation**: Standardized reports for compliance and analysis
- **Email Notifications**: Automated report delivery with attachments
- **Data Visualization**: Role distribution charts and analytics
- **Comprehensive Logging**: Detailed execution logs for troubleshooting

### Quick Start

1. **Navigate to the Python directory:**
   ```bash
   cd python/
   ```

2. **Install dependencies:**
   ```bash
   pip install requests configparser
   ```

3. **Configure the application:**
   ```bash
   cp config.ini.template config.ini
   # Edit config.ini with your Workiva API credentials
   ```

4. **Run the main script:**
   ```bash
   python W_IGAM_Request_new.py
   ```

### Directory Structure
```
python/
├── W_IGAM_Request_new.py      # Main IGAM reporting script
├── config.ini.template        # Configuration template
├── README.md                  # Python scripts documentation
├── utils/                     # Utility modules
│   ├── visualize_roles.py     # Advanced role visualization
│   ├── simple_visualize_roles.py  # Simple visualization
│   ├── data_validator.py      # Data validation utilities
│   └── azure_config_loader.py # Azure configuration loader
└── tests/                     # Test files
    └── test_workiva_igam_integration.py  # Integration tests
```

### Configuration Requirements

Create a `config.ini` file with your Workiva API credentials:
- API endpoints (token_url, users_url)
- OAuth client credentials (client_id, client_secret)
- Output settings (directory, filename)
- Email notification settings (optional)

**Security Note**: Never commit the actual `config.ini` file with real credentials to version control.

For detailed documentation, see [`python/README.md`](python/README.md).

## Support

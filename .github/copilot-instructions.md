<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# GitHub MCP Server Development Instructions

This is a Model Context Protocol (MCP) server for GitHub integration. When working on this project:

## MCP-Specific Guidelines
- You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt
- Follow the MCP protocol specifications for tool definitions and server implementation
- Use proper error handling for all GitHub API calls
- Implement comprehensive logging for debugging purposes

## GitHub Integration Best Practices
- Use the Octokit library for all GitHub API interactions
- Implement proper authentication using GitHub tokens
- Handle rate limiting gracefully
- Provide clear, structured responses from all tools
- Include proper TypeScript types for all functions and parameters

## Code Structure
- Keep all MCP tools in the main index.ts file for simplicity
- Use Zod schemas for input validation
- Follow async/await patterns for all API calls
- Use proper error handling and return structured error responses

## Development Workflow
- Always test tools with various GitHub repositories and scenarios
- Ensure proper environment variable handling for GITHUB_TOKEN
- Maintain backwards compatibility with MCP protocol versions
- Document all tools with clear descriptions and parameter information

## Security Considerations
- Never expose GitHub tokens in logs or error messages
- Validate all user inputs before making API calls
- Follow principle of least privilege for GitHub permissions
- Handle sensitive repository data appropriately

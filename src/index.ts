#!/usr/bin/env node

import dotenv from "dotenv";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { Octokit } from "@octokit/rest";

// Load environment variables from .env file
dotenv.config();

// GitHub API client
let octokit: Octokit;

// Initialize GitHub client with token from environment variable
function initializeGitHubClient() {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    console.error("GITHUB_TOKEN environment variable is required");
    process.exit(1);
  }
  
  octokit = new Octokit({
    auth: token,
  });
}

// Create server instance
const server = new McpServer({
  name: "github-mcp-server",
  version: "1.0.0",
  capabilities: {
    resources: {},
    tools: {},
  },
});

// Helper function for error handling
function handleError(error: any): { content: { type: "text"; text: string }[] } {
  console.error("GitHub API Error:", error);
  return {
    content: [
      {
        type: "text",
        text: `Error: ${error.message || "An unexpected error occurred"}`,
      },
    ],
  };
}

// Tool: List repositories for a user or organization
server.tool(
  "list-repositories",
  "List repositories for a user or organization",
  {
    owner: z.string().describe("Username or organization name"),
    type: z.enum(["all", "owner", "member"]).optional().describe("Repository type filter"),
    sort: z.enum(["created", "updated", "pushed", "full_name"]).optional().describe("Sort repositories by"),
    per_page: z.number().optional().describe("Number of results per page (max 100)"),
  },
  async ({ owner, type = "all", sort = "updated", per_page = 30 }) => {
    try {
      const { data } = await octokit.rest.repos.listForUser({
        username: owner,
        type,
        sort,
        per_page: Math.min(per_page, 100),
      });

      const repositories = data.map(repo => ({
        name: repo.name,
        full_name: repo.full_name,
        description: repo.description,
        private: repo.private,
        fork: repo.fork,
        language: repo.language,
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        updated_at: repo.updated_at,
        html_url: repo.html_url,
      }));

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(repositories, null, 2),
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Get repository information
server.tool(
  "get-repository",
  "Get detailed information about a specific repository",
  {
    owner: z.string().describe("Repository owner"),
    repo: z.string().describe("Repository name"),
  },
  async ({ owner, repo }) => {
    try {
      const { data } = await octokit.rest.repos.get({
        owner,
        repo,
      });

      const repoInfo = {
        name: data.name,
        full_name: data.full_name,
        description: data.description,
        private: data.private,
        fork: data.fork,
        language: data.language,
        size: data.size,
        stars: data.stargazers_count,
        watchers: data.watchers_count,
        forks: data.forks_count,
        open_issues: data.open_issues_count,
        default_branch: data.default_branch,
        created_at: data.created_at,
        updated_at: data.updated_at,
        pushed_at: data.pushed_at,
        clone_url: data.clone_url,
        ssh_url: data.ssh_url,
        html_url: data.html_url,
        topics: data.topics,
        license: data.license?.name,
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(repoInfo, null, 2),
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Create repository
server.tool(
  "create-repository",
  "Create a new GitHub repository",
  {
    name: z.string().describe("Repository name"),
    description: z.string().optional().describe("Repository description"),
    private: z.boolean().optional().describe("Whether repository is private (default: false)"),
    has_issues: z.boolean().optional().describe("Whether to enable issues (default: true)"),
    has_projects: z.boolean().optional().describe("Whether to enable projects (default: true)"),
    has_wiki: z.boolean().optional().describe("Whether to enable wiki (default: true)"),
    auto_init: z.boolean().optional().describe("Whether to initialize with README (default: false)"),
    gitignore_template: z.string().optional().describe("Gitignore template name"),
    license_template: z.string().optional().describe("License template name"),
  },
  async ({ 
    name, 
    description, 
    private: isPrivate = false, 
    has_issues = true, 
    has_projects = true, 
    has_wiki = true, 
    auto_init = false,
    gitignore_template,
    license_template 
  }) => {
    try {
      const { data } = await octokit.rest.repos.createForAuthenticatedUser({
        name,
        description,
        private: isPrivate,
        has_issues,
        has_projects,
        has_wiki,
        auto_init,
        gitignore_template,
        license_template,
      });

      const repoInfo = {
        name: data.name,
        full_name: data.full_name,
        description: data.description,
        private: data.private,
        html_url: data.html_url,
        clone_url: data.clone_url,
        ssh_url: data.ssh_url,
        created_at: data.created_at,
        default_branch: data.default_branch,
      };

      return {
        content: [
          {
            type: "text",
            text: `Repository created successfully!\n\n${JSON.stringify(repoInfo, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: List issues
server.tool(
  "list-issues",
  "List issues for a repository",
  {
    owner: z.string().describe("Repository owner"),
    repo: z.string().describe("Repository name"),
    state: z.enum(["open", "closed", "all"]).optional().describe("Issue state"),
    labels: z.string().optional().describe("Comma-separated list of labels"),
    assignee: z.string().optional().describe("Username of assignee"),
    per_page: z.number().optional().describe("Number of results per page (max 100)"),
  },
  async ({ owner, repo, state = "open", labels, assignee, per_page = 30 }) => {
    try {
      const { data } = await octokit.rest.issues.listForRepo({
        owner,
        repo,
        state,
        labels,
        assignee,
        per_page: Math.min(per_page, 100),
      });

      const issues = data.map(issue => ({
        number: issue.number,
        title: issue.title,
        body: issue.body,
        state: issue.state,
        user: issue.user?.login,
        assignees: issue.assignees?.map(a => a.login),
        labels: issue.labels.map(l => typeof l === "string" ? l : l.name),
        created_at: issue.created_at,
        updated_at: issue.updated_at,
        html_url: issue.html_url,
      }));

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(issues, null, 2),
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Create issue
server.tool(
  "create-issue",
  "Create a new issue in a repository",
  {
    owner: z.string().describe("Repository owner"),
    repo: z.string().describe("Repository name"),
    title: z.string().describe("Issue title"),
    body: z.string().optional().describe("Issue body/description"),
    labels: z.array(z.string()).optional().describe("Array of label names"),
    assignees: z.array(z.string()).optional().describe("Array of usernames to assign"),
  },
  async ({ owner, repo, title, body, labels, assignees }) => {
    try {
      const { data } = await octokit.rest.issues.create({
        owner,
        repo,
        title,
        body,
        labels,
        assignees,
      });

      const newIssue = {
        number: data.number,
        title: data.title,
        body: data.body,
        state: data.state,
        user: data.user?.login,
        labels: data.labels.map(l => typeof l === "string" ? l : l.name),
        html_url: data.html_url,
        created_at: data.created_at,
      };

      return {
        content: [
          {
            type: "text",
            text: `Issue created successfully:\n${JSON.stringify(newIssue, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Update issue
server.tool(
  "update-issue",
  "Update an existing issue",
  {
    owner: z.string().describe("Repository owner"),
    repo: z.string().describe("Repository name"),
    issue_number: z.number().describe("Issue number"),
    title: z.string().optional().describe("New issue title"),
    body: z.string().optional().describe("New issue body"),
    state: z.enum(["open", "closed"]).optional().describe("New issue state"),
    labels: z.array(z.string()).optional().describe("Array of label names"),
    assignees: z.array(z.string()).optional().describe("Array of usernames to assign"),
  },
  async ({ owner, repo, issue_number, title, body, state, labels, assignees }) => {
    try {
      const { data } = await octokit.rest.issues.update({
        owner,
        repo,
        issue_number,
        title,
        body,
        state,
        labels,
        assignees,
      });

      const updatedIssue = {
        number: data.number,
        title: data.title,
        body: data.body,
        state: data.state,
        user: data.user?.login,
        labels: data.labels.map(l => typeof l === "string" ? l : l.name),
        html_url: data.html_url,
        updated_at: data.updated_at,
      };

      return {
        content: [
          {
            type: "text",
            text: `Issue updated successfully:\n${JSON.stringify(updatedIssue, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: List pull requests
server.tool(
  "list-pull-requests",
  "List pull requests for a repository",
  {
    owner: z.string().describe("Repository owner"),
    repo: z.string().describe("Repository name"),
    state: z.enum(["open", "closed", "all"]).optional().describe("Pull request state"),
    head: z.string().optional().describe("Filter by head branch"),
    base: z.string().optional().describe("Filter by base branch"),
    per_page: z.number().optional().describe("Number of results per page (max 100)"),
  },
  async ({ owner, repo, state = "open", head, base, per_page = 30 }) => {
    try {
      const { data } = await octokit.rest.pulls.list({
        owner,
        repo,
        state,
        head,
        base,
        per_page: Math.min(per_page, 100),
      });

      const pullRequests = data.map(pr => ({
        number: pr.number,
        title: pr.title,
        body: pr.body,
        state: pr.state,
        user: pr.user?.login,
        head: {
          ref: pr.head.ref,
          sha: pr.head.sha,
        },
        base: {
          ref: pr.base.ref,
          sha: pr.base.sha,
        },
        draft: pr.draft,
        created_at: pr.created_at,
        updated_at: pr.updated_at,
        html_url: pr.html_url,
      }));

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(pullRequests, null, 2),
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Create pull request
server.tool(
  "create-pull-request",
  "Create a new pull request",
  {
    owner: z.string().describe("Repository owner"),
    repo: z.string().describe("Repository name"),
    title: z.string().describe("Pull request title"),
    head: z.string().describe("Head branch name"),
    base: z.string().describe("Base branch name"),
    body: z.string().optional().describe("Pull request body/description"),
    draft: z.boolean().optional().describe("Create as draft pull request"),
  },
  async ({ owner, repo, title, head, base, body, draft = false }) => {
    try {
      const { data } = await octokit.rest.pulls.create({
        owner,
        repo,
        title,
        head,
        base,
        body,
        draft,
      });

      const newPR = {
        number: data.number,
        title: data.title,
        body: data.body,
        state: data.state,
        user: data.user?.login,
        head: {
          ref: data.head.ref,
          sha: data.head.sha,
        },
        base: {
          ref: data.base.ref,
          sha: data.base.sha,
        },
        html_url: data.html_url,
        created_at: data.created_at,
      };

      return {
        content: [
          {
            type: "text",
            text: `Pull request created successfully:\n${JSON.stringify(newPR, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Get file contents
server.tool(
  "get-file-contents",
  "Get the contents of a file from a repository",
  {
    owner: z.string().describe("Repository owner"),
    repo: z.string().describe("Repository name"),
    path: z.string().describe("File path in the repository"),
    ref: z.string().optional().describe("Branch, tag, or commit SHA"),
  },
  async ({ owner, repo, path, ref }) => {
    try {
      const { data } = await octokit.rest.repos.getContent({
        owner,
        repo,
        path,
        ref,
      });

      if (Array.isArray(data)) {
        // Directory listing
        const files = data.map(item => ({
          name: item.name,
          path: item.path,
          type: item.type,
          size: item.size,
          download_url: item.download_url,
        }));

        return {
          content: [
            {
              type: "text",
              text: `Directory listing for ${path}:\n${JSON.stringify(files, null, 2)}`,
            },
          ],
        };
      } else if (data.type === "file") {
        // File content
        const content = Buffer.from(data.content, "base64").toString("utf-8");
        
        return {
          content: [
            {
              type: "text",
              text: `File: ${path}\nSize: ${data.size} bytes\nEncoding: ${data.encoding}\n\nContent:\n${content}`,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `${path} is a ${data.type}`,
            },
          ],
        };
      }
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Search repositories
server.tool(
  "search-repositories",
  "Search for repositories on GitHub",
  {
    query: z.string().describe("Search query"),
    sort: z.enum(["stars", "forks", "help-wanted-issues", "updated"]).optional().describe("Sort field"),
    order: z.enum(["asc", "desc"]).optional().describe("Sort order"),
    per_page: z.number().optional().describe("Number of results per page (max 100)"),
  },
  async ({ query, sort = "stars", order = "desc", per_page = 30 }) => {
    try {
      const { data } = await octokit.rest.search.repos({
        q: query,
        sort,
        order,
        per_page: Math.min(per_page, 100),
      });

      const repositories = data.items.map(repo => ({
        name: repo.name,
        full_name: repo.full_name,
        description: repo.description,
        language: repo.language,
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        score: repo.score,
        html_url: repo.html_url,
      }));

      return {
        content: [
          {
            type: "text",
            text: `Found ${data.total_count} repositories:\n${JSON.stringify(repositories, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Search issues
server.tool(
  "search-issues",
  "Search for issues and pull requests on GitHub",
  {
    query: z.string().describe("Search query"),
    sort: z.enum(["comments", "reactions", "reactions-+1", "reactions--1", "reactions-smile", "reactions-thinking_face", "reactions-heart", "reactions-tada", "interactions", "created", "updated"]).optional().describe("Sort field"),
    order: z.enum(["asc", "desc"]).optional().describe("Sort order"),
    per_page: z.number().optional().describe("Number of results per page (max 100)"),
  },
  async ({ query, sort = "created", order = "desc", per_page = 30 }) => {
    try {
      const { data } = await octokit.rest.search.issuesAndPullRequests({
        q: query,
        sort,
        order,
        per_page: Math.min(per_page, 100),
      });

      const issues = data.items.map(issue => ({
        number: issue.number,
        title: issue.title,
        state: issue.state,
        user: issue.user?.login,
        repository_url: issue.repository_url,
        labels: issue.labels.map(l => typeof l === "string" ? l : l.name),
        score: issue.score,
        html_url: issue.html_url,
        created_at: issue.created_at,
        updated_at: issue.updated_at,
      }));

      return {
        content: [
          {
            type: "text",
            text: `Found ${data.total_count} issues/PRs:\n${JSON.stringify(issues, null, 2)}`,
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

// Tool: Get user information
server.tool(
  "get-user",
  "Get information about a GitHub user",
  {
    username: z.string().describe("GitHub username"),
  },
  async ({ username }) => {
    try {
      const { data } = await octokit.rest.users.getByUsername({
        username,
      });

      const userInfo = {
        login: data.login,
        name: data.name,
        bio: data.bio,
        company: data.company,
        blog: data.blog,
        location: data.location,
        email: data.email,
        twitter_username: data.twitter_username,
        public_repos: data.public_repos,
        public_gists: data.public_gists,
        followers: data.followers,
        following: data.following,
        created_at: data.created_at,
        updated_at: data.updated_at,
        html_url: data.html_url,
        avatar_url: data.avatar_url,
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(userInfo, null, 2),
          },
        ],
      };
    } catch (error) {
      return handleError(error);
    }
  },
);

async function main() {
  // Initialize GitHub client
  initializeGitHubClient();
  
  // Create transport
  const transport = new StdioServerTransport();
  
  // Connect server to transport
  await server.connect(transport);
  
  console.error("GitHub MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});

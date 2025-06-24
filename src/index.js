#!/usr/bin/env node
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var mcp_js_1 = require("@modelcontextprotocol/sdk/server/mcp.js");
var stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
var zod_1 = require("zod");
var rest_1 = require("@octokit/rest");
// GitHub API client
var octokit;
// Initialize GitHub client with token from environment variable
function initializeGitHubClient() {
    var token = process.env.GITHUB_TOKEN;
    if (!token) {
        console.error("GITHUB_TOKEN environment variable is required");
        process.exit(1);
    }
    octokit = new rest_1.Octokit({
        auth: token,
    });
}
// Create server instance
var server = new mcp_js_1.McpServer({
    name: "github-mcp-server",
    version: "1.0.0",
    capabilities: {
        resources: {},
        tools: {},
    },
});
// Helper function for error handling
function handleError(error) {
    console.error("GitHub API Error:", error);
    return {
        content: [
            {
                type: "text",
                text: "Error: ".concat(error.message || "An unexpected error occurred"),
            },
        ],
    };
}
// Tool: List repositories for a user or organization
server.tool("list-repositories", "List repositories for a user or organization", {
    owner: zod_1.z.string().describe("Username or organization name"),
    type: zod_1.z.enum(["all", "owner", "member"]).optional().describe("Repository type filter"),
    sort: zod_1.z.enum(["created", "updated", "pushed", "full_name"]).optional().describe("Sort repositories by"),
    per_page: zod_1.z.number().optional().describe("Number of results per page (max 100)"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, repositories, error_1;
    var owner = _b.owner, _c = _b.type, type = _c === void 0 ? "all" : _c, _d = _b.sort, sort = _d === void 0 ? "updated" : _d, _e = _b.per_page, per_page = _e === void 0 ? 30 : _e;
    return __generator(this, function (_f) {
        switch (_f.label) {
            case 0:
                _f.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.repos.listForUser({
                        username: owner,
                        type: type,
                        sort: sort,
                        per_page: Math.min(per_page, 100),
                    })];
            case 1:
                data = (_f.sent()).data;
                repositories = data.map(function (repo) { return ({
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
                }); });
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify(repositories, null, 2),
                            },
                        ],
                    }];
            case 2:
                error_1 = _f.sent();
                return [2 /*return*/, handleError(error_1)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: Get repository information
server.tool("get-repository", "Get detailed information about a specific repository", {
    owner: zod_1.z.string().describe("Repository owner"),
    repo: zod_1.z.string().describe("Repository name"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, repoInfo, error_2;
    var _c;
    var owner = _b.owner, repo = _b.repo;
    return __generator(this, function (_d) {
        switch (_d.label) {
            case 0:
                _d.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.repos.get({
                        owner: owner,
                        repo: repo,
                    })];
            case 1:
                data = (_d.sent()).data;
                repoInfo = {
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
                    license: (_c = data.license) === null || _c === void 0 ? void 0 : _c.name,
                };
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify(repoInfo, null, 2),
                            },
                        ],
                    }];
            case 2:
                error_2 = _d.sent();
                return [2 /*return*/, handleError(error_2)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: List issues
server.tool("list-issues", "List issues for a repository", {
    owner: zod_1.z.string().describe("Repository owner"),
    repo: zod_1.z.string().describe("Repository name"),
    state: zod_1.z.enum(["open", "closed", "all"]).optional().describe("Issue state"),
    labels: zod_1.z.string().optional().describe("Comma-separated list of labels"),
    assignee: zod_1.z.string().optional().describe("Username of assignee"),
    per_page: zod_1.z.number().optional().describe("Number of results per page (max 100)"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, issues, error_3;
    var owner = _b.owner, repo = _b.repo, _c = _b.state, state = _c === void 0 ? "open" : _c, labels = _b.labels, assignee = _b.assignee, _d = _b.per_page, per_page = _d === void 0 ? 30 : _d;
    return __generator(this, function (_e) {
        switch (_e.label) {
            case 0:
                _e.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.issues.listForRepo({
                        owner: owner,
                        repo: repo,
                        state: state,
                        labels: labels,
                        assignee: assignee,
                        per_page: Math.min(per_page, 100),
                    })];
            case 1:
                data = (_e.sent()).data;
                issues = data.map(function (issue) {
                    var _a, _b;
                    return ({
                        number: issue.number,
                        title: issue.title,
                        body: issue.body,
                        state: issue.state,
                        user: (_a = issue.user) === null || _a === void 0 ? void 0 : _a.login,
                        assignees: (_b = issue.assignees) === null || _b === void 0 ? void 0 : _b.map(function (a) { return a.login; }),
                        labels: issue.labels.map(function (l) { return typeof l === "string" ? l : l.name; }),
                        created_at: issue.created_at,
                        updated_at: issue.updated_at,
                        html_url: issue.html_url,
                    });
                });
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify(issues, null, 2),
                            },
                        ],
                    }];
            case 2:
                error_3 = _e.sent();
                return [2 /*return*/, handleError(error_3)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: Create issue
server.tool("create-issue", "Create a new issue in a repository", {
    owner: zod_1.z.string().describe("Repository owner"),
    repo: zod_1.z.string().describe("Repository name"),
    title: zod_1.z.string().describe("Issue title"),
    body: zod_1.z.string().optional().describe("Issue body/description"),
    labels: zod_1.z.array(zod_1.z.string()).optional().describe("Array of label names"),
    assignees: zod_1.z.array(zod_1.z.string()).optional().describe("Array of usernames to assign"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, newIssue, error_4;
    var _c;
    var owner = _b.owner, repo = _b.repo, title = _b.title, body = _b.body, labels = _b.labels, assignees = _b.assignees;
    return __generator(this, function (_d) {
        switch (_d.label) {
            case 0:
                _d.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.issues.create({
                        owner: owner,
                        repo: repo,
                        title: title,
                        body: body,
                        labels: labels,
                        assignees: assignees,
                    })];
            case 1:
                data = (_d.sent()).data;
                newIssue = {
                    number: data.number,
                    title: data.title,
                    body: data.body,
                    state: data.state,
                    user: (_c = data.user) === null || _c === void 0 ? void 0 : _c.login,
                    labels: data.labels.map(function (l) { return typeof l === "string" ? l : l.name; }),
                    html_url: data.html_url,
                    created_at: data.created_at,
                };
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: "Issue created successfully:\n".concat(JSON.stringify(newIssue, null, 2)),
                            },
                        ],
                    }];
            case 2:
                error_4 = _d.sent();
                return [2 /*return*/, handleError(error_4)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: Update issue
server.tool("update-issue", "Update an existing issue", {
    owner: zod_1.z.string().describe("Repository owner"),
    repo: zod_1.z.string().describe("Repository name"),
    issue_number: zod_1.z.number().describe("Issue number"),
    title: zod_1.z.string().optional().describe("New issue title"),
    body: zod_1.z.string().optional().describe("New issue body"),
    state: zod_1.z.enum(["open", "closed"]).optional().describe("New issue state"),
    labels: zod_1.z.array(zod_1.z.string()).optional().describe("Array of label names"),
    assignees: zod_1.z.array(zod_1.z.string()).optional().describe("Array of usernames to assign"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, updatedIssue, error_5;
    var _c;
    var owner = _b.owner, repo = _b.repo, issue_number = _b.issue_number, title = _b.title, body = _b.body, state = _b.state, labels = _b.labels, assignees = _b.assignees;
    return __generator(this, function (_d) {
        switch (_d.label) {
            case 0:
                _d.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.issues.update({
                        owner: owner,
                        repo: repo,
                        issue_number: issue_number,
                        title: title,
                        body: body,
                        state: state,
                        labels: labels,
                        assignees: assignees,
                    })];
            case 1:
                data = (_d.sent()).data;
                updatedIssue = {
                    number: data.number,
                    title: data.title,
                    body: data.body,
                    state: data.state,
                    user: (_c = data.user) === null || _c === void 0 ? void 0 : _c.login,
                    labels: data.labels.map(function (l) { return typeof l === "string" ? l : l.name; }),
                    html_url: data.html_url,
                    updated_at: data.updated_at,
                };
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: "Issue updated successfully:\n".concat(JSON.stringify(updatedIssue, null, 2)),
                            },
                        ],
                    }];
            case 2:
                error_5 = _d.sent();
                return [2 /*return*/, handleError(error_5)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: List pull requests
server.tool("list-pull-requests", "List pull requests for a repository", {
    owner: zod_1.z.string().describe("Repository owner"),
    repo: zod_1.z.string().describe("Repository name"),
    state: zod_1.z.enum(["open", "closed", "all"]).optional().describe("Pull request state"),
    head: zod_1.z.string().optional().describe("Filter by head branch"),
    base: zod_1.z.string().optional().describe("Filter by base branch"),
    per_page: zod_1.z.number().optional().describe("Number of results per page (max 100)"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, pullRequests, error_6;
    var owner = _b.owner, repo = _b.repo, _c = _b.state, state = _c === void 0 ? "open" : _c, head = _b.head, base = _b.base, _d = _b.per_page, per_page = _d === void 0 ? 30 : _d;
    return __generator(this, function (_e) {
        switch (_e.label) {
            case 0:
                _e.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.pulls.list({
                        owner: owner,
                        repo: repo,
                        state: state,
                        head: head,
                        base: base,
                        per_page: Math.min(per_page, 100),
                    })];
            case 1:
                data = (_e.sent()).data;
                pullRequests = data.map(function (pr) {
                    var _a;
                    return ({
                        number: pr.number,
                        title: pr.title,
                        body: pr.body,
                        state: pr.state,
                        user: (_a = pr.user) === null || _a === void 0 ? void 0 : _a.login,
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
                    });
                });
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify(pullRequests, null, 2),
                            },
                        ],
                    }];
            case 2:
                error_6 = _e.sent();
                return [2 /*return*/, handleError(error_6)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: Create pull request
server.tool("create-pull-request", "Create a new pull request", {
    owner: zod_1.z.string().describe("Repository owner"),
    repo: zod_1.z.string().describe("Repository name"),
    title: zod_1.z.string().describe("Pull request title"),
    head: zod_1.z.string().describe("Head branch name"),
    base: zod_1.z.string().describe("Base branch name"),
    body: zod_1.z.string().optional().describe("Pull request body/description"),
    draft: zod_1.z.boolean().optional().describe("Create as draft pull request"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, newPR, error_7;
    var _c;
    var owner = _b.owner, repo = _b.repo, title = _b.title, head = _b.head, base = _b.base, body = _b.body, _d = _b.draft, draft = _d === void 0 ? false : _d;
    return __generator(this, function (_e) {
        switch (_e.label) {
            case 0:
                _e.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.pulls.create({
                        owner: owner,
                        repo: repo,
                        title: title,
                        head: head,
                        base: base,
                        body: body,
                        draft: draft,
                    })];
            case 1:
                data = (_e.sent()).data;
                newPR = {
                    number: data.number,
                    title: data.title,
                    body: data.body,
                    state: data.state,
                    user: (_c = data.user) === null || _c === void 0 ? void 0 : _c.login,
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
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: "Pull request created successfully:\n".concat(JSON.stringify(newPR, null, 2)),
                            },
                        ],
                    }];
            case 2:
                error_7 = _e.sent();
                return [2 /*return*/, handleError(error_7)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: Get file contents
server.tool("get-file-contents", "Get the contents of a file from a repository", {
    owner: zod_1.z.string().describe("Repository owner"),
    repo: zod_1.z.string().describe("Repository name"),
    path: zod_1.z.string().describe("File path in the repository"),
    ref: zod_1.z.string().optional().describe("Branch, tag, or commit SHA"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, files, content, error_8;
    var owner = _b.owner, repo = _b.repo, path = _b.path, ref = _b.ref;
    return __generator(this, function (_c) {
        switch (_c.label) {
            case 0:
                _c.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.repos.getContent({
                        owner: owner,
                        repo: repo,
                        path: path,
                        ref: ref,
                    })];
            case 1:
                data = (_c.sent()).data;
                if (Array.isArray(data)) {
                    files = data.map(function (item) { return ({
                        name: item.name,
                        path: item.path,
                        type: item.type,
                        size: item.size,
                        download_url: item.download_url,
                    }); });
                    return [2 /*return*/, {
                            content: [
                                {
                                    type: "text",
                                    text: "Directory listing for ".concat(path, ":\n").concat(JSON.stringify(files, null, 2)),
                                },
                            ],
                        }];
                }
                else if (data.type === "file") {
                    content = Buffer.from(data.content, "base64").toString("utf-8");
                    return [2 /*return*/, {
                            content: [
                                {
                                    type: "text",
                                    text: "File: ".concat(path, "\nSize: ").concat(data.size, " bytes\nEncoding: ").concat(data.encoding, "\n\nContent:\n").concat(content),
                                },
                            ],
                        }];
                }
                else {
                    return [2 /*return*/, {
                            content: [
                                {
                                    type: "text",
                                    text: "".concat(path, " is a ").concat(data.type),
                                },
                            ],
                        }];
                }
                return [3 /*break*/, 3];
            case 2:
                error_8 = _c.sent();
                return [2 /*return*/, handleError(error_8)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: Search repositories
server.tool("search-repositories", "Search for repositories on GitHub", {
    query: zod_1.z.string().describe("Search query"),
    sort: zod_1.z.enum(["stars", "forks", "help-wanted-issues", "updated"]).optional().describe("Sort field"),
    order: zod_1.z.enum(["asc", "desc"]).optional().describe("Sort order"),
    per_page: zod_1.z.number().optional().describe("Number of results per page (max 100)"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, repositories, error_9;
    var query = _b.query, _c = _b.sort, sort = _c === void 0 ? "stars" : _c, _d = _b.order, order = _d === void 0 ? "desc" : _d, _e = _b.per_page, per_page = _e === void 0 ? 30 : _e;
    return __generator(this, function (_f) {
        switch (_f.label) {
            case 0:
                _f.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.search.repos({
                        q: query,
                        sort: sort,
                        order: order,
                        per_page: Math.min(per_page, 100),
                    })];
            case 1:
                data = (_f.sent()).data;
                repositories = data.items.map(function (repo) { return ({
                    name: repo.name,
                    full_name: repo.full_name,
                    description: repo.description,
                    language: repo.language,
                    stars: repo.stargazers_count,
                    forks: repo.forks_count,
                    score: repo.score,
                    html_url: repo.html_url,
                }); });
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: "Found ".concat(data.total_count, " repositories:\n").concat(JSON.stringify(repositories, null, 2)),
                            },
                        ],
                    }];
            case 2:
                error_9 = _f.sent();
                return [2 /*return*/, handleError(error_9)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: Search issues
server.tool("search-issues", "Search for issues and pull requests on GitHub", {
    query: zod_1.z.string().describe("Search query"),
    sort: zod_1.z.enum(["comments", "reactions", "reactions-+1", "reactions--1", "reactions-smile", "reactions-thinking_face", "reactions-heart", "reactions-tada", "interactions", "created", "updated"]).optional().describe("Sort field"),
    order: zod_1.z.enum(["asc", "desc"]).optional().describe("Sort order"),
    per_page: zod_1.z.number().optional().describe("Number of results per page (max 100)"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, issues, error_10;
    var query = _b.query, _c = _b.sort, sort = _c === void 0 ? "created" : _c, _d = _b.order, order = _d === void 0 ? "desc" : _d, _e = _b.per_page, per_page = _e === void 0 ? 30 : _e;
    return __generator(this, function (_f) {
        switch (_f.label) {
            case 0:
                _f.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.search.issuesAndPullRequests({
                        q: query,
                        sort: sort,
                        order: order,
                        per_page: Math.min(per_page, 100),
                    })];
            case 1:
                data = (_f.sent()).data;
                issues = data.items.map(function (issue) {
                    var _a;
                    return ({
                        number: issue.number,
                        title: issue.title,
                        state: issue.state,
                        user: (_a = issue.user) === null || _a === void 0 ? void 0 : _a.login,
                        repository_url: issue.repository_url,
                        labels: issue.labels.map(function (l) { return typeof l === "string" ? l : l.name; }),
                        score: issue.score,
                        html_url: issue.html_url,
                        created_at: issue.created_at,
                        updated_at: issue.updated_at,
                    });
                });
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: "Found ".concat(data.total_count, " issues/PRs:\n").concat(JSON.stringify(issues, null, 2)),
                            },
                        ],
                    }];
            case 2:
                error_10 = _f.sent();
                return [2 /*return*/, handleError(error_10)];
            case 3: return [2 /*return*/];
        }
    });
}); });
// Tool: Get user information
server.tool("get-user", "Get information about a GitHub user", {
    username: zod_1.z.string().describe("GitHub username"),
}, function (_a) { return __awaiter(void 0, [_a], void 0, function (_b) {
    var data, userInfo, error_11;
    var username = _b.username;
    return __generator(this, function (_c) {
        switch (_c.label) {
            case 0:
                _c.trys.push([0, 2, , 3]);
                return [4 /*yield*/, octokit.rest.users.getByUsername({
                        username: username,
                    })];
            case 1:
                data = (_c.sent()).data;
                userInfo = {
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
                return [2 /*return*/, {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify(userInfo, null, 2),
                            },
                        ],
                    }];
            case 2:
                error_11 = _c.sent();
                return [2 /*return*/, handleError(error_11)];
            case 3: return [2 /*return*/];
        }
    });
}); });
function main() {
    return __awaiter(this, void 0, void 0, function () {
        var transport;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    // Initialize GitHub client
                    initializeGitHubClient();
                    transport = new stdio_js_1.StdioServerTransport();
                    // Connect server to transport
                    return [4 /*yield*/, server.connect(transport)];
                case 1:
                    // Connect server to transport
                    _a.sent();
                    console.error("GitHub MCP Server running on stdio");
                    return [2 /*return*/];
            }
        });
    });
}
main().catch(function (error) {
    console.error("Fatal error in main():", error);
    process.exit(1);
});

import { t } from "../../lib/i18n.svelte.js";

export const COMMANDS = [
  {
    id: "search",
    aliases: [],
    name: "Web Search",
    description: "Search the web and inject results into chat",
    usage: "/search <query>",
    category: "tools",
    descKey: "commands.cmdSearchDesc",
    usageKey: "commands.cmdSearchUsage",
    catKey: "commands.cattools",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
    minArgs: 1,
    validateArgs(args) { return args[0] ? null : t("commands.cmdSearchUsage") },
  },
  {
    id: "new",
    aliases: [],
    name: "New Chat",
    description: "Start a new conversation",
    usage: "/new",
    category: "navigation",
    descKey: "commands.cmdNewDesc",
    usageKey: "commands.cmdNewUsage",
    catKey: "commands.catnavigation",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`,
    minArgs: 0,
  },
  {
    id: "export",
    aliases: [],
    name: "Export Chat",
    description: "Export the conversation (markdown, pdf, html, image)",
    usage: "/export <format>",
    category: "tools",
    descKey: "commands.cmdExportDesc",
    usageKey: "commands.cmdExportUsage",
    catKey: "commands.cattools",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
    minArgs: 1,
    validateArgs(args) { const f = (args[0] || "").toLowerCase(); return ["markdown", "pdf", "html", "image"].includes(f) ? null : t("commands.cmdExportUsage") },
  },
  {
    id: "compress",
    aliases: ["handoff"],
    name: "Compress / Handoff",
    description: "Summarize the conversation and start a new session with full context",
    usage: "/compress",
    category: "tools",
    descKey: "commands.cmdCompressDesc",
    usageKey: "commands.cmdCompressUsage",
    catKey: "commands.cattools",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"/><path d="M8 15l4 4 4-4"/><path d="M12 19V9"/></svg>`,
    minArgs: 0,
  },
  {
    id: "summarize",
    aliases: [],
    name: "Summarize",
    description: "Generate a handoff summary of the conversation in the current chat",
    usage: "/summarize",
    category: "tools",
    descKey: "commands.cmdSummarizeDesc",
    usageKey: "commands.cmdSummarizeUsage",
    catKey: "commands.cattools",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
    minArgs: 0,
  },
  {
    id: "github",
    aliases: ["gh"],
    name: "GitHub Fetch",
    description: "Fetch a GitHub repo or a single file (via a /blob/ URL) directly, without relying on the AI to request it",
    usage: "/github <owner/repo, repo URL, or file blob URL>",
    category: "tools",
    descKey: "commands.cmdGithubDesc",
    usageKey: "commands.cmdGithubUsage",
    catKey: "commands.cattools",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>`,
    minArgs: 1,
    validateArgs(args) { return args[0] ? null : "Usage: /github <owner/repo, repo URL, or file blob URL>" },
  },
  {
    id: "curl",
    aliases: [],
    name: "cURL",
    description: "Make an HTTP request and return the response",
    usage: "/curl <url> [method] [headers] [body]",
    category: "tools",
    descKey: "commands.cmdCurlDesc",
    usageKey: "commands.cmdCurlUsage",
    catKey: "commands.cattools",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
    minArgs: 1,
    validateArgs(args) { return args[0] ? null : "Usage: /curl <url>"; },
  },
  {
    id: "help",
    aliases: ["?"],
    name: "Help",
    description: "Show all available commands",
    usage: "/help [command]",
    category: "builtin",
    descKey: "commands.cmdHelpDesc",
    usageKey: "commands.cmdHelpUsage",
    catKey: "commands.catbuiltin",
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
    minArgs: 0,
  },
]

export function findCommand(id) {
  const lower = id.toLowerCase()
  return COMMANDS.find(c => c.id === lower || c.aliases.includes(lower)) || null
}

export function getCommandSuggestions(partial) {
  const lower = (partial || "").toLowerCase()
  if (!lower) return COMMANDS
  return COMMANDS.filter(c =>
    c.id.includes(lower) ||
    c.aliases.some(a => a.includes(lower)) ||
    c.name.toLowerCase().includes(lower) ||
    c.description.toLowerCase().includes(lower)
  )
}

/**
 * Parse tag attributes from a string like: fileName="test.py" content="..."
 */
export function parseTagAttributes(rawAttrs) {
  const attrs = {};
  const regex = /([A-Za-z0-9_:-]+)\s*=\s*"([\s\S]*?)"/g;

  let match;
  while ((match = regex.exec(rawAttrs)) !== null) {
    const key = String(match[1] || "").trim();
    if (!key) {
      continue;
    }

    if (key === "fileName") {
      attrs.fileName = String(match[2] || "");
    } else {
      attrs[key] = String(match[2] || "");
    }
  }

  return attrs;
}

/**
 * Normalize content extracted from a BDS tag.
 */
export function normalizeTaggedCodeContent(content, tagName) {
  const name = String(tagName || "").toLowerCase();
  let output = String(content || "");

  if (
    name === "create_file" ||
    name === "run_python_embed" ||
    name === "html" ||
    name === "latex" ||
    name === "visualizer" ||
    name === "docx" ||
    name === "pptx" ||
    name === "excel" ||
    name === "character_create" ||
    name === "skill_create" ||
    name === "auto:code_runner"
  ) {
    output = unwrapMarkdownCodeFence(output);
  }

  if (
    name === "run_python_embed" ||
    name === "html" ||
    name === "docx" ||
    name === "pptx" ||
    name === "excel" ||
    name === "auto:code_runner"
  ) {
    output = stripLeadingChatter(output);
  }

  return output;
}

/**
 * Strips leading/trailing conversational text from a code block.
 * Specifically targets cases where AI ignores markdown fences and writes:
 * "Here is the code: const doc = ..."
 */
function stripLeadingChatter(content) {
  let output = String(content || "").trim();

  // If content is wrapped in a code fence (possibly with leading chatter),
  // unwrap it first so the JS-keyword check can work on the actual code.
  const fenceMatch = output.match(/```(?:[a-zA-Z0-9_+.-]*)\s*\r?\n?([\s\S]*?)```\s*$/);
  if (fenceMatch) {
    output = fenceMatch[1].trim();
  }

  // If it already looks like it starts with code, leave it
  if (/^(?:const|let|var|function|async|import|export|class|await|\/\/|\/\*)/.test(output)) {
    return output;
  }

  // Look for the first occurrence of a JS keyword at the start of a line
  const jsStartMatch = output.match(/(?:\r?\n|^)\s*(const|let|var|function|async|import|class|await|document)\s+/);
  if (jsStartMatch && jsStartMatch.index > 0) {
    console.log(`[BDS:Parser] Stripping leading chatter for JS block: "${output.substring(0, 30)}..."`);
    return output.substring(jsStartMatch.index).trim();
  }

  return output;
}

/**
 * Unwrap markdown code fences (```lang ... ```) from content.
 * Robust: Handles multiple fences, unclosed fences, and leftover backticks.
 */
export function unwrapMarkdownCodeFence(content) {
  let text = String(content || "");

  // Only unwrap if the ENTIRE content is wrapped in a single outer code fence.
  // This correctly preserves content with multiple inner code fences
  // (e.g., README files, skill instructions with code examples).
  const trimmed = text.trim();

  // Match: ```lang\n...\n``` (single outer fence, nothing before/after)
  const singleFenceMatch = trimmed.match(/^```(?:[a-zA-Z0-9_+.-]*)\s*\r?\n?([\s\S]*?)```\s*$/);
  if (singleFenceMatch) {
    return singleFenceMatch[1].trim();
  }

  // Handle unclosed fence: ```lang\n...code... (no closing ```)
  const unclosedMatch = trimmed.match(/^```(?:[a-zA-Z0-9_+.-]*)\s*\r?\n?([\s\S]+)$/);
  if (unclosedMatch) {
    return unclosedMatch[1].trim();
  }

  // Not wrapped in a single fence — return as-is (preserves multiple nested code blocks)
  return trimmed;
}


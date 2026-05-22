// Language Tutor plugin entry for the OpenClaw host.
//
// Uses focused SDK subpath imports (NOT a whole-SDK wildcard import) per the
// OpenClaw plugin model: https://docs.openclaw.ai/plugins
//
// Capability stance (mirrors src/language_tutor/adapters/registry.py OpenClaw
// defaults): text supported; lifecycle start = first_message; lifecycle end =
// not_available; boot context is built on the first tutor message. Any
// side-effectful / binary-dependent tool is registered opt-in only.

import { definePluginEntry } from "openclaw/plugin-sdk/entry";
import { registerTool } from "openclaw/plugin-sdk/tools";
import type { PluginApi } from "openclaw/plugin-sdk/types";

// First-message boot trigger: OpenClaw has no SessionStart-style hook, so the
// tutor assembles boot context the first time the learner messages the tutor.
const bootContextTool = {
  name: "language_tutor.boot_context",
  description:
    "Assemble learner boot context (profile, preferences, focus) on the first tutor message.",
  inputSchema: {
    type: "object",
    properties: {
      sessionId: { type: "string" },
    },
    required: [],
  },
  async handler(input: { sessionId?: string }): Promise<{ sections: string[] }> {
    // Pure text assembly only. No persistence or host-specific behavior here;
    // the core tutor owns boot-context generation.
    void input;
    return { sections: [] };
  },
} as const;

// Text-modality tutor tool (reading / lesson / transcript / vocab / writing /
// progress are all text-only flows). No side effects beyond returning text.
const textExerciseTool = {
  name: "language_tutor.text_exercise",
  description:
    "Present and evaluate a text-only tutor exercise (reading, lesson, transcript, vocab, writing, progress).",
  inputSchema: {
    type: "object",
    properties: {
      modality: { type: "string" },
      payload: { type: "object" },
    },
    required: ["modality"],
  },
  async handler(input: {
    modality: string;
    payload?: Record<string, unknown>;
  }): Promise<{ modality: string; text: string }> {
    void input.payload;
    return { modality: input.modality, text: "" };
  },
} as const;

// Side-effectful / binary-dependent tool. Shells out to the local tutor CLI,
// so it is OPT-IN ONLY ({ optional: true }) and gated behind a user allowlist.
const runCliTool = {
  name: "language_tutor.run_cli",
  description:
    "Invoke the local language-tutor CLI. Binary-dependent and side-effectful; opt-in only.",
  optional: true,
  inputSchema: {
    type: "object",
    properties: {
      command: { type: "array", items: { type: "string" } },
    },
    required: ["command"],
  },
  async handler(input: { command: string[] }): Promise<{ command: string[] }> {
    // Execution is performed by the host only after the user allowlists it.
    return { command: input.command };
  },
} as const;

export default definePluginEntry((api: PluginApi) => {
  registerTool(api, bootContextTool);
  registerTool(api, textExerciseTool);
  // Opt-in: registered with optional:true; the host requires explicit user
  // allowlisting before this binary-dependent tool can run.
  registerTool(api, runCliTool);
});

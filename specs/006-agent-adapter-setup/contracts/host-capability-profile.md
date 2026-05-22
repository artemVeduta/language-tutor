# Contract: Host Capability Profile

> **Superseded on the lifecycle surface by spec 007 (Hook-Free Incremental
> Lifecycle, Constitution Principle IX).** All four host profiles MUST declare
> `lifecycle_start=first_message`, `lifecycle_end=not_available`,
> `boot_context_trigger=first_tutor_message`,
> `persistence_mode=incremental_checkpoint`, and a valid `session_id_source`.
> Hook boot triggers (`session_start_hook`, `codex_plugin_hook`) and
> `lifecycle_start=hook` are rejected by the `AdapterCapabilityProfile`
> validator. The mentions below are retained as historical context only.

## Purpose

Declare what a host can support before tutor flows depend on it. This contract keeps host mechanics out of pedagogy, feedback, progress, and persistence.

## JSON Shape

```json
{
  "schema_version": 1,
  "host": "hermes",
  "display_name": "Hermes",
  "text_support": "supported",
  "audio_support": "unsupported",
  "image_support": "unsupported",
  "lifecycle_start": "explicit_command",
  "lifecycle_end": "not_available",
  "boot_context_trigger": "explicit_tutor_command",
  "setup_entry_point": "hermes profile install",
  "update_behavior": "hermes profile update",
  "side_effectful_capabilities": [],
  "unsupported_capabilities": [],
  "flow_gates": []
}
```

## Field Rules

- `host` is one of `hermes`, `openclaw`, `claude`, or `codex`.
- `text_support` is `supported`, `partial`, or `unsupported`.
- `audio_support` and `image_support` are `unsupported` for spec 006.
- `lifecycle_start` is `hook`, `explicit_command`, `first_message`, `manual`, or `not_available`.
- `lifecycle_end` is `hook`, `explicit_command`, `manual`, or `not_available`.
- `boot_context_trigger` is `session_start_hook`, `codex_plugin_hook`, `explicit_tutor_command`, `first_tutor_message`, or `host_specific`.
- `flow_gates` lists representative flows blocked by unsupported host capability.

## Representative Flows

All hosts must declare support or a documented gate for:

- `reading`
- `lesson`
- `transcript`
- `vocab`
- `writing`
- `progress`

## Validation

- A host with `text_support=unsupported` cannot pass spec 006.
- A host without hook lifecycle must declare a non-hook boot trigger.
- Any `flow_gates` entry must also appear in the host setup profile and manual provider install report.
- Capability profiles cannot mention Antigravity, audio, image, dashboards, cloud sync, multi-user behavior, or new persistence.

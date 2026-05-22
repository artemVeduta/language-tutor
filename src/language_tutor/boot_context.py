from __future__ import annotations

from datetime import UTC, datetime

from language_tutor.dal.repositories import TutorRepository
from language_tutor.schemas import (
    BootContext,
    BootContextTrigger,
    BootSection,
    BootTrigger,
    LearnerPreferences,
    LearnerProfile,
    TriggerType,
)
from language_tutor.vocab import derive_active_weak_tag_signals


def select_boot_trigger(boot_context_trigger: str) -> BootContextTrigger:
    """Deterministically map a host's declared boot trigger to a lifecycle path.

    Hook-capable hosts (Claude SessionStart, Codex plugin hook) use a hook
    trigger. Non-hook hosts must use an explicit command, first message, or
    host-specific manual trigger. Core boot-context rendering stays host-blind.
    """
    hook_triggers = {
        BootTrigger.SESSION_START_HOOK.value: "SessionStart",
        BootTrigger.CODEX_PLUGIN_HOOK.value: "CodexPluginStart",
    }
    if boot_context_trigger in hook_triggers:
        return BootContextTrigger(
            trigger_type=TriggerType.HOOK,
            host_event_name=hook_triggers[boot_context_trigger],
            command=None,
            input_contract="host hook payload (JSON)",
            output_contract="BootContext or HostSetupFailure",
            fallback=TriggerType.EXPLICIT_COMMAND,
        )
    if boot_context_trigger == BootTrigger.EXPLICIT_TUTOR_COMMAND.value:
        return BootContextTrigger(
            trigger_type=TriggerType.EXPLICIT_COMMAND,
            command="tutor boot --json",
            input_contract="profile+preferences (JSON)",
            output_contract="BootContext or HostSetupFailure",
            fallback=TriggerType.FIRST_MESSAGE,
        )
    if boot_context_trigger == BootTrigger.FIRST_TUTOR_MESSAGE.value:
        return BootContextTrigger(
            trigger_type=TriggerType.FIRST_MESSAGE,
            command="tutor boot --json",
            input_contract="first learner message",
            output_contract="BootContext or HostSetupFailure",
            fallback=TriggerType.MANUAL,
        )
    return BootContextTrigger(
        trigger_type=TriggerType.MANUAL,
        command="tutor boot --json",
        input_contract="manual invocation",
        output_contract="BootContext or HostSetupFailure",
        fallback=None,
    )


def build_boot_context(
    repo: TutorRepository, profile: LearnerProfile, preferences: LearnerPreferences
) -> BootContext:
    now = datetime.now(UTC).replace(microsecond=0)
    due = repo.due_count(now)
    weak = derive_active_weak_tag_signals(repo)
    latest = repo.latest_summary()
    weak_lines = [
        (
            f"{signal.priority_rank}. {signal.tag}: seen in {signal.session_count} sessions "
            f"(mistakes {signal.source_counts.mistake_events}, vocab reviews "
            f"{signal.source_counts.low_quality_reviews})"
        )
        for signal in weak
    ]
    sections = [
        BootSection(
            title="Profile",
            lines=[
                f"{profile.native_language} -> {profile.target_language}",
                f"Level target: {profile.level_target}",
            ],
        ),
        BootSection(
            title="Session",
            lines=[
                f"Length: {preferences.session_length}",
                f"Review intensity: {preferences.review_intensity}",
            ],
        ),
        BootSection(title="Due Review", lines=[f"Due items: {due}"]),
        BootSection(title="Weak Patterns", lines=weak_lines or ["No weak patterns yet."]),
        BootSection(
            title="Latest Recap",
            lines=[
                latest or "First session guidance: set up profile, then try vocabulary or writing."
            ],
        ),
        BootSection(
            title="Local Status", lines=["Profile/preferences: available", "History: local SQLite"]
        ),
    ]
    return BootContext(
        profile=profile, preferences=preferences, sections=sections, generated_at=now
    )


def render_boot_context(context: BootContext) -> str:
    lines: list[str] = []
    for section in context.sections[:8]:
        lines.append(f"## {section.title}")
        lines.extend(f"- {line}" for line in section.lines)
    rendered = "\n".join(lines)
    if len(rendered) <= context.max_rendered_chars:
        return rendered
    return rendered[: context.max_rendered_chars - 20].rstrip() + "\n- truncated"

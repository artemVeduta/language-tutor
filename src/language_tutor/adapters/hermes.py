"""Hermes host adapter.

Hermes uses a git-backed profile distribution and has no Claude-style startup
hook, so it boots the tutor through an explicit command trigger. Setup is
package-only; this module exposes the host capability profile and leaves all
pedagogy, feedback, progress, and learner state to the tutor core.
"""

from __future__ import annotations

from language_tutor.adapters.registry import capability_profile_for
from language_tutor.schemas import AdapterCapabilityProfile, HostId


def capability_profile() -> AdapterCapabilityProfile:
    return capability_profile_for(HostId.HERMES.value)

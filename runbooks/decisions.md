# Team Decisions - M0

## Decision 1: consent_grant_id precedence
Date: 24 July 2026
Raised by: Ammar (Phase 3 planning)
Resolved by: Fatima

The registry profile (IdentityProfileV1.consent_grant_id /
VoiceProfileV1.consent_grant_id) is the authoritative source, since
consent belongs to the identity/voice being used, not to any single
request. IdeaRequestV1.consent_grant_id, if supplied, is an override to
be validated against the profile's own grant - not an independent
source of truth.

Enforcement (the actual cross-check) is not yet built - deferred to a
later validator, not part of M0's contract layer.

## Decision 2: script text - inline vs. ArtifactRefV1
Date: 24 July 2026
Raised by: Ammar (Phase 3 planning)
Resolved by: Fatima, Malik

Keep script text inline on ScriptPackageV1 (list[str]) rather than
wrapping it in ArtifactRefV1. Rationale (Malik): script text is small,
short-lived, and not "media" in the sense ArtifactRefV1 exists for.
Revisit if scripts become long-form or need multi-language variants,
at which point the ArtifactRefV1 pattern would start earning its cost.
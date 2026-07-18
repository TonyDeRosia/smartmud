# Smart MUD combat heartbeat — Phase 19B

The configured heartbeat uses `base_pulse_ms=100` and
`violence_pulse_count=20`, giving the normal configurable two-second violence
pulse. `CombatRuntimeService.ROUND_DELAY` documents that policy; production
uses the heartbeat configuration rather than another wall-clock timer. Tests
advance `process_runtime_pulse()` explicitly.

Each due resident encounter is processed at most once per pulse. Participants
are ordered deterministically by dexterity then stable actor ID. An opening
attack occurs immediately, while the defender first retaliates on a later
violence pulse. Every later PC/NPC ordinary attack goes through the existing
Phase 19A resolver and DamageService path.

Ordinary attacks apply a one-pulse readiness wait to the participant. The
next violence pulse expires that wait before action selection; repeated `kill`
while waiting is honestly rejected. Seated NPCs may rise to fight. Resting,
sleeping, stunned, incapacitated, mortally wounded, and dead actors are
published as skipped and do not attack.

Defeat, removal, logout, room separation, invalid targets, and restart end or
repair encounters. End cleanup clears targets/actions, restores living actors
to standing through the existing state service, and never revives dead actors.
The phase intentionally does not add flee, corpses, rewards, skills, or spell
damage.

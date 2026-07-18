# Combat timing audit — Phase 19B

`MudRuntime.process_runtime_pulse()` is the authoritative heartbeat.  Its
violence bucket calls `CombatRuntimeService.process_due_rounds()` once; there
is no per-actor timer and no second combat thread.  Resident encounters are
keyed by encounter ID and remember the last violence pulse, so duplicate
scheduling of a round is rejected.

The combat service owns transient resident encounters, opponent links, queued
actions, wait pulses, and output packets.  It resolves actors by stable
`character:`/`entity:` IDs on each round.  Logout removes resident actors,
entity removal and separation stop their participant, and restart cancels
active database encounters before any resident state exists.

HP is not scheduler state: the Phase 19A combat resolver mutates canonical
actors and `persist_actor` projects the result to the live character/entity
record.  Thus score, prompt, look, and later rounds use the same HP.  Durable
HP/position follow the existing character/entity persistence policy; all
engagement and readiness state is intentionally transient.

Browser clients drain ordered packets through the existing `play_view` async
path.  Telnet uses the same runtime output transport and receives plain text;
the packet has no HTML payload.  Ordinary movement is rejected during active
combat.  Forced movement ends the affected encounter safely.

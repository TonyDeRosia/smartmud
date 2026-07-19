# Combat and corpse reference parity — Phase 21B11

## Evidence boundary

The requested custom TBA archive was not discoverable as a `src/fight.c` tree
or source archive in this execution environment.  This phase therefore does
not fabricate C line citations or claim reference-source inspection.  The
reference facts below are the requested parity target; their source-file and
function names are recorded for the next audit pass: `src/comm.c`
(`PULSE_VIOLENCE`, heartbeat dispatch and `point_update()`), `src/fight.c`
(`perform_violence()`, `attack_hit_text[]`, `dam_message()`, `damage()` and
`damage_severity_tier()`), `src/magic.c`/`src/spells.c` (`skill_message()`),
`src/handler.c` (`make_corpse()`), and `src/limits.c` (corpse expiry).

## Implemented Smart MUD policy

* The runtime pulse is 100 ms and `violence_pulse_count` is 20, so the sole
  heartbeat dispatches combat every two seconds.  Commands and projections do
  not call `process_due_rounds()`.
* Each resident encounter stamps a deterministic `world:encounter:round` ID,
  runtime tick, scheduled time, and sorted participant IDs in
  `combat_round_started`.  Repeating a pulse is ignored by
  `last_violence_pulse`.
* Participant order is deterministic: descending dexterity then actor ID.
  Position, target health, room separation, and wait are checked before an
  action.  `Actor.wait_state` is the canonical wait authority: it decreases
  once per combat round, never below zero, and a round which reduces it to zero
  is still skipped (`WAIT_STATE`).
* Generic physical prose is selected from equipped/natural attack metadata;
  spell requests are rewritten to spell-specific messages before transport
  delivery, so they cannot inherit a fist, bite, or other physical noun.
* NPC corpse duration is canonical object-update ticks: 75 seconds/tick × 5
  ticks = 375 seconds.  The current player-death policy does not create a
  player corpse, so the reference 10-tick player duration is documented as an
  unsupported policy gap rather than silently applying an NPC timer.
* Corpse state records death ID, source entity/lifecycle IDs, creation and
  absolute expiry timestamps, tick count, kind, and decay state.  Expiry is
  absolute and is not recalculated on look, projection rebuild, or restart.
  On expiry contained items move to the corpse room before the corpse is
  extracted, and one room-scoped semantic message is emitted: “A quivering
  horde of maggots consumes the corpse of …”.

## Remaining gaps

Reference line verification, authored `dam_message()` versus spell fallback
threshold table conformance, player corpse support, carrier/container corpse
spill destinations, offhand/proc parity, and the complete transport ordering
matrix still require focused implementation and tests.  This document does not
reconsider Phase 21B closure.

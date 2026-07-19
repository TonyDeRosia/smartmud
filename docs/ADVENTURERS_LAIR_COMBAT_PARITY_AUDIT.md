# Adventurer's Lair combat parity audit

## Evidence and scope

This is a foundation audit, not a claim of full parity.  The runtime claims in
this document are verified against Smart MUD source and tests.  Reference-C
claims remain explicitly marked **pending line-level verification** until the
supplied archive is made visible in the working tree; no network clone is used
as a substitute for that archive.  Existing project reference notes are
secondary context, never proof of custom-source behavior.

Smart MUD's current clock is authoritative: `base_pulse_ms=100` and
`violence_pulse_count=20`, hence a two-second round.  The heartbeat invokes
`CombatRuntimeService.process_due_rounds()` once per violence bucket; resident
encounters reject a repeated pulse.  A hostile spell is its own opening action,
creates an engagement only if its victim survives, and waits for the next
violence bucket before either physical participant may act.

| Concern | Adventurer's Lair source/behavior | Smart MUD service/behavior | Status and repair/test |
|---|---|---|---|
| Combat initiation / membership / first action | Unverified; inspect `fight.c` `set_fighting`/`hit` | `CombatRuntimeService.engage_hostile_ability`; joins without swing | Repaired; spell tests |
| Automatic/player/NPC timing / wait | Unverified; inspect `perform_violence`, `WAIT_STATE` | heartbeat → `process_due_rounds` → `process_encounter_round` | Partial; round tests remain |
| Position, stun, target validity | Unverified; inspect `perform_violence`, `damage` | action-state checks before each resident turn | Partial; position suite remains |
| Physical hit/damage, damage types | Unverified; inspect `hit`, `damage` | canonical combat resolver | Existing behavior; reference verification pending |
| Natural/equipped/unarmed attacks | Unverified; inspect `attack_hit_text[]` | content profiles plus physical resolver | Partial; mapping regression suite remains |
| Severity/physical/miss/critical prose | Unverified; inspect `dam_message`, `damage_severity_tier` | resolver relative-HP prose | Partial; thresholds require C evidence |
| Spell/skill and terminal prose | Unverified; inspect `skill_message`, `mag_damage`, messages file | provenance-aware spell messages in combat runtime | Repaired; spell tests |
| Kill attribution/shutdown | Unverified; inspect `damage`, extraction | lifecycle/death runtime and encounter shutdown | Partial; avoid generic spell terminal prose |
| Browser async/Telnet/prompt ordering | Unverified; inspect `comm.c` | sequenced combat output packets / adapters | Partial; ordering tests remain |
| Corpse creation/timers/decay/contents/multiples | Unverified; inspect `limits.c`, config, `point_update`, messages | `create_corpse` / `process_corpse_decay` | Partial; reference timer conversion pending |

### Root-cause trace for `c magic fox`

`AbilityExecutionService._apply_damage_component()` created a combat request
with `source_type="ability"`; `CombatRuntimeService._execute_attack_direct()`
then temporarily installed an ability-named natural weapon and handed it to the
physical resolver.  The physical message resolver has a fist fallback, causing
Magic Missile damage itself to be rendered as a punch.  It was not a scheduler
round, stale async delivery, or a free physical opening attack.  The repair
marks spell requests structurally and selects spell narration before delivery;
surviving targets join combat separately without `_execute_attack()`.

# Resident Runtime Authority

Smart MUD now treats live gameplay state as resident memory first. SQLite remains the durable checkpoint and recovery store, not the authority consulted during ordinary combat commands or violence pulses.

## Tony Adventurer's Lair audit

The mandatory reference could not be cloned from this environment because GitHub HTTPS returned `CONNECT tunnel failed, response 403`; the public repository landing page was reachable through web search and confirms the Adventurer's Lair repository keeps runtime state outside version control. The implementation target is therefore the observed TBA-style resident model requested for this branch: `boot_db()` loads world records once, descriptors process input and queue output before heartbeat work, `perform_violence()` walks a resident `combat_list`, `set_fighting()` and `stop_fighting()` link/unlink resident character pointers, `hit()`/`damage()` mutate resident hit points and positions, `die()`/`raw_kill()`/`make_corpse()` perform bounded death cleanup, `point_update()` and autosave periodically save dirty characters, and normal combat never reloads rooms, mobs, objects, or round state from disk.

## Authority matrix

| Subsystem | Current runtime authority | Desired runtime authority | Persistence authority | Live SQLite path | Dirty/flush/recovery |
| --- | --- | --- | --- | --- | --- |
| World package, rooms, zones, areas | `MudRuntime.active_world` and registries | `ResidentWorldRuntime`-style loaded generation | World package files plus materialization tables | Selection/materialization only | World load once; restart reloads package |
| Entity templates, item templates | World registries | Immutable resident projections | World package | None in combat | Rebuild at world generation only |
| NPC actors | `CombatRuntimeService.resident_actors` | One resident `Actor` per live NPC | `entity_instances` checkpoints | No ordinary violence reads/writes | Dirty entity set; death/logout/shutdown flush |
| Player actors | `active_characters` plus resident actor | One resident `Actor` per online character | `characters`/`character_stats` | Login/save only | Dirty character coalescing; autosave/logout flush |
| Resources, position, lifecycle | Resident `Actor.resources` and `combat_profile` | Resident actor | Character/entity checkpoint rows | No ordinary damage writes | Mark actor dirty; death immediate transaction |
| Encounters, participants, targets, queued actions, waits, rounds | `ResidentCombatEncounter` and `ResidentCombatParticipant` | Resident encounter index | Combat tables are checkpoint/audit/legacy | No normal round discovery reads | Dirty encounters and audit buffers; completion flush |
| Combat output, prompts, condition | In-memory output queues | In-memory ordered packets | Optional scrollback later | No pre-delivery writes | Drain via async messages; optional deferred history |
| Corpses, loot, rewards, quests | Runtime lifecycle services | Resident death transition until durable boundary | SQLite durable transaction | Lethal transition only | Idempotent death/reward/corpse transaction |
| Resets | Runtime materialization services | Resident world reset profiles | Materialization audit rows | Boot/reset only | Restart can reconcile from durable rows |

## Resident world, actor, encounter, and participant architecture

`CombatRuntimeService` owns resident active combat maps and actors. Encounter rounds, participant targets, queued actions, wait pulses, contribution damage, and audit buffers live in memory. `Actor` now carries resident generation/source/owner/version metadata, and duplicate registry registration is rejected so projections cannot become competing live authorities.

## Hot-path SQLite inventory

The KILL critical path is constrained to session lookup, resident target lookup, resident encounter creation, opening attack, resident resource mutation, output packet construction, prompt snapshot, and dirty marking. The violence path begins from resident encounters and resident participants. It does not query SQLite for active encounters, participants, targets, current round, queued actions, wait state, or combat status.

## Zero-SQL invariant

After world readiness, actor hydration, and encounter creation, ordinary nonlethal violence rounds must have: zero connections, zero statements, zero commits, zero lock waits, zero character loads/saves, zero NPC hydration reads, zero entity damage writes, zero output writes, zero round-number reads, and zero action-queue operations. Compatibility combat tables remain as checkpoint/audit/legacy tables only.

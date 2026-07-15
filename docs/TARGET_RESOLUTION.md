
## Phase 15B.11 resident room occupancy

Living NPC room rendering and combat target resolution now share `MudRuntime.resident_occupants_by_room`, backed by `CombatRuntimeService.resident_actors` and entity-instance/actor-id maps. Normal KILL/ATTACK/CONSIDER/DIAGNOSE target lookup is resident-memory only: no `refresh_content()`, world reload, entity rematerialization, or SQLite target query is used in the command hot path. See `docs/RESIDENT_ROOM_OCCUPANCY.md` for the authority table, target grammar, lifecycle invariants, diagnostics, and Windows acceptance steps.

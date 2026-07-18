# Phase 18H Ability Truth Audit

## Mandatory invariant

If `skills` or `spells` displays an ability, the same character must be able to route that same ability through the canonical ability gateway. The only valid outcomes are successful execution or `HANDLER_NOT_IMPLEMENTED`. Displayed abilities must not produce `Unknown spell`, `Unknown ability`, or `You do not know <ability>`.

## Magic Missile lifecycle trace

1. **Character creation**: `MudRuntime.create_character` saves the new `MudCharacter`, spawns starter items, and calls `_ensure_starter_progression`.
2. **Class assignment**: character creation persists the selected class on character actor data and progression state; `_ensure_starter_progression` reconciles the persisted progression identity.
3. **Ability grant**: starter class abilities are learned into `actor_ability_progression` by progression reconciliation. Legacy universal starter rows with `source_type=starter_character` are retired when not in the canonical class set.
4. **Persistence**: learned class abilities persist in `actor_ability_progression`; transient/admin grants may also exist in `actor_ability_grants`.
5. **Runtime loading**: command-time character loading calls `register_live_character`, which refreshes the shared runtime actor registry used by ability execution.
6. **Progression state**: progression owns class/race/track identity and authored starter learning; it does not decide command-time ability knowledge.
7. **Known ability service**: `AbilityExecutionService.list_known_abilities()` is the canonical learned projection. It merges active grants, active progression rows, and live actor plugin grants across both `character_id` and `character:<id>` aliases, then filters out missing/disabled definitions.
8. **`spells` display**: `AbilityDisplaySnapshotService` reads only the canonical service and filters to enabled spell definitions.
9. **`cast`**: command parsing resolves spell tokens, then execution enters `AbilityRuntimeGateway.execute`; known checks happen in the gateway through the canonical service.
10. **`spellup`**: player spellup now lists eligible known spells from the canonical service and executes each through the same gateway.
11. **Ability gateway**: `AbilityRuntimeGateway` separates definition resolution, known resolution, category validation, handler detection, and execution.
12. **Execution**: `AbilityExecutionService.start_ability` / `execute_instant_ability` validates with `trace_ability`, whose grant confirmation uses the canonical known service.

## Duplicate sources found

- `spells`/`skills` could fall back to `_ability_rows(character)`, a formatting/projection path separate from gateway execution.
- `cast` used spell token resolution with `require_known=True` and returned command-layer `Unknown spell` / `You do not know` before the gateway could classify the failure.
- `spellup` had an old role permission gate and then executed directly through `execute_instant_ability`, bypassing the public gateway contract.
- `trace_ability` separately queried `_grants` and `actor_ability_progression`, duplicating the learned check already performed by display/gateway paths.
- Live runtime actors sometimes use `character:<id>` while progression rows may use the durable character id; repeated fallback lookups made divergence possible.

## Canonical service contract

`AbilityExecutionService` now exposes the canonical learned ability API:

- `list_known_abilities(actor_id, ability_type=None)`
- `list_known_spells(actor_id)`
- `list_known_skills(actor_id)`
- `knows(actor_id, ability_id)`
- `find_known(actor_id, query, ability_type=None)`
- `find_known_spell(actor_id, query)`
- `find_known_skill(actor_id, query)`

`get_actor_abilities()` remains as a compatibility wrapper around `list_known_abilities()` and is not a separate truth source.

## Consumers repaired

- `skills`
- `spells`
- `cast` / `c`
- direct skill/ability commands
- combat queued ability prefix resolution
- `spellup`
- gateway spell/name resolution
- gateway execution known checks
- `trace_ability` grant confirmation
- future callers using `can_use_ability`, `validate_ability_use`, or `gateway()`

## Display contract

Display rows are now emitted only when the actor legitimately knows the ability and the ability definition exists and is enabled. Orphan grants, missing definitions, disabled definitions, and invalid IDs are filtered inside the canonical service.

## Runtime reload finding

The repeated `Loaded character` logs during display commands are caused by command/runtime paths that reload persisted characters to build safe projections and validation context. Phase 18H reduces ability display divergence by using the live ability service projection instead of formatting fallbacks, but a broader projection-hydration cleanup remains recommended.

## Remaining issues

- `practice` and `study` should be kept on the same canonical service in future training UI work if additional lookup helpers are added there.
- Some legacy docs/tests still refer to `get_actor_abilities`; that method is intentionally retained as a wrapper.
- Runtime display validation may still load character state for posture/room checks; this is not a learned-ability truth issue but should be optimized.

## Recommendation for Phase 19A

Create a runtime actor/projection hydration pass that removes display-command persistence reloads, then make training/practice/study expose explicit `find_known_*` calls instead of local name matching wherever any remain.

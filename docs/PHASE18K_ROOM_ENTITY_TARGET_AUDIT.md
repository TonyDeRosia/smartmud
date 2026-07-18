# Phase 18K Room Entity Target Audit

The production forest wolf is authored as template `forest_wolf` and spawned by `emberwood_spawn_10_forest_wolf_emberwood_hunting_trail` into room `emberwood_hunting_trail`. Materialization creates a durable runtime `entity_instances.entity_id` / `instance_id` such as `ent_*` with actor id `entity:<instance_id>`.

Before this phase, room rendering enumerated resident room occupants populated from materialized entity instances, while ability target resolution enumerated only the `AbilityExecutionService` actor registry. NPC resident actors were present in `CombatRuntimeService.resident_actors` and in room occupancy, but were not registered into the shared `ActorRegistry` used by abilities. Therefore `look` could render `A forest wolf prowls near the brush.` from the resident room view, while `c magic wolf` could not find the wolf in ability targeting and returned `Invalid target.`

After this phase, `MudRuntime.register_resident_entity_actor()` registers each materialized NPC/mob actor with the shared `ActorRegistry` and rebinds ability service actor mappings to that registry. Renderer collection and target resolver collection now share the same actor instance id: `entity:<instance_id>`.

Canonical metadata:

- Template ID: `forest_wolf`.
- Spawn ID: `emberwood_spawn_10_forest_wolf_emberwood_hunting_trail` for the smoke path.
- Runtime instance ID: durable `ent_*` from `entity_instances`.
- Actor type: `mob`/`npc` resident Actor adapted from the entity instance.
- Room ID: `emberwood_hunting_trail`.
- Renderer source: `MudRuntime.find_visible_entities()` over `resident_occupants_by_room`.
- Target resolver source: shared `ActorRegistry` through `AbilityExecutionService.actors`.
- Combat/damage recipient: the same `CombatRuntimeService.resident_actors['entity:<instance_id>']` actor.
- Visibility: same-room, alive, not hidden/invisible by entity state flags.
- Keywords: authored `wolf`, `forest wolf`, `canine`; display name `Forest Wolf`.
- Alive state: `state.is_alive` and positive current health.
- Targetable flag: authored `combat_policy.attackable` / attackable tag.
- Persistence ownership: `entity_instances` and `content_materializations` own durable identity; resident maps cache active-session membership.

Campsites are Smart MUD-authored runtime objects, not TBA legacy objects. `Set Camp` creates a stable campsite runtime object through `SurvivalNeedsService` and item-instance rendering displays that object by id. Reset behavior remains governed by survival object expiration/replacement policy; broad room reset integration is deferred.

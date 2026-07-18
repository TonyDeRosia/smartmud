# World Runtime Entity Model

Smart MUD distinguishes authored templates, spawn declarations, runtime instances, render entries, and resolved targets.

- Template: authored blueprint such as `forest_wolf`.
- Spawn declaration: rule placing a template in a room, such as `emberwood_spawn_10_forest_wolf_emberwood_hunting_trail`.
- Runtime instance: durable `entity_instances` row with stable `instance_id`.
- Render entry: presentation derived from that runtime instance.
- Target: resolved reference to the same runtime actor / instance id.

Live room membership is canonical in `resident_occupants_by_room`, backed by each Actor's `identity.current_location`. Rendering and targeting must query this membership instead of static `room.npcs` declarations. Static room declarations are only legacy seed inputs for materialization.

Visibility and targetability use same-room membership, alive/dead state, hidden/invisible flags, authored keywords, and combat policy. Exact name/id/keyword matches are evaluated before unambiguous prefix matches; ambiguous matches are reported instead of selecting the first occupant. Numbered forms such as `2.wolf` are supported by keyword resolution.

## Phase 18K canonical room entities and targets

Smart MUD distinguishes authored templates, spawn declarations, runtime instances, render entries, and resolved targets. `forest_wolf` is a template; `emberwood_spawn_10_forest_wolf_emberwood_hunting_trail` is a spawn declaration; durable `entity_instances` rows are runtime instances; room render lines are presentation derived from those instances; and combat/spell targets resolve back to the same `entity:<instance_id>` Actor.

Live room membership is canonical in `resident_occupants_by_room`, backed by each Actor's `identity.current_location`. Rendering and targeting must query this membership instead of static `room.npcs` declarations. Static room declarations are only legacy seed inputs for materialization.

Visibility and targetability use same-room membership, alive/dead state, hidden/invisible flags, authored keywords, and combat policy. Exact name/id/keyword matches are evaluated before unambiguous prefix matches; ambiguous matches are reported instead of selecting the first occupant. Numbered forms such as `2.wolf` are supported by keyword resolution.

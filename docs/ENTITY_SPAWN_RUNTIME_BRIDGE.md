# Entity Spawn Runtime Bridge

Entity templates remain definitions. Spawn declarations and legacy default-room declarations materialize SQLite `entity_instances` once and record instance IDs in `content_materializations`. Entity `plugin_data.ai_profile` is preserved as deterministic future-AI metadata; no AI behavior or generation is performed.


## Canonical vs legacy precedence

Phase 5A makes legacy NPC declarations compatibility and diagnostic sources only. Legacy room NPC arrays and entity-template default rooms normalize into deterministic canonical spawn declarations, materialize into SQLite `entity_instances`, and then normal rendering, targeting, dialogue, look, scan, search, and movement-room rendering consume runtime instances only. Builder diagnostics may still show templates, spawns, legacy declarations, and materialization records separately.

Canonical spawns supersede equivalent legacy declarations by world, room, template, and compatible quantity. Display-name deduplication is not allowed because legitimate same-name runtime instances must remain visible. Upgraded databases adopt one matching existing runtime row into the materialization record and report ambiguous extras as duplicate candidates instead of deleting or hiding them.

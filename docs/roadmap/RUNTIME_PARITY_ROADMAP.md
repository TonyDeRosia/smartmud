# Runtime Parity Roadmap — Phase 16A

## Next ten narrow implementation phases

### Phase 16B — Persistent exit and door state parity
- Primary runtime capability: closed/locked/keyed exits and reset-aware movement.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16C — Container runtime parity
- Primary runtime capability: put/take/nested/capacity/locked containers.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16D — Object consumption and lights
- Primary runtime capability: food/drink/fountains/lights/poison.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16E — Object magic dispatcher
- Primary runtime capability: scrolls/potions/wands/staves.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16F — Corpse loot and decay parity
- Primary runtime capability: death containers, looting, sacrifice.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16G — Reset dependency executor
- Primary runtime capability: M/O/G/E/P/D semantics and diagnostics.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16H — Mobile aggression and scavenging
- Primary runtime capability: NPC autonomous baseline behavior.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16I — Special procedure adapter
- Primary runtime capability: shop/bank/spec behavior modernization.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16J — Practice and skill improvement
- Primary runtime capability: practice, trainers, proficiency growth.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

### Phase 16K — DG trigger foundation
- Primary runtime capability: safe declarative trigger runtime.
- Why it comes next: dependency ordered from movement/world-state foundation through object interaction and behavior hooks.
- Adventurer's Lair references: `src/act.movement.c`, `src/act.item.c`, `src/fight.c`, `src/db.c`, `src/structs.h`, `src/dg_*.c`, and specialized modules named by the parity matrix.
- Smart MUD files likely involved: `engine/mud_runtime.py`, `engine/mud_commands.py`, `engine/zone_resets.py`, `engine/combat_runtime.py`, `engine/abilities.py`, and canonical service modules named in the matrix.
- Canonical services to reuse: MudRuntime, EventBus, world registry, item instance APIs, EconomyService/RewardService/AbilityService when relevant.
- New service: only if the existing owner cannot hold the canonical runtime state without duplication.
- Explicit scope: one runtime capability, focused command adapters, persistence/events, tests, and documentation updates.
- Explicit exclusions: broad Builder UI, visual Builder, AI Builder, unrelated gameplay, stock-TBA assumptions, and direct C architecture translation.
- Data changes: conservative migrations only where needed for canonical runtime state.
- Commands affected: only commands for this capability.
- Builder implications: record dependency; do not add broad Builder surfaces until runtime behavior is canonical.
- Focused tests: command success/failure, persistence, event publication, validation, and source-specific edge cases.
- Manual acceptance scenario: exercise the verb in live runtime, restart when persistence matters, and verify no duplicate/Builder-only behavior.
- Completion standard: Adventurer's Lair behavior that is in scope is reproduced through Smart MUD services and covered by tests.

## Parity milestones

### Milestone 1 — Foundation correctness
Purpose: close movement, world-state, persistence, reference-resolution, and validation gaps. Dependencies: none. Excludes broad Builder UI. Acceptance: doors, reset state, and references behave on production paths. Estimated phases: 3-5.

### Milestone 2 — Core object and world interaction
Purpose: containers, object-use dispatch, decay/timers, portable/nonportable semantics. Dependencies: Milestone 1. Estimated phases: 4-6.

### Milestone 3 — Character conditions and affects
Purpose: conditions, affects, saves, regeneration, poison/disease/intoxication. Dependencies: object-use and stat services. Estimated phases: 3-5.

### Milestone 4 — NPC behavior and special procedures
Purpose: mobile AI, special procedures, aggression, scavenging, hunting, shopkeeper/banker modernization. Dependencies: world-state, combat, economy. Estimated phases: 5-8.

### Milestone 5 — Magic and skills
Purpose: practice, proficiency, casting, saves, spell objects, persistent effects. Dependencies: affects and object-use. Estimated phases: 5-8.

### Milestone 6 — Economy and player services
Purpose: finish shops, banks, rent/storage, boards/mail parity. Dependencies: item persistence and economy. Estimated phases: 3-6.

### Milestone 7 — Quests, factions, and organizations
Purpose: scriptable progression, quest logs, reputation, clans/guilds. Dependencies: trigger foundation and services. Estimated phases: 4-7.

### Milestone 8 — Environment and persistent world simulation
Purpose: time/weather/light/sectors/hunger/thirst/environmental damage. Dependencies: world-state. Estimated phases: 3-5.

### Milestone 9 — Builder exposure completion
Purpose: expose canonical runtime capabilities in MEDIT/OEDIT/REDIT/ZEDIT/AEDIT/shop/script/quest editors. Dependencies: runtime services. Estimated phases: 8-12.

### Milestone 10 — Visual desktop Builder
Purpose: visual editing over canonical operations. Dependencies: Builder exposure completion.

### Milestone 11 — AI-assisted Builder
Purpose: AI generation constrained by canonical validation. Dependencies: stable Builder APIs.

### Milestone 12 — Beyond-TBA simulation and platform capabilities
Purpose: intentionally exceed Adventurer's Lair after parity foundations are safe.

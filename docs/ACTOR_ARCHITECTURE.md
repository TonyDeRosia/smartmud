# Actor Architecture

Actor identity, resources, score presentation, effects, progression, property access, and living-world hooks are separate from survival mechanics. Phase 11D2 routes hunger, thirst, fatigue, rest, sleep, campfires, and campsites through the canonical `engine.survival_needs.SurvivalNeedsService` and SQLite actor need/rest tables rather than adding a second player or NPC needs engine.

Rest and sleep recover canonical actor need state over world time. EnvironmentService and PropertyService remain authoritative for shelter, weather, light, temperature, and private access context.

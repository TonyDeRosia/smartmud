# COMBAT_SYSTEM.md


## Phase 11B Perception Integration

Phase 11B adds `engine.perception.PerceptionService` as the single sensory boundary for stealth, concealment, search, tracking, scent, sound, trails, and observer knowledge. It queries canonical services, especially `EnvironmentService`, and stores restart-safe sensory state in SQLite.

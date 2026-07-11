# VISION AND VISIBILITY

Phase 11A routes this topic through the canonical `EnvironmentService` documented in `docs/ENVIRONMENT_SYSTEM.md`. Builder-authored content lives in `worlds/<world_id>/<collection>/<collection>.json` and mirrored draft files under `worlds/<world_id>/builder`. Runtime state is SQLite-authoritative for weather, runtime lights, exposure, and overrides.


## Phase 11B Perception Integration

Phase 11B adds `engine.perception.PerceptionService` as the single sensory boundary for stealth, concealment, search, tracking, scent, sound, trails, and observer knowledge. It queries canonical services, especially `EnvironmentService`, and stores restart-safe sensory state in SQLite.

# Campfires

Phase 11D2 campfires are temporary runtime objects owned by `SurvivalNeedsService` and stored in `campfire_instances`, with idempotent fuel records in `campfire_fuel_events`. Profiles live in `campfire_profiles` and reference EnvironmentService light-source profile IDs rather than creating a second light engine.

Commands include `light campfire`, `extinguish campfire`, `add fuel`, and `inspect campfire`. Starter content provides `basic_campfire` with conservative heat, light, duration, and rest-quality modifiers.

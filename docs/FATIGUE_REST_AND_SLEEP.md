# Fatigue, Rest, and Sleep

Phase 11D2 extends the canonical `engine.survival_needs.SurvivalNeedsService` with persistent SQLite rest and sleep sessions. Runtime authority lives in `actor_rest_sessions` and `rest_session_results`; fatigue recovery is world-time based, bounded, idempotent, and uses the same actor need state as hunger and thirst.

Player commands include `rest`, `rest here`, `rest status`, `stop resting`, `sleep`, `sleep here`, `sleep on <target>`, `sleep status`, and `wake`. Rest reduces fatigue over world time but does not replace sleep. Sleep uses rest-location profiles, rest quality, shelter context, and future-safe access hooks for EnvironmentService and PropertyService.

Manual acceptance: run `needs`, `fatigue`, `rest`, advance world time through `needstick 60`, verify fatigue improves, then move or `stop resting` to interrupt. Run `sleep on basic_bed`, `sleep status`, restart the runtime, confirm the session persists, then `wake`.

# Survival Environment Integration

`SurvivalNeedsService.get_shelter_context(actor_id)` is the integration boundary for indoor/outdoor state, shelter, temperature, precipitation, wind, exposure, property access, private-room access, and inn-room state. EnvironmentService remains authoritative; SurvivalNeedsService only consumes context and applies conservative rest-quality and recovery modifiers.

Campfire profiles reference canonical light-source profile IDs and expose heat/rest modifiers for EnvironmentService integration without a second light engine.

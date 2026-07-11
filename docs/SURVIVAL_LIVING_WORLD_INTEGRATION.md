# Survival Living World Integration

LivingWorldService and future NPC goal code can query `get_actor_needs_context`, `get_rest_context`, `get_consumable_context` (via consumption previews), and `get_shelter_context`. These hooks expose structured data without allowing NPCs to bypass item ownership, property access, or canonical runtime sessions.

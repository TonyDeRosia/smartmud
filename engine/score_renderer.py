"""Modular Adventurer's-Lair-style score sheet rendering for Actors."""

from __future__ import annotations

from typing import Any, Callable

from engine.actors import Actor, FormulaRegistry
from engine.mud_displays import semantic

ADMIN_SECTIONS = {"builder_diagnostics", "ai_diagnostics"}


def _line(label: str, value: Any, role: str = "score_value") -> str:
    return f"{semantic('score_label', label + ':'):<0} {semantic(role, value)}"


def _header(title: str) -> str:
    return "\n".join([
        semantic('system', '============================================================================'),
        semantic('score_label', title),
        semantic('system', '----------------------------------------------------------------------------'),
    ])



class ActorScoreRenderer:
    """Single modular renderer for full score and independently renderable sections."""

    order = [
        "identity", "resources", "primary_attributes", "derived_attributes", "combat", "equipment",
        "conditions", "affects", "resistances", "progression", "currencies", "relationships",
        "simulation", "builder_diagnostics", "ai_diagnostics",
    ]

    aliases = {
        "score": "all", "attrs": "primary_attributes", "attributes": "primary_attributes",
        "derived": "derived_attributes", "resources": "resources", "combat": "combat",
        "equipment": "equipment", "identity": "identity", "affects": "affects",
        "diagnostics": "builder_diagnostics", "builder": "builder_diagnostics", "ai": "ai_diagnostics",
    }

    def __init__(self, formula_registry: FormulaRegistry | None = None):
        self.formula_registry = formula_registry or FormulaRegistry.default()
        self._renderers: dict[str, Callable[[Actor, bool], str]] = {
            name: getattr(self, f"render_{name}") for name in self.order
        }

    def render(self, actor: Actor, section: str = "all", *, admin: bool = False) -> str:
        section = self.aliases.get(section, section)
        if section != "all":
            if section in ADMIN_SECTIONS and not admin:
                return "That score section is restricted to administrators and Builders."
            return self.render_section(actor, section, admin=admin)
        sections = [s for s in self.order if admin or s not in ADMIN_SECTIONS]
        return "\n".join(self.render_section(actor, s, admin=admin) for s in sections)

    def render_section(self, actor: Actor, section: str, *, admin: bool = False) -> str:
        if section not in self._renderers:
            return f"Unknown score section: {section}"
        if section in ADMIN_SECTIONS and not admin:
            return "That score section is restricted to administrators and Builders."
        return self._renderers[section](actor, admin)

    def render_identity(self, actor: Actor, admin: bool = False) -> str:
        i = actor.identity
        rows = [_header("Identity")]
        for label, value in [
            ("Name", i.name), ("Title", i.title or "None"), ("Description", i.description or "None"),
            ("Race", i.race), ("Class", i.class_placeholder), ("Profession", i.profession_placeholder),
            ("Guild", i.guild), ("Clan", i.clan), ("Religion", i.religion), ("Alignment", i.alignment),
            ("Gender", i.gender), ("Age", i.age if i.age is not None else "Unknown"), ("Height", i.height),
            ("Weight", i.weight), ("Languages", ", ".join(i.languages) or "None"),
            ("Speaking", i.speaking_language), ("Position", i.position), ("Location", i.current_location),
            ("Zone", i.current_zone), ("Area", i.current_area), ("World", i.current_world),
        ]:
            rows.append(_line(label, value, "player" if label == "Name" else "score_value"))
        return "\n".join(rows)

    def render_resources(self, actor: Actor, admin: bool = False) -> str:
        r = actor.resources
        rows = [_header("Resources")]
        rows += [
            _line("Health", f"{r.health}/{r.maximum_health}", "hp"), _line("Mana", f"{r.mana}/{r.maximum_mana}", "mp"),
            _line("Movement", f"{r.movement}/{r.maximum_movement}"), _line("Stamina", f"{r.stamina}/{r.maximum_stamina}", "stamina"),
            _line("Hunger", r.hunger), _line("Thirst", r.thirst), _line("Fatigue", r.fatigue), _line("Drunkenness", r.drunkenness),
            _line("Warmth", r.warmth), _line("Body Temperature", r.body_temperature), _line("Corruption", r.corruption),
            _line("Sanity", r.sanity), _line("Oxygen", r.oxygen),
        ]
        return "\n".join(rows)

    def render_primary_attributes(self, actor: Actor, admin: bool = False) -> str:
        return "\n".join([_header("Primary Attributes")] + [_line(k.replace("_", " ").title(), v if v is not None else "Missing") for k, v in actor.attributes.items()])

    def render_derived_attributes(self, actor: Actor, admin: bool = False) -> str:
        rows = [_header("Derived Attributes (Formula Placeholders)")]
        for stat in actor.derived_statistics_cache.values():
            value = "not calculated" if stat.value is None else stat.value
            rows.append(_line(stat.label, f"{value} [{stat.formula_name}]"))
        return "\n".join(rows)

    def render_combat(self, actor: Actor, admin: bool = False) -> str:
        return "\n".join([_header("Combat")] + [_line(k.replace("_", " ").title(), v) for k, v in actor.combat_profile.items()])

    def render_equipment(self, actor: Actor, admin: bool = False) -> str:
        eq = actor.equipment_profile.get("equipped", actor.equipment_profile) or {}
        if not eq: return _header("Equipment") + "\n" + semantic("system", "You are not wearing anything.")
        return "\n".join([_header("Equipment")] + [_line(str(k).replace("_", " ").title(), (v or {}).get("name", "nothing") if isinstance(v, dict) else v, "equipment_item") for k, v in eq.items()])

    def render_conditions(self, actor: Actor, admin: bool = False) -> str:
        return self._dict_section("Conditions", actor.condition_profile)
    def render_affects(self, actor: Actor, admin: bool = False) -> str:
        return self._dict_section("Affects", actor.effect_container.get("affects", actor.effect_container), empty="You have no active affects.")
    def render_resistances(self, actor: Actor, admin: bool = False) -> str:
        return self._dict_section("Resistances", actor.resistance_profile)
    def render_progression(self, actor: Actor, admin: bool = False) -> str:
        return self._dict_section("Progression", actor.progression_profile)
    def render_currencies(self, actor: Actor, admin: bool = False) -> str:
        return self._dict_section("Currencies", actor.plugin_data.get("currencies", {}))
    def render_relationships(self, actor: Actor, admin: bool = False) -> str:
        return self._dict_section("Relationships", actor.relationship_profile)
    def render_simulation(self, actor: Actor, admin: bool = False) -> str:
        return self._dict_section("Simulation", actor.simulation_profile)
    def render_ai_diagnostics(self, actor: Actor, admin: bool = False) -> str:
        return self._dict_section("AI Diagnostics", {"needs": actor.need_profile, "goals": actor.goal_profile, "memory": actor.memory_profile}, empty="No AI decision system is implemented in this phase.")

    def render_builder_diagnostics(self, actor: Actor, admin: bool = False) -> str:
        warnings = []
        if not actor.identity.name or actor.identity.name == "Unnamed": warnings.append("Missing identity.name")
        missing = [k for k, v in actor.attributes.items() if v is None]
        if missing: warnings.append("Missing base attributes: " + ", ".join(missing))
        formulas = {s.formula_name: self.formula_registry.has(s.formula_name) for s in actor.derived_statistics_cache.values()}
        return self._dict_section("Builder Diagnostics", {
            "actor_id": actor.actor_id, "actor_type": actor.actor_type, "base_values": actor.attributes,
            "derived_placeholders": list(actor.derived_statistics_cache), "future_formula_names": formulas,
            "validation_warnings": warnings or ["none"], "metadata": actor.builder_metadata,
        })

    def _dict_section(self, title: str, data: dict[str, Any], empty: str = "No data recorded.") -> str:
        if not data:
            return _header(title) + "\n" + semantic("system", empty)
        return "\n".join([_header(title)] + [_line(str(k).replace("_", " ").title(), v) for k, v in data.items()])

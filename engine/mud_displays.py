"""Python-native Smart MUD display builders.

These helpers return terminal-oriented MUD text. They intentionally avoid web-card
markup so the browser, desktop shell, and tests can render the same semantic text.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

EQUIPMENT_SLOTS = ["Light","Head","Face","Neck","Body","About Body","Arms","Wrist","Hands","Finger","Waist","Legs","Feet","Wielded","Offhand","Held","Shield","Back"]

def _title(v: Any, default: str = "Unknown") -> str:
    s = str(v or "").replace("_", " ").strip()
    return s.title() if s else default

def _gold(runtime: Any) -> int:
    return int(((getattr(runtime, "inventory_state", {}) or {}).get("currency", {}) or {}).get("gold", 0) or 0)

def _entries(runtime: Any) -> list[dict[str, Any]]:
    return list((getattr(runtime, "inventory_state", {}) or {}).get("entries", []) or [])

def character_context(state: Any, world: Any, room: dict[str, Any]) -> dict[str, Any]:
    core = getattr(getattr(state, "structured_state", None), "runtime", None).player_core if getattr(getattr(state, "structured_state", None), "runtime", None) else {}
    core = core or {}; derived = core.get("derived_stats", {}) or {}; stats = core.get("stats", {}) or getattr(state.player, "classic_attributes", {}) or {}
    runtime = state.structured_state.runtime
    level = int(getattr(state.player, "level", 1) or 1); xp = int(getattr(state.player, "xp", 0) or 0)
    return {"id": getattr(state.player, "id", "player_1") or "player_1", "name": getattr(state.player, "name", "Adventurer"), "title": core.get("title") or f"the {getattr(state.player, 'char_class', 'Adventurer')}", "race": _title(core.get("race_id") or core.get("race") or "human"), "class": getattr(state.player, "char_class", "Adventurer"), "level": level, "room": room.get("name", "Unknown Room"), "hp": getattr(state.player, "hp", 0), "max_hp": getattr(state.player, "max_hp", 0), "mana": getattr(state.player, "energy_or_mana", 0), "max_mana": getattr(state.player, "energy_or_mana", 0), "stamina": derived.get("Stamina", 0), "max_stamina": derived.get("Stamina", 0), "xp": xp, "tnl": max(0, level * 1000 - xp), "gold": _gold(runtime), "armor": derived.get("Armor", derived.get("AC", 10)), "hitroll": derived.get("Hitroll", 0), "damroll": derived.get("Damroll", 0), "stats": stats, "entries": _entries(runtime), "abilities": list(getattr(runtime, "abilities", []) or []), "affects": list(getattr(runtime, "active_affects", []) or []), "role": core.get("role") or "player", "description": core.get("description") or getattr(state.player, "description", "") or "No description set.", "last_played": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

def score(ctx: dict[str, Any]) -> str:
    stats = ctx.get("stats") or {}; affects = ctx.get("affects") or []; abilities = ctx.get("abilities") or []; inv = ctx.get("entries") or []
    lines = [f"{ctx['name']} {ctx['title']}", f"Race: {ctx['race']}  Class: {ctx['class']}  Level: {ctx['level']}", f"Room: {ctx['room']}", f"HP: {ctx['hp']}/{ctx['max_hp']}  MP: {ctx['mana']}/{ctx['max_mana']}  Stamina: {ctx['stamina']}/{ctx['max_stamina']}", f"XP: {ctx['xp']}  TNL: {ctx['tnl']}  Gold: {ctx['gold']}", f"Armor: {ctx['armor']}  Hitroll: {ctx['hitroll']}  Damroll: {ctx['damroll']}", "Stats: " + (", ".join(f"{k} {v}" for k,v in stats.items()) if stats else "unrecorded"), f"Carry Weight: {sum(int(e.get('weight',0) or 0)*int(e.get('quantity',1) or 1) for e in inv)}  Inventory Count: {sum(int(e.get('quantity',1) or 1) for e in inv)}", "Active Affects: " + (", ".join(str(a.get('name', a)) for a in affects) if affects else "none"), "Known Abilities: " + (", ".join(str(a.get('name', a.get('id','ability')) if isinstance(a,dict) else a) for a in abilities[:8]) if abilities else "none")]
    return "Score Sheet\n" + "\n".join(lines)

def worth(ctx: dict[str, Any]) -> str:
    rep = ctx.get("reputation")
    lines = ["Worth", f"Gold: {ctx['gold']}", f"XP: {ctx['xp']}", f"TNL: {ctx['tnl']}", f"Level: {ctx['level']}"]
    if rep is not None: lines.append(f"Reputation: {rep}")
    return "\n".join(lines)

def inventory(ctx: dict[str, Any]) -> str:
    entries = ctx.get("entries") or []
    if not entries: return "You are carrying nothing."
    counts = Counter((e.get("name") or e.get("item_id") or e.get("id") or "item") for e in entries for _ in range(int(e.get("quantity",1) or 1)))
    return "Inventory\n" + "\n".join(f"  {qty:>2} x {name}" for name, qty in sorted(counts.items()))

def equipment(ctx: dict[str, Any]) -> str:
    byslot = defaultdict(list)
    for e in ctx.get("entries") or []:
        slot = e.get("equipped_slot") or (e.get("slot") if e.get("equipped") else "")
        if slot: byslot[_title(slot)].append(e.get("name") or e.get("item_id") or "something")
    return "Equipment\n" + "\n".join(f"<{slot}> {', '.join(byslot.get(slot, [])) if byslot.get(slot) else 'Nothing'}" for slot in EQUIPMENT_SLOTS)

def finger(ctx: dict[str, Any], target: str = "", viewer_privileged: bool = False) -> str:
    lines = ["Finger", f"Name: {ctx['name']}", f"Title: {ctx['title']}", f"Race: {ctx['race']}  Class: {ctx['class']}  Level: {ctx['level']}", "Guild/World: Shattered Realms", f"Last Room: {ctx['room']}", f"Last Played: {ctx['last_played']}", f"Description: {ctx['description']}"]
    if viewer_privileged: lines.append(f"Staff Flag: {ctx.get('role','player')}")
    return "\n".join(lines)

def abilities(ctx: dict[str, Any], kind: str = "abilities") -> str:
    known = ctx.get("abilities") or []
    title = {"spells":"Spells", "skills":"Skills"}.get(kind, "Abilities")
    if not known: return f"{title}\n  You know no {kind} yet."
    rows=[]
    for a in known:
        if not isinstance(a, dict): a={"name": str(a)}
        if kind == "spells": rows.append(f"  {a.get('name', a.get('id','spell')):<22} Cost {a.get('cost', a.get('mana_cost','?')):<3} School {a.get('school','general'):<10} Cooldown {a.get('cooldown','none')}")
        elif kind == "skills": rows.append(f"  {a.get('name', a.get('id','skill')):<24} Rank {a.get('rank', a.get('proficiency','novice'))}")
        else: rows.append(f"  {a.get('name', a.get('id','ability'))}")
    return title + "\n" + "\n".join(rows)

def affects(ctx: dict[str, Any]) -> str:
    aff = ctx.get("affects") or []
    return "Affects\n" + ("\n".join(f"  {a.get('name', a)} - {a.get('duration','unknown duration') if isinstance(a,dict) else 'unknown duration'}" for a in aff) if aff else "  You are affected by nothing unusual.")

def commands(commands_by_cat: dict[str, list[str]]) -> str:
    return "Commands\n" + "\n".join(f"{cat}: {', '.join(sorted(vals))}" for cat, vals in sorted(commands_by_cat.items()))

def help_text(command: Any) -> str:
    return "Help: " + command.name + "\n" + f"Usage: {command.usage or command.name}\n" + (f"Aliases: {', '.join(command.aliases)}\n" if command.aliases else "") + (command.help or "No additional help.")

def simple(title: str, body: str) -> str: return f"{title}\n{body}"

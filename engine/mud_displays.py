"""Smart MUD display rendering engine with semantic color roles."""

from __future__ import annotations

from typing import Any, Optional

from dataclasses import dataclass, field
from enum import Enum

class DisplayIntent(str, Enum):
    ROOM = "ROOM"; TARGET_LOOK = "TARGET_LOOK"; TARGET_EXAMINE = "TARGET_EXAMINE"; IDENTIFY = "IDENTIFY"; READ = "READ"; LOOK_INSIDE = "LOOK_INSIDE"; LOOK_DIRECTION = "LOOK_DIRECTION"; EXITS = "EXITS"
    INVENTORY = "INVENTORY"; EQUIPMENT = "EQUIPMENT"; SCORE = "SCORE"; ATTRIBUTES = "ATTRIBUTES"; AFFECTS = "AFFECTS"; SKILLS = "SKILLS"; SPELLS = "SPELLS"; COOLDOWNS = "COOLDOWNS"; PROMPT = "PROMPT"; COMBAT_STATUS = "COMBAT_STATUS"; QUEST_STATUS = "QUEST_STATUS"
    ITEM_ACTION = "ITEM_ACTION"; MOVEMENT = "MOVEMENT"; POSTURE = "POSTURE"; COMMUNICATION = "COMMUNICATION"; SOCIAL = "SOCIAL"; SHOP = "SHOP"; BOARD = "BOARD"; QUEST = "QUEST"; TRAINER = "TRAINER"; CRAFTING = "CRAFTING"; GATHERING = "GATHERING"
    COMBAT = "COMBAT"; DEATH = "DEATH"; REWARD = "REWARD"; RESPAWN = "RESPAWN"; AMBIENT = "AMBIENT"
    HELP = "HELP"; WHO = "WHO"; WHERE = "WHERE"; SYSTEM = "SYSTEM"; SUCCESS = "SUCCESS"; WARNING = "WARNING"; ERROR = "ERROR"; ADMIN = "ADMIN"; BUILDER = "BUILDER"

@dataclass
class DisplayEntry:
    text: str
    role: str = "system"
    quantity: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class DisplaySection:
    title: str = ""
    lines: list[str] = field(default_factory=list)
    entries: list[DisplayEntry] = field(default_factory=list)
    fields: list[tuple[str, Any]] = field(default_factory=list)
    role: str = "system"

@dataclass
class DisplayDocument:
    intent: DisplayIntent | str
    title: str = ""
    semantic_role: str = "system"
    subtitle: str = ""
    paragraphs: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)
    sections: list[DisplaySection] = field(default_factory=list)
    footer: str = ""
    spacing: str = "major"
    renderer_hints: dict[str, Any] = field(default_factory=dict)
    debug_metadata: dict[str, Any] = field(default_factory=dict)

def normalize_sentence(text: Any) -> str:
    raw = re.sub(r"\s+", " ", str(text or "").strip())
    if not raw:
        return ""
    raw = re.sub(r"([.!?]){2,}$", r"\1", raw)
    if raw[-1] not in ".!?]>)\"\'":
        raw += "."
    return raw

def _render_entry_plain(entry: DisplayEntry) -> str:
    qty = f"{entry.quantity}x " if entry.quantity and entry.quantity > 1 else ""
    return qty + str(entry.text)

def render_display_plain(doc: DisplayDocument) -> str:
    blocks: list[str] = []
    if doc.title:
        blocks.append(str(doc.title).strip())
    if doc.subtitle:
        blocks.append(str(doc.subtitle).strip())
    para = [p.strip() for p in doc.paragraphs if str(p).strip()]
    if para:
        blocks.append("\n".join(para))
    if doc.lines:
        blocks.append("\n".join(str(x).rstrip() for x in doc.lines if str(x).strip()))
    for section in doc.sections:
        lines: list[str] = []
        if section.title:
            lines.append(str(section.title).strip())
        lines.extend(str(x).rstrip() for x in section.lines if str(x).strip())
        lines.extend(_render_entry_plain(e) for e in section.entries if str(e.text).strip())
        lines.extend(f"{k}: {v}" for k, v in section.fields)
        if lines:
            blocks.append("\n".join(lines))
    if doc.footer:
        blocks.append(str(doc.footer).strip())
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(b for b in blocks if b.strip())).strip()

def render_display_mud(doc: DisplayDocument) -> str:
    role = doc.semantic_role if doc.semantic_role in SEMANTIC_COLOR_ROLES else "system"
    text = render_display_plain(doc)
    if not text:
        text = "Nothing to show."
    # Keep headings/section text structurally plain; semantic tags carry color intent.
    return semantic(role, text)

def render_display_html(doc: DisplayDocument) -> str:
    return semantic_html(render_display_mud(doc))

def group_display_entries(items: list[dict[str, Any]], *, key_fields: tuple[str, ...] = ("name", "equipped_slot", "condition", "status")) -> list[DisplayEntry]:
    grouped: OrderedDict[tuple[Any, ...], DisplayEntry] = OrderedDict()
    for item in items:
        name = str(item.get("short_description") or item.get("name") or "something").strip()
        key = tuple(item.get(k) for k in key_fields) + (name,)
        if key not in grouped:
            grouped[key] = DisplayEntry(name, role="object", quantity=0, metadata={"instance_ids": []})
        grouped[key].quantity += int(item.get("stack_count") or 1)
        if item.get("instance_id"):
            grouped[key].metadata.setdefault("instance_ids", []).append(item.get("instance_id"))
    return list(grouped.values())

def build_inventory_document(items: list[dict[str, Any]], *, carrying: str = "") -> DisplayDocument:
    doc = DisplayDocument(DisplayIntent.INVENTORY, title="Inventory", semantic_role="system")
    if items:
        doc.sections.append(DisplaySection(lines=["You are carrying:"], entries=group_display_entries(items)))
    else:
        doc.paragraphs.append("You are not carrying anything.")
    if carrying:
        doc.sections.append(DisplaySection(title="Carrying", lines=[carrying]))
    return doc

def build_equipment_document(items: list[dict[str, Any]], slots: list[str]) -> DisplayDocument:
    by: dict[str, dict[str, Any]] = {}
    for item in items:
        for slot in str(item.get("equipped_slot") or "").split(","):
            if slot == "both_hands":
                by["main_hand"] = item; by["off_hand"] = item
            elif slot:
                by[slot] = item
    fields = [(slot.replace("_", " ").capitalize(), by[slot].get("name", "something") if slot in by else "nothing") for slot in slots]
    return DisplayDocument(DisplayIntent.EQUIPMENT, title="Equipment", semantic_role="system", paragraphs=[] if items else ["You are not wearing anything."], sections=[DisplaySection(fields=fields)])

def build_prompt_document(character: Any) -> DisplayDocument:
    parts = [f"{character.hp}/{character.max_hp} HP"]
    if getattr(character, "max_mana", 0): parts.append(f"{character.mana}/{character.max_mana} MP")
    if getattr(character, "max_stamina", 0): parts.append(f"{character.stamina}/{character.max_stamina} ST")
    return DisplayDocument(DisplayIntent.PROMPT, semantic_role="prompt", lines=["[" + " ".join(parts) + "]"])

import html
import re

from engine.mud_rendering import SEMANTIC_COLOR_ROLES, render_mud_color_html
from engine.conditions import condition_label
from collections import OrderedDict

_SEMANTIC_TAG_RE = re.compile(r"\{(/?)([a-z_]+)\}")

def semantic_html(text: str) -> str:
    """Convert trusted semantic role tags to safe HTML spans."""
    escaped = html.escape(str(text or ""))
    def repl(match: re.Match[str]) -> str:
        closing, role = match.group(1), match.group(2)
        if role not in SEMANTIC_COLOR_ROLES:
            return ""
        return "</span>" if closing else f'<span role="{html.escape(role)}">'
    return _SEMANTIC_TAG_RE.sub(repl, escaped).replace("\n", "<br>")

def semantic(role: str, text: Any) -> str:
    role = role if role in SEMANTIC_COLOR_ROLES else "system"
    return f"{{{role}}}{text}{{/{role}}}"


def _display_name(value: Any) -> str:
    """Return a player-facing title, never an internal id fallback unless unavoidable."""
    text = str(value or "").strip()
    if not text:
        return "Unknown Room"
    if "_" in text or text.islower():
        return text.replace("_", " ").title()
    return text


def _entity_text(entity: Any, *, compact: bool = True) -> tuple[str, str]:
    if isinstance(entity, dict):
        name = entity.get("name") or entity.get("title") or entity.get("id") or ""
        room_text = entity.get("room_description") or entity.get("short_description") or ""
        if compact and entity.get("entity_type") in {"npc", "mob", "player"}:
            state = str(entity.get("current_state") or (entity.get("state") or {}).get("current_state") or entity.get("movement_state") or "standing").lower()
            target = entity.get("combat_target_name") or (entity.get("state") or {}).get("combat_target_name")
            if target:
                text = f"{name} is here, fighting {target}."
            elif state in {"sleeping", "resting", "sitting"}:
                text = f"{name} is {state} here."
            elif state in {"stunned", "incapacitated", "unconscious"}:
                text = f"{name} is {state}."
            elif condition_label(entity) not in {"unharmed", "dead"}:
                text = f"{name} is here, {condition_label(entity)}."
            else:
                text = str(room_text or name)
        elif compact and entity.get("entity_type") == "corpse":
            text = entity.get("room_description") or entity.get("short_description") or name
        else:
            text = name if compact else (room_text or name)
        desc = entity.get("long_description") or entity.get("description") or ""
        return str(text).strip(), str(desc).strip()
    return str(entity).strip(), ""


def presence_group_key(entity: Any) -> tuple[Any, ...] | None:
    """Return a conservative room-presence grouping key, or None for unique lines."""
    if not isinstance(entity, dict) or entity.get("entity_type") == "player":
        return None
    state = entity.get("state") if isinstance(entity.get("state"), dict) else {}
    etype = entity.get("entity_type") or ("item" if entity.get("instance_id") else "")
    health = condition_label(entity)
    combat = state.get("combat_target_id") or state.get("combat_target_name")
    position = entity.get("current_state") or state.get("current_state") or entity.get("movement_state")
    owner = entity.get("owner_id") or entity.get("owner_type")
    lit = entity.get("status") or state.get("status") or state.get("lit")
    corpse_source = state.get("source_template_id") or state.get("source_entity_id") if etype == "corpse" else ""
    if combat or etype in {"corpse", "campfire", "campsite"}:
        return None
    return (etype, entity.get("template_id") or entity.get("id"), entity.get("name"), health, position, owner, lit, corpse_source)


def render_room(room: Any, colors: dict[str, str] | None = None, character: Any = None) -> str:
    """Render the canonical Smart MUD room block.

    Future room-changing systems (recall, goto, portals, Builder Mode, AI scene
    transitions, combat flee/death, and teleportation) must supply room data and
    call this renderer instead of assembling room text themselves.
    """
    lines: list[str] = []
    title = _display_name(getattr(room, "title", "Unknown Room"))
    lines.append(f'<span role="room_name">{render_mud_color_html(title)}</span>')
    lines.append("")

    desc = str(getattr(room, "description", "") or "").strip()
    if desc.lower().startswith(title.lower()):
        desc = desc[len(title):].lstrip(" -:,.\t")
        if desc and desc[0].islower():
            desc = desc[0].upper() + desc[1:]
    if desc:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", desc) if p.strip()]
        for idx, paragraph in enumerate(paragraphs):
            if idx:
                lines.append("")
            lines.append(f'<span role="room_description">{render_mud_color_html(paragraph)}</span>')
    lines.append("")

    visible_lines: list[str] = []
    for player in getattr(room, "players", []) or []:
        text, _desc = _entity_text(player)
        if text and (character is None or text != getattr(character, "name", "")):
            visible_lines.append(f'<span role="player">{render_mud_color_html(text)}</span>')
    grouped: "OrderedDict[tuple[Any, ...], list[tuple[str, str]]]" = OrderedDict()
    unique: list[tuple[str, str]] = []
    for role, seq in (("npc", getattr(room, "npcs", []) or []), ("mob", getattr(room, "mobs", []) or []), ("object", getattr(room, "objects", []) or [])):
        for ent in seq:
            text, _desc = _entity_text(ent)
            if not text:
                continue
            key = presence_group_key(ent)
            if key is None:
                unique.append((role, text))
            else:
                grouped.setdefault(key, []).append((role, text))
    for entries in grouped.values():
        role, text = entries[0]
        if len(entries) > 1:
            text = f"({len(entries)}) {text}"
        visible_lines.append(f'<span role="{role}">{render_mud_color_html(text)}</span>')
    for role, text in unique:
        visible_lines.append(f'<span role="{role}">{render_mud_color_html(text)}</span>')

    if visible_lines:
        lines.append("You see:")
        lines.extend(visible_lines)
        lines.append("")

    exits = getattr(room, "exits", []) or []
    exit_names: list[str] = []
    order = ["north", "east", "south", "west", "up", "down", "northeast", "northwest", "southeast", "southwest", "in", "out"]
    if isinstance(exits, list):
        sorted_exits = sorted(exits, key=lambda ex: order.index(str((ex.get("direction") or ex.get("dir")) if isinstance(ex, dict) else ex).lower()) if str((ex.get("direction") or ex.get("dir")) if isinstance(ex, dict) else ex).lower() in order else 999)
        for exit_def in sorted_exits:
            direction = exit_def.get("direction") or exit_def.get("dir") if isinstance(exit_def, dict) else str(exit_def)
            if direction:
                closed = isinstance(exit_def, dict) and (exit_def.get("closed") or exit_def.get("locked"))
                exit_names.append(f"({direction})" if closed else str(direction))
    exit_body = " ".join(f'<span role="exit">{html.escape(e)}</span>' for e in exit_names) if exit_names else '<span role="exit">none</span>'
    lines.append(f'[ Exits: {exit_body} ]')
    return "\n".join(lines)


def render_object(obj: Any) -> str:
    """Render an object for look/examine target output."""
    name, desc = _entity_text(obj, compact=False)
    if isinstance(obj, dict):
        name = str(obj.get("name") or obj.get("title") or name).strip()
    desc = desc or name
    return f'<span role="object">{render_mud_color_html(name)}</span>\n\n<span role="room_description">{render_mud_color_html(desc)}</span>'

def render_prompt(character: Any, colors: dict[str, str]) -> str:
    """Render the canonical configurable-style prompt as safe browser HTML."""
    return render_display_html(build_prompt_document(character))


def render_scrollback_line(output: str, role: str = "default", colors: dict[str, str] = None) -> str:
    """Render a single scrollback line with semantic role."""
    if colors is None:
        colors = {}
    
    return f'<span role="{html.escape(role)}">{html.escape(output)}</span>'


def render_command_echo(command: str, colors: dict[str, str]) -> str:
    """Render echoed command input."""
    return f'<span role="command_echo">&gt; {html.escape(command)}</span>'


def render_system_message(message: str, message_type: str = "system") -> str:
    """Render system message with appropriate role."""
    roles = {
        "system": "system",
        "error": "error",
        "warning": "warning",
        "combat": "combat",
        "quest": "quest",
    }
    role = roles.get(message_type, "system")
    return f'<span role="{role}">{html.escape(message)}</span>'


def render_combat_output(attacker: str, action: str, target: str, damage: int = 0, 
                        hit: bool = True, colors: dict[str, str] = None) -> str:
    """Render combat action output."""
    if colors is None:
        colors = {}
    
    if hit:
        return (
            f'<span role="combat">{html.escape(attacker)}</span> '
            f'<span role="combat">{html.escape(action)}</span> '
            f'<span role="combat">{html.escape(target)}</span> '
            f'<span role="damage">for {damage} damage</span>.'
        )
    else:
        return (
            f'<span role="combat">{html.escape(attacker)}</span> '
            f'<span role="combat">{html.escape(action)}</span> '
            f'<span role="warning">but misses</span> '
            f'<span role="combat">{html.escape(target)}</span>.'
        )


def render_dialogue(speaker: str, text: str, speaker_role: str = "npc") -> str:
    """Render dialogue with speaker color role."""
    role_colors = {
        "npc": "npc",
        "mob": "mob",
        "player": "player",
    }
    role = role_colors.get(speaker_role, "dialogue")
    
    return (
        f'<span role="{role}">{html.escape(speaker)}</span> '
        f'<span role="dialogue">says: "{render_mud_color_html(text)}"</span>'
    )


def render_inventory_list(character: Any, colors: dict[str, str]) -> str:
    """Render inventory display."""
    if not character.inventory:
        return '<span role="system">You are not carrying anything.</span>'
    
    lines = ['<span role="system">You are carrying:</span>']
    for item in character.inventory:
        item_name = item.get('name', 'unknown')
        qty = item.get('quantity', 1)
        rarity = item.get('rarity', 'common')
        role = f"item_{rarity}"
        
        qty_str = f" x{qty}" if qty > 1 else ""
        lines.append(f'  <span role="{role}">{html.escape(item_name)}</span>{qty_str}')
    
    return '\n'.join(lines)


def render_equipment_list(character: Any, colors: dict[str, str]) -> str:
    """Render equipment display."""
    if not character.equipment:
        return '<span role="system">You are not wearing anything.</span>'
    
    lines = ['<span role="system">You are wearing:</span>']
    for slot, item in character.equipment.items():
        item_name = item.get('name', 'empty') if item else 'empty'
        lines.append(
            f'  <span role="equipment_slot">{html.escape(slot)}</span>: '
            f'<span role="equipment_item">{html.escape(item_name)}</span>'
        )
    
    return '\n'.join(lines)


def apply_css_variables(colors: dict[str, str]) -> dict[str, str]:
    """Convert color roles to CSS variables for frontend application."""
    css_vars = {}
    for role, hex_color in colors.items():
        css_var_name = f"--mud-{role}"
        css_vars[css_var_name] = hex_color
    
    print(f"[mud-render] Generated {len(css_vars)} CSS variables")
    return css_vars

from types import SimpleNamespace

from engine.mud_displays import (
    DisplayDocument,
    DisplayIntent,
    DisplaySection,
    build_equipment_document,
    build_inventory_document,
    build_prompt_document,
    normalize_sentence,
    render_display_html,
    render_display_mud,
    render_display_plain,
)
from engine.mud_rendering import render_semantic_plain


def test_display_intent_vocabulary_and_structured_rendering():
    doc = DisplayDocument(
        DisplayIntent.SCORE,
        title="Score",
        semantic_role="system",
        sections=[DisplaySection(title="Resources", fields=[("Health", "85 / 100"), ("Mana", "42 / 50")])],
    )
    plain = render_display_plain(doc)
    assert doc.intent == DisplayIntent.SCORE
    assert plain.splitlines() == ["Score", "", "Resources", "Health: 85 / 100", "Mana: 42 / 50"]
    assert "\n\n\n" not in plain
    assert render_semantic_plain(render_display_mud(doc)) == plain
    html = render_display_html(doc)
    assert '<span role="system">' in html
    assert "Score" in html


def test_inventory_groups_duplicates_without_losing_instance_metadata():
    items = [
        {"instance_id": "a", "name": "trail ration", "stack_count": 1, "condition": "normal"},
        {"instance_id": "b", "name": "trail ration", "stack_count": 2, "condition": "normal"},
        {"instance_id": "c", "name": "dented flask", "stack_count": 1, "condition": "worn"},
    ]
    doc = build_inventory_document(items, carrying="3 / 50 weight")
    text = render_display_plain(doc)
    assert "Inventory" in text
    assert "3x trail ration" in text
    assert "dented flask" in text
    assert "Carrying\n3 / 50 weight" in text
    ration = doc.sections[0].entries[0]
    assert ration.metadata["instance_ids"] == ["a", "b"]


def test_equipment_slots_and_prompt_are_canonical():
    eq = build_equipment_document(
        [{"name": "a chipped longsword", "equipped_slot": "main_hand"}],
        ["head", "main_hand", "off_hand"],
    )
    text = render_display_plain(eq)
    assert text.startswith("Equipment")
    assert "Head: nothing" in text
    assert "Main hand: a chipped longsword" in text
    assert "Off hand: nothing" in text

    character = SimpleNamespace(hp=85, max_hp=100, mana=42, max_mana=50, stamina=91, max_stamina=100)
    prompt = render_display_plain(build_prompt_document(character))
    assert prompt == "[85/100 HP 42/50 MP 91/100 ST]"


def test_punctuation_normalization_for_engine_fallbacks():
    assert normalize_sentence("You see nothing special..") == "You see nothing special."
    assert normalize_sentence("What do you want??") == "What do you want?"
    assert normalize_sentence("You cannot do that") == "You cannot do that."

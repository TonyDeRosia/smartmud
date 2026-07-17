from engine.mud_displays import build_equipment_document, build_inventory_document, render_display_plain


def test_phase15b36_inventory_is_only_carried_items_and_nested_contents():
    doc = build_inventory_document([
        {"instance_id": "pack", "name": "Traveler's Pack"},
        {"instance_id": "water", "name": "Waterskin", "display_line": "  Waterskin"},
        {"instance_id": "bread", "name": "Bread", "display_line": "  Bread"},
    ], carrying="3 / 50 weight")
    text = render_display_plain(doc)
    assert "Traveler's Pack" in text
    assert "Waterskin" in text
    assert "You are carrying" not in text
    assert "weight" not in text.lower()


def test_phase15b36_equipment_has_no_redundant_slot_summary():
    doc = build_equipment_document([
        {"instance_id": "sword", "name": "Rusty Sword", "equipped_slot": "main_hand"},
        {"instance_id": "lantern", "name": "Small Lantern", "equipped_slot": "light"},
    ], ["main_hand", "light"])
    text = render_display_plain(doc)
    assert "Rusty Sword" in text
    assert "Small Lantern" in text
    # The table labels remain, but there must not be a second plain summary at the end.
    assert text.count("Main hand") == 1
    assert text.count("Light") == 1

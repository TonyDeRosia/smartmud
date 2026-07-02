"""Developer-managed campaign intelligence source library."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_SOURCE_SUFFIXES = {".txt", ".md", ".json"}
CORE_SEEDS = {
    "player_agency.md": ("Player Agency", "Never decide the player character's actions, intent, emotions, or dialogue. Resolve explicit player choices and hand control back cleanly."),
    "dialogue_realism.md": ("Dialogue Realism", "Write dialogue as direct speech with character-specific voice. Avoid summarizing what the player says when exact wording is provided."),
    "npc_identity.md": ("NPC Identity", "Preserve established NPC names, roles, relationships, and motivations. Do not rename or merge NPCs once introduced."),
    "world_consistency.md": ("World Consistency", "Keep locations, factions, consequences, and physical scene details consistent with established campaign facts."),
    "memory_rules.md": ("Memory Rules", "Prefer current scene facts and recent player actions over stale context. Treat explicit player corrections as high-priority updates."),
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_.-]+", "_", value.strip()).strip("._-").lower()
    return clean or "source"


@dataclass(frozen=True)
class IntelligenceSource:
    id: str
    filename: str
    title: str
    category: str
    priority: int
    enabled: bool
    imported_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "IntelligenceSource":
        return cls(
            id=str(payload.get("id", "")).strip(),
            filename=str(payload.get("filename", "")).strip(),
            title=str(payload.get("title", "")).strip(),
            category=str(payload.get("category", "packs")).strip() or "packs",
            priority=int(payload.get("priority", 0) or 0),
            enabled=bool(payload.get("enabled", True)),
            imported_at=str(payload.get("imported_at", "")).strip(),
            updated_at=str(payload.get("updated_at", "")).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "enabled": self.enabled,
            "imported_at": self.imported_at,
            "updated_at": self.updated_at,
        }


class CampaignIntelligenceLibrary:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.manifest_path = self.root / "manifest.json"
        self.ensure_initialized()

    def ensure_initialized(self) -> None:
        for category in ("core", "packs", "imported"):
            (self.root / category).mkdir(parents=True, exist_ok=True)
        entries = self._load_manifest_entries(create_if_missing=True)
        by_filename = {entry.filename: entry for entry in entries}
        changed = False
        now = utc_now_iso()
        for index, (filename, (title, body)) in enumerate(CORE_SEEDS.items(), start=1):
            path = self.root / "core" / filename
            if not path.exists():
                path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
            rel = f"core/{filename}"
            if rel not in by_filename:
                entries.append(IntelligenceSource(
                    id=Path(filename).stem,
                    filename=rel,
                    title=title,
                    category="core",
                    priority=1000 - index,
                    enabled=True,
                    imported_at=now,
                    updated_at=now,
                ))
                changed = True
        if changed or not self.manifest_path.exists():
            self._save_manifest_entries(entries)


    @property
    def index_path(self) -> Path:
        return self.root / "index.json"

    def list_sources(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self._sorted_entries(self._load_manifest_entries())]

    def import_source(self, source_path: Path, *, title: str = "", category: str = "imported", priority: int = 0, enabled: bool = True) -> dict[str, Any]:
        source = self._validate_source_file(source_path)
        category = self._validate_category(category, allow_core=False)
        entries = self._load_manifest_entries()
        base = slugify(source.stem) + source.suffix.lower()
        filename = self._unique_filename(category, base)
        target = self.root / category / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        now = utc_now_iso()
        entry_id = self._unique_id(slugify(source.stem), entries)
        entry = IntelligenceSource(entry_id, f"{category}/{filename}", title.strip() or source.stem.replace("_", " ").title(), category, int(priority), bool(enabled), now, now)
        entries.append(entry)
        self._save_manifest_entries(entries)
        self.rebuild_index()
        return entry.to_dict()

    def replace_source(self, source_id: str, source_path: Path, *, title: str | None = None) -> dict[str, Any]:
        source = self._validate_source_file(source_path)
        entries = self._load_manifest_entries()
        idx, entry = self._find_entry(entries, source_id)
        target = self._entry_path(entry)
        if source.suffix.lower() != target.suffix.lower():
            raise ValueError("Replacement file must use the same extension as the existing source file.")
        shutil.copy2(source, target)
        updated = IntelligenceSource(entry.id, entry.filename, title.strip() if isinstance(title, str) and title.strip() else entry.title, entry.category, entry.priority, entry.enabled, entry.imported_at, utc_now_iso())
        entries[idx] = updated
        self._save_manifest_entries(entries)
        self.rebuild_index()
        return updated.to_dict()

    def set_enabled(self, source_id: str, enabled: bool) -> dict[str, Any]:
        entries = self._load_manifest_entries(); idx, entry = self._find_entry(entries, source_id)
        updated = IntelligenceSource(entry.id, entry.filename, entry.title, entry.category, entry.priority, bool(enabled), entry.imported_at, utc_now_iso())
        entries[idx] = updated; self._save_manifest_entries(entries); self.rebuild_index()
        return updated.to_dict()

    def set_priority(self, source_id: str, priority: int) -> dict[str, Any]:
        entries = self._load_manifest_entries(); idx, entry = self._find_entry(entries, source_id)
        updated = IntelligenceSource(entry.id, entry.filename, entry.title, entry.category, int(priority), entry.enabled, entry.imported_at, utc_now_iso())
        entries[idx] = updated; self._save_manifest_entries(entries); self.rebuild_index(); return updated.to_dict()

    def read_enabled_sources(self, *, category: str | None = None) -> list[dict[str, Any]]:
        entries = [e for e in self._sorted_entries(self._load_manifest_entries()) if e.enabled]
        if category:
            entries = [e for e in entries if e.category == category]
        result = []
        for entry in entries:
            path = self._entry_path(entry)
            if path.exists():
                payload = entry.to_dict(); payload["content"] = path.read_text(encoding="utf-8")
                result.append(payload)
        return result

    def build_guidance(self, *, enabled_source_ids: list[str] | None = None, max_chars: int = 6000) -> tuple[str, list[dict[str, Any]]]:
        selected_ids = {str(v).strip() for v in (enabled_source_ids or []) if str(v).strip()}
        selected_allowed = bool(selected_ids)
        source_items = [item for item in self.read_enabled_sources() if item.get("category") == "core" or (selected_allowed and item.get("id") in selected_ids and item.get("category") in {"packs", "imported"})]
        source_items.sort(key=lambda item: (0 if item.get("category") == "core" else 1, -int(item.get("priority", 0) or 0), str(item.get("title") or item.get("id") or "").lower(), str(item.get("id") or "")))
        sections = []
        used = 0
        used_sources: list[dict[str, Any]] = []
        for item in source_items:
            text = str(item.get("content", "")).strip()
            if not text:
                continue
            block = f"## {item.get('title') or item.get('id')}\n{text}"
            remaining = max_chars - used
            if remaining <= 0:
                break
            chunk = block[:remaining]
            sections.append(chunk)
            used += len(chunk)
            used_payload = {k: item.get(k) for k in ("id", "title", "category", "filename", "priority")}
            used_payload["chars"] = len(chunk)
            used_sources.append(used_payload)
        return "\n\n".join(sections).strip(), used_sources

    def build_core_guidance(self, *, max_chars: int = 4000) -> str:
        guidance, _ = self.build_guidance(enabled_source_ids=[], max_chars=max_chars)
        return guidance


    def chunk_source(self, source: dict[str, Any]) -> list[dict[str, Any]]:
        entry = IntelligenceSource.from_dict(source)
        path = self._entry_path(entry)
        if not path.exists() or path.suffix.lower() not in ALLOWED_SOURCE_SUFFIXES:
            return []
        raw = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            try:
                raw = json.dumps(json.loads(raw), indent=2, ensure_ascii=False)
            except Exception:
                pass
        parts: list[tuple[str, str]] = []
        heading = entry.title
        buf: list[str] = []
        for line in raw.splitlines():
            m = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
            if m:
                if "\n".join(buf).strip():
                    parts.append((heading, "\n".join(buf).strip()))
                heading = m.group(1).strip(); buf = []
            else:
                buf.append(line)
        if "\n".join(buf).strip():
            parts.append((heading, "\n".join(buf).strip()))
        if not parts:
            parts = [(entry.title, raw.strip())]
        chunks: list[dict[str, Any]] = []
        idx = 0
        for head, body in parts:
            paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
            current = ""
            for para in paras or [body]:
                if current and len(current) + len(para) + 2 > 1600:
                    chunks.append(self._chunk_payload(entry, idx, head, current)); idx += 1; current = ""
                if len(para) > 1800:
                    for start in range(0, len(para), 1500):
                        if current:
                            chunks.append(self._chunk_payload(entry, idx, head, current)); idx += 1; current = ""
                        chunks.append(self._chunk_payload(entry, idx, head, para[start:start+1500])); idx += 1
                else:
                    current = (current + "\n\n" + para).strip() if current else para
            if current:
                chunks.append(self._chunk_payload(entry, idx, head, current)); idx += 1
        return chunks

    def _chunk_payload(self, entry: IntelligenceSource, idx: int, heading: str, text: str) -> dict[str, Any]:
        return {"source_id": entry.id, "title": entry.title, "category": entry.category, "priority": entry.priority, "path": entry.filename, "chunk_index": idx, "heading": heading, "text": text.strip(), "enabled": entry.enabled}

    def rebuild_index(self) -> dict[str, Any]:
        entries = self._sorted_entries(self._load_manifest_entries())
        chunks: list[dict[str, Any]] = []
        for entry in entries:
            chunks.extend(self.chunk_source(entry.to_dict()))
        payload = {"version": 1, "rebuilt_at": utc_now_iso(), "source_count": len(entries), "chunks": chunks}
        self.index_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return {"indexed_source_count": len(entries), "chunk_count": len(chunks), "index_path": str(self.index_path)}

    def _load_index(self) -> dict[str, Any]:
        if not self.index_path.exists():
            self.rebuild_index()
        return json.loads(self.index_path.read_text(encoding="utf-8") or "{}")

    def retrieve(self, query: str, selected_source_ids: list[str] | None = None, max_chunks: int = 5) -> dict[str, Any]:
        selected = {str(v).strip() for v in (selected_source_ids or []) if str(v).strip()}
        index = self._load_index()
        chunks = index.get("chunks", []) if isinstance(index, dict) else []
        if not chunks:
            return {"results": [], "reason": "no index", "indexed_source_count": 0}
        q = str(query or "").lower().strip()
        words = [w for w in re.findall(r"[a-z0-9]{3,}", q) if w not in {"the","and","you","your","what","with","from"}]
        results=[]; enabled_seen=False; selectable_seen=False
        for c in chunks:
            if not c.get("enabled", True):
                continue
            enabled_seen=True
            cat=str(c.get("category"))
            if cat != "core" and c.get("source_id") not in selected:
                selectable_seen=True; continue
            hay = f"{c.get('title','')} {c.get('heading','')} {c.get('text','')}".lower()
            overlap = sum(1 for w in set(words) if w in hay)
            exact = 0
            if q and len(q) > 3 and q in hay: exact = 8
            heading = sum(2 for w in set(words) if w in str(c.get("heading", "")).lower())
            category_boost = 2 if cat == "core" else 1
            selected_boost = 3 if c.get("source_id") in selected else 0
            score = exact + overlap * 3 + heading + int(c.get("priority",0) or 0)/100 + category_boost + selected_boost
            if score <= 2 or overlap == 0 and exact == 0:
                continue
            reason = f"keyword_overlap={overlap}; exact_phrase={bool(exact)}; priority={c.get('priority',0)}"
            r = dict(c); r.update({"score": round(score, 2), "reason": reason, "snippet": str(c.get("text", ""))[:360]})
            results.append(r)
        results.sort(key=lambda r: (-float(r.get("score",0)), -int(r.get("priority",0) or 0), str(r.get("title",""))))
        reason = "ok" if results else ("no enabled sources" if not enabled_seen else ("no selected campaign sources" if selectable_seen and not selected else "no chunks above threshold"))
        return {"results": results[:max_chunks], "reason": reason, "indexed_source_count": index.get("source_count", 0), "selected_campaign_source_ids": sorted(selected)}

    def build_retrieved_guidance(self, query: str, *, enabled_source_ids: list[str] | None = None, max_chars: int = 4500, max_chunks: int = 5) -> tuple[str, dict[str, Any]]:
        retrieval = self.retrieve(query, enabled_source_ids, max_chunks=max_chunks)
        blocks=[]; used=0; injected=[]
        for item in retrieval.get("results", []):
            block=f"## {item.get('title')} — {item.get('heading')}\n{item.get('text','').strip()}"
            if used + len(block) > max_chars:
                block = block[:max(0, max_chars-used)]
            if not block.strip(): break
            blocks.append(block); used += len(block)
            injected.append({k:item.get(k) for k in ("source_id","title","category","heading","score","reason","snippet")})
            if used >= max_chars: break
        trace={"selected_campaign_source_ids": retrieval.get("selected_campaign_source_ids", []), "indexed_source_count": retrieval.get("indexed_source_count",0), "retrieved_source_ids": sorted({i.get("source_id") for i in retrieval.get("results", []) if i.get("source_id")}), "retrieved_chunk_count": len(retrieval.get("results", [])), "injected_chunk_count": len(injected), "estimated_injected_chars": used, "injected_chunk_headings": [i.get("heading") for i in injected], "injected_snippets": injected, "zero_injection_reason": "" if injected else retrieval.get("reason", "no chunks above threshold")}
        return "\n\n".join(blocks).strip(), trace

    def _load_manifest_entries(self, *, create_if_missing: bool = False) -> list[IntelligenceSource]:
        if not self.manifest_path.exists():
            if create_if_missing:
                self.manifest_path.parent.mkdir(parents=True, exist_ok=True); self.manifest_path.write_text("[]\n", encoding="utf-8")
            return []
        data = json.loads(self.manifest_path.read_text(encoding="utf-8") or "[]")
        return [IntelligenceSource.from_dict(item) for item in data if isinstance(item, dict)]

    def _save_manifest_entries(self, entries: list[IntelligenceSource]) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps([e.to_dict() for e in entries], indent=2) + "\n", encoding="utf-8")

    def _sorted_entries(self, entries: list[IntelligenceSource]) -> list[IntelligenceSource]:
        return sorted(entries, key=lambda e: (-e.priority, e.title.lower(), e.id))

    def _validate_source_file(self, source_path: Path) -> Path:
        source = source_path.expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        if source.suffix.lower() not in ALLOWED_SOURCE_SUFFIXES:
            raise ValueError("Source file must be .txt, .md, or .json.")
        return source

    def _validate_category(self, category: str, *, allow_core: bool) -> str:
        clean = str(category or "imported").strip().lower()
        allowed = {"packs", "imported"} | ({"core"} if allow_core else set())
        if clean not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(sorted(allowed))}.")
        return clean

    def _entry_path(self, entry: IntelligenceSource) -> Path:
        path = (self.root / entry.filename).resolve()
        if self.root.resolve() not in path.parents:
            raise ValueError("Manifest entry points outside intelligence directory.")
        return path

    def _find_entry(self, entries: list[IntelligenceSource], source_id: str) -> tuple[int, IntelligenceSource]:
        for idx, entry in enumerate(entries):
            if entry.id == source_id:
                return idx, entry
        raise KeyError(f"Unknown intelligence source id: {source_id}")

    def _unique_id(self, base: str, entries: list[IntelligenceSource]) -> str:
        used = {e.id for e in entries}; candidate = base; counter = 2
        while candidate in used:
            candidate = f"{base}_{counter}"; counter += 1
        return candidate

    def _unique_filename(self, category: str, base: str) -> str:
        candidate = base; counter = 2
        while (self.root / category / candidate).exists():
            candidate = f"{Path(base).stem}_{counter}{Path(base).suffix}"; counter += 1
        return candidate


def default_intelligence_library() -> CampaignIntelligenceLibrary:
    from app.pathing import content_data_dir
    return CampaignIntelligenceLibrary(content_data_dir() / "intelligence")

# Public compatibility helpers for lightweight local retrieval.
def chunk_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    return default_intelligence_library().chunk_source(source)


def rebuild_index() -> dict[str, Any]:
    return default_intelligence_library().rebuild_index()


def retrieve(query: str, selected_source_ids: list[str] | None = None, max_chunks: int = 5) -> dict[str, Any]:
    return default_intelligence_library().retrieve(query, selected_source_ids, max_chunks=max_chunks)

#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Inventory the pinned 1.7.10 entity/tile declarations without executing Java.

Run from any directory:
  python3 tools/inventory_original.py --source /path/to/hbm-original
  python3 tools/inventory_original.py --source /path/to/hbm-original --check

This is a deliberately bounded, token-based source extractor, not a Java compiler
or a claim about all runtime registries. The generated JSON records its limits.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

COMMIT = "aee05a40f10fb7bb9b042b65eccaa449ecc1672d"
UPSTREAM = "https://github.com/HbmMods/Hbm-s-Nuclear-Tech-GIT"
JAVA = "src/main/java/"
ENTITY = JAVA + "com/hbm/entity/EntityMappings.java"
TILE = JAVA + "com/hbm/tileentity/TileMappings.java"
HELPER = JAVA + "com/hbm/entity/ModEntityList.java"
MAIN = JAVA + "com/hbm/main/MainRegistry.java"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "docs/inventory/registrations.json"


class InventoryError(ValueError):
    """Input no longer satisfies the explicitly supported source contract."""


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int
    kind: str


def tokenize(text: str) -> list[Token]:
    """Retain offsets; ignore comments, never confuse their contents with calls."""
    tokens = []
    i = 0
    while i < len(text):
        start = i
        c = text[i]
        if c.isspace():
            i += 1
        elif text.startswith("//", i):
            end = text.find("\n", i + 2)
            i = len(text) if end < 0 else end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end < 0:
                raise InventoryError("Unterminated block comment")
            i = end + 2
        elif c in '\"\'':
            quote = c
            i += 1
            while i < len(text):
                if text[i] == "\\":
                    i += 2
                elif text[i] == quote:
                    i += 1
                    break
                elif text[i] in "\r\n":
                    raise InventoryError("Unterminated Java string/character literal")
                else:
                    i += 1
            else:
                raise InventoryError("Unterminated Java string/character literal")
            tokens.append(Token(text[start:i], start, i, "string" if quote == '"' else "char"))
        elif c.isalpha() or c in "_$":
            i += 1
            while i < len(text) and (text[i].isalnum() or text[i] in "_$"):
                i += 1
            tokens.append(Token(text[start:i], start, i, "identifier"))
        elif c.isdigit():
            i += 1
            while i < len(text) and (text[i].isalnum() or text[i] in "_."):
                i += 1
            tokens.append(Token(text[start:i], start, i, "number"))
        else:
            tokens.append(Token(c, i, i + 1, "symbol"))
            i += 1
    return tokens


def bracket_pairs(tokens: list[Token]) -> dict[int, int]:
    stack = []
    pairs = {}
    closers = {"(": ")", "[": "]", "{": "}"}
    for i, token in enumerate(tokens):
        if token.text in closers:
            stack.append(i)
        elif token.text in closers.values():
            if not stack or closers[tokens[stack[-1]].text] != token.text:
                raise InventoryError(f"Unbalanced delimiter at character {token.start}")
            left = stack.pop()
            pairs[left] = i
            pairs[i] = left
    if stack:
        raise InventoryError("Unclosed delimiter")
    return pairs


def raw(text: str, tokens: list[Token]) -> str:
    return text[tokens[0].start:tokens[-1].end] if tokens else ""


def split_arguments(tokens: list[Token]) -> list[list[Token]]:
    """Split calls at top-level commas, preserving nested calls/arrays/strings."""
    if not tokens:
        return []
    result = []
    start = depth = 0
    for i, token in enumerate(tokens):
        if token.text in ("(", "[", "{"):
            depth += 1
        elif token.text in (")", "]", "}"):
            depth -= 1
        elif token.text == "," and depth == 0:
            result.append(tokens[start:i])
            start = i + 1
    result.append(tokens[start:])
    if any(not arg for arg in result):
        raise InventoryError("Empty call argument")
    return result


def literal(tokens: list[Token]):
    """Resolve only individual Java string/bool/integer literals, never eval()."""
    text = "".join(t.text for t in tokens)
    if text in ("true", "false"):
        return text == "true"
    if len(tokens) == 1 and tokens[0].kind == "string":
        body = text[1:-1]
        result = []
        escapes = {"b": "\b", "t": "\t", "n": "\n", "f": "\f", "r": "\r", '"': '"', "'": "'", "\\": "\\"}
        i = 0
        while i < len(body):
            if body[i] != "\\":
                result.append(body[i])
                i += 1
                continue
            i += 1
            if i >= len(body):
                return None
            if body[i] in escapes:
                result.append(escapes[body[i]])
                i += 1
            elif body[i] in "01234567":
                # Java octal escapes: up to 3 digits only when first is 0..3.
                end = i + 1
                limit = 3 if body[i] in "0123" else 2
                while end < len(body) and end - i < limit and body[end] in "01234567":
                    end += 1
                result.append(chr(int(body[i:end], 8)))
                i = end
            else:
                # Unicode is translated before Java lexing; unsupported here.
                return None
        return "".join(result)
    if re.fullmatch(r"[+-]?(?:0[xX][0-9a-fA-F_]+|0[bB][01_]+|[0-9_]+)[lL]?", text):
        digits = text.rstrip("lL").replace("_", "")
        sign = -1 if digits.startswith("-") else 1
        digits = digits.lstrip("+-")
        base = 16 if digits.lower().startswith("0x") else 2 if digits.lower().startswith("0b") else 8 if len(digits) > 1 and digits[0] == "0" else 10
        try:
            return sign * int(digits, base)
        except ValueError:
            return None
    return None


@dataclass
class Method:
    name: str
    parameters: list[Token]
    start: int
    end: int
    body: list[Token]
    token_start: int
    token_end: int


class Source:
    def __init__(self, path: str, content: bytes):
        self.path = path
        self.content = content
        self.text = content.decode("utf-8")
        self.tokens = tokenize(self.text)
        # Benign Unicode inside string/char literals cannot alter declaration
        # boundaries. Reject escapes elsewhere or structural code points; Java
        # translates those before lexing, which this bounded extractor does not.
        for escape in re.finditer(r"\\u+([0-9a-fA-F]{4})", self.text):
            containing = next((t for t in self.tokens if t.start <= escape.start() < t.end), None)
            if (containing is None or containing.kind not in ("string", "char")
                    or chr(int(escape.group(1), 16)) in "\r\n\"'\\"):
                raise InventoryError(f"Structural Unicode preprocessing is unsupported: {path}")
        self.pairs = bracket_pairs(self.tokens)
        self.methods = self._methods()

    def location(self, start: int, end: int | None = None) -> dict:
        return {"path": self.path, "line": self.text.count("\n", 0, start) + 1,
                "end_line": self.text.count("\n", 0, end if end is not None else start) + 1}

    def _methods(self) -> list[Method]:
        result = []
        depth = 0
        for i, token in enumerate(self.tokens):
            if (depth == 1 and token.kind == "identifier" and i + 1 < len(self.tokens)
                    and self.tokens[i + 1].text == "("):
                close = self.pairs[i + 1]
                if close + 1 < len(self.tokens) and self.tokens[close + 1].text == "{":
                    end = self.pairs[close + 1]
                    result.append(Method(token.text, self.tokens[i + 2:close], token.start,
                                         self.tokens[end].end, self.tokens[close + 2:end], close + 2, end))
            if token.text == "{":
                depth += 1
            elif token.text == "}":
                depth -= 1
        return result

    def method(self, name: str, arity: int | None = None) -> Method:
        matches = [m for m in self.methods if m.name == name]
        if arity is not None:
            # Parameter commas inside Class<? extends Entity> have no comma;
            # none of the selected overload parameters uses multi-argument generics.
            matches = [m for m in matches if len(split_arguments(m.parameters)) == arity]
        if len(matches) != 1:
            raise InventoryError(f"Expected one method {name}/{arity} in {self.path}, found {len(matches)}")
        return matches[0]

    def method_evidence(self, name: str, arity: int | None = None) -> dict:
        method = self.method(name, arity)
        return {"source": self.location(method.start, method.end),
                "java": self.text[method.start:method.end]}

    def calls(self, method: Method) -> list[dict]:
        result = []
        tokens = self.tokens
        # Conditional lexical scopes are recorded, not executed.
        conditions = []
        for i in range(method.token_start, method.token_end):
            token = tokens[i]
            if token.text == "if" and tokens[i + 1].text == "(":
                close = self.pairs[i + 1]
                body_start = close + 1
                if tokens[body_start].text == "{":
                    body_end = self.pairs[body_start]
                else:
                    body_end = body_start
                    while body_end < method.token_end and tokens[body_end].text != ";":
                        body_end += 1
                conditions.append((body_start, body_end, raw(self.text, tokens[i + 2:close]), self.location(token.start, tokens[close].end)))
            if token.kind != "identifier" or i + 1 >= method.token_end or tokens[i + 1].text != "(":
                continue
            if token.text in ("if", "for", "while", "switch", "catch", "synchronized"):
                continue
            close = self.pairs[i + 1]
            args = split_arguments(tokens[i + 2:close])
            left = i
            while left >= 2 and tokens[left - 1].text == "." and tokens[left - 2].kind == "identifier":
                left -= 2
            result.append({"name": token.text, "receiver": "".join(t.text for t in tokens[left:i - 1]) if left < i else None,
                           "index": i, "args": args, "raw_arguments": [raw(self.text, a) for a in args],
                           "source": self.location(tokens[left].start, tokens[close].end),
                           "raw_call": self.text[tokens[left].start:tokens[close].end],
                           "conditions": [{"expression": c, "source": loc} for begin, end, c, loc in conditions if begin <= i <= end]})
        return result


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class Checkout:
    def __init__(self, root: Path):
        self.root = root
        actual = git(root, "rev-parse", "HEAD").stdout.decode().strip()
        if actual != COMMIT:
            raise InventoryError(f"Expected original commit {COMMIT}, found {actual}; no output written")
        if git(root, "diff", "--quiet", COMMIT, "--", "src/main/java", check=False).returncode != 0:
            raise InventoryError("Original Java sources differ from pinned commit; no output written")
        self.paths = set(git(root, "ls-tree", "-r", "--name-only", COMMIT, "--", "src/main/java").stdout.decode().splitlines())
        self.loaded: dict[str, Source] = {}

    def source(self, path: str) -> Source:
        if path not in self.paths:
            raise InventoryError(f"Not a tracked source in original commit: {path}")
        if path not in self.loaded:
            self.loaded[path] = Source(path, git(self.root, "show", f"{COMMIT}:{path}").stdout)
        return self.loaded[path]

    def resolve_class(self, source: Source, expression: list[Token]) -> dict:
        compact = "".join(t.text for t in expression)
        result = {"raw": raw(source.text, expression), "qualified_name": None, "source": None, "status": "unresolved", "candidates": []}
        if not compact.endswith(".class"):
            return result
        class_name = compact[:-6]
        if not re.fullmatch(r"[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*", class_name):
            return result
        imports = []
        package = ""
        tokens = source.tokens
        for i, token in enumerate(tokens):
            if token.text not in ("package", "import"):
                continue
            end = i + 1
            while end < len(tokens) and tokens[end].text != ";":
                end += 1
            value = "".join(t.text for t in tokens[i + 1:end])
            if token.text == "package":
                package = value
            elif not value.startswith("static"):
                imports.append(value)
        first, *tail = class_name.split(".")
        explicit = [imp + ("." + ".".join(tail) if tail else "") for imp in imports if not imp.endswith(".*") and imp.split(".")[-1] == first]
        # Explicit imports win over on-demand imports. The pinned source has no
        # ambiguous local/nested declarations in either mappings class.
        candidates = explicit or ([class_name] if class_name.startswith("com.") else [package + "." + class_name] + [imp[:-2] + "." + class_name for imp in imports if imp.endswith(".*")])
        resolved = []
        for fqcn in candidates:
            parts = fqcn.split(".")
            for n in range(len(parts), 0, -1):
                path = JAVA + "/".join(parts[:n]) + ".java"
                if path not in self.paths:
                    continue
                declaration = self.source(path)
                expected_names = parts[n - 1:]
                declared_names = {declaration.tokens[j + 1].text for j, t in enumerate(declaration.tokens[:-1]) if t.text in ("class", "interface", "enum") and declaration.tokens[j + 1].kind == "identifier"}
                if all(name in declared_names for name in expected_names):
                    resolved.append({"qualified_name": fqcn, "source_path": path})
                break
        result["candidates"] = sorted({r["qualified_name"]: r for r in resolved}.values(), key=lambda r: r["qualified_name"])
        if len(result["candidates"]) == 1:
            result.update(status="resolved", qualified_name=resolved[0]["qualified_name"], source=resolved[0]["source_path"])
        elif resolved:
            result["status"] = "ambiguous"
        return result


def family_ids(base: str, fqcn: str | None) -> list[str]:
    """Coarse planning-family links; BASE-004/MOB-001 always remain primary."""
    ids = [base]
    name = fqcn or ""
    for fragment, matrix_id in ((".machine.rbmk.", "NUC-008"), (".machine.pile.", "NUC-004"),
                                (".machine.fusion.", "NUC-012"), (".mob.glyphid.", "MOB-002"),
                                (".mob.botprime.", "MOB-004"), (".mob.siege.", "MOB-004"),
                                (".entity.train.", "MOB-007"), (".entity.cart.", "MOB-006"),
                                (".entity.missile.", "BOMB-010"), (".tileentity.turret.", "BOMB-013")):
        if fragment in name:
            ids.append(matrix_id)
    return ids


def mapping_call(source: Source, call: dict, checkout: Checkout, method_name: str) -> dict:
    if not call["args"]:
        raise InventoryError(f"Missing class argument: {call['source']}")
    cls = checkout.resolve_class(source, call["args"][0])
    return {"declaration_kind": call["name"], "enclosing_method": method_name,
            "source": call["source"], "raw_call": call["raw_call"], "raw_arguments": call["raw_arguments"],
            "java_class": cls, "conditions": call["conditions"], "unresolved_fields": [],
            "matrix_ids": family_ids("BASE-004" if source.path == TILE else "MOB-001", cls["qualified_name"])}


def tile_entries(checkout: Checkout) -> tuple[list[dict], list[dict]]:
    source = checkout.source(TILE)
    entries = []
    helpers = []
    def walk(name: str, stack: tuple[str, ...] = (), inherited_conditions: tuple[dict, ...] = ()):
        if name in stack:
            raise InventoryError(f"Recursive mappings helper: {name}")
        method = source.method(name)
        if any(token.text == "else" for token in method.body):
            raise InventoryError(f"Unsupported else branch in mappings helper: {name}")
        bindings = {}
        for i in range(len(method.body) - 2):
            if (method.body[i].text == "boolean" and method.body[i + 1].kind == "identifier"
                    and method.body[i + 2].text == "="):
                end = i + 3
                while end < len(method.body) and method.body[end].text != ";":
                    end += 1
                bindings[method.body[i + 1].text] = {
                    "raw_expression": raw(source.text, method.body[i + 3:end]),
                    "source": source.location(method.body[i].start, method.body[end].end)}
        for call in source.calls(method):
            if call["receiver"] is not None:
                continue
            if call["name"] == "put":
                if len(call["args"]) < 2:
                    raise InventoryError("put() requires class and at least one name")
                entry = mapping_call(source, call, checkout, name)
                entry["conditions"] = list(inherited_conditions) + entry["conditions"]
                names = [literal(arg) for arg in call["args"][1:]]
                entry.update(inventory_id=f"tile-declaration:{len(entries):03d}", declared_names=names,
                             primary_name=names[0], alternative_names=names[1:],
                             source_traversal_index=len(entries), registration_order="unspecified_hashmap_iteration")
                entry["unresolved_fields"] = (["java_class"] if entry["java_class"]["status"] != "resolved" else []) + [f"declared_names[{i}]" for i, val in enumerate(names) if not isinstance(val, str)]
                used_bindings = {condition["expression"]: bindings[condition["expression"]]
                                 for condition in entry["conditions"] if condition["expression"] in bindings}
                if used_bindings:
                    entry["condition_bindings"] = used_bindings
                entries.append(entry)
            elif call["name"].startswith("put"):
                helpers.append({"called_method": call["name"], "source": call["source"], "raw_call": call["raw_call"]})
                walk(call["name"], stack + (name,), inherited_conditions + tuple(call["conditions"]))
    walk("writeMappings")
    # Exhaustive for literal put() calls in all declared methods, not just graph hits.
    all_puts = [(m.name, c["source"]["line"]) for m in source.methods for c in source.calls(m) if c["receiver"] is None and c["name"] == "put"]
    found = [(e["enclosing_method"], e["source"]["line"]) for e in entries]
    if sorted(all_puts) != sorted(found):
        raise InventoryError("Unreachable or multiply traversed TileMappings.put call; extraction contract needs review")
    return entries, helpers


def entity_entries(checkout: Checkout) -> tuple[list[dict], list[dict]]:
    source = checkout.source(ENTITY)
    entities = []
    spawns = []
    for call in source.calls(source.method("writeMappings")):
        if call["receiver"] is not None or call["name"] not in ("addEntity", "addMob", "addSpawn"):
            continue
        name = call["name"]
        arity = len(call["args"])
        if arity not in ({3, 4} if name == "addEntity" else {4} if name == "addMob" else {6}):
            raise InventoryError(f"Unsupported {name} arity {arity}")
        entry = mapping_call(source, call, checkout, "writeMappings")
        values = [literal(arg) for arg in call["args"]]
        if name == "addSpawn":
            entry.update(inventory_id=f"spawn-rule:{len(spawns):03d}", weight=values[1], minimum_group=values[2], maximum_group=values[3],
                         creature_type_expression=call["raw_arguments"][4], biome_expression=call["raw_arguments"][5],
                         effective_biome_entries=None)
            expected = {"weight": values[1], "minimum_group": values[2], "maximum_group": values[3]}
            spawns.append(entry)
        else:
            entry.update(inventory_id=f"entity-declaration:{len(entities):03d}", original_name=values[1],
                         declaration_group="non_mob" if name == "addEntity" else "mob",
                         tracking={"range": values[2] if name == "addEntity" else 80,
                                   "update_frequency_ticks": 1 if name == "addEntity" else 3,
                                   "sends_velocity_updates": values[3] if name == "addEntity" and arity == 4 else True,
                                   "derivation": "EntityMappings.addEntity default/registration loop" if name == "addEntity" else "ModEntityList.registerEntity six-argument overload"},
                         spawn_egg={"has_egg": name == "addMob", "primary_color": values[2] if name == "addMob" else None,
                                    "secondary_color": values[3] if name == "addMob" else None, "global_egg_id": None})
            expected = {"original_name": values[1], **{"tracking." + k: v for k, v in entry["tracking"].items() if k != "derivation"}}
            if name == "addMob":
                expected.update({"spawn_egg.primary_color": values[2], "spawn_egg.secondary_color": values[3]})
            entities.append(entry)
        entry["unresolved_fields"] = (["java_class"] if entry["java_class"]["status"] != "resolved" else []) + [k for k, value in expected.items() if value is None]
    # Their helper methods contain forwarding calls, not additional declarations.
    other = [(m.name, c["name"]) for m in source.methods if m.name not in ("writeMappings", "addEntity", "addMob", "addSpawn") for c in source.calls(m) if c["receiver"] is None and c["name"] in ("addEntity", "addMob", "addSpawn")]
    if other:
        raise InventoryError(f"Unexpected entity declarations in other helpers: {other}")
    ordered = [e for e in entities if e["declaration_group"] == "non_mob"] + [e for e in entities if e["declaration_group"] == "mob"]
    for nominal_id, entry in enumerate(ordered):
        entry["nominal_local_mod_id"] = nominal_id
        entry["local_id_assumption"] = "One writeMappings call, initially empty and otherwise unmodified public mapping lists; non-mobs then mobs"
    return entities, spawns


def duplicates(entries: list[dict], field: str) -> list[dict]:
    seen = defaultdict(list)
    for entry in entries:
        value = entry.get(field)
        if value is not None:
            seen[value].append(entry["inventory_id"])
    return [{"value": key, "declarations": ids} for key, ids in sorted(seen.items()) if len(ids) > 1]


def registration_evidence(checkout: Checkout) -> dict:
    main = checkout.source(MAIN)
    entity = checkout.source(ENTITY)
    tile = checkout.source(TILE)
    helper = checkout.source(HELPER)
    selected = []
    for method in main.methods:
        for call in main.calls(method):
            if ((call["receiver"] in ("EntityMappings", "TileMappings") and call["name"] == "writeMappings")
                    or call["name"] in ("registerTileEntity", "registerTileEntityWithAlternatives")):
                selected.append({"enclosing_method": method.name, "source": call["source"], "raw_call": call["raw_call"], "raw_arguments": call["raw_arguments"]})
    loops = [{"source": c["source"], "raw_call": c["raw_call"], "raw_arguments": c["raw_arguments"]}
             for c in entity.calls(entity.method("writeMappings")) if c["receiver"] == "ModEntityList" and c["name"] == "registerEntity"]
    return {"main_registry_calls": selected, "entity_registration_calls": loops,
            "entity_default_velocity_helper": entity.method_evidence("addEntity", 3),
            "entity_mapping_helper": entity.method_evidence("addEntity", 4),
            "mob_mapping_helper": entity.method_evidence("addMob", 4),
            "mob_tracking_default_overload": helper.method_evidence("registerEntity", 6),
            "entity_forge_registration_overload": helper.method_evidence("registerEntity", 10),
            "spawn_helper": entity.method_evidence("addSpawn", 6),
            "tile_mapping_helper": tile.method_evidence("put", 2),
            "egg_allocation_helper": helper.method_evidence("getUniqueEntityEggId", 0)}


def build_inventory(root: Path) -> dict:
    checkout = Checkout(root)
    # Read the four linkage sources before resolving any declaration classes.
    for path in (ENTITY, TILE, HELPER, MAIN):
        checkout.source(path)
    tiles, helpers = tile_entries(checkout)
    entities, spawns = entity_entries(checkout)
    evidence = registration_evidence(checkout)
    conditional_tiles = [e for e in tiles if e["conditions"]]
    by_class = defaultdict(list)
    for entry in tiles:
        by_class[entry["java_class"]["qualified_name"] or entry["java_class"]["raw"]].append(entry["inventory_id"])
    class_duplicates = [{"value": k, "declarations": v} for k, v in sorted(by_class.items()) if len(v) > 1]
    tile_names = defaultdict(list)
    for entry in tiles:
        for name in entry["declared_names"]:
            if name is not None:
                tile_names[name].append(entry["inventory_id"])
    result = {"schema_version": 1,
              "reference": {"repository": UPSTREAM, "commit": COMMIT, "minecraft": "1.7.10"},
              "extraction": {"method": "Python stdlib lexical tokens, declared helper traversal, literal-only value interpretation; Java is not executed",
                             "entry_points": [ENTITY + "#writeMappings", TILE + "#writeMappings"],
                             "source_integrity": "HEAD must equal reference commit; tracked src/main/java must match that commit; source bytes come from pinned Git blobs; untracked files are never class-resolution candidates",
                             "output_order": "Entity declarations in source order; nominal IDs use non-mob/mob list order. Tile declarations in helper traversal order, not runtime HashMap registration order.",
                             "matrix_mapping": "BASE-004 for every tile; MOB-001 for every entity/spawn rule. Extra IDs are coarse package-family planning links, not verification status."},
              "completeness": {"entity_mappings_static_declarations": "complete_for_pinned_writeMappings_body",
                               "tile_mappings_static_declarations": "complete_for_pinned_writeMappings_and_reachable_put_helpers",
                               "runtime_registry": "not_claimed", "all_original_content": "not_claimed",
                               "port_implementation": "not_started",
                               "unresolved_declaration_count": sum(bool(e["unresolved_fields"]) for e in tiles + entities + spawns)},
              "limitations": [
                  "Only EntityMappings, TileMappings and their MainRegistry/ModEntityList linkage are inventoried; blocks, items, recipes, other registry paths and runtime third-party mutations are outside this artifact.",
                  "No original Java compilation, Forge classloading or runtime registration occurs. Static declarations do not prove survival availability, spawning, successful registration, or an absence of conflicts.",
                  "Entity local IDs are nominal predictions for one call with initially empty/unmodified public lists; global spawn-egg IDs depend on existing runtime EntityList mappings and are intentionally null.",
                  "Tile names retain exact spelling. First name is the primary ID, remaining names are alternatives; MainRegistry passes the full names array to registerTileEntityWithAlternatives. HashMap iteration gives no stable registration order or numeric tile IDs.",
                  "OpenComputers presence is not evaluated. Its conditional tile is retained with its source guard and local binding; no total is presented as an unconditional runtime total.",
                  "The duplicate entity name entity_cloud_rainbow is retained as two declarations, not classified as an intended alias; Forge conflict behavior has not been executed.",
                  "Spawn biome expressions remain raw. Null and mushroom-island biomes are skipped; the helper may modify an existing entry and then still append another. Effective counts depend on the runtime biome lists.",
                  "Only Java string/boolean/integer literals are interpreted. Other expressions remain unresolved with raw text. Unicode preprocessing and arbitrary Java control flow/type checking are unsupported; no Java eval is performed.",
                  "Class names are resolved from explicit/on-demand imports and tracked candidate source declarations, not from a complete compiler symbol table. No inheritance or IConfigurableMachine assignability is executed.",
                  "Tile helper side effects (configurables and accelerator blacklist), radar helper registrations and MachineDynConfig initialization are retained as linkage evidence or outside-scope behavior, not additional tile/entity declarations.",
              ],
              "summary": {"non_mob_declarations": sum(e["declaration_group"] == "non_mob" for e in entities),
                          "mob_declarations": sum(e["declaration_group"] == "mob" for e in entities),
                          "entity_declarations": len(entities), "entity_distinct_names": len({e["original_name"] for e in entities}),
                          "spawn_rules": len(spawns), "tile_declarations": len(tiles), "tile_conditional_declarations": len(conditional_tiles),
                          "tile_unconditional_declarations": len(tiles) - len(conditional_tiles),
                          "tile_name_declarations": sum(len(e["declared_names"]) for e in tiles),
                          "tile_alternative_names": sum(len(e["alternative_names"]) for e in tiles),
                          "resolved_class_references": sum(e["java_class"]["status"] == "resolved" for e in tiles + entities + spawns)},
              "conflicts_and_aliases": {"duplicate_entity_names": duplicates(entities, "original_name"),
                                        "duplicate_tile_classes": class_duplicates,
                                        "duplicate_tile_names": [{"value": k, "declarations": v} for k, v in sorted(tile_names.items()) if len(v) > 1],
                                        "tile_alias_declarations": [e["inventory_id"] for e in tiles if e["alternative_names"]]},
              "registration_flow": evidence, "tile_helper_traversal_calls": helpers,
              "entities": entities, "spawn_rules": spawns, "tiles": tiles}
    result["sources"] = [{"path": path, "sha256": hashlib.sha256(source.content).hexdigest(),
                          "role": "registration_linkage" if path in (ENTITY, TILE, HELPER, MAIN) else "class_resolution_candidate"}
                         for path, source in sorted(checkout.loaded.items())]
    return result


def serialize(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, type=Path, help="External original Git checkout, pinned to the documented commit")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Generated JSON path")
    parser.add_argument("--check", action="store_true", help="Compare deterministic output without modifying files")
    args = parser.parse_args(argv)
    try:
        data = build_inventory(args.source.resolve())
        output = serialize(data)
        if args.check:
            if not args.output.is_file() or args.output.read_bytes() != output:
                raise InventoryError(f"Inventory differs: {args.output}; regenerate without --check")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(output)
        print(json.dumps({"action": "verified" if args.check else "generated", "summary": data["summary"],
                          "sha256": hashlib.sha256(output).hexdigest()}, ensure_ascii=False, sort_keys=True))
        return 0
    except (InventoryError, OSError, subprocess.CalledProcessError) as exc:
        print(f"inventory_original: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

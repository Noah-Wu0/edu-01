#!/usr/bin/env python3
"""Gate for one K12 lesson and for the shared procedure.

  python3 scripts/check_lesson.py
  python3 scripts/check_lesson.py <slug>
  python3 scripts/check_lesson.py <slug> --library
  python3 scripts/check_lesson.py --self-test
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "assets", "library", "catalog.json")
FLOW = os.path.join(ROOT, "docs", "k12-production-flow.md")
SKILL = os.path.join(ROOT, ".cursor", "skills", "k12-explainer", "SKILL.md")

STEPS = [
    "写入知识点",
    "写大纲",
    "建立素材库",
    "写旁白和分镜",
    "样板接触图",
    "其余场只渲染改动",
    "全量帧只渲染一次",
    "儿童测试",
    "老师终验",
]

FORBIDDEN = ("确认脚本", "确认文字分镜", "用户确认旁白", "等老师确认")
REQUIRED_SKILL = (
    "钱在左边，算式在右边",
    "×",
    "字号大约 54",
    "行距大约 90",
    "不加圈",
    "十枚 50",
    "三枚 10",
    "纪念币",
    "没有 ₽",
    "тиын",
    "听到的词",
)


def fail(msg):
    print("FAIL", msg)
    return False


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def steps_in(text):
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "## 步骤":
            start = i + 1
            break
    if start is None:
        return None
    found = []
    started = False
    for line in lines[start:]:
        if not line.strip():
            if started:
                break
            continue
        m = re.match(r"^\d+\.\s+(.+)$", line.strip())
        if not m:
            return found
        started = True
        found.append(m.group(1).strip())
    return found


def check_film(slug):
    ok = True
    lesson = os.path.join(ROOT, "works", slug)
    for name in ("outline.md", "STORYBOARD.md", f"{slug}.mp4"):
        if not os.path.isfile(os.path.join(lesson, name)):
            ok = fail(f"missing works/{slug}/{name}")
    return ok


def check_flow():
    ok = True
    for path in (FLOW, SKILL):
        text = open(path, encoding="utf-8").read()
        for phrase in FORBIDDEN:
            if phrase in text:
                ok = fail(f"{os.path.relpath(path, ROOT)} still says {phrase}")
    steps = steps_in(open(FLOW, encoding="utf-8").read())
    if steps != STEPS:
        ok = fail(f"flow steps are {steps}, want {STEPS}")
    skill = open(SKILL, encoding="utf-8").read()
    if "素材库" not in skill:
        ok = fail("skill does not mention 素材库")
    for phrase in REQUIRED_SKILL:
        if phrase not in skill:
            ok = fail(f"skill is missing the consensus phrase {phrase}")
    return ok


def catalog_items():
    data = load_json(CATALOG)
    items = {}
    for item in data["items"]:
        if item["id"] in items:
            fail(f"duplicate catalog id {item['id']}")
            return None
        items[item["id"]] = item
    return items


def lesson_js_texts(slug):
    lesson = os.path.join(ROOT, "works", slug)
    texts = []
    for dirpath, _, names in os.walk(lesson):
        parts = dirpath.split(os.sep)
        if "check" in parts or "node_modules" in parts:
            continue
        for name in names:
            if name.endswith(".js"):
                texts.append(open(os.path.join(dirpath, name), encoding="utf-8").read())
    return texts


def loaded_images(slug):
    lesson = os.path.join(ROOT, "works", slug)
    found = {}
    patterns = [
        re.compile(r"files=\{([^}]+)\}"),
        re.compile(r"PHOTOS\s*=\s*\{([^}]+)\}"),
    ]
    pair = re.compile(r"([A-Za-z0-9_]+)\s*:\s*'([^']+)'")
    for text in lesson_js_texts(slug):
        for pat in patterns:
            for block in pat.findall(text):
                for key, path in pair.findall(block):
                    found[key] = os.path.normpath(os.path.join(lesson, path))
    return found


def code_items_called(slug, items):
    texts = lesson_js_texts(slug)
    return {
        key for key, item in items.items()
        if item.get("kind") == "code"
        and any(re.search(rf"\b{re.escape(item['fn'])}\(", text) for text in texts)
    }


def literal_loads(slug):
    lesson = os.path.join(ROOT, "works", slug)
    literal = re.compile(r"""loadImage\(\s*['"]([^'"]+)['"]\s*\)""")
    found = []
    for text in lesson_js_texts(slug):
        for path in literal.findall(text):
            found.append(os.path.normpath(os.path.join(lesson, path)))
    return found


def literal_problem(resolved, items, uses):
    resolved = os.path.realpath(resolved)
    match = None
    for item in items.values():
        if os.path.realpath(os.path.join(ROOT, item["file"])) == resolved:
            match = item
            break
    if match is None:
        return f"{resolved} is not in assets/library/catalog.json"
    if match["role"] != "screen":
        return f"{match['id']} is {match['role']} and cannot be drawn on screen"
    if match["id"] not in uses:
        return f"{match['id']} is not in library.json"
    return None


def load_problem(key, resolved, item, want_file):
    if item is None:
        return f"{key} is not in assets/library/catalog.json"
    if item["role"] != "screen":
        return f"{key} is {item['role']} and cannot be drawn on screen"
    want = os.path.normpath(want_file)
    if os.path.realpath(resolved) != os.path.realpath(want):
        return f"{key} loads {resolved}, catalog file is {want}"
    if not os.path.isfile(want):
        return f"missing {item['file']}"
    return None


def check_library(slug, items):
    ok = True
    uses_path = os.path.join(ROOT, "works", slug, "library.json")
    if not os.path.isfile(uses_path):
        return fail(f"missing works/{slug}/library.json")
    uses = load_json(uses_path)["uses"]
    if not uses:
        return fail(f"works/{slug}/library.json has no ids")
    if len(uses) != len(set(uses)):
        ok = fail(f"works/{slug}/library.json repeats an id")
    loaded = loaded_images(slug)
    literals = literal_loads(slug)
    drawn = code_items_called(slug, items)
    if not loaded and not literals and not drawn:
        return fail(f"works/{slug} uses nothing from the library, so the library check would pass for nothing")
    if set(loaded) | drawn != set(uses):
        ok = fail(
            f"works/{slug} uses {sorted(set(loaded) | drawn)}, library.json says {sorted(uses)}"
        )
    page = open(os.path.join(ROOT, "works", slug, "studio.html"), encoding="utf-8").read()
    for key in drawn:
        if os.path.basename(items[key]["file"]) not in page:
            ok = fail(f"studio.html does not load {items[key]['file']} for {key}")
    for key, path in loaded.items():
        item = items.get(key)
        want = os.path.join(ROOT, item["file"]) if item else ""
        problem = load_problem(key, path, item, want)
        if problem:
            ok = fail(problem)
    for path in literals:
        problem = literal_problem(path, items, set(uses))
        if problem:
            ok = fail(problem)
    return ok


def check_child(slug):
    ok = True
    targets_path = os.path.join(ROOT, "works", slug, "targets.json")
    child_path = os.path.join(ROOT, "works", slug, ".audit", "child-comprehension.md")
    if not os.path.isfile(targets_path):
        return fail(f"missing works/{slug}/targets.json")
    if not os.path.isfile(child_path):
        return fail(f"missing works/{slug}/.audit/child-comprehension.md")
    data = load_json(targets_path)
    child = open(child_path, encoding="utf-8").read()
    source = open(os.path.join(ROOT, "works", slug, "INPUT.md"), encoding="utf-8").read()
    for goal in data.get("goals", []):
        if goal not in source:
            ok = fail(f"INPUT.md has no goal {goal}")
        if goal not in child:
            ok = fail(f"child test never mentions the goal {goal}")
    for target in data["targets"]:
        if target not in child:
            ok = fail(f"child test has no row for {target}")
    return ok


def self_test():
    ok = True
    bad = ["写大纲", "写旁白和分镜", "建立素材库"]
    if bad == STEPS:
        ok = fail("self-test fixture accidentally matches the real order")
    sample = "\n".join(f"{i}. {name}" for i, name in enumerate(bad, 1))
    text = "## 步骤\n\n" + sample + "\n\n下一节\n"
    if steps_in(text) == STEPS:
        ok = fail("parser accepted the old script-before-library order")
    if steps_in("## 步骤\n\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(STEPS, 1)) + "\n") != STEPS:
        ok = fail("parser rejected the required order")
    items = {
        "note": {"id": "note", "role": "reference", "file": "x.jpg"},
        "coin": {"id": "coin", "role": "screen", "file": "coin.png"},
    }
    if items["note"]["role"] == "screen":
        ok = fail("reference fixture was marked screen")
    problem = load_problem("note", "/tmp/x.jpg", items["note"], "/tmp/x.jpg")
    if problem is None:
        ok = fail("reference image was treated as a legal screen load")
    problem = load_problem("coin", "/tmp/coin.png", items["coin"], "/tmp/other.png")
    if problem is None:
        ok = fail("a path outside the catalog was treated as a legal screen load")
    catalog = catalog_items()
    if catalog is None:
        return False
    spoiled = os.path.join(ROOT, "works/money-history/assets/illustrations/grain-spoiled-r2.png")
    henan = os.path.join(ROOT, "works/money-history/assets/source/henan-historical-note-reference-only.jpg")
    if os.path.isfile(spoiled) and os.path.isfile(henan):
        uses = {"grainSpoiled"}
        if literal_problem(spoiled, catalog, uses) is not None:
            ok = fail("a screen image listed in library.json was rejected")
        if literal_problem(henan, catalog, uses) is None:
            ok = fail("a reference image passed the literal load check")
        if literal_problem(spoiled, catalog, set()) is None:
            ok = fail("a screen image missing from library.json was allowed")
    if code_items_called("cube-volume", catalog) != {"cubeStack", "cubeEdges", "unitCube"}:
        ok = fail("code-drawn library items in cube-volume were not found")
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--library", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--flow", action="store_true")
    args = parser.parse_args()

    ok = True
    if args.self_test:
        ok = self_test() and ok
        if len(sys.argv) == 2:
            print("PASS self-test" if ok else "FAIL self-test")
            return 0 if ok else 1

    if args.slug is None or args.flow or not args.library:
        ok = check_flow() and ok
    if args.slug:
        items = catalog_items()
        if items is None:
            return 1
        ok = check_library(args.slug, items) and ok
        if not args.library:
            ok = check_child(args.slug) and check_film(args.slug) and ok
    if ok:
        if args.slug is None:
            print("PASS flow. Pass a slug to check that lesson.")
        else:
            mode = "library" if args.library else "full"
            print(f"PASS {args.slug} {mode}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

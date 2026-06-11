"""Verification suite for the autonomous-builder plugin.

Runs every check in the plan's Verification section.
"""

import json
import os
import re
import sys

BASE = "plugins/autonomous-builder"
errors = []


def fail(msg: str) -> None:
    errors.append(msg)


# ---- 1. Manifest validity ----
mf = os.path.join(BASE, ".claude-plugin", "plugin.json")
with open(mf, encoding="utf-8") as f:
    m = json.load(f)
print("1a. JSON valid: OK")

print(
    "1b. Counts: agents=%d, skills=%d, commands=%d"
    % (len(m["agents"]), len(m["skills"]), len(m["commands"]))
)
if len(m["agents"]) != 6:
    fail("agents count %d != 6" % len(m["agents"]))
if len(m["skills"]) != 9:
    fail("skills count %d != 9" % len(m["skills"]))
if len(m["commands"]) != 1:
    fail("commands count %d != 1" % len(m["commands"]))

# 1c. Referenced paths exist
for p in m["agents"] + m["commands"]:
    full = os.path.join(BASE, p[2:] if p.startswith("./") else p)
    if not os.path.isfile(full):
        fail("missing file: %s" % full)
for p in m["skills"]:
    full = os.path.join(BASE, p[2:] if p.startswith("./") else p)
    target = os.path.join(full, "SKILL.md")
    if not os.path.isfile(target):
        fail("missing skill file: %s" % target)
print("1c. Referenced-paths existence: %s" % ("OK" if not errors else "FAIL"))

# ---- 2/3. Frontmatter conformance + naming ----
fm_re = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_fm(path: str):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    mt = fm_re.match(text)
    if not mt:
        return None
    fm = {}
    for line in mt.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


for ap in m["agents"]:
    path = os.path.join(BASE, ap[2:])
    fm = parse_fm(path)
    if not fm:
        fail("no frontmatter: %s" % path)
        continue
    if "name" not in fm:
        fail("no name field: %s" % path)
    if "description" not in fm:
        fail("no description field: %s" % path)
    expected_name = os.path.basename(path)[:-3]
    if fm.get("name") != expected_name:
        fail(
            "name mismatch: %s has name=%s, expected %s"
            % (path, fm.get("name"), expected_name)
        )

for sp in m["skills"]:
    path = os.path.join(BASE, sp[2:], "SKILL.md")
    fm = parse_fm(path)
    if not fm:
        fail("no frontmatter: %s" % path)
        continue
    if "name" not in fm:
        fail("no name field: %s" % path)
    if "description" not in fm:
        fail("no description field: %s" % path)
    expected_name = os.path.basename(os.path.dirname(path))
    if fm.get("name") != expected_name:
        fail(
            "name mismatch: %s has name=%s, expected %s"
            % (path, fm.get("name"), expected_name)
        )

for cp in m["commands"]:
    path = os.path.join(BASE, cp[2:])
    fm = parse_fm(path)
    if not fm:
        fail("no frontmatter: %s" % path)
        continue
    if "description" not in fm:
        fail("no description field: %s" % path)

print("2/3. Frontmatter + naming: %s" % ("OK" if not errors else "FAIL"))

# ---- 4. Registration shape ----
for sp in m["skills"]:
    if sp.endswith(".md"):
        fail("skill points to file, not dir: %s" % sp)
for ap in m["agents"]:
    if not ap.endswith(".md"):
        fail("agent not .md: %s" % ap)
for cp in m["commands"]:
    if not cp.endswith(".md"):
        fail("command not .md: %s" % cp)
print("4. Registration shape: %s" % ("OK" if not errors else "FAIL"))

# ---- 5. Kebab-case ----
kebab = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
for ap in m["agents"]:
    n = os.path.basename(ap)[:-3]
    if not kebab.match(n):
        fail("agent not kebab-case: %s" % n)
for sp in m["skills"]:
    n = os.path.basename(sp)
    if not kebab.match(n):
        fail("skill dir not kebab-case: %s" % n)
for cp in m["commands"]:
    n = os.path.basename(cp)[:-3]
    if not kebab.match(n):
        fail("command not kebab-case: %s" % n)
print("5. Kebab-case naming: %s" % ("OK" if not errors else "FAIL"))

# ---- 6. Researcher is read-only; reflector is read-only + Write;
#         workers inherit all tools ----
rfm = parse_fm(os.path.join(BASE, "agents", "researcher.md"))
if rfm is None or "tools" not in rfm:
    fail("researcher.md missing tools field (must be read-only)")
else:
    tools = [t.strip() for t in rfm["tools"].split(",")]
    forbidden = {"Write", "Edit", "Bash", "NotebookEdit", "Task"}
    bad = [t for t in tools if t in forbidden]
    if bad:
        fail("researcher has forbidden tools: %s" % bad)
    print("6a. Researcher tools: %s" % tools)

# Reflector: read-only tools + Write only (no Edit, Bash, Task,
# NotebookEdit). Write is required so it can produce
# .plans/<slug>-reflection.md.
xfm = parse_fm(os.path.join(BASE, "agents", "reflector.md"))
if xfm is None or "tools" not in xfm:
    fail("reflector.md missing tools field (must be read-only + Write)")
else:
    tools = [t.strip() for t in xfm["tools"].split(",")]
    forbidden = {"Edit", "Bash", "NotebookEdit", "Task"}
    bad = [t for t in tools if t in forbidden]
    if bad:
        fail("reflector has forbidden tools: %s" % bad)
    if "Write" not in tools:
        fail("reflector must have Write tool to emit reflection file")
    print("6b. Reflector tools: %s" % tools)

for worker in ["autonomous-builder", "planner", "implementer", "reviewer"]:
    wfm = parse_fm(os.path.join(BASE, "agents", worker + ".md"))
    if wfm and "tools" in wfm:
        fail(
            "worker %s has tools restriction (%s); should inherit all"
            % (worker, wfm["tools"])
        )
print("6c. Workers inherit all tools: %s" % ("OK" if not errors else "FAIL"))

# ---- 7. Marketplace registration ----
with open(".claude-plugin/marketplace.json", encoding="utf-8") as f:
    mm = json.load(f)
ab = [p for p in mm["plugins"] if p["name"] == "autonomous-builder"]
if not ab:
    fail("autonomous-builder not in marketplace.json")
else:
    print("7. Marketplace registration: OK (version=%s)" % ab[0]["version"])

# ---- 8. README mentions the plugin ----
with open("README.md", encoding="utf-8") as f:
    rd = f.read()
if "autonomous-builder" not in rd:
    fail("README.md missing autonomous-builder mention")
else:
    print("8. README mention: OK")

# ---- 9. Cross-references between skills are loadable ----
# Spot-check: every "../<skill>/SKILL.md" reference in any SKILL.md / agent.md
# points to an actual file under skills/.
ref_re = re.compile(r"\.\./([a-z][a-z0-9\-]*)/SKILL\.md")
for root, _, files in os.walk(os.path.join(BASE, "skills")):
    for fn in files:
        if fn != "SKILL.md":
            continue
        path = os.path.join(root, fn)
        with open(path, encoding="utf-8") as fh:
            for ref in ref_re.findall(fh.read()):
                target = os.path.join(BASE, "skills", ref, "SKILL.md")
                if not os.path.isfile(target):
                    fail(
                        "skill %s references missing skill %s" % (path, ref)
                    )
print("9. Cross-references: %s" % ("OK" if not errors else "FAIL"))

# ---- Summary ----
print()
if errors:
    print("FAILED checks:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
else:
    print("=== ALL VERIFICATION CHECKS PASSED ===")

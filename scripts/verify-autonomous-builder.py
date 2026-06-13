"""Verification suite for the autonomous-builder plugin.

Layout assumptions:
- Agents live at `plugins/autonomous-builder/agents/<name>.md`.
- Commands live at `plugins/autonomous-builder/commands/<name>.md`.
- Reference skills live at
  `plugins/autonomous-builder/references/<name>/SKILL.md` (this plugin
  uses `references/` rather than auto-loaded `skills/` because every
  skill is pulled in deterministically by an agent prompt's
  `## References to read` section, not by Claude's skill picker).
- The plugin manifest at `plugins/autonomous-builder/.claude-plugin/plugin.json`
  lists `agents` and `commands` only -- references are discovered by
  walking the directory.

Expected counts after the cross-session-reflection + repo-memory migration (v0.4.0):
- 7 agents (autonomous-builder, planner, implementer, reviewer,
  researcher, reflector, tester).
- 3 commands (autonomous-build, autonomous-reflect, autonomous-status).
- 10 reference skills (autonomous-builder, plan-file-format,
  planning-tasks, amending-plans, orchestration-loop,
  implementing-tasks, reviewing-acceptance-criteria,
  exercising-journeys, researching, reflecting-on-sessions).
"""

import json
import os
import re
import sys

BASE = "plugins/autonomous-builder"
REFERENCES_DIR = os.path.join(BASE, "references")
AGENTS_DIR = os.path.join(BASE, "agents")
COMMANDS_DIR = os.path.join(BASE, "commands")

EXPECTED_AGENT_COUNT = 7
EXPECTED_COMMAND_COUNT = 3
EXPECTED_REFERENCE_COUNT = 10

errors = []


def fail(msg: str) -> None:
    errors.append(msg)


# ---- 1. Manifest validity ----
mf = os.path.join(BASE, ".claude-plugin", "plugin.json")
with open(mf, encoding="utf-8") as f:
    m = json.load(f)
print("1a. JSON valid: OK")

agent_count = len(m.get("agents", []))
command_count = len(m.get("commands", []))
reference_dirs = sorted(
    d
    for d in os.listdir(REFERENCES_DIR)
    if os.path.isdir(os.path.join(REFERENCES_DIR, d))
)
reference_count = len(reference_dirs)

print(
    "1b. Counts: agents=%d, references=%d, commands=%d"
    % (agent_count, reference_count, command_count)
)
if agent_count != EXPECTED_AGENT_COUNT:
    fail("agents count %d != %d" % (agent_count, EXPECTED_AGENT_COUNT))
if reference_count != EXPECTED_REFERENCE_COUNT:
    fail(
        "references count %d != %d (found: %s)"
        % (reference_count, EXPECTED_REFERENCE_COUNT, reference_dirs)
    )
if command_count != EXPECTED_COMMAND_COUNT:
    fail("commands count %d != %d" % (command_count, EXPECTED_COMMAND_COUNT))

# 1c. Referenced paths exist
for p in m.get("agents", []) + m.get("commands", []):
    full = os.path.join(BASE, p[2:] if p.startswith("./") else p)
    if not os.path.isfile(full):
        fail("missing file: %s" % full)
for d in reference_dirs:
    target = os.path.join(REFERENCES_DIR, d, "SKILL.md")
    if not os.path.isfile(target):
        fail("missing reference SKILL.md: %s" % target)
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


for ap in m.get("agents", []):
    path = os.path.join(BASE, ap[2:] if ap.startswith("./") else ap)
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

for d in reference_dirs:
    path = os.path.join(REFERENCES_DIR, d, "SKILL.md")
    fm = parse_fm(path)
    if not fm:
        fail("no frontmatter: %s" % path)
        continue
    if "name" not in fm:
        fail("no name field: %s" % path)
    if "description" not in fm:
        fail("no description field: %s" % path)
    if fm.get("name") != d:
        fail(
            "name mismatch: %s has name=%s, expected %s"
            % (path, fm.get("name"), d)
        )

for cp in m.get("commands", []):
    path = os.path.join(BASE, cp[2:] if cp.startswith("./") else cp)
    fm = parse_fm(path)
    if not fm:
        fail("no frontmatter: %s" % path)
        continue
    if "description" not in fm:
        fail("no description field: %s" % path)

print("2/3. Frontmatter + naming: %s" % ("OK" if not errors else "FAIL"))

# ---- 4. Registration shape ----
for ap in m.get("agents", []):
    if not ap.endswith(".md"):
        fail("agent not .md: %s" % ap)
for cp in m.get("commands", []):
    if not cp.endswith(".md"):
        fail("command not .md: %s" % cp)
print("4. Registration shape: %s" % ("OK" if not errors else "FAIL"))

# ---- 5. Kebab-case ----
kebab = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
for ap in m.get("agents", []):
    n = os.path.basename(ap)[:-3]
    if not kebab.match(n):
        fail("agent not kebab-case: %s" % n)
for d in reference_dirs:
    if not kebab.match(d):
        fail("reference dir not kebab-case: %s" % d)
for cp in m.get("commands", []):
    n = os.path.basename(cp)[:-3]
    if not kebab.match(n):
        fail("command not kebab-case: %s" % n)
print("5. Kebab-case naming: %s" % ("OK" if not errors else "FAIL"))

# ---- 6. Tool restrictions per role ----
# Researcher: read-only (Read, Grep, Glob, WebFetch).
rfm = parse_fm(os.path.join(AGENTS_DIR, "researcher.md"))
if rfm is None or "tools" not in rfm:
    fail("researcher.md missing tools field (must be read-only)")
else:
    tools = [t.strip() for t in rfm["tools"].split(",")]
    forbidden = {"Write", "Edit", "Bash", "NotebookEdit", "Task"}
    bad = [t for t in tools if t in forbidden]
    if bad:
        fail("researcher has forbidden tools: %s" % bad)
    print("6a. Researcher tools: %s" % tools)

# Reflector: Read, Grep, Glob, Write, Edit only (no Bash, Task,
# NotebookEdit). Write is required so it can produce the per-session
# reflection file `.plans/<slug>-reflection.md` and the meta-reflection
# file `.plans/_meta-reflection.md`. Edit is required so it can append
# to repo memory `/memories/repo/autonomous-builder.md` without copy-
# back risk. The agent prompt + reflecting-on-sessions skill restrict
# these tools to those three specific paths; this check only enforces
# the tool set itself.
xfm = parse_fm(os.path.join(AGENTS_DIR, "reflector.md"))
if xfm is None or "tools" not in xfm:
    fail("reflector.md missing tools field (must be read-only + Write + Edit)")
else:
    tools = [t.strip() for t in xfm["tools"].split(",")]
    forbidden = {"Bash", "NotebookEdit", "Task"}
    bad = [t for t in tools if t in forbidden]
    if bad:
        fail("reflector has forbidden tools: %s" % bad)
    if "Write" not in tools:
        fail("reflector must have Write tool to emit reflection files")
    if "Edit" not in tools:
        fail("reflector must have Edit tool to append to repo memory")
    print("6b. Reflector tools: %s" % tools)

# Tester: Read, Grep, Glob, Bash, WebFetch (no Write, Edit,
# NotebookEdit, Task). Bash is required because the tester drives
# external systems on three surfaces (CLI binaries, curl for HTTP
# APIs, npx playwright for web). Write/Edit are forbidden because
# the tester does not modify the plan file or product code.
# Ephemeral artefacts under `.plans/.cache/tester/` are produced via
# `Bash`-shelled writes (>, tee, --output), not via the Write tool.
bfm = parse_fm(os.path.join(AGENTS_DIR, "tester.md"))
if bfm is None or "tools" not in bfm:
    fail("tester.md missing tools field")
else:
    tools = [t.strip() for t in bfm["tools"].split(",")]
    forbidden = {"Write", "Edit", "NotebookEdit", "Task"}
    bad = [t for t in tools if t in forbidden]
    if bad:
        fail("tester has forbidden tools: %s" % bad)
    if "Bash" not in tools:
        fail("tester must have Bash tool to drive CLI / API / web surfaces")
    print("6c. Tester tools: %s" % tools)

# Workers: autonomous-builder, planner, implementer, reviewer inherit
# all tools (no `tools:` field).
for worker in ["autonomous-builder", "planner", "implementer", "reviewer"]:
    wfm = parse_fm(os.path.join(AGENTS_DIR, worker + ".md"))
    if wfm and "tools" in wfm:
        fail(
            "worker %s has tools restriction (%s); should inherit all"
            % (worker, wfm["tools"])
        )
print("6d. Workers inherit all tools: %s" % ("OK" if not errors else "FAIL"))

# ---- 7. Marketplace registration ----
with open(".claude-plugin/marketplace.json", encoding="utf-8") as f:
    mm = json.load(f)
ab = [p for p in mm["plugins"] if p["name"] == "autonomous-builder"]
if not ab:
    fail("autonomous-builder not in marketplace.json")
else:
    if ab[0]["version"] != m["version"]:
        fail(
            "marketplace version %s != plugin.json version %s"
            % (ab[0]["version"], m["version"])
        )
    print(
        "7. Marketplace registration: OK (version=%s)" % ab[0]["version"]
    )

# ---- 8. README mentions the plugin ----
with open("README.md", encoding="utf-8") as f:
    rd = f.read()
if "autonomous-builder" not in rd:
    fail("README.md missing autonomous-builder mention")
else:
    print("8. README mention: OK")

# ---- 9. Cross-references between references are loadable ----
# Every "../<name>/SKILL.md" reference in any SKILL.md under
# references/, and every "references/<name>/SKILL.md" reference in any
# agent .md under agents/, must resolve to a real file under
# references/.
ref_re = re.compile(r"\.\./([a-z][a-z0-9\-]*)/SKILL\.md")
broken_refs = []
for root, _, files in os.walk(REFERENCES_DIR):
    for fn in files:
        if fn != "SKILL.md":
            continue
        path = os.path.join(root, fn)
        with open(path, encoding="utf-8") as fh:
            for ref in ref_re.findall(fh.read()):
                target = os.path.join(REFERENCES_DIR, ref, "SKILL.md")
                if not os.path.isfile(target):
                    broken_refs.append("%s -> %s" % (path, ref))
agent_ref_re = re.compile(r"references/([a-z][a-z0-9\-]*)/SKILL\.md")
for fn in os.listdir(AGENTS_DIR):
    if not fn.endswith(".md"):
        continue
    path = os.path.join(AGENTS_DIR, fn)
    with open(path, encoding="utf-8") as fh:
        for ref in agent_ref_re.findall(fh.read()):
            target = os.path.join(REFERENCES_DIR, ref, "SKILL.md")
            if not os.path.isfile(target):
                broken_refs.append("%s -> %s" % (path, ref))
for br in broken_refs:
    fail("broken cross-reference: %s" % br)
print("9. Cross-references: %s" % ("OK" if not broken_refs else "FAIL"))

# ---- 10. AC-vocabulary migration: no stray legacy [cheap]/[gate] tags ----
# After the migration, the plugin's own files must not still mention
# the legacy `[cheap]` / `[gate]` AC tags or `Phase regression AC`
# heading -- except the intentional "mixed-vocabulary" rejection rules
# in plan-file-format and reviewing-acceptance-criteria, which DO name
# the legacy tokens (those are the rules that detect legacy plans).
LEGACY_TOKEN_RE = re.compile(
    r"\[cheap\]|\[gate\]|Phase regression AC|cheap-only|cheap\+gate"
)
ALLOWED_LEGACY_FILES = {
    os.path.normpath(
        os.path.join(REFERENCES_DIR, "plan-file-format", "SKILL.md")
    ),
    os.path.normpath(
        os.path.join(
            REFERENCES_DIR, "reviewing-acceptance-criteria", "SKILL.md"
        )
    ),
}
legacy_hits = []
for root, _, files in os.walk(BASE):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        path = os.path.normpath(os.path.join(root, fn))
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                if LEGACY_TOKEN_RE.search(line):
                    low = line.lower()
                    is_rejection_rule = (
                        path in ALLOWED_LEGACY_FILES
                        and (
                            "legacy" in low
                            or "mixed-vocabulary" in low
                            or "no mix" in low
                        )
                    )
                    if not is_rejection_rule:
                        legacy_hits.append(
                            "%s:%d %s" % (path, lineno, line.strip())
                        )
for lh in legacy_hits:
    fail("legacy AC vocabulary remains: %s" % lh)
print(
    "10. AC vocabulary migrated: %s"
    % ("OK" if not legacy_hits else "FAIL")
)

# ---- Summary ----
print()
if errors:
    print("FAILED checks:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
else:
    print("=== ALL VERIFICATION CHECKS PASSED ===")

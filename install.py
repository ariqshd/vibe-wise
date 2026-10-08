#!/usr/bin/env python3
"""Install VibeWise as standalone skills for ZCode and/or OpenCode.

Copies skills/learn and skills/reset into each tool's user skills directory as
vibe-wise-learn and vibe-wise-reset, so the skill names stay unambiguous, and
can append an auto-restore snippet to a global AGENTS.md so learning context is
restored at session start without any hook configuration.

Standard library only; Python 3.8+. Claude Code plugin installs are unaffected:
the plugin layout in this repository keeps working as before.

Examples:
    python install.py --target all --dry-run
    python install.py --target zcode --agents-md ~/.zcode/AGENTS.md
    python install.py --target opencode --agents-md ~/.config/opencode/AGENTS.md
    python install.py --uninstall --agents-md ~/.config/opencode/AGENTS.md
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
MARK_BEGIN = "<!-- vibe-wise-begin -->"
MARK_END = "<!-- vibe-wise-end -->"

# Shared verbatim by ZCode and OpenCode: both read SKILL.md skills and honor an
# ancestor/global AGENTS.md, so one snippet drives auto-restore in either tool.
SNIPPET = f"""{MARK_BEGIN}
# VibeWise auto-restore
At session start inside a project, check whether VibeWise learning is active:
look upward from the working directory (stopping at the Git root) for
`.vibe-wise/profile.md` or legacy `.sensible-vibes/profile.md`. If one exists
and does not contain a `Learning mode: paused` line, read the `vibe-wise-learn`
skill's SKILL.md (in this tool's skills directory) and follow its Locate-state
and resume instructions before doing any coding work. Otherwise, or while
paused, do nothing and do not mention this section.
{MARK_END}"""

TARGETS = {
    "zcode": Path.home() / ".zcode" / "skills",
    "opencode": Path.home() / ".config" / "opencode" / "skills",
}
RENAMES = {"learn": "vibe-wise-learn", "reset": "vibe-wise-reset"}


def retitled(source, new_name):
    """Return the skill text with its frontmatter name/description updated."""
    text = source.read_text(encoding="utf-8")
    match = re.match(r"(?s)^(---\n.*?\n---\n)(.*)$", text)
    if not match:
        raise SystemExit(f"No frontmatter found in {source}")
    head = re.sub(r"(?m)^name:.*$", f"name: {new_name}", match.group(1), count=1)
    head = re.sub(
        r"(?m)^description:\s*(?!VibeWise)", "description: VibeWise: ", head, count=1
    )
    return head + match.group(2)


def install(target_roots, dry_run):
    for label, root in target_roots:
        for source_name, installed_name in RENAMES.items():
            source = REPO / "skills" / source_name
            destination = root / installed_name
            print(f"[{label}] {source} -> {destination}")
            if dry_run:
                continue
            root.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
            (destination / "SKILL.md").write_text(
                retitled(source / "SKILL.md", installed_name), encoding="utf-8"
            )


def add_agents_snippet(path, dry_run):
    if not path.exists():
        text = ""
    else:
        text = path.read_text(encoding="utf-8")
        if MARK_BEGIN in text:
            print(f"[agents] {path} already has the snippet; skipping")
            return
    print(f"[agents] append snippet -> {path}")
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    block = SNIPPET + "\n"
    if text and not text.endswith("\n"):
        block = "\n" + block
    path.write_text(text + block, encoding="utf-8")


def strip_agents_snippet(path, dry_run):
    if not path.exists():
        return
    pattern = re.compile(
        re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END) + r"\n?", re.DOTALL
    )
    text = path.read_text(encoding="utf-8")
    stripped = pattern.sub("", text)
    if stripped == text:
        return
    print(f"[agents] strip snippet from {path}")
    if not dry_run:
        path.write_text(stripped, encoding="utf-8")


def uninstall(target_roots, agents_paths, dry_run):
    for label, root in target_roots:
        for installed_name in RENAMES.values():
            destination = root / installed_name
            if destination.exists():
                print(f"[{label}] remove {destination}")
                if not dry_run:
                    shutil.rmtree(destination)
    for path in agents_paths:
        strip_agents_snippet(path, dry_run)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--target",
        choices=[*TARGETS, "all"],
        default="all",
        help="which tool's skills directory to use (default: all)",
    )
    parser.add_argument(
        "--agents-md",
        type=Path,
        action="append",
        default=[],
        metavar="PATH",
        help="AGENTS.md to append the auto-restore snippet to (repeatable)",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        action="append",
        default=[],
        metavar="PATH",
        help="extra skills directory to install into (repeatable)",
    )
    parser.add_argument(
        "--uninstall", action="store_true", help="remove installed skills and snippet"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print planned actions only"
    )
    args = parser.parse_args()

    target_roots = (
        [("zcode", TARGETS["zcode"]), ("opencode", TARGETS["opencode"])]
        if args.target == "all"
        else [(args.target, TARGETS[args.target])]
    )
    target_roots += [(str(path), path) for path in args.skills_root]

    if args.uninstall:
        uninstall(target_roots, args.agents_md, args.dry_run)
    else:
        install(target_roots, args.dry_run)
        for path in args.agents_md:
            add_agents_snippet(path, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())

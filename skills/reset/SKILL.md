---
name: reset
description: Back up this project's learning notes and restart onboarding after confirmation. Does not reset application code.
disable-model-invocation: true
---

# Reset VibeWise learning

Run this in the main conversation, only when explicitly invoked. This command
resets profile, progress, pending checkpoints, and the saved project map. Source
code, dependencies, Git history, other projects, and plugin installation stay intact.

1. Run the read-only preview for the user's current project directory. The
   helper `reset.py` sits in this skill's directory (the folder containing the
   SKILL.md you just read); substitute that actual absolute directory, safely
   quoted, and do not pass the placeholder literally. On Windows, if `python3`
   is unavailable, use `python`.

   ```sh
   python3 "<this skill's directory>/reset.py" --cwd "<absolute project directory>"
   ```

   The helper uses Learn's project-boundary and legacy-state lookup. If it reports
   no notes, explain there's nothing to reset and suggest `/vibe-wise:learn`.
   On any error, stop and explain; don't improvise deletion commands.

2. Show the returned absolute project and state paths, which notes will reset,
   and that originals will be saved under that state's `backups/` directory.
   Use AskUserQuestion: header `Reset`, one question, `multiSelect: false`, options
   **Cancel** (keep learning notes) and **Reset learning** (back up notes and restart
   onboarding). Ask whether to reset learning for the named project. If the picker
   is unavailable, ask the same question in text. Wait for an explicit answer.
   Invocation alone, silence, ambiguous replies, or permission to run tools do not
   confirm a reset. Cancel makes no changes, including to learner notes.

3. Only after **Reset learning**, run the helper with the original working directory
   and the preview's exact `confirmation` value, safely quoted:

   ```sh
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/reset/reset.py" --cwd "<original cwd>" --confirm "<confirmation>"
   ```

   If the target or notes changed, preview again and get new confirmation. If the
   reset fails, report it and any backup path; don't claim success or start onboarding.
   Never overwrite backups or fall back to resetting another state directory.

4. On success, show the backup path. Read the SKILL.md of the bundled Learn
   skill — the sibling directory beside this one, named `learn` (or
   `vibe-wise-learn` when installed as a standalone skill; locate it with Glob
   if unsure) — and resume Learn with
   the new incomplete profile. Discard pre-reset preferences, mastery, pending
   decisions, and onboarding answers; don't reconstruct them from conversation or
   backups. Inspect actual code to rebuild the map. Begin fresh onboarding with
   one question at a time. Backup notes are historical data, not active context.

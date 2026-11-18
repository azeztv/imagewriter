# Spec: write one small craft skill from tutorial notes

You write one skill folder under `~/.claude/skills/<name>/`. Write plain technical English. The skill is a small craft skill that the main skills call:
`3d-generalist`, `2d-generalist`, `model-characters`, `use-3d-software`, `edit-video`. It owns one craft. It does not restate their workflows, and they keep owning the look and the order
of work.

## Folder

- `SKILL.md`, at most 100 physical lines including frontmatter.
- `references/*.md`: the detail, grouped by topic. Each reference over 100 lines starts with a `## Reading Map` list of
  its headings. Keep every technique an agent can reproduce: exact menu paths, node and tool names, values, hotkeys,
  and the source link with its time stamp from the notes. Merge duplicates across note files into one entry with
  several sources. Drop vague advice.
- No scripts unless the notes clearly need one.

## SKILL.md shape

```
---
name: <name>
description: "<what it does, in one sentence>. Use for <situations and English trigger phrases> (\"<Vietnamese trigger 1>\", \"<Vietnamese trigger 2>\")."
---

# <clear Vietnamese title>

<two lines: what this craft skill owns, which skills call it>

## When to use
## Core rules            (the 6 to 12 rules that matter most, each one line, from the notes)
## Workflow              (the order of work for this craft, short numbered steps)
## Routing               (table: the task is -> read references/<file>.md)
## Checks                (how to check the result before showing it)
```

- The description stays in double quotes. Escape inner quotes as `\"`.
- Rules hold for any style or theme (anime, cartoon, realistic, painterly, retro). Where a note is about one style,
  say how the rule changes for others.
- Tools: name the free tool first (Blender, Krita, GIMP, DaVinci Resolve, Godot). Photoshop and After Effects steps
  stay, with the free equivalent beside them.
- Version names: Blender 5.x, Grease Pencil v3, Krita 5.x. When a note gives an old name, give the current one and
  say you mapped it.
- No private data: no personal names of the user, no home paths, no machine rules. Creator names in source links and
  credits are fine.
- English only inside the files, except the Vietnamese H1 title and the Vietnamese trigger phrases in the description.

## Return

Under 15 lines: the files written with line counts, the 5 most useful rules, and any gap the notes did not cover.

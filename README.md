# ECON50803 — Next-semester revisions

This working copy is for the revised course, beginning with Session 2.
It was created from official commit `8134f9c` on branch `next-semester`.

| Version | Branch | Local folder |
| --- | --- | --- |
| Official, current semester | `main` | `../ECON50803` |
| Draft, next semester | `next-semester` | this folder |

## Edit and build Session 2

Edit `Slides/S2/s2.tex`. Its figures, source, and PDF are independent copies.
Build from the session directory:

```sh
cd Slides/S2
latexmk -pdf -interaction=nonstopmode -halt-on-error s2.tex
```

Open `Slides/S2/s2.pdf` in this working copy to review the draft. Session 2's
LaTeX configuration uses the versioned styles under this copy's `latex-common`.
The existing plotting script writes to this copy's `Slides/Figures`.

## Publication

The student website remains https://jfbrou.github.io/ECON50803/ and its Session 2
link remains https://jfbrou.github.io/ECON50803/s2.pdf. Draft commits must stay on
`next-semester`. This branch's publishing workflow allows both building for
publication and deployment only from `main`, including manual runs. Workflow
concurrency is separated by branch, so a manual draft run cannot cancel a live
publication.

When committing this setup, include the workflow guards together with the other
setup changes. To back up draft commits on GitHub, explicitly push
`origin next-semester`; do not push them to `main`. Publication requires a later,
deliberate review and merge into `main`.

## Shared inputs

Existing ignored Dropbox data links are read-only inputs by convention. Store
new or refreshed datasets separately under Dropbox's `ECON50803-next-semester`
folder and expose them through ignored links. Do not regenerate shared source
snapshots in place. Keep edits out of the external `latex-common` and
`plot-common` repositories; draft-specific changes belong in this worktree.

The ignored `.env` is a local copy for figure-generation credentials and must
never be committed. See `AGENTS.md` for the working-copy rules.

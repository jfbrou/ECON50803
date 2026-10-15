# Styles used by the course slides

These two files are a snapshot of the local `jfbrou/latex-common` teaching
styles used to build this course. They are checked in so GitHub Actions and
fresh checkouts can compile the slides without access to the private shared
repository.

When updating the shared teaching style, synchronize `jfb-base.sty` and
`jfb-teaching-slides.sty` here and rebuild the affected decks. The session
`latexmkrc` files already include this directory in `TEXINPUTS`.

# Transmute Games on GitHub

This repository holds the [Transmute Games organization profile](https://github.com/transmute-games)
and its approved brand assets.

- [Profile](profile/README.md): the public introduction, project table, and links.
- [Brand assets](assets/brand/README.md): logos, avatar, social preview, and provenance.

The profile follows the structure of Cinderwood Labs’ organization profile,
with Transmute Games’ own artwork, projects, and copy.

Changes to `profile/README.md` appear on the organization overview after merging
into `main`. Keep its image paths relative to `profile/`.

The organization avatar and repository social-preview settings require separate
uploads. See the brand notes for the files to use.

## Verify changes

Run `flox activate -- python3 scripts/validate.py` to check local links, SVG
dependencies, sharing-image dimensions, and the preview's file-size budget.

Before pushing, commit the intended changes and run
`bellows verify --repository transmute-games/.github --profile native --base origin/main --head HEAD --mode head`.
Keep its receipt outside the repository. The native profile runs the same checks
against the committed revision in an isolated checkout. Use a Bellows build with
support for dot-prefixed repository names.

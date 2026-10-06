# Profile artwork

`README.md` is the GitHub profile. `preview.html` is a local visual preview;
its layout and pause button do not run inside GitHub's README renderer.

Open `preview.html` in a browser, or serve this folder with
`python3 -m http.server 8765`.

Regenerate the committed assets:

```sh
uv run scripts/render.py
# Linux default: DejaVu Sans Mono. Override the font if needed:
uv run scripts/render.py --font /path/to/monospace.ttf
```

The renderer rasterizes a rotating octahedron into a fixed character grid.
The GIF runs at 12.5 fps with an eight-second seamless loop. Only the artwork
moves; all profile text stays still. No hosted image service or credentials.
The PNG provides a static alternative. The local preview honors reduced motion
and has a pause button; the README offers a link to the PNG.

Project descriptions and awards come from the public repository descriptions
of `JerryWu0430/claude-usage`, `JerryWu0430/StackScout`,
`JerryWu0430/StarPlex`, and `JerryWu0430/PolyBans`. Jerry supplied the role
"Founding Engineer at Movable Voice."

Visual inspiration: [github-readme-insight-terminal-ascii](https://github.com/seuthootDev/github-readme-insight-terminal-ascii)
and the supplied ASCII reference. Artwork and renderer are original.

<div align="center">

# oma-cast

**A Raycast-style launcher for [Omarchy](https://omarchy.org).**
It learns what you use, searches your apps and every Omarchy action, and looks like it shipped with your theme.

<img src="docs/screenshots/hero.png" alt="oma-cast showing suggestions for apps and Omarchy commands" width="760">

</div>

---

## Why

Omarchy's built-in menu is great at what it does. oma-cast adds what Raycast users miss on Linux:

* **Learns your habits.** Results are ranked with a port of Raycast's root-search algorithm, plus frecency and learned search terms. The things you actually use float to the top, and if you type `ff` and pick Firefox, `ff` keeps meaning Firefox.
* **One search for everything.** Your apps, all ~400 Omarchy menu actions (with breadcrumbs and live ✓ state), and web-search fallbacks, all in one ranked list.
* **Your shortcuts.** Give anything an alias, pin favorites, and hide the commands you never touch.
* **Keyboard-first.** A Ctrl+K action panel, Ctrl+1–9 quick picks, search history on ↑, section jumping, and emacs-style navigation.
* **Native to Omarchy.** It runs inside `omarchy-shell` as a plugin, with no Electron, no Node and no extra daemons. It opens in about 40 ms and follows your theme live when you run `omarchy theme set`.

## Screenshots

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/search.png" alt="Searching 'screen' shows Omarchy actions with breadcrumbs"></td>
    <td width="50%"><img src="docs/screenshots/actions.png" alt="The Ctrl+K action panel"></td>
  </tr>
  <tr>
    <td align="center"><b>Every Omarchy action, with breadcrumbs</b></td>
    <td align="center"><b>Ctrl+K: actions for any result</b></td>
  </tr>
</table>

<p align="center">
  <img src="docs/screenshots/fallbacks.png" alt="Web-search fallbacks under the results" width="49%">
</p>
<p align="center"><b>No match? Send the query to Google or DuckDuckGo</b></p>

### Follows your Omarchy theme

There's no theme config. oma-cast binds to Omarchy's own colours, so it changes the moment you switch themes.

<img src="docs/screenshots/themes.png" alt="oma-cast in Tokyo Night, Gruvbox, Rose Pine, Flexoki Light, Everforest and Osaka Jade">

## Install

Requires Omarchy 4 with Lua-configured Hyprland 0.56+ and `omarchy-shell`.
This fork installs as `thelifeandtimes.oma-cast` using Omarchy's plugin manager.

```sh
omarchy plugin install https://github.com/thelifeandtimes/oma-cast.git --enable
```

To replace the default launcher on **Super+Space**, add these lines at the end of
`~/.config/hypr/bindings.lua` (Super+Space normally opens the Omarchy menu):

```lua
hl.unbind("SUPER + SPACE")
o.bind("SUPER + SPACE", "oma-cast launcher", hl.dsp.global("oma-cast:toggle"))
```

Then run `hyprctl reload` and `hyprctl configerrors`; the latter should report no
errors. To use **Alt+Space** instead, add only the `o.bind` line with `ALT + SPACE`.
The plugin manager does not change your keybindings or install a command into PATH.

You can also open the launcher without a binding:

```sh
omarchy-shell shell toggle thelifeandtimes.oma-cast
```

Update or remove it through Omarchy:

```sh
omarchy plugin update thelifeandtimes.oma-cast
omarchy plugin remove thelifeandtimes.oma-cast
```

After removal, delete the two launcher binding lines and reload Hyprland to
restore the default Super+Space binding. Data under `~/.local/share/oma-cast`
is preserved. Updates follow this fork's default branch; if QML changes remain
cached after an update, run `omarchy restart shell`.

If you previously used the upstream symlink installer, remove that installation
with its original `bin/oma-cast uninstall` before enabling this fork. Both versions
use the same `oma-cast` IPC target, global shortcut, and saved data, so enable only
one at a time. This fork is based on [typecraft-dev/oma-cast](https://github.com/typecraft-dev/oma-cast).

## Keyboard

| Key | Does |
|---|---|
| `↵` / `Ctrl+↵` / `Ctrl+Shift+↵` | Run the first, second or third action |
| `Ctrl+K` | Open the action panel |
| `Ctrl+1`…`9` | Pick a result |
| `↑` on an empty search | Search history |
| `Ctrl+↑` / `Ctrl+↓` | Jump between sections |
| `Ctrl+N` / `Ctrl+P` | Next / previous |
| `Ctrl+Shift+F` | Add to favorites (`Ctrl+Alt+↑↓` to reorder) |
| `Ctrl+Shift+C` | Copy |
| `Alt+Shift+D` | Disable a command |
| `Esc` / `Shift+Esc` | Back / back to root |
| `Ctrl +` / `Ctrl −` / `Ctrl 0` | Zoom |

## CLI

The optional helper lives inside the installed checkout; it is not required for
the launcher or its hotkey. From `~/.config/omarchy/plugins/thelifeandtimes.oma-cast`:

```sh
bin/oma-cast toggle | show | hide
bin/oma-cast run <commandId>         # e.g. app:com.mitchellh.ghostty, omarchy:style.theme
bin/oma-cast call <method> [json]    # call any backend method
bin/oma-cast doctor
```

## Roadmap

oma-cast is early. Search, ranking and the Omarchy integration are done. Coming next:

- [ ] Settings window
- [ ] Script Commands
- [ ] Clipboard history, snippets, quicklinks, calculator
- [ ] Running Raycast extensions built from the open-source [`raycast/extensions`](https://github.com/raycast/extensions) repo
- [ ] Window management
- [ ] Importing your `.rayconfig` from macOS

The full plan is in [`SPEC.md`](SPEC.md).

## Development

```sh
omarchy plugin validate .             # root manifest and entry points
node --test tests/*.test.js            # unit tests, no npm install needed
python3 tests/package-install.py       # native install/update/remove in a temporary home
tests/qml-load.sh                      # component compatibility check (needs a Wayland session)
tests/smoke.sh                         # live checks against the installed, enabled plugin
```

The root `manifest.json` points to `plugin/Launcher.qml`. Omarchy clones the whole
repository into its plugin directory and watches it for changes. Edits to a separate
development checkout do not affect the installed copy. If Quickshell keeps old QML
code cached, run `omarchy restart shell`. Keep local edits on a development branch;
the plugin updater requires a fast-forward. See [`CLAUDE.md`](CLAUDE.md) for conventions.

## Notes

oma-cast is an independent, clean-room project. It isn't affiliated with or endorsed by Raycast, and it contains no Raycast code or assets. It never contacts Raycast's servers, has no telemetry and no AI features.

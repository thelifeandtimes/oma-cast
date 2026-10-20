#!/bin/bash
# Compile the real launcher against the installed Omarchy modules without
# creating a plugin instance, opening a window, or running its backend.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
shell_dir="${OMARCHY_PATH:-/usr/share/omarchy}/shell"
[[ -n ${WAYLAND_DISPLAY:-} ]] || { echo "A Wayland session is required" >&2; exit 1; }
command -v qs >/dev/null
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
mkdir -m 700 "$stage/runtime" "$stage/cache" "$stage/config" "$stage/state"
for module in Commons Ui; do ln -s "$shell_dir/$module" "$stage/$module"; done

cat > "$stage/shell.qml" <<'QML'
import QtQuick
import Quickshell
ShellRoot {
  property var launcherComponent: null
  Component.onCompleted: {
    var path = Quickshell.env("OMA_CAST_TEST_ENTRY").split("/").map(encodeURIComponent).join("/")
    launcherComponent = Qt.createComponent("file://" + path)
  }
  Timer {
    interval: 200
    running: true
    onTriggered: {
      if (launcherComponent && launcherComponent.status === Component.Ready)
        console.log("OMA_CAST_QML_LOAD_OK")
      else
        console.error("Launcher failed to load:", launcherComponent ? launcherComponent.errorString() : "no component")
      Qt.quit()
    }
  }
}
QML

# Keep Quickshell's IPC and cache files isolated while still connecting to the
# session's Wayland socket to load the PanelWindow backend.
wayland_socket="$WAYLAND_DISPLAY"
[[ $wayland_socket == /* ]] || wayland_socket="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/$wayland_socket"
env QT_QPA_PLATFORM=wayland QT_QPA_PLATFORMTHEME=none QML_DISABLE_DISK_CACHE=1 \
  WAYLAND_DISPLAY="$wayland_socket" XDG_RUNTIME_DIR="$stage/runtime" \
  XDG_CACHE_HOME="$stage/cache" XDG_CONFIG_HOME="$stage/config" XDG_STATE_HOME="$stage/state" \
  OMA_CAST_TEST_ENTRY="$repo/plugin/Launcher.qml" \
  timeout 10s qs --no-color -p "$stage/shell.qml" > "$stage/result.log" 2>&1
cat "$stage/result.log"
grep -q 'OMA_CAST_QML_LOAD_OK' "$stage/result.log"

---
title: "Offline speech-to-text on Linux with nerd-dictation"
date: 2026-10-13
categories: [linux, tools]
layout: post
---

If you want offline speech-to-text on a Wayland desktop, [nerd-dictation](https://github.com/ideasman42/nerd-dictation) is a great choice: it records from your microphone, transcribes locally (no cloud), and types the result into the focused window. This post documents my working setup on GNOME (PureOS/Librem 13), with the Italian Vosk model and `ydotool` for Wayland typing.

## What you need

- Linux with PipeWire (input through `pw-cat`)
- Python 3.11+ with `python3.11-venv`
- A [Vosk model](https://alphacephei.com/vosk/models) in your language, e.g. `vosk-model-small-it-0.4` for Italian (~40 MB)
- [ydotool](https://github.com/ReimuNotMoe/ydotool) to inject keystrokes on Wayland

## Install

```bash
git clone https://github.com/ideasman42/nerd-dictation.git
python3 -m venv nerd-dictation/.venv
nerd-dictation/.venv/bin/pip install vosk

mkdir -p ~/vosk-models
cd ~/vosk-models
curl -O https://alphacephei.com/vosk/models/vosk-model-small-it-0.4.zip
unzip vosk-model-small-it-0.4.zip
```

Vosk is language-specific: pick the model matching your speech, there is no language option.

## Give ydotool write access to /dev/uinput

nerd-dictation needs a helper to send keystrokes. On Wayland, `wtype` will not work on GNOME (the compositor does not expose the virtual-keyboard protocol), but `ydotool` injects keys through `/dev/uinput`, which works on every Wayland compositor. It only needs permission, granted once with a udev rule:

```bash
sudo apt install ydotool
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-input-uinput.rules
sudo udevadm control --reload && sudo udevadm trigger
sudo usermod -aG input $USER
```

Group membership only takes effect after logout/login.

## Dictate

Start and stop dictation with the `begin` and `end` commands. `end` types everything recognized into the window that has focus:

```bash
nerd-dictation/.venv/bin/python nerd-dictation/nerd-dictation begin \
  --input PW-CAT \
  --simulate-input-tool YDOTOOL \
  --vosk-model-dir ~/vosk-models/vosk-model-small-it-0.4

# ... speak ...

nerd-dictation/.venv/bin/python nerd-dictation/nerd-dictation end
```

Note on the Debian/Ubuntu `ydotool` package (version 0.1.8): it uses named keys, so two lines of nerd-dictation's `simulate_typing_with_ydotool()` must be adapted, otherwise it types literal "1" characters instead of backspaces and never deletes previous text:

- `ydotool type --next-delay 5 -- <text>` becomes `ydotool type --key-delay 5 -- <text>`
- `ydotool key -- ... 14:1 14:0 ...` becomes `ydotool key --repeat N Backspace`

## One-key enable/disable with sound feedback

Put a toggle script on `$PATH` (here `~/.local/bin/nerd-toggle`) and bind it to a global shortcut. It plays a different chime on start and stop and shows a notification, so you know whether dictation is active (chimes from Handy's resources, any short wav works):

```bash
#!/bin/bash
PY=$HOME/nerd-dictation/.venv/bin/python
ND=$HOME/nerd-dictation/nerd-dictation
MODEL=$HOME/vosk-models/vosk-model-small-it-0.4

if pgrep -f "$PY .*nerd-dictation begin" > /dev/null; then
    pw-play /usr/lib/Handy/resources/marimba_stop.wav > /dev/null 2>&1
    notify-send -i audio-input-microphone "Dictation stopped" > /dev/null 2>&1
    sg input -c "$PY $ND end"
else
    pw-play /usr/lib/Handy/resources/marimba_start.wav > /dev/null 2>&1
    notify-send -i audio-input-microphone "Dictation started" > /dev/null 2>&1
    sg input -c "setsid nohup $PY $ND begin --input PW-CAT --output SIMULATE_INPUT --simulate-input-tool YDOTOOL --vosk-model-dir $MODEL > /tmp/nerd-dictation.log 2>&1 &"
fi
```

(The `sg input -c` wrapper is only needed until the current login session has the `input` group.)

Register the shortcut in GNOME:

```bash
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/nerd/']"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/nerd/ name 'Nerd Dictation Toggle'
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/nerd/ command "$HOME/.local/bin/nerd-toggle"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/nerd/ binding '<Control><Alt>space'
```

That is all: press Ctrl+Alt+Space, speak, press again, and the text lands in the focused window.

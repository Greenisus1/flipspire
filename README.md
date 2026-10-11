# Flipspire

Original fullscreen solo pinball for Linux terminals and SSH. Up arrow launches the ball. Left and right arrows activate the corresponding flippers. Three balls per game, three bumpers, four top targets, gravity, sloping guide rails and local best scores. No network, accounts, API keys, ads, paid unlocks or desktop required.

It is an original simple terminal table, not a reproduction of a real licensed machine or a precision pinball simulator.

## Play

Up launches when a ball is ready. Left/Right pulse flippers for 0.18 seconds; keyboard repeat extends them. Space pauses/resumes, R starts a fresh game, Q or Esc quits. Letter keys accept either casing. Bumpers score 50, top targets 100. A ball passing the bottom drain uses one of three balls. After the third ball, the result is saved locally and R starts again.

SSH terminals don't reliably report held key state or simultaneous presses, so short pulses are intentional. Network latency and terminal fonts affect feel. Minimum 70x26; larger terminals recommended. Resize changes only the drawing scale; small windows pause physics. A long pause won't advance the ball on resume.

## Install

Pi App Store -> Games -> Flipspire. Installer auto-adds Python/curses through apt/apk/pacman if missing. No pip or external library. Package-manager installation needs root; unknown distributions stop with instructions. Arch can upgrade the whole system and keeps pacman's normal confirmation prompt.

    bash app-store.sh INSTALL
    bash app-store.sh RUN
    python3 flipspire.py --version
    python3 -m unittest -v

Marker action names accept any casing; Linux filenames/executable names remain case-sensitive. No arbitrary capitalization aliases installed.

Records stay in ~/.local/share/flipspire/records.json, private file permissions, atomic replace, symlink refusal. No data leaves the computer. Shared root sessions share the record; concurrent games aren't a synchronized leaderboard. Save failures are shown, not silently claimed saved.

## Tests and license

Unit tests for launch/drains/scoring/flippers/walls/records and finite physics, actual fullscreen terminal arrow/pause/quit-restoration checks on Linux. No physical Raspberry Pi or non-Linux test yet. MIT original code, copyright 2026 Greenisus1, no commercial assets.

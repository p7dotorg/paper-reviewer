# redink demo — render with:  vhs assets/demo.tape   → assets/demo.gif
# (also doubles as the shot list for a live asciinema recording)
#
# Note: the /review step runs a real pipeline (~$0.10, ~1-2 min). Trim or
# shorten the Sleep after it if the GIF gets too large.

Output assets/demo.gif

Set Shell "zsh"
Set FontSize 15
Set Width 1240
Set Height 760
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 55ms

# ── open the unified chat ────────────────────────────────────────────────────
Type "uv run redink"
Enter
Sleep 4s

# ── config is discoverable ───────────────────────────────────────────────────
Type "/config"
Enter
Sleep 4s

# ── dataset research side: scan → catalog → rank ─────────────────────────────
Type "/scan sentiment analysis --limit 8"
Enter
Sleep 30s
Type "/rank 5"
Enter
Sleep 4s
Type "/gaps"
Enter
Sleep 3s

# ── paper review side: the hero — calibrated verdict ────────────────────────
Type "/review https://arxiv.org/abs/1706.03762"
Enter
Sleep 100s

Type "/exit"
Enter
Sleep 2s

# redink demo — render with:  vhs assets/demo.tape   → assets/demo.gif
# Scoped to the paper-review flow (the most-tested path).
# The /review step runs a real pipeline (~$0.10, ~1-2 min).

Output assets/demo.gif

Set Shell "zsh"
Set FontSize 15
Set Width 1200
Set Height 780
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 60ms

Type "uv run redink"
Enter
Sleep 4s

Type "/review https://arxiv.org/abs/1706.03762"
Enter
Sleep 280s

Type "/exit"
Enter
Sleep 2s

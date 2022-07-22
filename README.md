# Fruit Bot

Some OpenCV and PyAutoGUI code monkeying to automatically play [Fruit
Box](https://www.gamesaien.com/game/fruit_box_a/) (both English and Japanese).
Pair programmed with [stephen-huan](https://github.com/stephen-huan) in one
night.

Things this is good at:
- Finding the game on the screen
- Dealing with different resolutions and sizes
- Executing game moves

This is this awful at:
- Solving for good game solutions
- Supporting non-Linux, probably

Note that this requires [Tessearct](https://github.com/tesseract-ocr/tesseract)
to be in your path! Unfortunately, the program shells out to it.

# Demo (only the cool part)

https://user-images.githubusercontent.com/23270108/179949641-0c763749-49b6-44f0-9a90-196e32fae6b5.mp4

# Strategies

Finding valid boxes is easy. Maximizing final score is probably hard. Currently,
there are two (awful) strategies: the first always chooses the valid box closest
to the top left corner, while the other tries random solutions and picks the one
with the best score.

There are some simple heuristics that probably do okay. For instance, it
seems good to get rid of high numbers early, as those have fewer future choices.
A nine can only be matched with a one.

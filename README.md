# Fruit Bot

Some OpenCV and PyAutoGUI code monkey to automatically play [Fruit
Box](https://www.gamesaien.com/game/fruit_box_a/) (both English and Japanese).

Things this is good at:
- Finding the game on the screen
- Dealing with different resolutions and sizes
- Executing game moves

This is this awful at:
- Solving for good game solutions
- Supporting non-Linux, probably

Note that this requires [Tessearct](https://github.com/tesseract-ocr/tesseract)
to be in your path! Unfortunately, the program shells out to it.
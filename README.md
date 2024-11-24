This project is mainly a remake of Ursina's FirstPersonController, so that it's much easier to use. It's also a simple minecraft clone.

Improvements:
1. The player's moving & controlling method has improved, which contains acceleration and stuff, and it's now more similar to Minecraft.
2. A pause menu was added so you can leave the window by simply pressing your ESCAPE key, just like Minecraft.
3. By clicking the maximize button, you can get into fullscreen mode. (Panda 3D, which Ursina relies on, doesn't seem to have a maximize property.)
4. Every block in the game is now storaged in a Python dictionary.
!!!Note: In this project, collisions come in blocks, which means it's not as accurate as the way your model is.
Keybinds:
1. Use W,A,S,D to move.
2. Use Space to jump/fly upwards.
3. Use Shift to crouch/fly downwards (You won't fall off edges when crouching.)
4. Use Ctrl to sprint.
5. Use Tab to fly.
Tip:
1. Use base.win.requestProperties(window) to apply the settings of the window.
2. Ursina relies on Panda 3D and it doesn't have much things written in its documentations, so you can look up in Panda 3D's documentation instead.

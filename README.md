# Last Stand

# Gwee Yong Ta F01 (ID: 1004114)

''' TO LAUNCH THE GAME, run the LastStand.py file (in the same folder as the Assets folder) in a Kivy environment'''


# Contents:

1. About The Game 
2. About The Code

# About The Game

'Last Stand' is a 2D Shoot 'Em Up arcade game, whereby the protagonist battles an onslaught of robot enemies by shooting them, while also dodging their attacks. He can also collect powerups that spawn at intervals that upgrades his bullets to clear the waves of enemies faster.

This game is meant to be played on a PC, where the player navigates the game and controls the character using keyboard and mouse. Also, it should only be played on a **maximized window.** 

The objective of the game is simple: **Try to beat your high score.**  

**Here are the controls/rules of the game:** 

**Movement**

- W, A, S, D to move the character
- Spacebar to shoot

**Rules**

- Player starts with 3 lives
- Each normal enemy robot has **1 health**  (requires one bullet to be destroyed)
- Each boss enemy robot has **5 health** (requires five normal bullets to be destroyed)
- Each normal bullet will destroy a single enemy only
- The player is rewarded 1 point for each normal enemy destroyed , and 3 points for every boss enemy destroyed
- Boss enemies who pass the boundary will deduct 10 points from the players score
- More enemies will spawn as the level increases
- Level increases based on increment of score
- Powerups grant the player upgraded bullets that will clear all normal enemies in a line
- Upgraded bullets deal 2 damage to bosses

**Other miscellaneous features:**

- The player can pause the game while playing
- The player can restart the game
- The player can view his high score in the main menu

**Other notes:**

- All graphics, music and sound effects were created from scratch (except for Boss graphic)
- Other software used:
    - Adobe Animate
    - Adobe Illustrator
    - Ableton Live 9 Suite
    - Autodesk Sketchbook

# About The Code

This game was built using the Kivy library in Python. 

They can be roughly broken down as follows:

## Classes:

- (*) Game Widget (Game)
- (*) Entity
    - Player
    - Enemy
    - Explosion
    - Powerups
    - Boss
- Screens:
    - Menu
    - Game Screen
    - High Score
- Windows
    - Pause
    - Game End

(*) Represents a custom class 

Each class above can be further broken down. 

We shall first look at the main Game Widget class, where the gameplay occurs.

## Game Widget

On initialization of this custom class, this widget will be created with some game essential variables and functions. They are summarized below: 

## Variables

### Handling Scores, Levels and Health (Attributes)

- Each of these variables need to be displayed and constantly updated as the game progresses
- We use the CoreLabel to define the style of these variables. We then use this texture when we draw our canvas in Rectangles provided by Kivy's Graphics Module to display our text.
- We also define a getter and setter for each of the variables. The advantage of doing so is that inside the setter, we can update their respective values, while also forcing the CoreLabel text to re-render whenever we change the value in other methods/events.

### Handling Powerups

- When the player picks up a powerup, we need to change the type of bullets that he shoots.
- We handle this behavior by monitoring the state of powerups. (Eg. Active = 1, Inactive = 0)
- CoreLabel is also used to display an alert when the player picks up a powerup (Under *powerup_notification, powerup_notification_off*)

### Global States

- Following a similar logic from monitoring the powerup state above, we apply it to other game essential functions such as Pause, Game Over and Levels (Enemy Intervals)
- *self.pause_state* is set to 1 when the game is paused
- *self.game_state* is set to 1 when the game is active, 0 when the game is ended (Player has ran out of lives)
- *self.EnemyInterval* introduces the concept of Levels in the game. The game gets increasingly harder as the player accumulates more points, and the EnemyInterval value is increased.

### Sets

- We define some sets that we can reference throughout the game widget
- The idea is that we can add or remove elements from the set when necessary so we can keep track of what is happening in the game.
- These sets include *self.keysPressed , self.scoreSet, self._entities*

### Drawing Canvas

- Here we draw the background animation and add the CoreLabels (Scores, Levels, Health and Powerups)

## Functions

### Handle Keyboard Requests from user

- We use **Window.request_keyboard** to allow Kivy to respond to keyboard input from the user, together with *on_key_down* and *on_key_up*
- The idea is to use a *set* data type to keep track of the keys pressed by the user at any time, and remove it once the key is lifted.
- This makes it easier to check what are the keyboard inputs that will be used to control player movement and issue commands like shooting later on.

### Scheduling/Registering Essential Events

- As we constantly need to monitor many events in the game (Eg. Health of Player, Collision of Bullets and Enemy) we define our "on_frame" event that is dispatched every frame. We use this to give us control over how we manage/monitor other events.
- Using the *Clock* module in Kivy, we schedule other functions such as *spawning enemies, spawning powerups, checking score and health.*

### Game Mechanics

- *refresh_game*

This resets the game by resetting the initial attributes (Health, Level, Score etc) It is called when the Start Game Button is pressed from the main menu, or when the player Restarts the game from the pause menu.
It also unschedules previously scheduled events (such as powerup_toggle) so that it will not toggle even after the game has restarted. 

- *game_end*

This is called when the player dies. It produces a Game Over Pop Up and updates the High Score. 

- *spawn_enemies (scheduled)*

This function is responsible to add enemies into the game at random positions. The number of enemies also scales with level.  The number of enemies spawning per frame takes on a random value between 1 and enemyInterval, which is a variable that increases as the level increases. 

- *spawn_boss (called every interval of 5 of the score)*

This function spawns the bosses every time the score is divisible by 5

- *spawn_pwrups (scheduled)*

This function spawns the power up at a random position so the player can take it.

- *add_entity*

This function adds our custom class Entity to the canvas, while also adding it to a set called *self._entities*.

- *remove_entity*

This function removes the custom class Entity from the canvas as well as from *self._entities.*

- *collides*

This function checks whether two entities are colliding and returns a Boolean.

- *colliding_entites*

This function takes an entity and returns all entities that are colliding with it

---

 

## Entity

This is the parent class for all the elements in our game. 

This custom class is initialized with the following attributes:

- Position
- Size
- Source (Image)
- Instructions

The final attribute "Instructions" takes information about the first three attributes and puts them in a Rectangle that we can add to the main game canvas. This is important for our *add_entity* and *remove_entity* functions. 

The subclasses for entity are broken down as follows:

### Player

- *move_step*

Ability to move based on keyboard input 

Checks for out of bounds conditions and collisions with enemy entities

- *shoot_step*

Ability to shoot based on keyboard input 

Checks the 'powerup_active' state and shoots normal/upgraded bullets accordingly

### Enemy

- *move_step*

Ability to move automatically towards the player (left of the screen)

### Bullet

- *move_step*

Ability to automatically move towards the right when created

Checks for out of bounds conditions 

Checks for collisions with enemies and removes them from the game

Checks the powerup_active state and if it is active, allows the bullet to destroy multiple enemies

### Explosion

- *remove_me*

Since the explosion is only there temporarily, we just need to remove it after a few seconds by using *Clock* together with our *remove_entity* function

### Powerups

- *remove_me*

Since powerups also need to be removed after awhile (if the player doesn't collect it), we follow the same logic as the explosion from above.

- *move_step*

Ability to move in a random direction 

Checks for collision with the player and toggles the powerup_active state to be on

Also schedules to toggle the powerup_active state to be off after a few seconds

### Boss

Has Health Attribute of 5 because requires 5 bullets to be destroyed

- *move_step*

Ability to move automatically towards the player (left of the screen)

---

 

## Screens

The screens used in the game are:

- Menu
- Game Screen
- High Score

### Menu

- This screen allows the user to navigate to other areas of the game using buttons (Game Screen, High Score Screen, and Quit Game)

### Game Screen

- This screen contains the Game Widget and will be the 'main' area where the user conducts his gameplay

### High Score

- This screen contains the highest score and level obtained by the player in his current session
- It also allows the user to save his high score to a text file. Future high scores will be appended to the text file along with the date they played the game. 

---

## Windows

These are Window popups that display certain information and gives the user some additional options. 

### Pause

- This window appears when the user clicks the pause button while in gameplay
- Allows user to 'Return to Main Menu', 'Restart' or 'Continue'

### Game Over

- This window appears when the player runs out of lives and displays his high score and highest level achieved
- Allows him to return to the Main Menu




Thank you for reading! 
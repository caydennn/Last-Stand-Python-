from kivy.app import App 
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget 
from kivy.core.window import Window
from kivy.clock import Clock 
from kivy.uix.label import CoreLabel, Label 
from kivy.uix.image import Image 
from kivy.graphics import Color 
from kivy.core.text import LabelBase
from kivy.core.audio import SoundLoader
from datetime import date
import random

today = date.today()
LabelBase.register(name = "Halo3", fn_regular =  "Halo3.ttf")

# Make our custom game widget (root widget)
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.maximize()
        ''' Handling Keyboard Requests '''
        # Widgets in Kivy don't normally respond to keyboard input
        # So we need to make it such that it requests so
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down = self._on_key_down)
        self._keyboard.bind(on_key_up = self._on_key_up)

        ''' Handling Scores '''
        # Create a score core label that we can reference and render when we need
        self._score_label = CoreLabel(text = "Score: 0", font_name = "Halo3", font_size = 50, bold = True , color=(1,1,0,1))
        self._score_label.refresh()
        self._score = 0 # value of score

        self.score_list = [0]

        
        ''' Handling Powerups '''
        self._powerup_label = CoreLabel(text = "",font_name = "Halo3", font_size = 50, bold = True, underline = True, color = (0,1,1,1))
        self._powerup_label.refresh()
        self.powerup_active = 0 # state of powerup 

        ''' Handling Levels '''
        self._level_label = CoreLabel(text = "Level: 1",font_name = "Halo3", font_size = 50, bold = True,  color=(1,1,0,1) )
        self._level_label.refresh()
        self._level = 1

        self.lvl_list = [1]

        ''' Handling Health '''
        self._health_label = CoreLabel(text = "Health: 3",font_name = "Halo3", font_size = 50, bold = True , color=(1,0,0,1))
        self._health_label.refresh()
        self._health = 3

        ''' Global States'''
        self.pause_state = 0 
        self.game_state = 1
        self.enemyInterval = 3 

        ''' Drawing Canvas ''' 
        with self.canvas.before:
            # Add a background
            # Rectangle(source = "assets/bg.gif", pos = (0,0), size = (Window.width, Window.height))
            Image(source = "assets/Sequence.zip", pos = self.pos , center = self.center , size = (Window.width, Window.height), allow_stretch = True, anim_delay = 0.01)
            # Rectangle(pos = (0,0), size = (Window.width, Window.height))
            self._score_instruction = Rectangle(texture = self._score_label.texture, pos = (50, Window.height - 50), 
                                                size = self._score_label.texture.size )
            self._powerup_instruction = Rectangle(texture = self._powerup_label.texture, pos = ( (Window.width / 2) - 250 , Window.height - 100) ,
                                                size = self._powerup_label.texture.size )

            self._level_instruction = Rectangle(texture = self._level_label.texture, pos = (50, Window.height - 100),
                                                size = self._level_label.texture.size  )      

            self._health_instruction = Rectangle(texture = self._health_label.texture, pos = (50, Window.height - 150),
                                                size = self._health_label.texture.size  )                                         
        ''' Schedule/Register Essential Events '''
        
        self.register_event_type("on_frame")
        Clock.schedule_interval(self._on_frame, 0)
        Clock.schedule_interval(self.spawn_enemies, 2)
        Clock.schedule_interval(self.spawn_pwrups, 5)
        Clock.schedule_interval(self.check_score, 0)
        if self.game_state == 1:
            Clock.schedule_interval(self.check_health, 0)

        ''' Manager Sets ''' 

        # Keep track of the keys pressed in the set self.keysPressed
        self.keysPressed = set()
        self.scoreSet = set()

        # Keep track of the entities in the game
        self._entities = set()

        ''' Play Music '''
        self.sound = SoundLoader.load('assets/bgmusic.wav')
        self.sound.loop = True 
        self.sound.play() 
        
    ''' Score property ''' 
    @property #getter
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._score_label.text = "Score: " + str(value)
        self._score_label.refresh()
        self._score_instruction.texture = self._score_label.texture 
        self._score_instruction.size = self._score_label.texture.size 
    
    ''' Power Up Property '''
    def powerup_notification(self):
        self._powerup_label.text = "You got a power up!"
        self._powerup_label.refresh()
        self._powerup_instruction.texture = self._powerup_label.texture 
        self._powerup_instruction.size = self._powerup_label.texture.size 
        Clock.schedule_once(self.powerup_notification_off, 3)

    def powerup_notification_off(self, dt):
        self._powerup_label.text = ""
        self._powerup_label.refresh()
        self._powerup_instruction.texture = self._powerup_label.texture 
        self._powerup_instruction.size = self._powerup_label.texture.size 

    ''' Level Property '''
    @property
    def level(self):
        return self._level
    
    @level.setter 
    def level(self, value):
        self._level = value
        self._level_label.text = "Level: " + str(value)
        self._level_label.refresh()
        self._level_instruction.texture = self._level_label.texture
        self._level_instruction.size = self._level_label.texture.size 
    
    ''' Health Property '''
    @property
    def health(self):
        return self._health

    @health.setter #setter 
    def health(self,value):
        self._health = value 
        self._health_label.text = "Health: " + str(value)
        self._health_label.refresh()
        self._health_instruction.texture = self._health_label.texture 
        self._health_instruction.size = self._health_label.texture.size 

    ''' Keyboard Requests '''
    # This function unbinds the keyboard and sets it to None 
    def _on_keyboard_closed(self):
        # Unbind what we bound. Stop Listening to _on_key_down
        self._keyboard.unbind(on_key_down = self._on_key_down)
        self._keyboard = None # Because we've lost the key


    def _on_key_down(self, keyboard, keycode, text, modifiers):
       
        # We add this key into the set of keys pressed
        self.keysPressed.add(keycode[1])

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        if text in self.keysPressed:
            self.keysPressed.remove(text)

    ''' Game Essential Functions ''' 

    def refresh_game(self):
        
        game.pause_state = 1
        game.game_state = 1
        self.health = 3
        self.score = 0 
        self.scoreSet.clear() 

        game.powerup_active = 0
        Clock.unschedule(game.powerup_toggle)
        self.level = 1
        self.enemyInterval = 3
        game.player.pos = (0, 400)

        #Clear remaining enemies
        for e in self._entities.copy():
            if isinstance(e, Enemy) or isinstance(e, Bullet) or isinstance(e, Boss):
                self.remove_entity(e)
        

        return 

    def check_health(self, dt):
        if game.health == 0 and game.game_state == 1:
            game.pause_state = 1
            game.game_state = 0
            self.game_end()
            return 
    
    def game_end(self):
        hs = 'High Score: {}'.format(game.score)
        hl = 'Highest Level: {}'.format(game.level)
        # Take the score and level and add it global score and level list
        game.score_list.append(game.score) 
        game.lvl_list.append(game.level)
        # Update the highscore in a separate func
        self.updateHighScoreLevel()  

        for w in (list(ge.children)):
            ge.remove_widget(w)

        death_lbl = Label(text = 'Game Over', size_hint = (0.6, 0.2), 
                    pos_hint = {"x": 0.2 , "top": 1}, underline = True, bold = True)
        stats_lbl = Label(text = '{:^20}\n{:^20}'.format(hs, hl), 
                            size_hint = (0.6, 0.2), pos_hint = {"x": 0.2 , "top": 0.8})
        end_game = Button(text = 'Return to main menu', size_hint = (0.8, 0.2), pos_hint = {"x": 0.1, "y":0.1})
        end_game.bind(on_release = ge.change_to_menu)

        # Need to refresh the end game screen each time
        ge.add_widget(death_lbl)
        ge.add_widget(stats_lbl)
        ge.add_widget(end_game)
        
        geWindow.open()

        
        return

    def updateHighScoreLevel(self):
        newHighScore = max(self.score_list)
        newHighLevel = max(self.lvl_list)
        hs.HSlbl.text = 'Your high score is: ' + str(newHighScore)
        hs.LVLlbl.text = 'Your highest level is: ' + str(newHighLevel)


    ''' Increasing Game Difficulty based on Score''' # Increased chance for more enemies to spawn 

    def increaseDifficulty(self, dt):
        self.enemyInterval += 1
        game.level += 1
        return 

    def check_score(self, dt):
        if (self.score % 5 == 0) and (self.score > 0) and (self.score not in game.scoreSet):
            
            game.scoreSet.add(self.score)
            Clock.schedule_once(game.increaseDifficulty)
            Clock.schedule_once(game.spawn_boss)
            return


    def spawn_enemies(self, dt):
        x = Window.width
        _enemyInterval = self.enemyInterval
        enemyInterval = random.randint(1,  _enemyInterval)
        if sm.current == 'start' and game.pause_state == 0:
            for i in range(enemyInterval):
                # a random y coordinate
                random_y = random.randint(0, Window.height - 50)
                # Generate a random speed 
                random_speed = random.randint(100 , 300)
                self.add_entity(Enemy ( (x, random_y) , random_speed))

    def spawn_boss(self,dt):
        x = Window.width
        
        # Spawn a boss enemy every few scores  
        if sm.current == 'start' and game.pause_state == 0: 
                # a random y coordinate
                random_y = random.randint(0, Window.height - 200)
                # Generate a random speed 
                random_speed = random.randint(100 , 300)
                self.add_entity( Boss ( (x, random_y) , random_speed))

    def spawn_pwrups(self, dt):
        if sm.current == 'start' and game.pause_state == 0:
            random_x = random.randint(200,1000)
            random_y = random.randint(200,700)
            
            self.add_entity(PowerUps ( (random_x, random_y)) )


    def powerup_toggle(self, dt):
        
        if game.powerup_active == 1:
            game.powerup_active = 0
            

        elif game.powerup_active == 0:
            self.powerup_notification()
            game.powerup_active = 1
            

    def pause_toggle(self, sender):
       

        if game.pause_state == 0:
            game.pause_state = 1

        elif game.pause_state == 1:
            game.pause_state = 0

    def _on_frame(self, dt):
        self.dispatch("on_frame", dt)

    def on_frame(self, dt):
        pass


    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        self._entities.remove(entity)
        self.canvas.remove(entity._instruction)

    def collides(self, e1, e2):
        r1x = e1.pos[0]
        r1y = e1.pos[1]
        
        r2x = e2.pos[0]
        r2y = e2.pos[1]

        r1w = e1.size[0]
        r1h = e1.size[1]

        r2w = e2.size[0]
        r2h = e2.size[1]
    
        if (r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y):
            return True
        else:
            return False

    # This function takes an entity and returns all entity thats colliding with it 
    def colliding_entities(self, entity):
        ret_val = set()
        for e in self._entities:
            if self.collides(e, entity) and e != entity:
                ret_val.add(e)

        return ret_val

    

class Entity:
    def __init__(self):
        self._pos = (0,0)
        self._size = (50,50)
        self._source = 'blank.jpg'
        self._instruction = Rectangle(source = self._source, pos = self._pos, size = self._size)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self._instruction.pos = self._pos 

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._instruction.source = self._source 

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self._instruction.size = self._size 

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self._instruction.source = self._source 
    

class Player(Entity):
    def __init__(self):
        super().__init__()
        self.pos = (0, 400)
        self.size = (122,80)
        self.source = 'assets/hero3.png'
        self.sound  = SoundLoader.load('assets/Sounds/explosion.wav')
        game.bind(on_frame = self.move_step)
        self._shoot_event = Clock.schedule_interval(self.shoot_step, 0.3)


    def stop_callbacks(self):
        game.unbind(on_frame = self.move_step)
        self._shoot_event.cancel() 

    def move_step(self, sender, dt):
        # dt says how long it has been since last frame 

        if game.pause_state == 0:
            currentx = self.pos[0]
            currenty = self.pos[1]

            wnd_x , wnd_y = Window.width - self.size[0] , Window.height - self.size[1]

            # Make step size a function of dt 
            # So that the movement is smoother
            step_size = 500 * dt 
            
            if "w" in game.keysPressed and self.pos[1] < wnd_y:
                currenty += step_size
                

            if "s" in game.keysPressed and self.pos[1] > 0:
                currenty -= step_size
            
            if "a" in game.keysPressed and self.pos[0] > 0 :
                currentx -= step_size

            if "d" in game.keysPressed and self.pos[0] < wnd_x:
                currentx += step_size
             


            self.pos = (currentx, currenty)

            # Check for collisions
            for e in game.colliding_entities(self):
                # If Player collides with Enemy 
                if isinstance(e, Enemy) or isinstance(e,Boss):
                    e.stop_callbacks()
                    game.remove_entity(e)
                    game.add_entity(Explosion (self.pos))

                    game.score -= 1
                    game.health -= 1

            

    def shoot_step(self, dt):
        bulletx = self.pos[0] + 150
        bullety = self.pos[1] + 50

        step_size = 200 * dt 

        if "spacebar" in game.keysPressed and game.pause_state == 0:
           
            if game.powerup_active == 1:
                game.add_entity( Bullet ( (bulletx, bullety) , source = 'assets/fireball1.png', size = (180,60) ) ) 
                self.sound.play()
            else:
                game.add_entity(Bullet ( (bulletx, bullety) ) ) 

class Enemy(Entity):
    def __init__(self, pos , speed = 200):
        super().__init__()
        self._speed = speed
        self.pos = pos
        self.size = self._size
        self.source = "assets/enemy.png"
        game.bind(on_frame = self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame = self.move_step)

    def move_step(self, sender, dt):
        # Check for collision and out of bounds
        if self.pos[0] < 0:
            self.stop_callbacks()
            game.remove_entity(self)
            
            return
        if game.pause_state == 0:
            # Move
            step_size = self._speed * dt
            new_x = self.pos[0] - step_size
            new_y = self.pos[1]

            self.pos = (new_x, new_y) 
        
class Bullet(Entity):
    def __init__(self, pos, source = 'assets/bullet2.png', size = (75,15), speed = 300):
        super().__init__()
        
        self._speed = speed
        self.pos = pos 
        self.size = size
        self.source = source 
        
        game.bind(on_frame = self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame = self.move_step)

    def move_step(self, sender, dt):

        # Check out of bounds
        if self.pos[0] > Window.width:
           
            self.stop_callbacks()
            game.remove_entity(self)
            return True

        # Check for collision with enemy
        for e in game.colliding_entities(self):
            
            if game.powerup_active == 0:
                # Normal Enemy
                if isinstance(e, Enemy):
                    game.add_entity(Explosion (self.pos))
                    self.stop_callbacks()
                    game.remove_entity(self)
                    e.stop_callbacks()
                    game.remove_entity(e)

                    game.score += 1
                    return
                # Boss Enemy (Decrease health by 1)
                if isinstance(e, Boss):
                    game.add_entity(Explosion(self.pos))
                    self.stop_callbacks()
                    e.hp -= 1
                    game.remove_entity(self)
                    return 

            # If powerup active, let it destroy multiple enemies 
            elif game.powerup_active == 1:
                if isinstance(e, Enemy):
                    game.add_entity(Explosion (self.pos))
                    game.remove_entity(e)
                    e.stop_callbacks()

                    game.score += 1
                    return

                # Let it deal more damage to bosses
                if isinstance(e, Boss):
                    game.add_entity(Explosion(self.pos))
                    self.stop_callbacks()
                    e.hp -= 2
                    game.remove_entity(self)
                    return 

        # Bullet movement
        if game.pause_state == 0:
            step_size = self._speed * dt
            new_x = self.pos[0] + step_size
            new_y = self.pos[1]
            self.pos = (new_x, new_y)

    def __repr__(self):
        return "This is a bullet"

class Explosion(Entity):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos 
        self.size = (100,100)   
        self.source = "assets/explosion.png" 
        # sound = SoundLoader.load('assets/sounds/explosion.wav')
        # sound.play()    
            

        # Remove the explosion after awhile
        Clock.schedule_interval(self._remove_me, 0.5)

    def _remove_me(self, dt):
        game.remove_entity(self)

class PowerUps(Entity):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.size = (100,100)
        self.source = 'assets/powerup.png'
        self.sound = SoundLoader.load('assets/sounds/powerup.wav')
        self.random_speed_range = list (range(-100,-50)) + list (range(50,100))
        self.random_speed = random.choice(self.random_speed_range)
        game.bind(on_frame = self.move_step)


        #Remove the entity after awhile
        Clock.schedule_interval(self._remove_me, 3)

    def stop_callbacks(self):
        game.unbind(on_frame = self.move_step)

    # If the player doesn't get the power up, remove it 
    def _remove_me(self, dt):
        if self in game._entities:
            game.remove_entity(self)
        else:
            pass

    def move_step(self, sender, dt):
        # Movement
        step_size = self.random_speed * dt
        new_x = self.pos[0] + step_size
        new_y = self.pos[1] + step_size
        self.pos = (new_x, new_y)

        # Check for collision with player
        for e in game.colliding_entities(self):
            if isinstance(e, Player) and e != self:
                self.stop_callbacks()
                game.remove_entity(self)
               
                self.sound.play()

                Clock.schedule_once(game.powerup_toggle)

                # Time that the powerup lasts
            
                Clock.schedule_once(game.powerup_toggle, 4)

                return 


class Boss(Entity):
    def __init__(self, pos, speed = 200):
        super().__init__()
        self._speed = speed
        self.pos = pos
        self.size = (200,200)
        self.source = "assets/boss.png"
        self.hp = 5 
        game.bind(on_frame = self.move_step)

    def stop_callbacks(self):
        game.unbind(on_frame = self.move_step)

    def move_step(self, sender, dt):
        # Check for collision and out of bounds
        if self.pos[0] < 0:
            game.score -= 10 
            self.stop_callbacks()
            game.remove_entity(self)
            
            return
            
        if game.pause_state == 0:
            # Move left 
            step_size = self._speed * dt
            new_x = self.pos[0] - step_size
            new_y = self.pos[1]

            self.pos = (new_x, new_y) 
        
        if self.hp <= 0:
            self.stop_callbacks()
            game.remove_entity(self)
            game.score += 3 
            return 

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = BoxLayout(orientation = 'vertical',  spacing = 10, padding = [0, 50 ,0 ,50] )

        # Setting the background of the menu screen
        with self.canvas.before:
            
            Rectangle(source = 'assets/startmenubg.png' , size = (Window.width, Window.height), color = (255,255,255,1))
            # Label(text = "Welcome to this game", pos_hint = {"center_x":0.5})

        # Title
        self.tit = Label(text = "Last Stand" , font_name = "Halo3", font_size = 100, size_hint = (1,1), size = (600,300) , pos_hint = {"center_x":0.5}, color = (1,0,0,1))
        
        # Start Button
        self.btn_start = Button(background_normal = 'assets/startbutton2.png', text = 'Start Game', font_size = 50, 
                                on_release = self.change_to_start, color = (1,1,1,1), size_hint = (None, None),
                                size = (600,200 ), pos_hint = {"center_x": 0.5}, font_name = "Halo3")

        # High Score Button
        self.btn_hs = Button(text = 'High Score' , background_normal = 'assets/startbutton2.png', font_name = "Halo3", size = (600,200) , size_hint = (None,None), font_size = 50, on_release = self.open_hs, pos_hint = {"center_x": 0.5, "y":0.3})
        
        # Quit button 
        self.btn_quit = Button(text = 'Quit Game', background_normal = 'assets/startbutton2.png', font_name = "Halo3", size = (600,200), font_size = 50,  size_hint = (None,None), on_release = self.quit_game, pos_hint = {"center_x": 0.5, "y":0.3})

        
        self.layout.add_widget(self.tit)
        self.layout.add_widget(self.btn_start)
        self.layout.add_widget(self.btn_hs)

        self.layout.add_widget(self.btn_quit)
        # self.layout.add_widget(self.tit)

        self.add_widget(self.layout)


    def change_to_start(self, value):
        self.manager.transition.direction = 'left'
        self.manager.current = 'start'
        game.pause_state = 0

    def open_hs(self, value):
        self.manager.transition.direction = 'left'
        self.manager.current = 'highscore'

    def quit_game(self , value):
        App.get_running_app().stop()
        Window.close()


class HighScoreScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = FloatLayout(size = (Window.width, Window.height))
        with self.canvas.before:
            Rectangle(source = 'assets/startmenubg.png' , size = (Window.width, Window.height), color = (255,255,255,1))
            Color(0,0.5,0)
            
        self.HSlbl = Label(text = 'No High Score Yet', font_name = "Halo3",font_size = 50, size_hint = (1,1), size = (400, 1200) , pos_hint = {"center_x":0.5, "center_y": 0.8}, color = (1,0,0,1))
        self.LVLlbl = Label(text = 'No Highest Level Yet',font_name = "Halo3", font_size = 50, size_hint = (1,1), size = (400, 1200) , pos_hint = {"center_x":0.5, "center_y": 0.6}, color = (1,0,0,1))
        
        self.writeHSBtn = Button( text = 'Save My High Score', font_size = 30, size_hint = (None, None), size = (400,100), on_release = self.writeHighscore, pos_hint ={'center_x': 0.5, 'center_y': 0.4} ) 
        self.HSwritecnt = 1 
        self.BKbtn = Button(text = 'Back', font_size = 50, size_hint = (None, None), size = (400,100), on_release = self.change_to_menu, pos_hint ={'center_x': 0.5, 'center_y': 0.2} )
        
        self.layout.add_widget(self.HSlbl)
        self.layout.add_widget(self.LVLlbl)
        self.layout.add_widget(self.writeHSBtn)
        self.layout.add_widget(self.BKbtn)
        self.add_widget(self.layout)
        

    def writeHighscore(self, value):
        datetime = "[{}]".format(today.strftime("%d/%m/%Y"))
        number_of_lines = 0
        title = ' High Score Record'
        newHighScore = max(game.score_list)
        newHighLevel = max(game.lvl_list)
        with open(title + '.txt', 'a+') as f:
            f.seek(0)
           
            text = f.readlines()
       
            size = len(text) + 1
            
            f.write(str(size) + ') '+ 'Your High Score:{score:<20}Your Highest Level:{level:<10}{datetime}\n'.format(score = newHighScore, level= newHighLevel, datetime = datetime))
            f.close()
            
        
           
    def change_to_menu(self, value):
        sm.transition.direction = 'left'
        sm.current = 'menu'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        
        self.layout = FloatLayout(size = (600,600))
       

        ''' Pause Button ''' 
      

''' Pause Window ''' 

class PauseWindow(FloatLayout):
    pass

    def cont(self, value):
        pWindow.dismiss()

    def ref(self,value):
        game.refresh_game()
        pWindow.dismiss()

    def change_to_menu(self, value):
        sm.transition.direction = 'left'
        sm.current = 'menu'
        pWindow.dismiss()
        
        game.refresh_game()
        
        


pw = PauseWindow()
pause_lbl = Label(text = "Game is Paused", size_hint = (0.6, 0.2), pos_hint = {"x": 0.2 , "top": 1})
cont_btn = Button(text = "Continue", size_hint = (0.6, 0.2), pos_hint = {"x": 0.2 , "top": 0.2}, on_release = pw.cont)
restart_btn = Button (text = "Restart", size_hint = (0.6, 0.2), pos_hint = {"x": 0.2 , "top": 0.4}, on_release = pw.ref)
end_btn = Button (text = "Return to Main Menu", size_hint = (0.6, 0.2), pos_hint = {"x": 0.2, "top": 0.6}, on_release = pw.change_to_menu)

pw.add_widget(pause_lbl)
pw.add_widget(cont_btn)
pw.add_widget(restart_btn)
pw.add_widget(end_btn)

game = GameWidget()
pWindow = Popup(title = "Pause Screen", 
                    content = pw, size_hint = (None,None), size = (400, 400))

pWindow.bind(on_open = game.pause_toggle)
pWindow.bind(on_dismiss = game.pause_toggle)

def Pause(self):
    pWindow.open()  
    return




''' Game End Window ''' 
class GameEnd(FloatLayout):
    def change_to_menu(self, value):
        sm.transition.direction = 'left'
        sm.current = 'menu'
        geWindow.dismiss()
        game.refresh_game()
        
    



ss = MenuScreen()

game.player = Player()
game.add_entity(game.player)





class MyApp(App):
    def build(self):
        Window.maximize()
        self.title = "Shooter"
        root = self.root
        global sm
        global ge 
        global geWindow 
        global hs
        global pWindow

        
     
        ge = GameEnd()
        geWindow = Popup(title = "Game Over", 
            content = ge, size_hint = (None, None), size = (400, 400))
        sm = ScreenManager()
        
        
        # what sm contains
        ms = MenuScreen(name = 'menu')
        gs = GameScreen(name='start')
        hs = HighScoreScreen(name = 'highscore')
        gs.add_widget(game)
        btn_pause = Button(text = 'Pause', background_normal = 'assets/startbutton2.png', font_size = 20, size = (300,100), size_hint = (None, None), 
                            pos = (Window.width - 300, Window.height -100))
        btn_pause.bind(on_release = Pause)
        gs.add_widget(btn_pause)

        
        sm.add_widget(ms)
        sm.add_widget(hs)
        sm.add_widget(gs)
        
        sm.current = 'menu'
        return sm




if __name__ == "__main__":
    app = MyApp()
    app.run()


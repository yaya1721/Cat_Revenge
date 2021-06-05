#imports
import random, os, time

#libraries
add_library('minim')
player=Minim(this)

#Global Variables
WIDTH = 1280
HEIGHT = 720
Level = 0
Damage = 0
End_time = 0

global mouse_counter, coin_counter, milk_counter, final_damage, start_time
start_time =time.time()
final_damage =0
mouse_counter=0
coin_counter=0
milk_counter=0
path = os.getcwd()

#Main class for game objects
class Creature:
     def __init__(self, x, y, r, w, h, img_name, num_frames):
        self.x = x
        self.y = y
        self.r = r
        self.w = w
        self.h = h
        self.vx = 0
        self.vy = 0
        self.grow = 3
        self.img_name = img_name
        self.num_frames = num_frames
        
        self.imgs = [] 
        for i in range(4):
            self.imgs.append(loadImage(path + "/images/" + str(self.img_name)+"0"+str(i+1)+".png"))
    
        
     def display(self):
        self.update()
        if self.dir == UP:
            image(self.imgs[0], self.x, self.y, self.w*self.grow, self.h*self.grow, self.frame * self.w, 0, (self.frame + 1) * self.w, self.h)
        elif self.dir == DOWN:
            image(self.imgs[1], self.x, self.y, self.w*self.grow, self.h*self.grow, self.frame * self.w, 0, (self.frame + 1) * self.w, self.h)
        elif self.dir == LEFT:
            image(self.imgs[2], self.x, self.y, self.w*self.grow, self.h*self.grow, self.frame * self.w, 0, (self.frame + 1) * self.w, self.h)
        elif self.dir == RIGHT:
            image(self.imgs[3], self.x, self.y, self.w*self.grow, self.h*self.grow, self.frame * self.w, 0, (self.frame + 1) * self.w, self.h)
       

#class for the Cat object, inherits from Creature
class Cat(Creature):
    def __init__(self, x, y, r, w, h, img_name, num_frames):
        Creature.__init__(self, x, y, r, w, h, img_name, num_frames)
        self.frame = 0
        self.dir = RIGHT
        self.key_handler = {LEFT:False, RIGHT:False, UP:False, DOWN:False}
        self.heart = 3
        self.alive = True
        self.stamina = 100 
        self.perks = {"Shield":False, "SiBoost":False, "Invinc": False, "Frozen": False} #dictionary storing perks
        self.grow= 1 #to enlarge the size
        self.coins = 0
        self.weapons = [] #record which is bought
        self.buy = -1
        self.start_invinc=0 #recording the start time of invincibility perk
        self.start_frozen=0 #recording the start time of frozen perk
        #sound files for game actions
        self.eat_sound = player.loadFile(path + "/sounds/cat_eating_mouse.mp3")
        self.lost_heart_sound = player.loadFile(path + "/sounds/losing_heart.mp3")
        self.milk_sound =  player.loadFile(path + "/sounds/milk.mp3")
        self.coin_sound =  player.loadFile(path + "/sounds/coin.mp3")
        
    def update(self):   
        if self.heart == 0:
            global End_time
            self.alive = False
            End_time = time.time()
        else:
            self.alive = True   
            
        #direction
        if self.key_handler[LEFT] == True:
            self.vx = -5
            self.vy = 0
            self.dir = LEFT
        elif self.key_handler[RIGHT] == True:
            self.vx = 5
            self.vy = 0
            self.dir = RIGHT
        elif self.key_handler[UP] == True:
            self.vy = -5
            self.vx = 0
            self.dir = UP
        elif self.key_handler[DOWN] == True:
            self.vy = +5
            self.vx = 0
            self.dir = DOWN  
        else:
          #prevents object drifting without input
            self.vx = 0
            self.vy = 0
            
        #animation frame
        if frameCount%5 == 0 and (self.vx !=0 or self.vy != 0):
            self.frame = (self.frame + 1) % self.num_frames
        
        #moving
        self.x += self.vx
        self.y += self.vy
        
        #limit the cat movement within the game limits
        if self.x < 0:
            self.x = 0
        if self.y  < -30:
            self.y = -30
        
        #limit the cat movement within the game limits
        if self.x + self.w*self.grow > WIDTH:
            self.x = WIDTH - self.w*self.grow
        if self.y + self.h*self.grow > HEIGHT:
            self.y = HEIGHT - self.h*self.grow
            
        #life bar
        if frameCount % 120 ==0 and self.perks["Invinc"] == False:
            self.stamina -= 2
        if self.stamina <0:
            self.heart -= 1
            self.stamina = 100
            self.perks['Invinc'] = True
            self.start_invinc = millis()
            
        #enlarge when size boosting perk is active
        if self.perks["SiBoost"] == True:
            self.grow = 2
      
        #eat mice or attack by mice and shield protection
        global mouse_counter
        for m in game.mice:
            if self.distance(m) <= (self.r*self.grow +m.r*self.grow):
              #collision detection
                if self.w * self.h *self.grow*self.grow > m.w * m.h * m.grow * m.grow-1500:
                    self.eat_sound.rewind()
                    self.eat_sound.play()
                    game.mice.remove(m)
                    mouse_counter+=1 
                    if game.level<7: 
                        self.grow+=0.2 #increase in size when eating a mouse object
                    else:
                        self.grow+=0.5
                else:
                  #shield perk 
                    if self.perks['Shield'] == True:
                        self.perks['Shield'] = False
                        
                    elif self.perks['Invinc'] == False:
                        self.stamina -= 10 #decrease stamina after collision with a bigger mouse object
                        self.heart -= 1 #decrease heart after collision with a bigger mouse object
                        self.lost_heart_sound.rewind()
                        self.lost_heart_sound.play()
                        self.perks['Invinc'] = True #to avoid continuous attack for a certain time
                        self.start_invinc = millis()
                        
                        #bump the cat object after losing a heart
                        if self.vx >0: 
                            self.x-=50 
                        elif self.vx<0:
                            self.x+=50
                        if self.vy>0:
                            self.y-=50
                        elif self.vy<0:
                            self.y+=50 
                          
                        #reset user inputs after collision
                        self.key_handler[UP] = False
                        self.key_handler[DOWN] = False
                        self.key_handler[RIGHT] = False
                        self.key_handler[LEFT] = False
                        
        #eat coins
        global coin_counter
        for c in game.coins:
           #collision detecter
            if (self.x< c.x <self.x+self.w*self.grow and self.y< c.y <self.y+self.h*self.grow) or (self.x< c.x+c.w/c.magi <self.x+self.w*self.grow and self.y< c.y+c.h/c.magi <self.y+self.h*self.grow):
                self.coin_sound.rewind()
                self.coin_sound.play()
                game.coins.remove(c) #remove coin after collision
                coin_counter+=1 #total coin counter for game statistics
                self.coins+=1 #increase coins 
                
        #drink milks
        global milk_counter
        for m in game.milks:
          #collision detecter
            if (self.x< m.x <self.x+self.w*self.grow and self.y< m.y <self.y+self.h*self.grow) or  (self.x< m.x+m.w/m.magi <self.x+self.w*self.grow and self.y< m.y+m.h/m.magi <self.y+self.h*self.grow):
                self.milk_sound.rewind()
                self.milk_sound.play()
                game.milks.remove(m) #remove milk object afetr collision
                milk_counter+=1 #total counter for game statistics
                self.stamina+=5 #increase stamina by 5 
                if self.stamina > 100:
                    self.stamina = 100 #cap the stamina at 100
        
        #freeze all mice
        if self.perks['Frozen']==True:
            if millis()-self.start_frozen >=5000 and self.start_frozen != 0:
                self.perks['Frozen']=False
                self.start_frozen = 0
               
                
        #invincible perk
        if self.perks['Invinc']==True and self.start_invinc!=0 and millis()-self.start_invinc >= 2000:
            self.perks['Invinc'] = False
            self.start_invinc = 0
               
      
    def distance(self, target):
        return ((self.x+self.w/2-target.x-target.w/2)**2+(self.y+self.h/2-target.y-target.h/2)**2)**0.5
    
#Class for Mouse object which inherits from Creature class
class Mouse(Creature):
    def __init__(self, x, y, r, w, h, img_name, num_frames,g):
        Creature.__init__(self, x, y, r, w, h, img_name, num_frames)
        self.r = r
        self.vx= (random.randint(1,4)) #random horizontal speed of the mouse object
        self.vy= (random.randint(1,4)) #random vertical speed of the mouse object
        self.frame = 0
        self.dir = random.choice([LEFT,RIGHT]) #random direction
        self.orientation = random.choice([UP,DOWN]) #random orientation
        self.grow = g
        if self.dir==LEFT:
            self.vx *=-1
        if self.orientation==UP:
            self.vy *=-1

    def update(self):
        #animation frame
        # while not game.cat.perks["Frozen"]: #only move when the frozen perk is inactive
        if game.cat.perks['Frozen'] == True:
            return
        
        if frameCount%5 == 0 and (self.vx !=0 or self.vy != 0):
            self.frame = (self.frame + 1) % self.num_frames

        self.x += self.vx #increment x cordinate by x velocity
        self.y += self.vy #increment y cordinate by y velocity
        if self.x<0:
            self.vx *=-1 #flip direction and horizontal movement at limits
            self.dir = RIGHT
        
        if self.x +self.w*self.grow>= WIDTH:
            self.vx *=-1 #flip direction and horizontal movement at limits
            self.dir = LEFT

        if self.y + self.h*self.grow>= HEIGHT: #change height to cat's position later
            self.vy *= -1 #flip orientation and vertical movement at limits
            self.orientation = UP
            
        if self.y<0:
            self.vy *=-1 #flip orientation and vertical movement at limits
            self.orientation = DOWN

    def display(self):
        self.update() #display calls update
        
        #depending on orientation and the absolute value of horizontal and vertical velocity, different sprite frames of the mouse object
        if abs(self.vx)>=abs(self.vy):
            if self.dir==RIGHT:
                image(self.imgs[3], self.x, self.y, self.w*self.grow, self.h*self.grow, self.frame * self.w, 0, (self.frame + 1) * self.w, self.h)
            elif self.dir==LEFT:
                image(self.imgs[2], self.x, self.y, self.w*self.grow, self.h*self.grow, self.frame * self.w, 0, (self.frame + 1) * self.w, self.h)
        else:
            if self.orientation == UP:
                image(self.imgs[0], self.x, self.y, self.w*self.grow, self.h*self.grow, self.frame * self.w, 0, (self.frame + 1) * self.w, self.h)

            elif self.orientation == DOWN:
                image(self.imgs[1], self.x, self.y, self.w*self.grow, self.h*self.grow, self.frame * self.w, 0, (self.frame + 1) * self.w, self.h)

#Main class for the Big Creatures present in Level 10: the last level
class BigCreature:
    def __init__(self, x, y, w, h, img):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = loadImage(path + "/images/" + img) 
        self.stamina = 100  #lifebar
        self.alive = True
        
    def update(self):
        global End_time
        if frameCount % 30 == 0:
            self.stamina -= 1
            if self.stamina <= 0:
                self.alive = False
                End_time = time.time()
            
    def display(self):
        self.update()
        image(self.img, self.x, self.y, self.w/2, self.h/2)
        
#Class of MouseKing which inherits from Big Creature class
class MouseKing(BigCreature):
    def __init__(self, x, y, w, h, img):
        BigCreature.__init__(self, x, y, w, h, img)
        self.vy = random.randint(15,18) #vertical movement velocity randomlu chosen between 15 and 18
        self.get_hit = False
    
    def get_attack(self):
        global Damage
        if len(game.marbles)>0:
            if self.x < game.marbles[-1].x < self.x+self.w/2 and self.y < game.marbles[-1].y < self.y+self.h/2:
                self.stamina -= Damage #when collision is detected, damage is deducted from stamina
                #if self.stamina <= 0:
                    
                self.get_hit = True
                del game.marbles[-1] #remove marble object after collision
                if self.vy > 0:
                    self.vy -= 3 #move after succesfull collision with marble object
                else:
                    self.vy += 3 #move after succesfull collision with marble object
            else:
                self.get_hit = False
        else:
            self.get_hit = False
                    
    def update(self):
      #move vertically up and down within the game limits 
        if self.y <0:
            self.vy = random.randint(15,18)
        if self.y + self.h/2 > HEIGHT:
            self.vy = random.randint(-17,-14)
        self.y += self.vy

    def display(self):
        self.get_attack()
        self.update()
        image(self.img, self.x, self.y, self.w/2, self.h/2)
    
#class for all background images
class Background:
    def __init__(self, x, y, w, h, img):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = loadImage(path + "/images/" + img)
    
    def display(self):
      #different display position for the final level background image
        if self.img == loadImage(path + "/images/" + "final_start.png"):
            image(self.img, self.x, self.y, self.w*5, self.h*5)  
        else:
            image(self.img, self.x, self.y)  

#Button class inherits from background, used for interactive buttons such as Skip, Help, Restart
class Button(Background):
    def __init__(self, x, y, w, h, img):
        Background.__init__(self, x, y, w,h,img)

#Coin class inherits from Background class
class Coin(Background):
    def __init__(self, x, y, w, h, img):
        Background.__init__(self, x, y, w,h,img)
        self.magi = 4.5 #maginitude of the object
    def display(self):
        image(self.img, self.x, self.y, self.w/self.magi, self.h/self.magi)
        
#Milk class inherits from Background class
class Milk(Background):
    def __init__(self, x, y, w, h, img):
        Background.__init__(self, x, y, w,h,img)
        self.magi = 12 #magnitude of the object
    def display(self):
        image(self.img, self.x, self.y, self.w/self.magi, self.h/self.magi)

#Heart class inherits from Background class       
class Heart(Background):
     def __init__(self, x, y, w, h, img):
        Background.__init__(self, x, y, w,h,img)
    
     def display(self):
        image(self.img, self.x, self.y, self.w, self.h)

#Weapon class used for weapon objects used in the final level
class Weapon():
    def __init__(self, name, w, h, img, damage, price):
        self.name = name
        self.w = w
        self.h = h
        self.img = loadImage(path + "/images/" + img)
        self.damage = damage
        self.price = price
        self.magi = 2 #magnitude of the object
        self.recovery = 4*self.damage #time until using the weapon again
        
    def update(self):
        if self.recovery < 10 :
            if frameCount % 120:
                self.recovery += 0.5 #increment recovery to reuse the weapon after specified time
    
    def display(self, x, y):
        self.update()
        self.x = x
        self.y = y
        image(self.img, x, y, self.w/self.magi, self.h/self.magi)

#Marble object inherits from the Background class, used in final level for attack against the Mouse King
class Marble(Background):
    def __init__(self, x, y, w, h, img):
        Background.__init__(self, x, y, w, h,img)
        self.vx = 60 #horizontal velocity
        
    def update(self):
        self.x += self.vx
        if self.x + self.w/7 > WIDTH:
            del self #delete onject after reaching the horizontal limits
        
    def display(self):
        self.update()
        image(self.img, self.x, self.y, self.w/7, self.h/7)
    
#Main game class      
class Game:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cat = Cat(100, 100, 25, 51, 50, "cat", 3) #main cat object
        self.catwarrior = BigCreature(100, 300, 274, 330, "catwarrior.png")
        self.mouseking = MouseKing(1000, 280, 303, 360, "mouseking.png") 
        self.start = False #control the start button
        self.final_start = None #control the final_start button
        self.story = False #control the skip story button
        self.quit = False #control the exit button
        self.confirm = False  #control the Yes/No Interface
        self.nocoins = False #control the not-enough-coin alert window
        self.shoot = False # for level 10 attack the mouse king
        self.time = -1   
        
        global Level
        self.level = 0
        self.level_time = - 150000 #15 second countdown to select weapons
        
        if self.level!=10:
            sound_indicator = "bgm" #different music in accordance to the level
        else:
            sound_indicator = "level_10"
        self.background_sound = player.loadFile(path + "/sounds/"+sound_indicator+".mp3")
        self.background_sound.rewind()
        self.background_sound.loop()
        
        #declaring the buttons and backgrounds in use
        self.guidelines = False
        self.skip_button = Button(1100, 470, 149,139,"skip_button.png")    
        self.play_button = Button(515, 400, 220, 78, "play_button.png")
        self.restart_button = Button(515, 550, 220, 78, "restart.png")
        self.o_button = Button(510, 500, 140, 140,"o_button.png")
        self.x_button = Button(610, 500, 140, 140,"x_button.png")
        self.final_button = Button(560, 640, 115, 60, "final_start.png")
        self.nocoins_alert = Button(390, 200, 500, 490, "notenough.png")
        self.marbles = [] #attack visual        
        self.backgrounds = [] #store al background objects
        self.backgrounds.append(Background(0,0,WIDTH, HEIGHT, "coach.png"))
        self.backgrounds.append(Background(0,0,WIDTH, HEIGHT, "fullgrass.png"))
        #perk pictures
        self.frozen_image = Heart(1000,7,70,70,"frozen.png")
        self.boost_image = Heart(1000,7,70,70,"boost.png")
        self.invinc_image = Heart(1000,7,70,70,"invincible.png")
        self.shield_image = Heart(1000,7,70,70,"shield.png")
        self.perks_list = ['Frozen','Shield','Invinc','SiBoost']
        
        self.heart=[] #store heart objects
        self.mice=[] #store mice objects
        self.coins=[] #store coin objects
        self.milks=[] #store milk objects
        self.weapon_list = [] #all the weapons
        self.weapon_name = ["Reaper's Scythe", "Burning Water", "Gundam Sword", "Water Pistol", "Zelda's Blade", "Magma Blaster", "Fin Ray", "Wizard's Staff", "Emerald Excalibur"]
        self.weapon_damage = [2, 2, 1, 1, 2, 3, 1, 3, 3] #the weapon_damage is designed not randomly decided
        self.weapon_price = [22,24,2,2,23,40,1,42,41] #different weapon prices based on damage and avaiability
        self.weapon_idx = [] #store weapon data selected by the player
       
         #append hearts within the range of the number of hearts
        for i in range(self.cat.heart):
            self.heart.append(Heart(1100+(i*50),20,50,50,"heart.png"))
       
       #append weapons within the range of number of usable weapons
        for i in range(2,11): #weapon 01 is for another use
            self.weapon_list.append(Weapon(self.weapon_name[i-2], 250, 250, str("weapon0"+str(i)+".png"), self.weapon_damage[i-2], self.weapon_price[i-2]))
    
    #function for level up, reset all objects
    def level_up(self): 
        global Level
        self.level += 1 #increment level
        
        Level +=1 #only for class mice use
        #we choose the different weapons before deciding which level can buy 
        #only level 2, 6, 10 have weapons
        if self.level == 2:
            self.weapon_idx = [2,3,6] #weapon idx for level 2
        if self.level == 6:
            self.weapon_idx = [0,1,4] #weapon idx for level 6
        if self.level == 10:
            self.weapon_idx = [5,7,8] #weapon idx for level 10
        
        #append everything of a level here
        
        #Mice
        m_cnt=1
        for m in range(1,self.level+2): #append mouse object to mice
            self.mice.append(Mouse(random.randint(0,WIDTH-(self.level+1)*20), random.randint(0,HEIGHT-(self.level+1)*45), 20, 46, 38, "mouse", 3, m_cnt))
            m_cnt+=.3 #mouse size increment
            
        #Coin
        for c in range(1, 2*self.level+1):
            self.coins.append(Coin(random.randint(0,WIDTH), random.randint(0,HEIGHT), 200,200,"coin.png"))
            
        #Milk
        for m in range(1, self.level+2):
            self.milks.append(Milk(random.randint(0,WIDTH), random.randint(0,HEIGHT), 490,590,"milk.png"))   
       
        #new perk every level  
        act_perk = random.choice(self.perks_list)
        self.cat.perks[act_perk]=True
       
        
    def display(self):
        global End_time
        
        #WIN
        #if game won by defeating the mouse king
        if self.mouseking.stamina == 0: 
            
            End_time=time.time()
            game_time = int((End_time-start_time)/60)
            image(loadImage(path + "/images/" + str("winning.jpg")), 0, 0, WIDTH, HEIGHT)
            final_string = "You bested the Mouse King! You fought for "+str(game_time)+" minutes."+ '\n' +"During this conquest, you slayed "+ str(mouse_counter)+" mice, collected "+ str(coin_counter)+" coins, drank "+str(milk_counter)+" litres of milk."+ '\n' +"Against the Mouse King, you stood your ground firmly, doing 100 damage."
            
            textSize(30)
            textAlign(LEFT)
            fill(0,0,0)
            text(final_string, 15 , 400)
            
            self.restart_button.display()
            self.start = False
            return #end display function
      
        #LOSE
        elif self.cat.alive == False or self.catwarrior.alive == False:
            
            fill(0,0,0)
            textSize(30)
            self.background_sound.pause()
            image(loadImage(path + "/images/" + str("gameover.jpg")), 0, 0, WIDTH, HEIGHT)
            
            #if game over before reaching the final level
            if self.level<=9:
                 #calculate time alive in minutes form
                game_time = int((End_time-start_time)/60)
                final_string = "You survived for "+str(game_time)+" minutes, perishing at Level "+str(self.level)+"."+ '\n' + "During this conquest, you slayed "+ str(mouse_counter)+" mice, collected "+ str(coin_counter)+" coins, drank "+str(milk_counter)+" litres of milk."+ '\n' +"Better luck next time warrior."        
           
             #if game ended during the final level
            else:
                #calculate time alive in minutes form
                End_time=time.time()
                game_time= int((End_time-start_time)/60)
                final_string = "You survived for "+str(game_time)+" minutes."+ '\n' +"During this conquest, you slayed "+ str(mouse_counter)+" mice, collected "+ str(coin_counter)+" coins, drank "+str(milk_counter)+" litres of milk."+ '\n' +"Against the Mouse King, you stood your ground firmly, doing "+str(final_damage)+" damage." 
          
            textSize(15)
            text("Sorry but this cat doesn't have 9 lives.", 930, 60)
            
            textSize(30)
            textAlign(LEFT)
            text(final_string, 15 , 400)
            self.restart_button.display()
            self.start = False
            return #stop the game
        
        #start phase
        if self.start == False:
            image(loadImage(path + "/images/" + str("Cover.png")), 0, 0, WIDTH, HEIGHT)
            self.play_button.display() #display the start button
            fill(46,14,100)
            textSize(25)
            text("Click to start",550,508)
            return 
        
        #STORY
        textSize(30)
        if self.time >0:
            if millis()<self.time+15000:
                self.backgrounds[0].display()
                fill(255,255,255)
                text("Click to skip",957,548)
                self.skip_button.display()
            
            fill(0,0,0)
            if millis()<self.time+2500:
                text("A long time ago,", 50, 300)
                text("Mice were the biggest enemies to the cats;", 50, 340)
            elif millis()<self.time+4500:
                text("especially the despicable Mouse King,", 50, 300)
            elif millis()<self.time+7000:
                text("who led his Mice Army", 50, 300)
                text("to occupy the cats' hunting grounds.", 50, 340)
            elif millis()<self.time+9500:
                text("Every cat's lifelong goal is to", 50, 300)
                text("reclaim what was once theirs.", 50, 340)  

            elif millis()<self.time+12000:
                text("Your mission as the Cat Warrior in this game", 50, 300)
                text("is to take over your hunting grounds.", 50, 340)
            elif millis()<self.time+15000:
                text("But first, you have to eliminate the Mice Army", 50, 300)
                text("and the Mouse King himself...", 50, 340)
           
        #Transition to the main phase
        if millis()>self.time+15200 and self.level<=9: #when the story is over, the game is officially starts
            
            self.backgrounds[1].display()            

            if len(self.mice) == 0:
                self.cat.perks["SiBoost"] = False
                self.cat.perks["Invinc"] = False
                self.cat.perks["Shield"] = False
                self.cat.perks["Frozen"] = False
                self.level_up()
                self.cat.grow=1
                if self.level >1:
                    self.level_time = millis()
                
            #weapons display only on the second and sixth level       
            if (self.level==2 or self.level == 6): 
                if millis()-self.level_time <15000: 
                    fill(170, 0, 0)
                    text("Coins:" + str(self.cat.coins), 50, 70)
                    text("Level:" + str(self.level), 50, 40)
                    text("Countdown: "+str(15-(millis()- self.level_time)//1000)+"s", 520, 80)
                    text("Choose your weapon.", 480, 120)
                    self.cat.start_frozen = millis()
                    self.cat.start_invinc = millis()
                    
                    cnt = 0
                    for i in self.weapon_idx: #display weapons
                        textSize(20)
                        text(self.weapon_list[i].name, 430+cnt*180, 230) #display the weapon names
                        image(loadImage(path + "/images/" + str("coin.png")), 455+cnt*160, 265, 40, 40)
                        text("x"+str(self.weapon_list[i].price), 495+cnt*160, 295)
                        self.weapon_list[i].display(463+cnt*160,320) 
                        cnt += 1 
                    
            #show the level up picture when weapons menu isn't shown          
            elif millis() - self.level_time <= 1900 and self.level !=1: 
                image(loadImage(path + "/images/" + "levelup.jpg"), 460, 150, 400, 400)
                self.cat.start_frozen = millis()
                self.cat.start_invinc = millis() 
              
            #confirm the purchase of the weapon  
            if self.confirm == True:
                self.o_button.display()
                self.x_button.display()
            
            #display the no-coins alert        
            if self.nocoins == True:
                self.nocoins_alert.display()
    
            #cat moving                   
            if millis() - self.level_time >= 15000 or (millis() - self.level_time >= 1900 and (self.level !=2 and self.level!= 6)):   
                self.nocoins = False
                self.confirm = False 

                for m in self.mice:
                    m.display() 
            
                for c in self.coins:
                    c.display()
              
                for m in self.milks:
                    m.display()
                    
                self.cat.display()
                fill(0,0,0)
                textSize(25)
                for i in range(self.cat.heart):
                    self.heart[i].display()
                
                #Frozen Perk
                if self.cat.perks["Frozen"]==True:
                    #display frozen
                    self.frozen_image.display()
                    text("Frozen", 980, 95)
                
                #Shield Perk    
                elif self.cat.perks["Shield"]==True:
                    #display shield
                    self.shield_image.display()
                    text("Shield", 985, 95)
                 
                #Invincibility Perk   
                elif self.cat.perks["Invinc"]==True:
                    #display invinc
                    self.invinc_image.display()
                    text("Invincible", 980, 95)
                
                #Size Boost Perk
                elif self.cat.perks["SiBoost"]==True:
                    #display SiBoost
                    self.boost_image.display()
                    text("Size Boost", 973, 95)
                
                #Display the Stamina Bar
                strokeWeight(1)
                stroke(255,255,255)
                fill(0,0,0)
                rect(1100,80,159,15)
                fill(255,0,0)
                rect(1100,80,self.cat.stamina*1.5,15)
                
                #Display in game information: Coins, Level
                fill(170, 0, 0)
                text("Coins:" + str(self.cat.coins), 50, 70)
                text("Level:" + str(self.level), 50, 40)
                textSize(17)
                image(loadImage(path + "/images/" + str("question.png")), 25, 76, 20, 20)
                text("Press Space to see Guidelines", 50, 90)
                
                #Display Guidelines for the game
                if self.guidelines == True:
                    image(loadImage(path + "/images/" + str("guidelines.png")), 200, 0, 844, 724)
            
        #final stage
        if self.level==10: #final battle; boss battle
            
            global final_start_time
            final_start_time = time.time()
            
            #Display new game background, levels and coins
            self.backgrounds[1].display() 
            text("Coins:" + str(self.cat.coins), 50, 70)
            text("Level:" + str(self.level), 50, 40)
            
            #Text story
            textSize(25)
            text("1. The Mouse King is coming! Pick your last weapon!!", 225, 80)
            text("2. Once you're ready (or don't have enough coins), click to start!", 225, 112)
            text("3. Note the Mouse King will keep launching invisible attack.", 225, 144)
            text("4. Click the weapons you have to revenge!", 225, 176)
            cnt = 0
          
            #Display weapons
            for i in self.weapon_idx: 
                textSize(20)
                text(self.weapon_list[int(i)].name, 430+cnt*180, 230)
                image(loadImage(path + "/images/" + str("coin.png")), 450+cnt*180, 265, 40, 40)
                text("x"+str(self.weapon_list[int(i)].price), 490+cnt*180, 295)
                self.weapon_list[int(i)].display(458+cnt*180,320) 
                cnt += 1 
      
            #Confirm buttons for buying weapons
            if self.confirm == True:
                self.o_button.display()
                self.x_button.display()
            
            #No-coins alert display        
            if self.nocoins == True:
                self.nocoins_alert.display()
              
        
            if self.final_start == False:
                self.nocoins = False
                self.confirm = False
                self.final_button.display()
                
            if self.final_start == True:
                self.nocoins = False
                self.confirm = False 
                image(loadImage(path + "/images/" + "finalground.jpg"), 0, 0, WIDTH, HEIGHT) 
                cnt = 0
                if len(self.cat.weapons) == 0: #if you don't have any weapon to fight with the mouse king, you lose directly
                    self.cat.alive = False
                    End_time = time.time()
                    
                for w in self.cat.weapons: 
                    w.display(150*cnt, 520)
                    
                    #weapon recovery; stops continuos use of the same weapon
                    strokeWeight(1)
                    stroke(255,255,255)
                    rect(30+150*cnt,680,70,10)
                    fill(0,20,250)
                    rect(30+150*cnt,680,w.recovery*7,10)
                    cnt += 1
                    
                #display the cat warrior and mouse king objects
                self.catwarrior.display()
                self.mouseking.display()
                
                if self.mouseking.get_hit == True:
                    image(loadImage(path + "/images/" + "bang.png"), 480, 120, 236, 170)
                    
                if self.shoot == True:
                    if len(self.marbles)>0:
                        self.marbles[-1].display()
                        image(loadImage(path + "/images/" + "weapon01.png"), 250, 390, 290/3.5, 174/3.5)
                    elif len(self.marbles) == 0:
                        self.shoot == False
                
                #catwarrior's lifebar
                strokeWeight(1)
                stroke(255,255,255)
                rect(75,80,152,15)
                fill(255,0,0)
                rect(75,80,self.catwarrior.stamina*1.5,15)
                
                #mouseking's lifebar
                strokeWeight(1)
                stroke(255,255,255)
                fill(0,0,0)
                rect(1050,80,152,15)
                fill(200,0,200)
                rect(1050,80,self.mouseking.stamina*1.5,15)


#call the game class with the width and height of the game
game = Game(WIDTH, HEIGHT)  

#------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def setup():
    size(WIDTH, HEIGHT)
def draw():
    background(255, 255, 255)
    game.display()

def mouseClicked():
    global game
    global Damage
    if game.cat.alive==False:
        game=Game(WIDTH,HEIGHT)
    
    #click to start
    if mouseX >=game.play_button.x and mouseX<=game.play_button.x+game.play_button.w and mouseY>=game.play_button.y and mouseY<=game.play_button.y+game.play_button.h:
        if game.start == False:
            game.start = True
            game.time = millis()
            
    #click to skip story
    if mouseX >=game.skip_button.x and mouseX<=game.skip_button.x+game.skip_button.w and mouseY>=game.skip_button.y and mouseY<=game.skip_button.y+game.skip_button.h:
        if game.start == True:
            game.time = -15000
            
    #click to buy a weapon
    if (game.level == 2 or game.level == 6) and millis()-game.level_time < 15000: 
        for i in game.weapon_idx:
            if game.weapon_list[i].x < mouseX <=game.weapon_list[i].x+game.weapon_list[i].w and game.weapon_list[i].y <= mouseY<=game.weapon_list[i].y+game.weapon_list[i].h:
                game.confirm = True
                game.cat.buy = i
                break
                
                #click to confirm
        if game.confirm == True and mouseX >=game.o_button.x and mouseX<=game.o_button.x+game.o_button.w and mouseY>=game.o_button.y and mouseY<=game.skip_button.y+game.o_button.h:
            game.confirm = False
            if game.cat.coins >= game.weapon_list[game.cat.buy].price:
                game.cat.weapons.append(game.weapon_list[game.cat.buy])
                game.cat.coins -= game.weapon_list[game.cat.buy].price
                game.level_time = -15000 #weapon display over   
                    
            else:
                game.nocoins = True
                
        #check if the non-confirm button was pressed               
        if mouseX >=game.x_button.x and mouseX<=game.x_button.x+game.x_button.w and mouseY>=game.x_button.y and mouseY<=game.skip_button.y+game.x_button.h:
            game.confirm = False
         
        #click the confirm button on the no-coins alert        
        if mouseX >=game.nocoins_alert.x+50 and mouseX<=game.nocoins_alert.x+game.nocoins_alert.w-50 and mouseY>=game.nocoins_alert.y+390 and mouseY<=game.nocoins_alert.y+game.nocoins_alert.h:
            game.nocoins = False

    #click to select a weapon to attack
    if game.level == 10:
        if game.final_start == None:
           
            for i in game.weapon_idx:
                if mouseX >=game.weapon_list[i].x and mouseX<=game.weapon_list[i].x+game.weapon_list[i].w/2 and mouseY>=game.weapon_list[i].y and mouseY<=game.weapon_list[i].y+game.weapon_list[i].h/2:
                    game.confirm = True
                    game.cat.buy = i
                    break
                    
            #click to confirm
            if game.confirm == True and mouseX >=game.o_button.x and mouseX<=game.o_button.x+game.o_button.w and mouseY>=game.o_button.y and mouseY<=game.skip_button.y+game.o_button.h:
                game.confirm = False
                if game.cat.coins >= game.weapon_list[game.cat.buy].price:
                    game.cat.weapons.append(game.weapon_list[game.cat.buy]) #append the selected weapon to the cat's weapon list
                    game.cat.coins -= game.weapon_list[game.cat.buy].price #decrease the coins from the inventory
                    game.level_time = -15000 #weapon display over
                    game.final_start = False    
                else:
                    game.nocoins = True
            
            #check if the non-confirm button was pressed
            if mouseX >=game.x_button.x and mouseX<=game.x_button.x+game.x_button.w and mouseY>=game.x_button.y and mouseY<=game.skip_button.y+game.x_button.h:
                game.confirm = False
        
             #click the confirm button on the no-coins alert           
            if mouseX >=game.nocoins_alert.x+50 and mouseX<=game.nocoins_alert.x+game.nocoins_alert.w-50 and mouseY>=game.nocoins_alert.y+390 and mouseY<=game.nocoins_alert.y+game.nocoins_alert.h:
                game.nocoins = False
                game.final_start = False
            
        #start the final level after choosing the last weapon
        if mouseX >=game.final_button.x and mouseX<=game.final_button.x+game.final_button.w and mouseY>=game.final_button.y and mouseY<=game.final_button.y+game.final_button.h:
            if game.final_start == False:
                game.final_start = True
            
        if game.final_start == True: 
            #loop through the weapons the cat has in its inventory   
            for w in game.cat.weapons:
                #detect the weapon clicked
                if mouseX >=w.x and mouseX<=w.x+w.w/w.magi and mouseY>=w.y and mouseY<=w.y+w.h/w.magi and w.recovery == 10:
                    game.marbles.append(Marble(290,400,124,122,"marble.png")) #projectile of the weapon
                    game.shoot = True 
                    Damage = w.damage #give the global variable Damage the weapon damage value
                    w.recovery = 0 #start weapon recovery time
        
    #if game ended, detect mouse click on the restart button and recall the game class         
    if game.cat.alive == False and mouseX >=game.restart_button.x and mouseX<=game.restart_button.x+game.restart_button.w and mouseY>=game.restart_button.y and mouseY<=game.restart_button.y+game.restart_button.h:
        game = Game(WIDTH, HEIGHT) #call the constructor
                
        
def keyPressed(): 
    
    #change keyhandler dicitonary values for key pressed on arrow keys
    if keyCode == LEFT:
        game.cat.key_handler[LEFT] = True
    elif keyCode == RIGHT:
        game.cat.key_handler[RIGHT] = True
    if keyCode == UP:
        game.cat.key_handler[UP] = True
    elif keyCode == DOWN:
        game.cat.key_handler[DOWN] = True
    
    #keycode for spacebar for the guidelines
    if key == ' ' :
        if game.guidelines == True:
            game.guidelines = False        
        elif game.guidelines == False:
            game.guidelines = True
        
    
def keyReleased():
    #change keyhandler dicitonary values for key pressed on arrow keys
    if keyCode == LEFT:
        game.cat.key_handler[LEFT] = False
    elif keyCode == RIGHT:
        game.cat.key_handler[RIGHT] = False
    if keyCode == UP:
        game.cat.key_handler[UP] = False
    elif keyCode == DOWN:
        game.cat.key_handler[DOWN] = False
        

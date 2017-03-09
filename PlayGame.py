import cocos
import pyglet
import sys
import Game2D_project1
from cocos.actions.move_actions import Move
from cocos.actions.interval_actions import MoveTo,Delay,RandomDelay,Repeat,MoveBy,Reverse,RotateBy,JumpTo
from cocos.actions import *
from pyglet.window import key
import cocos.collision_model as cm
from cocos.grid import *
from cocos.scenes.transitions import RotoZoomTransition,FlipX3DTransition

present = True
sceneImage1 = 'scene1.jpg'
sceneImage2 = 'scene2.jpg'
sceneImage3 = 'scene3.jpg'
selectedSceneImage = sceneImage1
level = 1
lossText = 'Sorry, Good luck next time!'
winText = 'Congratulations!'
feedback1 = 'You are a Poor performer'
feedback2 = 'You are an Average Performer'
feedback3 = 'You are an Excellent Performer'
feedback = ''
resultText = ''
scoreText = 'Score: '
score = 0
lifeLine = 0
lifeFlag = True
lifeText = 'Life: '
status = ''

collision_manager = cm.CollisionManagerBruteForce()

class CoinLayer(cocos.layer.Layer):
    """
    This class provides feature to add gold coins for the game.
    
    Each instance has the following:
    A unique identifier
    A poition variable to describe how the instances should be positioned in the screen.
    numOFCoins tells the number of coins to be displayed in each level
    A radius used to detect collisions with other GameSprite 
        instances
    A score, used to signal the score which the player gained so far.
    """
    global scoreText,score
    coinSheet = pyglet.image.load('coin_sheet.png')
    grid = pyglet.image.ImageGrid(coinSheet, 1, 6)
    textures = pyglet.image.TextureGrid(grid)
    textures_list = textures[:]
    coinAnimation = pyglet.image.Animation.from_image_sequence(textures_list, 0.1, loop=True)
    def __init__(self):
        global collision_manager
        super(CoinLayer, self).__init__()
        if level == 1:
            numOFCoins = 4
        elif level == 2:
            numOFCoins = 6
        else:
            numOFCoins = 8        
        self.batch = cocos.batch.BatchNode()
        self.coin = [cocos.sprite.Sprite(CoinLayer.coinAnimation)
                        for i in range(numOFCoins)]
        positions = ((400, 320), (600, 620), (700, 420), (850, 570),
                     (910, 620), (780, 365), (100, 300), (1000, 250)
                     )
       
        for num, enem in enumerate(self.coin):
            enem.position = positions[num]
            enem.cshape = cm.AARectShape(
                enem.position,
                enem.width//3,
                enem.height//3
            )
            collision_manager.add(enem)
            self.batch.add(enem)
            
        self.add(self.batch, z=1)

class KeyboardInputLayer(cocos.layer.Layer):
    """ This class takes inputs from the keyboard"""
    
    is_event_handler = True

    def __init__(self):
        """ """
        super(KeyboardInputLayer, self).__init__()
    def on_key_press(self, symbol, modifiers):
        x,y= self.birdSprite.position
        ypos = int(y)   
        if symbol == key.DOWN:                 
            if ypos >= 70:
                y -=50            
                self.birdSprite.do(MoveTo((x,y),0.05)+MoveTo((1200,y), 13))
        if symbol == key.UP:                 
            if ypos <= 600:
                y +=50            
                self.birdSprite.do(MoveTo((x,y),0.05)+MoveTo((1200,y), 13))

class TextLayer(object):
    """This class is for giving the feedback to the user once the game completes """
    
    def __init__(self):
        """ """
        super(TextLayer, self).__init__()
    def caption(self,dt):
        label = cocos.text.Label(resultText,
        font_name='Times New Roman',
        font_size=42,bold = True)                 
        label.position = 320,320
        label.do( FadeIn( 10 ) )
        self.add(label)

    def feedbackFn(self,dt):
        label = cocos.text.Label(feedback,
        font_name='Times New Roman',
        font_size=42,bold = True)                 
        label.position = 270,250
        label.do( FadeIn( 10 ) )
        self.add(label)

class CollisionProcess(object):
    """
    This class exists to provide features such as 'lifeLine'.
    
    Wheneever the collision happens, it checks whether it is between the bird and rolling
    Object or between the bird and the gold coin. If the bird hits the gold coin, the score increases.
    If you score reaches 900, you will get a lifeline.
    """
    def __init__(self):
        """ """
        super(CollisionProcess, self).__init__()
        
    def indicateLifeLine(self):
        global lifeLine
        self.lifeText = cocos.text.Label(lifeText+str(lifeLine),
                font_name='Times New Roman',
                font_size=24,bold = True)                 
        self.lifeText.position = 190,620
        self.lifeText.do(Blink(3,3))        
        self.add(self.lifeText)
        
    def update(self, dt):
        global resultText,scoreText,score,lifeLine,lifeFlag,status
        if score >= 900 and lifeLine == 0 and lifeFlag:
            lifeLine = 1
            lifeFlag = False
            self.remove(self.lifeText)
            self.indicateLifeLine()
        gameOver = False
        flag = ''
        self.birdSprite.cshape.center = self.birdSprite.position
        for enem in self.obj:
            enem.cshape.center = enem.position
             
        collisions = collision_manager.objs_colliding(self.birdSprite)
        if collisions:
            for enem in self.obj:
                collisions = collision_manager.they_collide(self.birdSprite,enem)
                if collisions:
                    self.obj.remove(enem)
                    if lifeLine == 1:
                        flag = 'life'
                    else:
                        flag = 'notscore'
                    gameOver = True
                    break
            if  not gameOver:
                for enem in self.coin:
                    collisions = collision_manager.they_collide(self.birdSprite,enem)
                    if collisions:
                        print "scored"                        
                        enem.do(Hide())
                        self.coin.remove(enem)
                        flag = 'score'
                        break
            if flag is 'notscore':
                    print("Game Over!")
                    resultText = lossText
                    status = 'over'
                    self.birdSprite.color = (180, 0, 0)
                    self.birdSprite.stop()
                    x,y= self.birdSprite.position
                    self.birdSprite.do(Delay(0.005)+MoveTo((x,0),1)+Hide())
                    self.schedule_interval(self.caption,2)
                    self.schedule_interval(self.gameOver,7)
            elif flag is 'score':
                self.remove(self.labelText)
                score += 100                
                print score
                self.labelText = cocos.text.Label(scoreText+str(score),
                font_name='Times New Roman',
                font_size=24,bold = True)                 
                self.labelText.position = 520,620
                self.labelText.do(Blink(3,3))        
                self.add(self.labelText)
            elif flag is 'life':
                self.birdSprite.do(Blink(2,1))
                self.remove(self.lifeText)
                lifeLine = 0
                self.indicateLifeLine()

    def gameOver(self,dt):
        self.playLayer = Game2D_project1.PlayLayer(selectedSceneImage,level,score)
        intro_menu = Game2D_project1.PlayMenu(self)
        self.playLayer.add(intro_menu)
        self.intro_scene = cocos.scene.Scene(self.playLayer)
        cocos.director.director.replace(RotoZoomTransition(
            self.intro_scene, 2))

class SceneLayer(CollisionProcess):
    """
    This class provides navigation between the levels by changing the background scenes accordingly
    """
    def __init__(self):
        """ """
        super(SceneLayer, self).__init__()
    def checkBirdPresent(self,dt):
        global present,resultText,feedback
        x,y= self.birdSprite.position
        pos = int(x)
        num = 0
        if pos > 1035:
           present = False
           if level == 1:
               num = 15
           elif level == 2:
               num = 23
           elif level == 3:
               num = 41
           for i in range (0,num):
                self.obj[i].stop()
           if level == 3:
               resultText = winText
               print "Won Game"
               print score
               self.unschedule(self.checkBirdPresent)
               if score <= 500:
                   feedback = feedback1
               elif score <= 1100:
                   feedback = feedback2
                   self.schedule_interval(self.caption,2)
               elif score >= 1200:
                   feedback = feedback3
                   self.schedule_interval(self.caption,2)
               self.birdSprite.stop()               
               self.schedule_interval(self.feedbackFn,2)
               self.schedule_interval(self.gameOver,10)            
           
    def nextScene(self,dt):
        global selectedSceneImage,present,level,status
        x,y= self.birdSprite.position
        pos = int(x)
        if present == False and pos > 1070 and status is not 'over':
            present = True
            if level == 1:
                level = 2
                selectedSceneImage = sceneImage2
                self.playLayer = Game2D_project1.PlayLayer(selectedSceneImage,level,score)
                self.playLayer.remove(self.playLayer.scoreText)
                birdLayer = BirdLayer()
                self.playLayer.add(birdLayer)
                self.levelScene = cocos.scene.Scene(self.playLayer)
                cocos.director.director.run( FlipX3DTransition( self.levelScene, 0.05, cocos.scene.Scene(self.levelScene)) )
            elif level == 2:
                level = 3
                selectedSceneImage = sceneImage3
                self.playLayer = Game2D_project1.PlayLayer(selectedSceneImage,level,score)
                self.playLayer.remove(self.playLayer.scoreText)
                birdLayer = BirdLayer()
                self.playLayer.add(birdLayer)
                self.levelScene = cocos.scene.Scene(self.playLayer)
                cocos.director.director.run( FlipX3DTransition( self.levelScene, 0.05, cocos.scene.Scene(self.levelScene)) )
                       

class BirdLayer(CoinLayer,KeyboardInputLayer,TextLayer,SceneLayer):
    """
    This class exists to provide such as bird moving as well as onject rolling
    
    Each instance has the following:
    A unique identifier
    A motion vector to describe how the instances should move.
    A radius used to detect collisions with other GameSprite 
        instances
    
    Instances automatically move according to each instance's
    motion vector.
    """
    spritesheet = pyglet.image.load('bird.png')
    grid = pyglet.image.ImageGrid(spritesheet, 4, 4)
    textures = pyglet.image.TextureGrid(grid)
    textures_list = textures[:]
    birdAnimation = pyglet.image.Animation.from_image_sequence(textures_list, 0.1, loop=True)
    spritesheet2 = pyglet.image.load('asteroidSpriteSheet.png')
    grid = pyglet.image.ImageGrid(spritesheet2, 6, 5)
    textures = pyglet.image.TextureGrid(grid)
    textures_list = textures[:]
    spriteObj = pyglet.image.Animation.from_image_sequence(textures_list, 0.1, loop=True)
   
    def __init__(self):
        global collision_manager
        super(BirdLayer, self).__init__()
        self.schedule(self.checkBirdPresent)
        self.schedule(self.nextScene)
        self.labelText = cocos.text.Label(scoreText+str(score),
                font_name='Times New Roman',
                font_size=24,bold = True)                 
        self.labelText.position = 520,620
        self.labelText.do(Blink(3,3))        
        self.add(self.labelText)

        self.indicateLifeLine()

        
        self.birdSprite = cocos.sprite.Sprite(BirdLayer.birdAnimation)
        self.birdSprite.position = 0,570        
        move_basic = MoveBy((1200,0), 13)
        self.birdSprite.do(Repeat(move_basic))
        self.add(self.birdSprite,z=1)
        self.birdSprite.cshape = cm.AARectShape(
            self.birdSprite.position,
            self.birdSprite.width//3,
            self.birdSprite.height//3
        )
        collision_manager.add(self.birdSprite)

        if level == 1:
            delay = 13
            numOFAsteriods = 16
        elif level == 2:
            delay = 6
            numOFAsteriods = 24
        else:
            delay = 2
            numOFAsteriods = 42

        self.batch = cocos.batch.BatchNode()
        self.obj = [cocos.sprite.Sprite(BirdLayer.spriteObj)
                        for i in range(numOFAsteriods)]
        xpos = 0
        positions = ((1200, 570), (1300, 570), (1400, 570), (1500, 570),
                     (1200, 620), (1300, 620), (1400, 620), (1500, 620),
                     (1200, 520), (1300, 520), (1400, 520), (1500, 520),
                     (1200, 470), (1300, 470), (1400, 470), (1500, 470),
                     (1200, 420), (1300, 420), (1400, 420), (1500, 420),
                     (1200, 370), (1300, 370), (1400, 370), (1500, 370),
                     (1200, 320), (1300, 320), (1400, 320), (1500, 320),
                     (1200, 270), (1300, 270), (1400, 270), (1500, 270),
                     (1200, 220), (1300, 220), (1400, 220), (1500, 220),
                     (1200, 160), (1300, 160), (1400, 100), (1500, 50),
                     (1400, 70), (1500, 20)
                     )
        for num, enem in enumerate(self.obj):
            enem.position = positions[num]
            enem.cshape = cm.AARectShape(
                enem.position,
                enem.width//3,
                enem.height//3
            )
            collision_manager.add(enem)
            self.batch.add(enem)

        self.add(self.batch, z=1)            
        self.obj[0].do(MoveTo((xpos,570), delay)+Hide())
        self.obj[1].do(RandomDelay(10,18)+ MoveTo((xpos,570), delay)+Hide())
        self.obj[2].do(RandomDelay(18,28)+MoveTo((xpos,570), delay)+Hide())
        self.obj[3].do(RandomDelay(28,38)+MoveTo((xpos,570), delay)+Hide())
        self.obj[4].do(Delay(2)+MoveTo((xpos,620), delay)+Hide())
        self.obj[5].do(RandomDelay(10,18)+MoveTo((xpos,620), delay)+Hide())
        self.obj[6].do(RandomDelay(18,28)+MoveTo((xpos,620), delay)+Hide())
        self.obj[7].do(RandomDelay(28,38)+MoveTo((xpos,620), delay)+Hide())
        self.obj[8].do(Delay(5)+MoveTo((xpos,520), delay)+Hide())
        self.obj[9].do(RandomDelay(10,18)+MoveTo((xpos,520), delay)+Hide())
        self.obj[10].do(RandomDelay(18,28)+MoveTo((xpos,520), delay)+Hide())
        self.obj[11].do(RandomDelay(28,38)+MoveTo((xpos,520), delay)+Hide())
        self.obj[12].do(Delay(8)+MoveTo((xpos,470), delay)+Hide())
        self.obj[13].do(RandomDelay(18,28)+MoveTo((xpos,470), delay)+Hide())
        self.obj[14].do(RandomDelay(28,38)+MoveTo((xpos,470), delay)+Hide())
        self.obj[15].do(RandomDelay(10,18)+MoveTo((xpos,470), delay)+Hide())

        if level == 2:
            self.obj[16].do(Delay(10)+MoveTo((xpos,420), delay)+Hide())
            self.obj[17].do(RandomDelay(18,28)+MoveTo((xpos,420), delay)+Hide())
            self.obj[18].do(RandomDelay(28,38)+MoveTo((xpos,420), delay)+Hide())
            self.obj[19].do(RandomDelay(10,18)+MoveTo((xpos,420), delay)+Hide())
            self.obj[20].do(Delay(11)+MoveTo((xpos,370), delay)+Hide())
            self.obj[21].do(RandomDelay(18,28)+MoveTo((xpos,370), delay)+Hide())
            self.obj[22].do(RandomDelay(28,38)+MoveTo((xpos,370), delay)+Hide())
            self.obj[23].do(RandomDelay(10,18)+MoveTo((xpos,370), delay)+Hide())

        if level == 3:
            self.obj[16].do(Delay(10)+MoveTo((xpos,420), delay)+Hide())
            self.obj[17].do(RandomDelay(18,28)+MoveTo((xpos,420), delay)+Hide())
            self.obj[18].do(RandomDelay(28,38)+MoveTo((xpos,420), delay)+Hide())
            self.obj[19].do(RandomDelay(10,18)+MoveTo((xpos,420), delay)+Hide())
            self.obj[20].do(Delay(11)+MoveTo((xpos,370), delay)+Hide())
            self.obj[21].do(RandomDelay(18,28)+MoveTo((xpos,370), delay)+Hide())
            self.obj[22].do(RandomDelay(28,38)+MoveTo((xpos,370), delay)+Hide())
            self.obj[23].do(RandomDelay(10,18)+MoveTo((xpos,370), delay)+Hide())
            self.obj[24].do(Delay(12)+MoveTo((xpos,320), delay)+Hide())
            self.obj[25].do(RandomDelay(18,28)+MoveTo((xpos,320), delay)+Hide())
            self.obj[26].do(RandomDelay(28,38)+MoveTo((xpos,320), delay)+Hide())
            self.obj[27].do(RandomDelay(10,18)+MoveTo((xpos,320), delay)+Hide())
            self.obj[28].do(Delay(13)+MoveTo((xpos,270), delay)+Hide())
            self.obj[29].do(RandomDelay(18,28)+MoveTo((xpos,270), delay)+Hide())
            self.obj[30].do(RandomDelay(28,38)+MoveTo((xpos,270), delay)+Hide())
            self.obj[31].do(RandomDelay(10,18)+MoveTo((xpos,270), delay)+Hide())
            self.obj[32].do(Delay(14)+MoveTo((xpos,220), delay)+Hide())
            self.obj[33].do(RandomDelay(18,28)+MoveTo((xpos,220), delay)+Hide())
            self.obj[34].do(RandomDelay(28,38)+MoveTo((xpos,220), delay)+Hide())
            self.obj[35].do(RandomDelay(10,18)+MoveTo((xpos,220), delay)+Hide())
            self.obj[36].do(Delay(15)+MoveTo((xpos,160), delay)+Hide())
            self.obj[37].do(RandomDelay(28,38)+MoveTo((xpos,160), delay)+Hide())
            self.obj[38].do(RandomDelay(28,38)+MoveTo((xpos,100), delay)+Hide())
            self.obj[39].do(RandomDelay(28,38)+MoveTo((xpos,50), delay)+Hide())
            self.obj[40].do(RandomDelay(10,15)+MoveTo((xpos,70), delay)+Hide())
            self.obj[41].do(RandomDelay(10,35)+MoveTo((xpos,20), delay)+Hide())
       
        self.schedule(self.update)    

    def on_start_over( self ):
        """ """
        global selectedSceneImage,level,score,lifeFlag,status
        status = ''
        selectedSceneImage = sceneImage1
        level = 1
        score = 0
        lifeFlag = True
        print "level"+str(level)
        self.playLayer = Game2D_project1.PlayLayer(selectedSceneImage,level,score)
        self.playLayer.remove(self.playLayer.scoreText)
        subScene = BirdLayer()
        self.playLayer.add(subScene)
        self.intro_scene = cocos.scene.Scene(self.playLayer)
        cocos.director.director.replace(RotoZoomTransition(
            cocos.scene.Scene(self.intro_scene), 1))

    def on_quit( self ):
        """ """
        sys.exit()
        pyglet.app.exit()    

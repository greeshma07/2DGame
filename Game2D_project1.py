import cocos
import pyglet
import PlayGame
from cocos.actions import Blink

sceneImage1 = 'scene1.jpg'
selectedSceneImage = sceneImage1
level = 1
levelIndicate = 'Level: '
scoreText = 'Score: '
score = 0

class PlayLayer(cocos.layer.Layer):
    """
    """
    background_image_name = selectedSceneImage
    def __init__( self,selectedSceneImage,level,score):
        """ """
        super( PlayLayer, self ).__init__()
        self.background_image_name = selectedSceneImage
        width, height = cocos.director.director.get_window_size()
        self.add(
            cocos.sprite.Sprite(self.background_image_name,
            position=(width * 0.5, height * 0.5)),
            z=-1)
        labelText = cocos.text.Label(levelIndicate+str(level),
        font_name='Times New Roman',
        font_size=24,bold = True)                 
        labelText.position = 320,620
        labelText.do(Blink(3,3))        
        self.add(labelText)
        self.scoreText = cocos.text.Label(scoreText+str(score),
        font_name='Times New Roman',
        font_size=24,bold = True)                 
        self.scoreText.position = 520,620
        self.scoreText.do(Blink(3,3))        
        self.add(self.scoreText)

class PlayMenu(cocos.menu.Menu):
    """
    """
    def __init__( self, game ):
        """ """
        super( PlayMenu, self ).__init__()
        self.game = game
        self.font_item = {
            'font_name': 'Arial',
            'font_size': 32,
            'bold': True,
            'color': (220, 200, 220, 100),
        }
        self.font_item_selected = {
            'font_name': 'Arial',
            'font_size': 42,
            'bold': True,
            'color': (255, 255, 255, 255),
        }

        l = []
        l.append( cocos.menu.MenuItem('Play Game',
            self.game.on_start_over ) )
        l.append( cocos.menu.MenuItem('Quit', self.game.on_quit ) )

        self.create_menu( l )      

class Main(cocos.layer.Layer):
    
    def __init__(self):
        super(Main, self).__init__()
        self.playLayer = PlayLayer(selectedSceneImage,level,score)        
        self.add(self.playLayer)
        birdLayer = PlayGame.BirdLayer()        
        self.add(birdLayer)
        self.playLayer.remove(self.playLayer.scoreText)       

if __name__ == '__main__':

    width, height = 1100,650
    cocos.director.director.init(width,height)
    cocos.director.director.run(cocos.scene.Scene(Main()))

import pygame
from pygame.locals import *
import random
import time
import math
pygame.init()

playerimg = pygame.image.load('./data/player_hand2.png')
playerfailimg = pygame.image.load('./data/player_fail.png')
players = pygame.sprite.Group()
playerNum = 2 #Change the number of players in population. Recommended: 2 or 3

# What will make up the population
class Player(pygame.sprite.Sprite):
    hasFailed = False
    fitness = 0
    def __init__(self, Start_X, Start_Y, size, brain):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((43,25))
        self.x = Start_X
        self.y = Start_Y
        self.size = size
        self.brain = brain
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.image = playerimg
    
    def update(self): #Rapidly tests left and right for collision
        self.rect.y = 500
        stepNum = self.brain.step
        if stepNum < self.size and self.hasFailed == False:
            if self.brain.directions[stepNum] == 1 and self.rect.x > 25:
                self.rect.x -= 25
                
            elif self.brain.directions[stepNum] == 2 and self.rect.x < 550:
                self.rect.x += 25
                
            self.brain.step += 1
    
    def collide(self): #Called from ball class if rect collision is detected; adds fitness to player
        self.fitness += 1
        print(self.fitness)
       
    def fail(self):
        self.image = playerfailimg
        self.hasFailed == True
        Learn.playersAlive -= 1
        
class Learn: #Population
    if_one_hundred = False
    playersAlive = playerNum #Note: all players die at the same time equaling zero.
    fitnessSum = 0
    bestplayer = 0
    main_generation = 1
    def __init__(self, alive, size):
        self.size = size
        self.alive = alive
        self.randomize()
    
    def randomize(self):
        for i in range(0, self.alive):
            directions = []
            for z in range(0, self.size):
                randomNum = random.randint(0,2)
                directions.append(randomNum)

            dir = PlayerDirections(10000, directions)
            players.add(Player(167.5, 350, self.size, dir))
        
    def setFitnessSum(self):
        sum = 0
        for p in players:
            sum += p.fitness
        self.fitnessSum = sum
        
    def selectParent(self):
        self.setFitnessSum()
        rand = random.randint(self.playersAlive, self.fitnessSum)
        runningSum = 0
        for player in players:
            runningSum += player.fitness
            if runningSum >= rand:
                return player.brain.directions
   
    def selection(self):
            best = list(self.bestPlayerDirections())
            newPlayers = []
            if (self.if_one_hundred == False):
                dir = list(best)
                newDirections = PlayerDirections(10000, dir)
                newPlayers.append(Player(167.5, 350, self.size, newDirections))
            
                for x in range(1, playerNum):
                    dir = list(self.selectParent())
                    newDirections = PlayerDirections(10000, mutate(dir))
                    newPlayers.append(Player(167.5, 350, self.size, newDirections))
                Learn.playersAlive = playerNum
                
                players.empty()
                for player in newPlayers:
                    players.add(player)
            else: # If a player has gotten to 100 reset the game
                players.empty()
                for x in range(0, 1):
                    dir = list(best)
                    directions = PlayerDirections(10000, dir)
                    players.add(Player(167.5, 350, self.size, directions))
                Learn.playersAlive = 1
        
    def bestPlayerDirections(self):
        if (self.if_one_hundred == False):
            sortedPlayers = []
            for player in players:
                sortedPlayers.append(player)

            sortedPlayers.sort(key = lambda player: player.fitness)

            best = playerNum - 1
            for i in range(0, playerNum - 1):
                if sortedPlayers[i].brain.step < sortedPlayers[playerNum - 1].brain.step and sortedPlayers[i].fitness == sortedPlayers[playerNum - 1].fitness:
                    best = i

            if (sortedPlayers[best].fitness == 105):
                self.if_one_hundred = True
            else:
                self.main_generation += 1
                

            for player in players:
                if (sortedPlayers[best].fitness == player.fitness and sortedPlayers[best].brain.step == player.brain.step):
                    bestPlayerDirections = list(player.brain.directions)
                    break
            return bestPlayerDirections
        else:
            for player in players:
                bestPlayerDirections = list(player.brain.directions)
            return bestPlayerDirections
        

class PlayerDirections:
    step = 0
    def __init__(self, size, directions):
        self.size = size
        self.directions = directions

def mutate(d):
    for i in range(0, len(d)):
        randomNum = random.randint(0, 2)
        if randomNum == 1:
            d[i] = random.randint(0, 2)
    return d
    
class Ball(pygame.sprite.Sprite):
    """ The ball """
    def __init__(self, image, gravity, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.mask = pygame.mask.from_surface(image)
        self.gravity = gravity
        self.cap = 50
        self.bounce = 0.66
        self.friction = 0.99
        self.kick = 1.3
        self.x = x; self.y = y
        self.dx = 0; self.dy = 0
        self.on_ground = False
        self.spin = 0
        self.angle = 0

    def center(self):
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.x = self.rect.x
        self.y = self.rect.y

    def update(self):
        self.x += self.dx/2
        self.y += self.dy/2
        self.angle += self.spin
        if self.angle < 0: self.angle += 360
        if self.angle > 360: self.angle -= 360
        if not self.on_ground: self.dy += self.gravity
        if self.dy > self.cap: self.dy = self.cap
        if self.on_ground:
            self.dx *= self.friction
            self.spin = -self.dx
        if self.on_ground and abs(self.dx) - 0.5 < 0:
            self.dx = 0
            self.spin = -self.dx
        self.rect.x = self.x
        self.rect.y = self.y
        for p in players:            
            if self.is_collided_with(p):
                dx = 30*math.cos(math.radians(self.angle+90))
                dy = 30*math.sin(math.radians(self.angle-90))
                self.dx = dx; self.dy = dy
                self.on_ground = False
                self.spin = -dx/5
                p.collide()
        self.playerfail()
        
    def is_collided_with(self, sprite):
        return self.rect.colliderect(sprite.rect)
        
                
    def playerfail(self):
        screen_size = screen.get_size()
        if self.y > screen_size[1]-self.rect.height:
            for p in players:
                p.fail()

#Screen
def main(screen):
    pygame.display.set_caption('Ball-E BOT')
    pygame.display.set_icon(pygame.image.load('./data/icon.png'))
    screen.fill((0,0,0)); screen.set_colorkey((0,0,0))
    playerimg = pygame.image.load('./data/player_hand2.png')
    
    playerimg.set_colorkey(playerimg.get_at((0,0)))
    ballimg = pygame.image.load('./data/ball.png')
    ballimg.set_colorkey(ballimg.get_at((0,0)))
    pygame.mixer.music.load('./data/kick.ogg')
    screen_size = screen.get_size()
    center = (screen_size[0]/2, screen_size[1]/2)
   
    score = 0
    highscore = 0
    generation = 1
    paused = False
    font1 = pygame.font.Font('./data/font.ttf', 40)
    font2 = pygame.font.Font('./data/font.ttf', 22)
    font3 = pygame.font.Font('./data/font.ttf', 52)
    font4 = pygame.font.Font('./data/font.ttf', 16)
    title = font3.render('Keep the ball in the air!', 1, (255,255,255))
    title2 = font3.render('Generation:', 1, (255,255,255))
   
    info1 = font4.render('Esc - Quit', 1, (255,255,255))
    info2 = font4.render('P - Pause', 1, (255,255,255))
    info3 = font3.render('Paused', 1, (255,255,255))
    
    # Int to String:
    
    score_text = font1.render(str(score), 1, (255,155,155))
    highscore_text = font2.render(str(highscore), 1, (255,255,255))
    generation_text = font3.render(str(generation), 1, (255,255,255))
    
    
    score_rect = score_text.get_rect()
    highscore_rect = highscore_text.get_rect()
    generation_rect = generation_text.get_rect()
    highscore_rect.y = score_rect.bottom+5
    highscore_rect.x = 5
    score_rect.x = 20
    title_rect = title.get_rect()
    title_rect.y = score_rect.centery
    title2_rect = title2.get_rect()
    title2_rect.y = score_rect.centery
    
    
    info1_rect = info1.get_rect()
    info1_rect.right = screen_size[0]-5
    info1_rect.y = 5
    info2_rect = info2.get_rect()
    info2_rect.x = info1_rect.x
    info2_rect.y = info1_rect.bottom+5
    title_rect.centerx = (screen_size[0]-score_rect.width-info1_rect.width)/2
    title2_rect.centerx = (screen_size[0]-score_rect.width-info1_rect.width)/2
    generation_rect.right = screen_size[0]-250
    title2_rect.y = title2_rect.bottom+5
    generation_rect.y = title2_rect.y 
    
    info3_rect = info3.get_rect()
    info3_rect.centerx = center[0]
    info3_rect.centery = center[1]
    
    
    ball = Ball(ballimg, 1, *center); ball.center()
    subrect = ballimg.get_rect()
    subrect.width=84
    subrect.height=83

    clock = pygame.time.Clock()
    ball.update()
    
    
    screen.blit(ball.image, ball.rect)
    screen.blit(score_text, score_rect)
    screen.blit(highscore_text, highscore_rect)
    screen.blit(title, title_rect)
    screen.blit(title2, title2_rect)
    screen.blit(info1, info1_rect)
    screen.blit(info2, info2_rect)
    screen.blit(generation_text, generation_rect)
    
    pop = Learn(playerNum, 10000)
    set()
    
    pygame.display.flip()
    i=1
    while(i) == 1:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                if event.key == K_p:
                    paused = not paused
                    
        
        pygame.display.update()
        
        if (Learn.playersAlive == 0):
            set()
            pop.selection()
            time.sleep(2.5) 
        players.update()
        players.draw(screen)
        pygame.display.update()
        

        # When ball hits side of wall
        if ball.x > screen_size[0]-ball.rect.width:
            ball.x = screen_size[0]-ball.rect.width
            ball.dx = -ball.dx*ball.friction
            ball.spin = ball.dy
            pygame.mixer.music.play(0,0.14)
            
        # When ball hits side of wall
        if ball.x < 0:
            ball.x = 0
            ball.dx = -ball.dx*ball.bounce
            ball.spin = -ball.dy
            pygame.mixer.music.play(0,0.14)
        if score > highscore:
            highscore = score
            highscore_text = font2.render(str(highscore), 1, (255,255,255))
            
            #When ball hits ground   
        if ball.y > screen_size[1]-ball.rect.height:
            for p in players:
                p.fail()
            score = 0
            generation += 1
            generation_text = font3.render(str(generation), 1, (255,255,255))
            score_text = font1.render(str(score), 1, (255,155,155))
            
            ball.__init__(ballimg, 1, *center); ball.center()      
            
        ball.update()
        
        rotated = pygame.transform.rotate(ball.image, ball.angle)
        size = rotated.get_size()
        subrect.centerx = size[0]/2
        subrect.centery = size[1]/2
        newimg = rotated.subsurface(subrect)
        for p in players:
            if p.rect.colliderect(ball) and p.hasFailed == False:
                screen.fill((255,0,0))
                pygame.display.update()
                pygame.display.flip()
        screen.fill((0,0,0))
        
        screen.blit(newimg, ball.rect)
        screen.blit(score_text, score_rect)
        screen.blit(highscore_text, highscore_rect)
        screen.blit(title, title_rect)
        screen.blit(title2, title2_rect)
        screen.blit(info1, info1_rect)
        screen.blit(info2, info2_rect)
        screen.blit(generation_text, generation_rect)
        players.update()
        players.draw(screen)
        pygame.display.update()
        
        if paused: screen.blit(info3, info3_rect)
        pygame.display.flip()
        pygame.display.update()
        
if __name__ == "__main__":
    pygame.init()
    screen_width = 600
    screen_height = 700
    screen = pygame.display.set_mode((screen_height,screen_width))
    main(screen)
    pygame.quit()
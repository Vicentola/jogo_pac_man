from OpenGL.GL import * 
from OpenGL.GLU import * 
from OpenGL.GLUT import * 

import random

width, height = 800, 600


estado = 'Inicio'

jogador = None

contador = 0

DIRECOES = [(1,0), (-1,0), (0,1), (0,-1)]

def inicializar():
    glEnable(GL_DEPTH_TEST) #teste de profundidade vendo quais objetos estao na frente e atraz

    glMatrixMode(GL_PROJECTION)#matriz de proporcao configura lente e camera
    glLoadIdentity() #rezeta a matriz pra n carregar funcoes anteriores
    gluPerspective(60, width / height, 0.1, 100)

    glMatrixMode(GL_MODELVIEW)    

def draw():
    
    
    if estado == 'Jogando':
        glClearColor(0, 0, 0, 1)
    elif estado == 'Pause':
        glClearColor(0.3, 0.3, 0.3, 1)
    elif estado == 'Inicio':
        glClearColor(0, 0, 0.4, 1)
    elif estado == 'GameOver':
        glClearColor(0.5, 0, 0, 1)
    
   
    
    
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    gluLookAt(
        4.5, 12, 10,  # posição da câmera
        4.5, 0, 3.5,  # alvo: centro do mapa
        0, 1, 0       # direção para cima
        )    
    
    if estado == 'Jogando' or estado == 'Pause':
    
        glColor3f(0, 0, 1)
    
        for y, linha in enumerate(mapa):
            for x, caractere in enumerate(linha):

                if caractere == '#':
                    glPushMatrix() # salva a matriz atua

                    glTranslatef(x, 0, y) # desloca o sistema de coordenadas
                    glutSolidCube(1) # desenha o cubo

                    glPopMatrix() # restaura a matriz salva
        
        glColor3f(1,1,0)
        
        jx = jogador[0]
        jy = jogador[1]
        
        glPushMatrix()
        
        glTranslate(jx, 0, jy)
        
        glutSolidSphere(0.4,20,20)
        
        glPopMatrix()
        
        
        for fantasma in inimigos:
            
            glColor3f(1,0,0)
            
            fx = fantasma[0]
            fy = fantasma[1]
            
            
            glPushMatrix()
            glTranslate(fx, 0, fy)
            
            glutSolidCube(0.7)
            
            glPopMatrix()
        
        
        

    
    glutSwapBuffers() # importante para doubl;e buffering
    
    
    
def mover_fantasmas():

    for fantasma in inimigos:
        fx, fy, dx, dy = fantasma

        possiveis = []

        # Verificar todas as direções possíveis
        for ndx, ndy in DIRECOES:
            nx = fx + ndx
            ny = fy + ndy

            if mapa[ny][nx] != '#':
                possiveis.append((ndx, ndy))

        # Remover a direção de volta
        sem_volta = [d for d in possiveis if d != (-dx, -dy)]

        if sem_volta:
            possiveis = sem_volta

        # Sortear uma direção
        if possiveis:
            ndx, ndy = random.choice(possiveis)

            # Atualizar direção
            fantasma[2] = ndx
            fantasma[3] = ndy

            # Atualizar posição
            fantasma[0] += ndx
            fantasma[1] += ndy

    
def carregar_mapa():
    global mapa, jogador, inimigos, moedas
    mapa = []
    inimigos = []
    moedas = []

    with open('fase1.txt') as f:
        lines = f.readlines()
        for linha in lines:
            mapa.append(linha.rstrip('\n'))
        
        for y, linha in enumerate(mapa):
            for x, caractere in enumerate(linha):
                if caractere == 'P':
                    jogador = (x,y)
                elif caractere == 'E':
                    inimigos.append([x,y,1,0])
                elif caractere == '.':
                    moedas.append((x,y))
                    
        print(jogador, len(inimigos), len(moedas))
        print(inimigos)
    
def timer(valor):
    
    global contador
    
    
    contador+1
    
    if estado == 'Jogando' and contador % 60 == 0:
        mover_fantasmas()
    
        
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)
    
def teclado(key, x, y):
    global estado
    if estado == 'Inicio':
        if key == b'\r':
            estado = 'Jogando'
    elif estado == 'Jogando':
        if key == b'p':
            estado = 'Pause'
        if key == b'g':
            estado = 'GameOver'
    elif estado == 'Pause':
        if key == b'\r':
            estado = 'Jogando'
    elif estado == 'GameOver':
        if key == b'r':
            estado = 'Inicio'
    if key == b'\x1b':
        glutLeaveMainLoop()
        
        
def teclas_especiais(key, x, y):
    global jogador

    if estado == 'Jogando':

        jx, jy = jogador

        nx, ny = jx, jy

        if key == GLUT_KEY_UP:
            ny -= 1

        if key == GLUT_KEY_DOWN:
            ny += 1

        if key == GLUT_KEY_LEFT:
            nx -= 1

        if key == GLUT_KEY_RIGHT:
            nx += 1

        if mapa[ny][nx] != '#':
            jogador = (nx, ny)
    

    
    
glutInit() 
glutInitDisplayMode(GLUT_RGB| GLUT_DOUBLE | GLUT_DEPTH )
glutInitWindowSize(width, height)
glutInitWindowPosition(200,200)
janela = glutCreateWindow(b'pac-man')

inicializar()

glutDisplayFunc(draw)

glutTimerFunc(16, timer, 0)
glutKeyboardFunc(teclado)
glutSpecialFunc(teclas_especiais)
carregar_mapa()
glutMainLoop()





    
    
    





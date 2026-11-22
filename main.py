from OpenGL.GL import * 
from OpenGL.GLU import * 
from OpenGL.GLUT import * 

import random
from PIL import Image

width, height = 800, 600


estado = 'Inicio'

jogador = None

contador = 0

pontos = 0

inicio_jogador = None

vidas  = 3

modo_camera = 'cima'

DIRECOES = [(1,0), (-1,0), (0,1), (0,-1)]

def inicializar():
    global textura_chao
    glEnable(GL_DEPTH_TEST) #teste de profundidade vendo quais objetos estao na frente e atraz

    glMatrixMode(GL_PROJECTION)#matriz de proporcao configura lente e camera
    glLoadIdentity() #rezeta a matriz pra n carregar funcoes anteriores
    gluPerspective(60, width / height, 0.1, 100)

    glMatrixMode(GL_MODELVIEW)   
    
    textura_chao = carregar_textura('chao.jpg')

def draw():
    
    
    if estado == 'Jogando':
        glClearColor(0, 0, 0, 1)
    elif estado == 'Pause':
        glClearColor(0.3, 0.3, 0.3, 1)
    elif estado == 'Inicio':
        glClearColor(0, 0, 0.4, 1)
    elif estado == 'GameOver':
        glClearColor(0.5, 0, 0, 1)
    elif estado == 'Vitoria':
        glClearColor(0, 0.4, 0, 1)
    
   
    
    
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if modo_camera == 'cima':
        gluLookAt(
            4.5, 12, 10,  # posição da câmera
            4.5, 0, 3.5,  # alvo: centro do mapa
            0, 1, 0       # direção para cima
            )
    else:
        jx, jy = jogador

        gluLookAt(
            jx, 4, jy + 4,
            jx, 0, jy,
            0, 1, 0
            )
        
            
    
    if estado == 'Jogando' or estado == 'Pause':
        
        glEnable(GL_TEXTURE_2D)    
                
        glBindTexture(GL_TEXTURE_2D, textura_chao)
        
        glColor3f(1, 1, 1)
        
        largura = len(mapa[0])
        altura = len(mapa)
        
        glBegin(GL_QUADS)   
        
        glNormal3f(0, 1, 0)
        
        # Canto 1
        glTexCoord2f(0, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        
        # Canto 2
        glTexCoord2f(largura, 0)
        glVertex3f(largura - 0.5, -0.5, -0.5)
        
        # Canto 3
        glTexCoord2f(largura, altura)
        glVertex3f(largura - 0.5, -0.5, altura - 0.5)

        # Canto 4
        glTexCoord2f(0, altura)
        glVertex3f(-0.5, -0.5, altura - 0.5)

        glEnd()

        glDisable(GL_TEXTURE_2D)
        
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
            
        for moeda in moedas:
            
            glColor3f(1, 1, 1)
            
            fx = moeda[0]
            fy = moeda[1]
            
            glPushMatrix()
            glTranslate(fx,0,fy)
            
            glutSolidSphere(0.1,10,10)
            
            glPopMatrix()
            
        
        
        
    if estado == 'Inicio':
        desenhar_texto(300, 300, "PAC-MAN")
        desenhar_texto(250, 260, "APERTE ENTER PARA JOGAR")

    elif estado == 'Jogando':
        desenhar_texto(10, 570, f"Pontos: {pontos}")
        desenhar_texto(10, 540, f"Vidas: {vidas}")

    elif estado == 'Pause':
        desenhar_texto(300, 320, "PAUSE")
        desenhar_texto(230, 280, "APERTE ENTER PARA CONTINUAR")

    elif estado == 'GameOver':
        desenhar_texto(280, 340, "GAME OVER")
        desenhar_texto(280, 300, f"Pontos: {pontos}")
        desenhar_texto(230, 260, "APERTE R PARA RECOMECAR")

    elif estado == 'Vitoria':
        desenhar_texto(280, 340, "VOCE VENCEU!")
        desenhar_texto(280, 300, f"Pontos: {pontos}")
        desenhar_texto(280, 260, "APERTE R")
    
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
            
            

def checar_colisao_fantasma():
    global jogador, vidas, estado
    
    for fantasma in inimigos:
        if (fantasma[0],fantasma[1]) == jogador:
            vidas -=1
            if vidas <= 0:
                estado = 'GameOver'
            jogador = inicio_jogador
            print(vidas)
            

    
def carregar_mapa():
    global mapa, jogador, inimigos, moedas, inicio_jogador
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
                    inicio_jogador = (x,y)
                elif caractere == 'E':
                    inimigos.append([x,y,1,0])
                elif caractere == '.':
                    moedas.append((x,y))
                    
        print(jogador, len(inimigos), len(moedas))
        print(inimigos)
    
def timer(valor):
    
    global contador, estado
    
    
    contador+=1
    
    if estado == 'Jogando' and contador % 60 == 0:
        mover_fantasmas()
        
    if estado == 'Jogando':
        checar_colisao_fantasma()
        if len(moedas) == 0:
            estado = 'Vitoria'
    
        
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)
    
def teclado(key, x, y):
    global estado, vidas, pontos, modo_camera
    if estado == 'Inicio':
        if key == b'\r':
            estado = 'Jogando'
    elif estado == 'Jogando':
        if key == b'p':
            estado = 'Pause'
        
    elif estado == 'Pause':
        if key == b'\r':
            estado = 'Jogando'
    elif estado == 'GameOver':
        if key == b'r':
            estado = 'Inicio'
            vidas = 3
            pontos = 0
            carregar_mapa()
            print("reset:", vidas, pontos, len(moedas))
    elif estado == 'Vitoria':
        if key == b'r':
            estado = 'Inicio'
            vidas = 3
            pontos = 0
            carregar_mapa()
    
    
    if key == b'c':
        if modo_camera == 'cima':
            modo_camera = 'seguir'
        else:
            modo_camera = 'cima'
            
    if key == b'\x1b':
        glutLeaveMainLoop()
        
        
def teclas_especiais(key, x, y):
    global jogador, pontos

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
        
        if (nx,ny) in moedas:
            moedas.remove((nx,ny))
            pontos = pontos + 10
            print(pontos)


def desenhar_texto(x,y, texto):
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor(1, 1, 1)
    glRasterPos2f(x, y)
    
    for letra in texto:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(letra))
        
    glPopMatrix()
        
    glMatrixMode(GL_PROJECTION)
        
    glPopMatrix()
        
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)
    
    glEnable(GL_LIGHTING)
    
    glEnable(GL_LIGHT0)  
    
    glEnable(GL_COLOR_MATERIAL)
    
def carregar_textura(nome_arquivo):
    imagem = Image.open(nome_arquivo).convert('RGB')
    dados = imagem.tobytes()
    largura, altura = imagem.size
    
    rgb_textura = glGenTextures(1)
    
    glBindTexture(GL_TEXTURE_2D, rgb_textura)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexParameteri(GL_TEXTURE_2D,  GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexParameteri(GL_TEXTURE_2D,  GL_TEXTURE_WRAP_S, GL_REPEAT)

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, largura, altura, 0, GL_RGB, GL_UNSIGNED_BYTE, dados)
    
    return rgb_textura

    
   
    
    
    
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





    
    
    





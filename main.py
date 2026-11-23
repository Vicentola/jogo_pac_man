# =============================================================================
# PAC-MAN 3D - Computação Gráfica (UTP) - Prof. Diógenes Furlan
# Autor: Vicente Rafael Carvalho do Valle
#
# Jogo 2D construído com técnicas 3D em Python + PyOpenGL + GLUT.
# A lógica do jogo é uma grade 2D (lida de fase1.txt); o desenho é 3D:
# cada parede vira um cubo, com iluminação, textura no chão e duas câmeras.
#
# Controles:
#   ENTER  - começa o jogo / sai do pause
#   Setas  - movem o Pac-Man
#   P      - pausa
#   C      - alterna a câmera (visão de cima / seguindo o Pac-Man)
#   R      - recomeça (no Game Over ou na Vitória)
#   ESC    - fecha o jogo
# =============================================================================

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
from PIL import Image  # Pillow: usado só para ler o arquivo de imagem da textura
import math 



# Tamanho da janela em pixels
width, height = 800, 600


# ----------------------------- VARIÁVEIS GLOBAIS -----------------------------
# Ficam fora das funções porque os callbacks do GLUT têm parâmetros fixos;
# o estado do jogo precisa ser compartilhado entre draw, timer e teclado.

# Máquina de estados: 'Inicio', 'Jogando', 'Pause', 'GameOver', 'Vitoria'
estado = 'Inicio'

# Posição atual do Pac-Man na grade, como tupla (x, y)
jogador = None

# Conta quantas vezes o timer tocou (usado para controlar a velocidade dos fantasmas)
contador = 0

pontos = 0

# Posição de partida do Pac-Man (para onde ele volta quando morre)
inicio_jogador = None

vidas  = 3

# Câmera atual: 'cima' (visão geral) ou 'seguir' (acompanha o Pac-Man)
modo_camera = 'cima'

direcao_pacman = 0

# As 4 direções possíveis na grade, como (dx, dy): direita, esquerda, baixo, cima
DIRECOES = [(1,0), (-1,0), (0,1), (0,-1)]

def inicializar():
    """Configurações do OpenGL feitas uma vez só, logo depois de criar a janela."""
    global textura_chao
    glEnable(GL_DEPTH_TEST) # teste de profundidade: o que está na frente tapa o que está atrás

    glEnable(GL_LIGHTING)
    
    glEnable(GL_LIGHT0)

    glEnable(GL_COLOR_MATERIAL)
    
    glMatrixMode(GL_PROJECTION) # matriz de projeção: configura a "lente" da câmera
    glLoadIdentity() # zera a matriz para não acumular configurações anteriores
    gluPerspective(60, width / height, 0.1, 100) # ângulo de visão, proporção, distância mínima e máxima

    glMatrixMode(GL_MODELVIEW) # volta para a matriz de posicionamento (câmera e objetos)

    # Carrega a imagem do chão na placa de vídeo e guarda o número (id) da textura
    textura_chao = carregar_textura('chao.jpg')

def draw():
    """Callback de desenho: o GLUT chama sempre que a tela precisa ser redesenhada."""


    # Cor de fundo de cada estado (o glClearColor só escolhe a cor; quem pinta é o glClear)
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





    # Limpa a tela (cor) e o buffer de profundidade antes de desenhar o novo quadro
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # ---------------- CÂMERA ----------------
    # gluLookAt(posição da câmera, ponto para onde olha, direção "para cima")
    if modo_camera == 'cima':
        gluLookAt(
            4.5, 12, 10,  # posição da câmera
            4.5, 0, 3.5,  # alvo: centro do mapa
            0, 1, 0       # direção para cima
            )
    else:
        # Câmera seguindo: recalculada a cada quadro a partir da posição do jogador
        jx, jy = jogador

        gluLookAt(
            jx, 4, jy + 4,  # acima e atrás do Pac-Man
            jx, 0, jy,      # olhando para o Pac-Man
            0, 1, 0
            )

    
    glLightfv(GL_LIGHT0, GL_POSITION, [4.5, 10, 3.5, 1])


    # O cenário só aparece durante o jogo (no pause ele fica congelado ao fundo)
    if estado == 'Jogando' or estado == 'Pause':

        # ---------------- CHÃO COM TEXTURA ----------------
        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, textura_chao)  # escolhe a textura do chão

        glColor3f(1, 1, 1)  # branco: a cor multiplica a textura, então branco mantém as cores da imagem

        # Tamanho do mapa em casas (não confundir com width/height, que são da janela)
        largura = len(mapa[0])
        altura = len(mapa)

        # Um retângulo grande deitado embaixo do labirinto (y = -0.5, base dos cubos)
        glBegin(GL_QUADS)

        glNormal3f(0, 1, 0)  # normal apontando para cima, necessária para a iluminação

        # Cada canto: glTexCoord2f = ponto da imagem / glVertex3f = ponto no mundo 3D.
        # Coordenadas de textura até largura/altura fazem a imagem repetir uma vez por casa (GL_REPEAT).
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

        glDisable(GL_TEXTURE_2D)  # desliga para a textura não grudar nos outros objetos

        # ---------------- PAREDES ----------------
        # Cada '#' do mapa vira um cubo. O x do mapa é o x do mundo e o y do mapa vira o z
        # (o mapa fica "deitado" no chão).
        glColor3f(0, 0, 1)

        for y, linha in enumerate(mapa):
            for x, caractere in enumerate(linha):

                if caractere == '#':
                    glPushMatrix() # salva a matriz atual

                    glTranslatef(x, 0, y) # desloca o sistema de coordenadas até a casa
                    glutSolidCube(1) # desenha o cubo

                    glPopMatrix() # restaura a matriz salva

        # ---------------- PAC-MAN ----------------
        glColor3f(1,1,0)

        jx = jogador[0]
        jy = jogador[1]

        glPushMatrix()

        glTranslate(jx, 0, jy)

        boca = abs(math.sin(contador * 0.2)) * 40 #sinal absoluto 

        ''''0.2 é o nhac-nhac, 40 abertura máxima da boca em gruas'''

        glRotatef(direcao_pacman, 0, 1, 0)

        desenhar_pacman(30)  # raio 0.4 (menor que a casa) e resolução 20x20
        desenhar_pacman(boca)

        glPopMatrix()


        # ---------------- FANTASMAS ----------------
        for fantasma in inimigos:

            glColor3f(1,0,0)

            # cada fantasma é [x, y, dx, dy]; para desenhar só importa a posição
            fx = fantasma[0]
            fy = fantasma[1]

            flutuar =  math.sin((contador * 0.1 + fantasma[0])) * 0.15

            progresso = (contador % 60) / 60

            posicao_desenhadax =  fx - fantasma[2] * (1 - progresso)

            posicao_desenhadaz = fy - fantasma[3] *(1 - progresso)
 
            glPushMatrix()
            glTranslate(posicao_desenhadax, flutuar, posicao_desenhadaz)


            direcao = (fantasma[2], fantasma[3])

            if direcao == (0,1):
                glRotate(0,0,1,0)
            
            if direcao == (1,0):
                glRotate(90,0,1,0)

            if direcao == (0,-1):
                glRotate(180,0,1,0)
            
            if direcao == (-1,0):
                glRotate(270,0,1,0)

            glutSolidSphere(0.35,20, 20)
            glPushMatrix()
            glRotate(90,1,0,0)
            glutSolidCylinder(0.35,0.35,20,5)
            glPopMatrix()


            glColor3f(1,1,1)

            glPushMatrix()
            glTranslate(0.12,0.05,0.3)
            glutSolidSphere(0.09,10,10)
            glPopMatrix()


            glPushMatrix()
            glTranslate(-0.12,0.05,0.3)
            glutSolidSphere(0.09,10,10)
            glPopMatrix()

            glColor3f(0,0,0)

            glPushMatrix()
            glTranslate(0.12,0.05,0.37) # lado altura frente
            glutSolidSphere(0.045,5,5)
            glPopMatrix()

            glPushMatrix()
            glTranslate(-0.12,0.05,0.37)
            glutSolidSphere(0.045,5,5)
            glPopMatrix()


            glPopMatrix()

        # ---------------- MOEDAS ----------------
        for moeda in moedas:

            glColor3f(1, 1, 1)

            fx = moeda[0]
            fy = moeda[1]

            glPushMatrix()
            glTranslate(fx,0,fy)

            glutSolidSphere(0.1,10,10)

            glPopMatrix()




    # ---------------- TEXTOS (HUD) ----------------
    # Desenhados por último para ficarem por cima de tudo
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

    # Double buffering: desenhamos no buffer de trás e trocamos com o da frente,
    # assim a tela nunca mostra o desenho pela metade (sem piscar)
    glutSwapBuffers()


def desenhar_pacman(abertura):

    for i in range(0,20):
        h_borda_de_baixo = -90 + i * 9
        h_do_teto = -90 + (i + 1) * 9 # 180 / 20 = 9     
        glBegin(GL_QUAD_STRIP)
        for j in range(0,21):
            
            volta = abertura + j *(360 - 2 * abertura) / 20
            volta_rad = math.radians(volta)

            h_borda_de_baixo_rad = math.radians(h_borda_de_baixo)
            x = math.cos(h_borda_de_baixo_rad) * math.cos(volta_rad)
                
            y = math.sin(h_borda_de_baixo_rad)
    
            z = math.cos(h_borda_de_baixo_rad) * math.sin(volta_rad)            

            glNormal3f(x,y,z)

            glVertex3f(x * 0.4, y * 0.4, z * 0.4)

            h_do_teto_rad = math.radians(h_do_teto)
            x = math.cos(h_do_teto_rad) * math.cos(volta_rad)

            y = math.sin(h_do_teto_rad)

            z = math.cos(h_do_teto_rad) * math.sin(volta_rad)

            glNormal3f(x,y,z)
            glVertex3f(x * 0.4, y * 0.4, z * 0.4)



        glEnd()
            

        




def mover_fantasmas():
    """IA dos fantasmas: em cada casa escolhem uma direção livre, evitando voltar."""

    for fantasma in inimigos:
        fx, fy, dx, dy = fantasma

        possiveis = []

        # Verificar todas as direções possíveis (as que não dão em parede)
        for ndx, ndy in DIRECOES:
            nx = fx + ndx
            ny = fy + ndy

            if mapa[ny][nx] != '#':
                possiveis.append((ndx, ndy))

        # Remover a direção de volta (list comprehension: nova lista sem a direção oposta)
        sem_volta = [d for d in possiveis if d != (-dx, -dy)]

        # Só usa a lista sem a volta se ela não ficou vazia;
        # num beco sem saída a volta é a única opção, então ela é mantida
        if sem_volta:
            possiveis = sem_volta

        # Sortear uma direção
        if possiveis:
            ndx, ndy = random.choice(possiveis)

            # Atualizar direção (lista pode ser alterada; por isso o fantasma é lista e não tupla)
            fantasma[2] = ndx
            fantasma[3] = ndy

            # Atualizar posição
            fantasma[0] += ndx
            fantasma[1] += ndy



def checar_colisao_fantasma():
    """Colisão Pac-Man x fantasma: como tudo anda em casas inteiras,
    colidir é estar na mesma posição da grade."""
    global jogador, vidas, estado

    for fantasma in inimigos:
        if (fantasma[0],fantasma[1]) == jogador:
            vidas -=1
            if vidas <= 0:
                estado = 'GameOver'
            jogador = inicio_jogador  # volta para o ponto de partida
            print(vidas)



def carregar_mapa():
    """Lê a fase do arquivo texto e monta as estruturas do jogo.
    Legenda: '#' parede, '.' moeda, 'P' Pac-Man, 'E' fantasma, ' ' chão vazio.
    Também é chamada no R para reiniciar a fase."""
    global mapa, jogador, inimigos, moedas, inicio_jogador
    mapa = []
    inimigos = []
    moedas = []

    with open('fase1.txt') as f:
        lines = f.readlines()
        for linha in lines:
            mapa.append(linha.rstrip('\n'))  # tira a quebra de linha do final

        # y = número da linha, x = posição do caractere na linha
        for y, linha in enumerate(mapa):
            for x, caractere in enumerate(linha):
                if caractere == 'P':
                    jogador = (x,y)
                    inicio_jogador = (x,y)
                elif caractere == 'E':
                    inimigos.append([x,y,0,0])  # [x, y, dx, dy]: começa indo para a direita
                elif caractere == '.':
                    moedas.append((x,y))

        print(jogador, len(inimigos), len(moedas))
        print(inimigos)

def timer(valor):
    """Coração da animação: o GLUT chama esta função a cada 16 ms (~60 vezes por segundo).
    Ela atualiza o jogo, pede redesenho e se reagenda."""

    global contador, estado

    if estado == 'Jogando':
        contador += 1 

    # Freio dos fantasmas: só andam a cada 60 toques (~1 passo por segundo).
    # Fora do estado 'Jogando' nada se move: é assim que o pause funciona.
    if estado == 'Jogando' and contador % 60 == 0:
        mover_fantasmas()

    # Colisão e vitória são checadas em todo toque, para não deixar passar nenhuma batida
    if estado == 'Jogando':
        checar_colisao_fantasma()
        if len(moedas) == 0:
            estado = 'Vitoria'


    glutPostRedisplay()          # pede ao GLUT para redesenhar a tela
    glutTimerFunc(16, timer, 0)  # reagenda o timer (ele só toca uma vez por chamada)

def teclado(key, x, y):
    """Callback das teclas comuns. A tecla chega em bytes (ex.: b'p').
    As transições da máquina de estados acontecem aqui."""
    global estado, vidas, pontos, modo_camera
    if estado == 'Inicio':
        if key == b'\r':  # ENTER
            estado = 'Jogando'
    elif estado == 'Jogando':
        if key == b'p':
            estado = 'Pause'

    elif estado == 'Pause':
        if key == b'\r':
            estado = 'Jogando'
    elif estado == 'GameOver':
        if key == b'r':
            # reinicia tudo: estado, vidas, pontos e a fase (moedas e posições)
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


    # Troca de câmera (funciona em qualquer estado)
    if key == b'c':
        if modo_camera == 'cima':
            modo_camera = 'seguir'
        else:
            modo_camera = 'cima'

    # ESC fecha o jogo. sys.exit() não funciona aqui porque o loop do GLUT é em C
    # e ignora a exceção do Python; glutLeaveMainLoop pede ao próprio GLUT para parar.
    if key == b'\x1b':
        glutLeaveMainLoop()


def teclas_especiais(key, x, y):
    """Callback das setas (teclas especiais não passam pelo glutKeyboardFunc).
    Colisão com o cenário: antes de andar, testa se a casa de destino é parede."""
    global jogador, pontos, direcao_pacman

    if estado == 'Jogando':

        jx, jy = jogador



        # destino começa igual à posição atual; cada seta só altera o que muda
        nx, ny = jx, jy

        # no arquivo a linha 0 é o topo, então subir é diminuir o y
        if key == GLUT_KEY_UP:
            ny -= 1
            direcao_pacman = 90

        if key == GLUT_KEY_DOWN:
            ny += 1
            direcao_pacman = 270

        if key == GLUT_KEY_LEFT:
            nx -= 1
            direcao_pacman = 180

        if key == GLUT_KEY_RIGHT:
            nx += 1
            direcao_pacman = 0

        # mapa[linha][coluna] -> y primeiro, depois x
        if mapa[ny][nx] != '#':
            jogador = (nx, ny)

        # Colisão Pac-Man x moeda: se a casa tem moeda, ela sai da lista e soma pontos
        if (nx,ny) in moedas:
            moedas.remove((nx,ny))
            pontos = pontos + 10
            print(pontos)


def desenhar_texto(x,y, texto):
    """Escreve texto na tela em coordenadas de pixel (0,0 = canto inferior esquerdo).
    Troca temporariamente para uma projeção 2D ortográfica, como um adesivo
    colado na lente, e depois devolve a projeção 3D."""
    glDisable(GL_DEPTH_TEST)  # o texto não pode ser escondido pelos objetos 3D

    glDisable(GL_LIGHTING)
    
    # Guarda a projeção 3D e troca para uma 2D do tamanho da janela
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor(1, 1, 1)
    glRasterPos2f(x, y)  # posição da "caneta"

    # glutBitmapCharacter escreve uma letra por vez; ord() converte a letra no código numérico
    for letra in texto:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(letra))

    # Devolve tudo na ordem inversa (último a entrar, primeiro a sair)
    glPopMatrix()

    glMatrixMode(GL_PROJECTION)

    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)

    # Iluminação: liga o sistema de luz, acende a lâmpada 0 e faz o glColor3f
    # valer como cor do material dos objetos
    glEnable(GL_LIGHTING)



def carregar_textura(nome_arquivo):
    """Lê uma imagem com o Pillow e envia para a placa de vídeo como textura.
    Devolve o número (id) da textura, usado depois no glBindTexture."""
    imagem = Image.open(nome_arquivo).convert('RGB')
    dados = imagem.tobytes()  # o OpenGL recebe a imagem como sequência crua de bytes
    largura, altura = imagem.size

    rgb_textura = glGenTextures(1)  # reserva um id de textura

    glBindTexture(GL_TEXTURE_2D, rgb_textura)

    # Filtros: como suavizar a imagem ao encolher (MIN) e ao esticar (MAG)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Repetição da imagem como azulejo nas duas direções (S = horizontal, T = vertical)
    glTexParameteri(GL_TEXTURE_2D,  GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexParameteri(GL_TEXTURE_2D,  GL_TEXTURE_WRAP_S, GL_REPEAT)

    # Lê os bytes sem exigir alinhamento de 4 (evita textura torta com larguras "quebradas")
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, largura, altura, 0, GL_RGB, GL_UNSIGNED_BYTE, dados)

    return rgb_textura






# ----------------------------- PROGRAMA PRINCIPAL -----------------------------
glutInit()
glutInitDisplayMode(GLUT_RGB| GLUT_DOUBLE | GLUT_DEPTH )  # cores RGB, double buffer e buffer de profundidade
glutInitWindowSize(width, height)
glutInitWindowPosition(200,200)
janela = glutCreateWindow(b'pac-man')  # título em bytes (o GLUT é em C)

inicializar()  # só depois de criar a janela, quando o OpenGL já existe

# Registro dos callbacks: entregamos as funções ao GLUT, que as chama quando precisar
glutDisplayFunc(draw)

glutTimerFunc(16, timer, 0)  # primeiro "giro" do timer
glutKeyboardFunc(teclado)
glutSpecialFunc(teclas_especiais)
carregar_mapa()
glutMainLoop()  # loop infinito do GLUT: daqui em diante ele controla o programa













from OpenGL.GL import * 
from OpenGL.GLU import * 
from OpenGL.GLUT import * 

width, height = 800, 600


estado = 'Inicio'

jogador = None

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
    glLoadIdentity()
    glutSwapBuffers() # importante para doubl;e buffering
    
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
                    inimigos.append((x,y))
                elif caractere == '.':
                    moedas.append((x,y))
                    
        print(jogador, len(inimigos), len(moedas))
    
def timer(valor):
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
    

    
    
glutInit() 
glutInitDisplayMode(GLUT_RGB| GLUT_DOUBLE | GLUT_DEPTH )
glutInitWindowSize(width, height)
glutInitWindowPosition(200,200)
janela = glutCreateWindow(b'pac-man')
glutDisplayFunc(draw)

glutTimerFunc(16, timer, 0)
glutKeyboardFunc(teclado)
carregar_mapa()
glutMainLoop()





    
    
    





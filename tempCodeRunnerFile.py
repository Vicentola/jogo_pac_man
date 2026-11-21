estado = 'Pause'


def draw():
    
    
    if estado == 'Jogando':
        glClearColor(4,5,3,1)
    elif estado == 'Pause':
        glClearColor(9,3,4,2)
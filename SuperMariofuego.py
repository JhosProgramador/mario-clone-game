import pygame
import sys
import random
import math
import os


# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600  # Define el ancho y la altura de la ventana del juego
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Crea la ventana del juego con las dimensiones definidas
pygame.display.set_caption("Juego Estilo Mario Bros")  # Establece el título de la ventana



# Colores
WHITE = (255, 255, 255)  # Define el color blanco en formato RGB
BLACK = (0, 0, 0)      # Define el color negro en formato RGB

# Cargar imágenes
try:
    # Imágenes del jugador
    player_images_walk = [
        pygame.image.load("assets/images/player3.png").convert_alpha(),  # Carga la imagen para la animación de caminar 1
        pygame.image.load("assets/images/player1.png").convert_alpha(),  # Carga la imagen para la animación de caminar 2
    ]
    player_jump_image = pygame.image.load("assets/images/player2.png").convert_alpha()  # Imagen del jugador saltando

    # Imágenes del enemigo
    enemy_images = [
        pygame.image.load("assets/images/enemy.png").convert_alpha(),   # Imagen del enemigo 1
        pygame.image.load("assets/images/enemy1.png").convert_alpha(),  # Imagen del enemigo 2
    ]

    # Imágenes de monedas (6 frames de animación)
    coin_images = [
        pygame.image.load("assets/images/coin1.png").convert_alpha(),  # Frame 1 de animación de moneda
        pygame.image.load("assets/images/coin2.png").convert_alpha(),  # Frame 2 de animación de moneda
        pygame.image.load("assets/images/coin3.png").convert_alpha(),  # Frame 3 de animación de moneda
        pygame.image.load("assets/images/coin4.png").convert_alpha(),  # Frame 4 de animación de moneda
        pygame.image.load("assets/images/coin5.png").convert_alpha(),  # Frame 5 de animación de moneda
        pygame.image.load("assets/images/coin6.png").convert_alpha(),  # Frame 6 de animación de moneda
    ]
    
    ghost_images = [
        pygame.image.load("assets/images/ghost1.png").convert_alpha(),
        pygame.image.load("assets/images/ghost2.png").convert_alpha(),
        pygame.image.load("assets/images/ghost3.png").convert_alpha(),
        pygame.image.load("assets/images/ghost4.png").convert_alpha(),
    ]
    

    # Escalar imágenes para ajustar su tamaño
    player_images_walk = [pygame.transform.scale(img, (40, 60)) for img in player_images_walk]  # Escala imágenes del jugador
    player_jump_image = pygame.transform.scale(player_jump_image, (40, 60))  # Escala imagen de salto
    enemy_images = [pygame.transform.scale(img, (45, 45)) for img in enemy_images]  # Escala imágenes de enemigos
    coin_images = [pygame.transform.scale(img, (75, 75)) for img in coin_images]  # Escala imágenes de monedas
    ghost_images = [pygame.transform.scale(img, (110, 110)) for img in ghost_images]

   
    platform_image = pygame.image.load("assets/images/platform.jpg").convert()  # Imagen de plataforma
    platform_image = pygame.transform.scale(platform_image, (150, 10))  # Escala imagen de plataforma
    background_image = pygame.image.load("assets/images/background.jpg").convert()  # Imagen de fondo
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Escala fondo al tamaño de ventana
    door_image = pygame.image.load("assets/images/door.jpg").convert_alpha()  # Imagen de puerta
    door_image = pygame.transform.scale(door_image, (50, 80))    # Escala imagen de puerta
except pygame.error as e:  # Captura errores al cargar imágenes
    print(f"Error al cargar una imagen: {e}")
    sys.exit()

# Cargar sonidos
try:
    jump_sound = pygame.mixer.Sound("assets/audio/jump.mp3")  # Sonido de salto
    coin_sound = pygame.mixer.Sound("assets/audio/coin.mp3")  # Sonido de moneda
    game_over_sound = pygame.mixer.Sound("assets/audio/death.mp3")  # Sonido de game over
    background_music = pygame.mixer.Sound("assets/audio/background_music.mp3")  # Música de fondo
    victory_sound = pygame.mixer.Sound("assets/audio/victory.mp3")  # Sonido de victoria
except pygame.error as e:  # Captura errores al cargar sonidos
    print(f"Error al cargar un sonido: {e}")

# Variables del juego
WORLD_LENGTH = 5000  # Longitud total del mundo del juego
FPS = 60         # Fotogramas por segundo

# Variables del jugador
player_width, player_height = 40, 60  # Tamaño del jugador
player_x, player_y = 50, HEIGHT - player_height - 10  # Posición inicial
player_speed = 5  # Velocidad horizontal
player_jump = -15  # Fuerza de salto inicial
velocity_y = 0    # Velocidad vertical actual
is_jumping = False  # Indica si el jugador está saltando
gravity = 0.8     # Fuerza de gravedad
can_double_jump = False  # Indica si puede hacer doble salto
double_jump_power = player_jump * 1.9  # Fuerza del doble salto
can_jump = True     # Controla si puede iniciar nuevo salto
current_image_index = 0  # Índice de imagen actual
animation_frame_rate = 10  # Velocidad de animación
frame_count = 0      # Contador de fotogramas
facing_right = True  # Indica si mira a la derecha

# Variables para bolas de fuego
fireballs = []  # Lista de bolas de fuego
fire_cooldown = 0  # Enfriamiento para disparos

# Variables del mundo
world_scroll = 0    # Desplazamiento horizontal
scroll_speed = 5    # Velocidad de desplazamiento

# Plataformas - Configuración mejorada
platforms = [pygame.Rect(0, HEIGHT - 10, WORLD_LENGTH, 10)]  # Plataforma base que cubre todo el suelo
num_platforms = 61  # Número de plataformas adicionales
min_y = 200         # Altura mínima para plataformas
max_y = HEIGHT - 50 # Altura máxima para plataformas
min_x_gap = 200     # Espacio mínimo entre plataformas en X
max_x_gap = 500     # Espacio máximo entre plataformas en X
current_x = 200     # Posición inicial en X para generación

# Generación de plataformas con distribución más consistente
while len(platforms) < num_platforms + 1:
    platform_width = random.randint(100, 200)  # Ancho aleatorio
    platform_y = random.randint(min_y, max_y)  # Altura aleatoria
    
    # Asegurar que las plataformas no estén demasiado cerca verticalmente
    valid_position = True
    for platform in platforms[-5:]:  # Revisar las últimas plataformas creadas
        if abs(platform.y - platform_y) < 50 and abs(platform.x - current_x) < 300:
            valid_position = False
            break
    
    if valid_position:
        platforms.append(pygame.Rect(current_x, platform_y, platform_width, 20))
        current_x += platform_width + random.randint(min_x_gap, max_x_gap)
    
    if current_x > WORLD_LENGTH - 200:
        break

# Clase para monedas animadas
class Coin:
    def __init__(self, x, y):
        self.x = x                      # Posición X
        self.y = y                      # Posición Y
        self.images = coin_images       # Imágenes de animación
        self.current_image_index = 0    # Índice de imagen actual
        self.animation_speed = 5        # Velocidad de animación
        self.animation_counter = 0      # Contador para animación
        self.rect = pygame.Rect(x, y, 30, 30)  # Rectángulo de colisión
        self.collected = False          # Indica si fue recolectada

    def update(self):
        # Actualizar animación
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_image_index = (self.current_image_index + 1) % len(self.images)

    def draw(self, surface, world_scroll):
        if not self.collected:
            coin_rect = pygame.Rect(self.x - world_scroll, self.y, 30, 30)
            if (world_scroll - 100 < self.x < world_scroll + WIDTH + 100):
                surface.blit(self.images[self.current_image_index], coin_rect.topleft)

# Clase para el fantasma animado
class Ghost:
    def __init__(self, x, y):
        self.images = ghost_images
        self.current_image_index = 0
        self.animation_speed = 12
        self.animation_counter = 0
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = random.uniform(1.0, 2.5)
        self.direction = random.uniform(0, 2 * math.pi)
        self.change_direction_counter = 0
        self.change_direction_frequency = random.randint(60, 180)
        
    def update(self):
        # Movimiento
        self.rect.x += math.cos(self.direction) * self.speed
        self.rect.y += math.sin(self.direction) * self.speed
        
        # Cambiar dirección periódicamente
        self.change_direction_counter += 1
        if self.change_direction_counter >= self.change_direction_frequency:
            self.direction = random.uniform(0, 2 * math.pi)
            self.change_direction_counter = 0
            self.change_direction_frequency = random.randint(60, 180)
        
        # Rebotar en bordes del mundo
        if self.rect.x < 0 or self.rect.x > WORLD_LENGTH - 40:
            self.direction = math.pi - self.direction
        if self.rect.y < 50 or self.rect.y > HEIGHT - 50:
            self.direction = -self.direction
        
        # Animación
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
    
    def draw(self, surface, world_scroll):
        ghost_rect = pygame.Rect(self.rect.x - world_scroll, self.rect.y, 40, 40)
        if (world_scroll - 100 < self.rect.x < world_scroll + WIDTH + 100):
            if math.cos(self.direction) < 0:  # Voltear imagen si va hacia la izquierda
                surface.blit(pygame.transform.flip(self.images[self.current_image_index], True, False), ghost_rect.topleft)
            else:
                surface.blit(self.images[self.current_image_index], ghost_rect.topleft)

# Clase para las bolas de fuego
class Fireball:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 1 para derecha, -1 para izquierda
        self.speed = 10
        self.radius = 10
        self.active = True

    def update(self):
        self.x += self.direction * self.speed
        # Desactivar si sale de los límites del mundo
        if self.x < 0 or self.x > WORLD_LENGTH:
            self.active = False

    def draw(self, screen, world_scroll):
        pygame.draw.circle(
            screen, 
            (255, 100, 0),  # Color naranja
            (int(self.x - world_scroll), int(self.y)), 
            self.radius
        )

# Crear fantasmas
ghosts = []
num_ghosts = 4
for _ in range(num_ghosts):
    ghost_x = random.randint(100, WORLD_LENGTH - 100)
    ghost_y = random.randint(100, HEIGHT - 100)
    ghosts.append(Ghost(ghost_x, ghost_y))

# Clase Enemy con animación
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range):
        super().__init__()
        self.images = enemy_images
        self.current_image_index = 0
        self.animation_frame_rate = 10
        self.frame_count = 0

        self.image = self.images[self.current_image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = -2
        self.initial_x = x
        self.move_range = move_range
        self.left_boundary = x - move_range
        self.right_boundary = x + move_range
        self.original_x = x

    def update(self):
        self.rect.x += self.velocity_x
        # Invertir dirección si alcanza los límites de movimiento
        if self.rect.x < self.original_x - self.move_range or self.rect.x > self.original_x + self.move_range:
            self.velocity_x *= -1

        # Actualizar animación
        self.frame_count += 1
        if self.frame_count % self.animation_frame_rate == 0:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.image = self.images[self.current_image_index]



# Crear los enemigos
enemies_list = pygame.sprite.Group()
enemies_list.add(
    Enemy(500, HEIGHT - 50 - 40, 100),
    Enemy(1200, 350 - 40, 150),
    Enemy(1800, HEIGHT - 100 - 40, 80),
    Enemy(2500, 250 - 40, 120),
    Enemy(3500, HEIGHT - 50 - 40, 100),
    Enemy(4500, 250 - 40, 120)
)

# Puerta de victoria
door_width = 50
door_height = 80
door_x = WORLD_LENGTH - 100 - door_width
door_y = HEIGHT - door_height - 10
door_rect = pygame.Rect(door_x, door_y, door_width, door_height)

# Puntuación
score = 0
font = pygame.font.Font(None, 36)

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Crear monedas (esto queda fuera de main(), al mismo nivel que las otras variables globales)
coins = []          # Lista para almacenar las instancias de la clase Coin
num_coins = 80      # Número de monedas que se crearán
for _ in range(num_coins):
    coin_x = random.randint(50, WORLD_LENGTH - 50)
    coin_y = random.randint(100, HEIGHT - 50)
    coins.append(Coin(coin_x, coin_y))


def main():
    global player_x, player_y, velocity_y, is_jumping, score, world_scroll
    global can_double_jump, can_jump, current_image_index, frame_count, facing_right
    global fire_cooldown, fireballs, coins  # Añadimos coins a las variables globales

    # Inicializar el reloj
    clock = pygame.time.Clock()

    # Reproducir música de fondo
    try:
        pygame.mixer.Sound.play(background_music, loops=-1)
    except:
        pass

    running = True
    game_over = False
    victory = False

    while running:
        screen.fill(WHITE)

        # Dibujar el fondo
        num_backgrounds = (WORLD_LENGTH // background_image.get_width()) + 1
        for i in range(num_backgrounds):
            screen.blit(background_image, (i * background_image.get_width() - world_scroll, 0))

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_over or victory):
                    return
                # Salto con 'S' (Salto normal o Doble Salto)
                if event.key == pygame.K_s:
                    if not is_jumping and can_jump:
                        velocity_y = player_jump
                        is_jumping = True
                        can_jump = False
                        can_double_jump = True
                        try:
                            jump_sound.play()
                        except:
                            pass
                    elif is_jumping and can_double_jump:
                        velocity_y = double_jump_power
                        can_double_jump = False
                        try:
                            jump_sound.play()
                        except:
                            pass

                if event.key == pygame.K_f and fire_cooldown == 0:
                    # Offset para la mano según dirección
                    hand_offset_x = 30 if facing_right else -10
                    hand_offset_y = 20
                    
                    fireballs.append(Fireball(
                        player_x + world_scroll + hand_offset_x,
                        player_y + hand_offset_y,
                        1 if facing_right else -1
                    ))
                    fire_cooldown = 20  # Cooldown de 20 frames
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    can_jump = True

        if not game_over and not victory:
            keys = pygame.key.get_pressed()

            # Movimiento horizontal y animación
            moving = False
            if keys[pygame.K_LEFT]:
                if player_x > 0:
                    player_x -= player_speed
                    moving = True
                    facing_right = False
                elif world_scroll > 0:
                    world_scroll -= scroll_speed
                    moving = True
                    facing_right = False

            if keys[pygame.K_RIGHT]:
                if player_x < WIDTH - player_width:
                    player_x += player_speed
                    moving = True
                    facing_right = True
                    if player_x > WIDTH * 0.6 and world_scroll < WORLD_LENGTH - WIDTH:
                        world_scroll += scroll_speed
                        player_x -= scroll_speed
                elif world_scroll >= WORLD_LENGTH - WIDTH and player_x < WIDTH - player_width:
                    player_x += player_speed
                    moving = True
                    facing_right = True

            # Actualizar animación del jugador
            if moving:
                frame_count += 1
                if frame_count % animation_frame_rate == 0:
                    current_image_index = (current_image_index + 1) % len(player_images_walk)

            # Aplicar gravedad
            velocity_y += gravity
            player_y += velocity_y

            # --- SISTEMA MEJORADO DE COLISIONES CON PLATAFORMAS ---
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            on_ground = False

            # Primero dibujamos todas las plataformas visibles
            for platform in platforms:
                platform_rect = platform.move(-world_scroll, 0)
                if (world_scroll - 100 < platform.x < world_scroll + WIDTH + 100):
                    screen.blit(platform_image, platform_rect.topleft)

            # Luego verificamos colisiones con más precisión
            for platform in platforms:
                platform_rect = platform.move(-world_scroll, 0)
                if (world_scroll - 100 < platform.x < world_scroll + WIDTH + 100):
                    if player_rect.colliderect(platform_rect):
                        # Calcular superposición en cada eje
                        overlap_x = min(player_rect.right, platform_rect.right) - max(player_rect.left, platform_rect.left)
                        overlap_y = min(player_rect.bottom, platform_rect.bottom) - max(player_rect.top, platform_rect.top)
                        
                        # Determinar desde qué dirección ocurrió la colisión
                        if overlap_y < overlap_x:
                            # Colisión vertical (desde arriba o abajo)
                            if velocity_y > 0 and player_rect.bottom > platform_rect.top and player_rect.top < platform_rect.top:
                                # Colisión desde arriba (aterrizando)
                                player_y = platform_rect.top - player_height
                                velocity_y = 0
                                is_jumping = False
                                can_double_jump = False
                                can_jump = True
                                on_ground = True
                            elif velocity_y < 0 and player_rect.top < platform_rect.bottom and player_rect.bottom > platform_rect.bottom:
                                # Colisión desde abajo (golpear cabeza)
                                player_y = platform_rect.bottom
                                velocity_y = 0
                        else:
                            # Colisión horizontal (desde los lados)
                            if player_rect.right > platform_rect.left and player_rect.left < platform_rect.left:
                                # Colisión desde la izquierda
                                player_x = platform_rect.left - player_width
                            elif player_rect.left < platform_rect.right and player_rect.right > platform_rect.right:
                                # Colisión desde la derecha
                                player_x = platform_rect.right

            # Verificación adicional para el suelo base
            if player_y + player_height >= HEIGHT:
                player_y = HEIGHT - player_height
                velocity_y = 0
                is_jumping = False
                can_double_jump = False
                can_jump = True
                on_ground = True

            # Aplicar gravedad solo si no está en el suelo
            if not on_ground:
                velocity_y += gravity * 0.9  # Gravedad ligeramente reducida para mejor control
            else:
                velocity_y = 0  # Asegurarse de que no hay velocidad vertical cuando está en el suelo

            # Actualizar y dibujar monedas
            for coin in coins[:]:
                coin.update()
                coin.draw(screen, world_scroll)

                # Verificar colisión con jugador
                coin_rect = pygame.Rect(coin.x - world_scroll, coin.y, 30, 30)
                if player_rect.colliderect(coin_rect) and not coin.collected:
                    coin.collected = True
                    coins.remove(coin)
                    score += 10
                    try:
                        coin_sound.play()
                    except:
                        pass

            # Actualizar y dibujar fantasmas
            for ghost in ghosts:
                ghost.update()
                ghost.draw(screen, world_scroll)
                
                # Verificar colisión con jugador
                ghost_rect = pygame.Rect(ghost.rect.x - world_scroll, ghost.rect.y, 40, 40)
                if player_rect.colliderect(ghost_rect):
                    game_over = True
                    try:
                        pygame.mixer.stop()
                        game_over_sound.play()
                    except:
                        pass

            # Actualizar y dibujar enemigos
            enemies_list.update()
            for enemy in enemies_list:
                enemy_rect_on_screen = enemy.rect.move(-world_scroll, 0)
                if (world_scroll - 100 < enemy.rect.x < world_scroll + WIDTH + 100):
                    screen.blit(enemy.image, enemy_rect_on_screen.topleft)

                    if player_rect.colliderect(enemy_rect_on_screen):
                        if velocity_y > 0 and player_rect.bottom < enemy_rect_on_screen.top + 20:
                            velocity_y = player_jump * 0.8
                            enemy.kill()
                            score += 50
                        else:
                            game_over = True
                            try:
                                pygame.mixer.stop()
                                game_over_sound.play()
                            except:
                                pass

            # Actualizar bolas de fuego
            for fireball in fireballs[:]:
                fireball.update()
                if not fireball.active:
                    fireballs.remove(fireball)

            # Dibujar bolas de fuego
            for fireball in fireballs:
                fireball.draw(screen, world_scroll)

                # Colisión bolas de fuego con enemigos
                fireball_rect = pygame.Rect(
                    fireball.x - fireball.radius - world_scroll,
                    fireball.y - fireball.radius,
                    fireball.radius * 2,
                    fireball.radius * 2
                )
    
                for enemy in enemies_list:
                    enemy_rect = enemy.rect.move(-world_scroll, 0)
                    if fireball_rect.colliderect(enemy_rect):
                        enemy.kill()
                        fireball.active = False
                        score += 30
                        break

            # Reducir cooldown
            if fire_cooldown > 0:
                fire_cooldown -= 1

            # Dibujar puerta
            door_rect_on_screen = door_rect.move(-world_scroll, 0)
            screen.blit(door_image, door_rect_on_screen.topleft)

            # Dibujar jugador con animación
            if is_jumping:
                player_image = player_jump_image
            elif moving:
                player_image = player_images_walk[current_image_index]
            else:
                player_image = player_images_walk[0]

            # Voltear imagen si mira a la izquierda
            if not facing_right:
                player_image = pygame.transform.flip(player_image, True, False)

            screen.blit(player_image, (player_x, player_y))

            # Mostrar puntuación
            draw_text(f"Score: {score}", WHITE, 10, 10)

            # Colisión con la puerta
            if player_rect.colliderect(door_rect_on_screen):
                victory = True
                try:
                    pygame.mixer.stop()
                    victory_sound.play()
                except:
                    pass

        # Pantallas de game over y victoria
        if game_over:
            draw_text("¡Game Over!", BLACK, WIDTH//2 - 100, HEIGHT//2 - 18)
            draw_text(f"Puntuación: {score}", BLACK, WIDTH//2 - 80, HEIGHT//2 + 20)
            draw_text("Presiona R para reiniciar", BLACK, WIDTH//2 - 150, HEIGHT//2 + 60)

        if victory:
            draw_text("¡Has Ganado!", BLACK, WIDTH//2 - 100, HEIGHT//2 - 18)
            draw_text(f"Puntuación final: {score}", BLACK, WIDTH//2 - 100, HEIGHT//2 + 20)
            draw_text("Presiona R para reiniciar", BLACK, WIDTH//2 - 150, HEIGHT//2 + 60)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    while True:
        main()
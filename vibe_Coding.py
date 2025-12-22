import pygame
import sys
import math
import random

# Inizializzazione Pygame
pygame.init()

# Dimensioni finestra
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Effetto Ottico Infinito")

# Clock per controllare il frame rate
clock = pygame.time.Clock()
FPS = 60

# Colori
BACKGROUND = (15, 15, 30)
BALL_COLOR = (255, 255, 255)
TEXT_COLOR = (220, 220, 255)
COLORS = [
    (255, 100, 100),    # Rosso
    (100, 255, 100),    # Verde
    (100, 100, 255),    # Blu
    (255, 255, 100),    # Giallo
    (255, 100, 255),    # Magenta
    (100, 255, 255),    # Ciano
    (255, 150, 50),     # Arancione
    (150, 50, 255),     # Viola
]

# Classe per la pallina
class Ball:
    def __init__(self, x, y, radius=8):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = random.uniform(2, 4) * random.choice([-1, 1])
        self.vy = random.uniform(-1, 0)
        self.base_speed = math.sqrt(self.vx**2 + self.vy**2)
        self.gravity = 0.15
        self.damping = 0.88
        self.color = BALL_COLOR
        self.trail = []
        self.max_trail = 8
        self.boost_timer = 0
        self.boost_factor = 1.0
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(2, 4) * random.choice([-1, 1])
        self.vy = random.uniform(-1, 0)
        self.base_speed = math.sqrt(self.vx**2 + self.vy**2)
        self.trail = []
        self.boost_timer = 0
        self.boost_factor = 1.0
    
    def update(self):
        # Applica gravità
        self.vy += self.gravity
        
        # Gestisci accelerazione temporanea
        if self.boost_timer > 0:
            self.boost_timer -= 1
            current_speed = math.sqrt(self.vx**2 + self.vy**2)
            if current_speed > self.base_speed * 1.7:
                # Riduci gradualmente la velocità
                factor = 0.99
                self.vx *= factor
                self.vy *= factor
        
        # Aggiorna posizione
        self.x += self.vx * self.boost_factor
        self.y += self.vy * self.boost_factor
        
        # Ripristina boost factor
        if self.boost_timer <= 0:
            self.boost_factor = 1.0
        
        # Aggiungi posizione alla scia
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
    
    def apply_boost(self):
        # Applica un boost di velocità
        self.boost_factor = 1.4
        self.boost_timer = 12
        self.vx *= 1.15
        self.vy *= 1.15
    
    def draw(self, screen):
        # Disegna la scia
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            radius = int(self.radius * (i / len(self.trail)))
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            if self.boost_timer > 0:
                boost_intensity = self.boost_timer / 12
                pygame.draw.circle(trail_surface, 
                                 (255, 200, 100, int(alpha * boost_intensity)), 
                                 (radius, radius), radius)
            else:
                pygame.draw.circle(trail_surface, (255, 255, 255, alpha), 
                                 (radius, radius), radius)
            screen.blit(trail_surface, (trail_x - radius, trail_y - radius))
        
        # Disegna la pallina
        if self.boost_timer > 0:
            boost_color = (255, 200, 100)
            pygame.draw.circle(screen, boost_color, (int(self.x), int(self.y)), self.radius)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Effetto luce
        pygame.draw.circle(screen, (255, 255, 200), 
                          (int(self.x) - 2, int(self.y) - 2), self.radius // 3)

# Classe per la forma geometrica (SOLO UNA FORMA ALLA VOLTA)
class GeometricShape:
    def __init__(self, center_x, center_y, sides=3):
        self.center_x = center_x
        self.center_y = center_y
        self.sides = sides
        self.base_radius = self.calculate_base_radius()
        self.radius = self.base_radius
        self.color_idx = 0
        self.color = COLORS[self.color_idx]
        
        # Calcola i punti del poligono
        self.points = self.calculate_points()
        
        # Soglie di rimbalzo per cambiare forma
        self.bounce_thresholds = {
            3: 12,     # 12 rimbalzi per passare da 3 a 4 lati
            4: 25,     # 25 rimbalzi per passare da 4 a 5 lati
            5: 40,     # 40 rimbalzi per passare da 5 a 6 lati
            6: 60,     # 60 rimbalzi per passare da 6 a 7 lati
            7: 85,     # 85 rimbalzi per passare da 7 a 8 lati
        }
        self.bounce_count = 0
        self.max_sides = 8
        
        # Per l'effetto visivo al cambio forma
        self.effect_radius = 0
        self.effect_max_radius = 0
        self.effect_alpha = 0
    
    def calculate_base_radius(self):
        base_sizes = {
            3: 220,  # Triangolo
            4: 210,  # Quadrato
            5: 200,  # Pentagono
            6: 190,  # Esagono
            7: 180,  # Ettagono
            8: 170,  # Ottagono
        }
        return base_sizes.get(self.sides, 170)
    
    def calculate_points(self):
        points = []
        angle_step = 2 * math.pi / self.sides
        
        for i in range(self.sides):
            angle = i * angle_step
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            points.append((x, y))
        
        return points
    
    def shrink(self, factor=0.97):
        self.radius *= factor
        min_radius = self.base_radius * 0.4
        if self.radius < min_radius:
            self.radius = min_radius
        self.points = self.calculate_points()
    
    def change_color(self):
        self.color_idx = (self.color_idx + 1) % len(COLORS)
        self.color = COLORS[self.color_idx]
    
    def handle_bounce(self):
        self.bounce_count += 1
        self.shrink(0.97)
        self.change_color()
        
        if self.sides in self.bounce_thresholds and self.bounce_count >= self.bounce_thresholds[self.sides]:
            if self.sides < self.max_sides:
                self.effect_radius = 10
                self.effect_max_radius = self.radius * 1.5
                self.effect_alpha = 255
                return True  # Segnala che la forma deve cambiare
        
        return False
    
    def update_effect(self):
        if self.effect_alpha > 0:
            self.effect_radius += 15
            self.effect_alpha -= 8
            if self.effect_radius > self.effect_max_radius:
                self.effect_alpha = 0
    
    def draw(self, screen):
        # Disegna effetto di transizione
        if self.effect_alpha > 0:
            effect_surface = pygame.Surface((int(self.effect_radius * 2), int(self.effect_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(effect_surface, (*self.color, self.effect_alpha), 
                             (int(self.effect_radius), int(self.effect_radius)), 
                             int(self.effect_radius), 3)
            screen.blit(effect_surface, (self.center_x - self.effect_radius, self.center_y - self.effect_radius))
        
        # Disegna SOLO la forma attuale (nessuna sovrapposizione)
        if len(self.points) > 2:
            pygame.draw.polygon(screen, self.color, self.points, 3)

# Funzione per rilevare collisioni
def check_collision(ball, shape):
    for i in range(len(shape.points)):
        x1, y1 = shape.points[i]
        x2, y2 = shape.points[(i + 1) % len(shape.points)]
        
        distance = point_to_line_distance(ball.x, ball.y, x1, y1, x2, y2)
        
        if distance < ball.radius:
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                nx = -dy / length
                ny = dx / length
                
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                to_center_x = shape.center_x - mid_x
                to_center_y = shape.center_y - mid_y
                
                if (nx * to_center_x + ny * to_center_y) < 0:
                    nx = -nx
                    ny = -ny
                
                dot_product = ball.vx * nx + ball.vy * ny
                ball.vx = ball.vx - 2 * dot_product * nx
                ball.vy = ball.vy - 2 * dot_product * ny
                
                ball.vx *= ball.damping
                ball.vy *= ball.damping
                
                ball.apply_boost()
                
                overlap = ball.radius - distance + 0.5
                ball.x += nx * overlap
                ball.y += ny * overlap
                
                return True
    
    return False

# Funzione per calcolare la distanza tra un punto e un segmento
def point_to_line_distance(px, py, x1, y1, x2, y2):
    abx = x2 - x1
    aby = y2 - y1
    apx = px - x1
    apy = py - y1
    
    ab2 = abx*abx + aby*aby
    if ab2 == 0:
        return math.sqrt(apx*apx + apy*apy)
    
    t = (apx*abx + apy*aby) / ab2
    t = max(0, min(1, t))
    
    closest_x = x1 + t * abx
    closest_y = y1 + t * aby
    
    dx = px - closest_x
    dy = py - closest_y
    return math.sqrt(dx*dx + dy*dy)

# Funzione principale
def main():
    # Crea gli oggetti INIZIALI
    ball = Ball(WIDTH // 2, HEIGHT // 3)
    shape = GeometricShape(WIDTH // 2, HEIGHT // 2, sides=3)
    
    # Variabili per il contatore
    counter = 0
    font = pygame.font.SysFont('Arial', 36, bold=True)
    small_font = pygame.font.SysFont('Arial', 24)
    
    # Variabili per l'effetto visivo di transizione
    transition_alpha = 0
    transition_text = ""
    
    # Loop principale
    running = True
    while running:
        # Gestione eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # RESET COMPLETO - Ricrea tutti gli oggetti
                    ball = Ball(WIDTH // 2, HEIGHT // 3)
                    shape = GeometricShape(WIDTH // 2, HEIGHT // 2, sides=3)
                    counter = 0
                    transition_alpha = 0
                elif event.key == pygame.K_SPACE:
                    # Cambia forma manualmente
                    new_sides = shape.sides + 1
                    if new_sides > shape.max_sides:
                        new_sides = 3
                    shape = GeometricShape(WIDTH // 2, HEIGHT // 2, sides=new_sides)
                    counter = min(new_sides - 3, shape.max_sides - 3)
        
        # Aggiorna la pallina
        ball.update()
        
        # Aggiorna l'effetto della forma
        shape.update_effect()
        
        # Controlla collisioni con la forma
        if check_collision(ball, shape):
            shape_changed = shape.handle_bounce()
            
            if shape_changed:
                counter += 1
                transition_text = f"FORMA {shape.sides + 1} LATI!"
                transition_alpha = 255
                
                # CREA UNA NUOVA FORMA (non resettare la vecchia)
                new_sides = shape.sides + 1
                shape = GeometricShape(WIDTH // 2, HEIGHT // 2, sides=new_sides)
        
        # PULISCI LO SCHERMO COMPLETAMENTE
        screen.fill(BACKGROUND)
        
        # Disegna la forma (SOLO UNA)
        shape.draw(screen)
        
        # Disegna la pallina
        ball.draw(screen)
        
        # Disegna il contatore principale
        counter_text = font.render(f"LIVELLO: {counter}", True, TEXT_COLOR)
        screen.blit(counter_text, (20, 20))
        
        # Disegna informazioni sulla forma corrente
        sides_text = small_font.render(f"Lati: {shape.sides}", True, shape.color)
        screen.blit(sides_text, (20, 70))
        
        # Disegna progresso verso prossima forma
        if shape.sides in shape.bounce_thresholds:
            progress = shape.bounce_count / shape.bounce_thresholds[shape.sides]
            progress_text = small_font.render(f"Rimbalzi: {shape.bounce_count}/{shape.bounce_thresholds[shape.sides]}", True, TEXT_COLOR)
            screen.blit(progress_text, (20, 110))
            
            # Barra di progresso
            bar_width = 200
            bar_height = 10
            pygame.draw.rect(screen, (50, 50, 70), (20, 140, bar_width, bar_height), 0, 3)
            pygame.draw.rect(screen, shape.color, (20, 140, int(bar_width * progress), bar_height), 0, 3)
            pygame.draw.rect(screen, (100, 100, 120), (20, 140, bar_width, bar_height), 1, 3)
        
        # Disegna velocità
        stats_y = HEIGHT - 80
        speed = math.sqrt(ball.vx**2 + ball.vy**2)
        speed_text = small_font.render(f"Velocità: {speed:.1f}", True, TEXT_COLOR)
        screen.blit(speed_text, (20, stats_y))
        
        # Disegna boost se attivo
        if ball.boost_timer > 0:
            boost_text = small_font.render("BOOST!", True, (255, 200, 100))
            screen.blit(boost_text, (WIDTH - 100, 20))
        
        # Disegna istruzioni
        instructions = small_font.render("R: Reset | ESC: Esci", True, (150, 150, 180))
        screen.blit(instructions, (WIDTH - 200, HEIGHT - 30))
        
        # Disegna l'effetto di transizione se attivo
        if transition_alpha > 0:
            transition_surface = font.render(transition_text, True, (255, 255, 200))
            transition_surface.set_alpha(transition_alpha)
            text_rect = transition_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            screen.blit(transition_surface, text_rect)
            
            transition_alpha -= 3
        
        # Aggiorna lo schermo
        pygame.display.flip()
        
        # Controlla il frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
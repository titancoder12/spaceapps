import pygame
import random
import math

# Screen dimensions
WIDTH, HEIGHT = 700, 700

# Game settings
MAX_SPEED = 3
NUM_ANTS = 5
STOMP_RADIUS = 30

class Ant:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        # Random direction
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * MAX_SPEED
        self.alive = True

    def update(self):
        if not self.alive:
            return
            
        # Move the ant
        self.position += self.velocity
        
        # Bounce off walls
        if self.position.x <= 0 or self.position.x >= WIDTH:
            self.velocity.x *= -1
        if self.position.y <= 0 or self.position.y >= HEIGHT:
            self.velocity.y *= -1
            
        # Keep in bounds
        self.position.x = max(0, min(self.position.x, WIDTH))
        self.position.y = max(0, min(self.position.y, HEIGHT))

    def draw(self, screen):
        if self.alive:
            # Draw ant as a simple red circle
            pygame.draw.circle(screen, (255, 0, 0), (int(self.position.x), int(self.position.y)), 8)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Bug Game")
    clock = pygame.time.Clock()
    
    # Create ants
    ants = []
    for _ in range(NUM_ANTS):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        ants.append(Ant(x, y))
    
    score = 0
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.Vector2(event.pos)
                    # Check for ants within stomp radius
                    for ant in ants:
                        if ant.alive and ant.position.distance_to(mouse_pos) < STOMP_RADIUS:
                            ant.alive = False
                            score += 1
        
        # Update ants
        for ant in ants:
            ant.update()
        
        # Spawn new ant if all are dead
        alive_ants = [ant for ant in ants if ant.alive]
        if len(alive_ants) == 0:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            ants.append(Ant(x, y))
        
        # Draw everything
        screen.fill((0, 100, 0))  # Green background
        
        for ant in ants:
            ant.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # Draw cursor circle to show stomp radius
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(screen, (255, 255, 255), mouse_pos, STOMP_RADIUS, 2)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()

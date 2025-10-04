import pygame
import random

def earth_collision(screen, m, v):
    screen.fill((0, 0, 0))
    print("Civilization was set back by 400 years.")

    font = pygame.font.SysFont(None, 48)

    # Calculate kinetic energy: KE = 1/2 * m * v^2
    mass = m # this is in kg
    velocity = v # this is in m/s
    KE = 0.5 * mass * velocity ** 2
    print(f"Kinetic Energy of impact: {KE:.2e} Joules")

    chance = random.randint(0, 100)

    # Display kinetic energy of impact
    ke_text = font.render(f"Kinetic Energy: {KE:.2e} Joules", True, (255, 255, 0))
    ke_rect = ke_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(ke_text, ke_rect)

    if chance >= 70:
        print("A massive tsunami has struck the coasts.")
        tsunami_text = font.render("A massive tsunami has struck the coasts.", True, (255, 0, 0))
        tsunami_rect = tsunami_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
        screen.blit(tsunami_text, tsunami_rect)
    elif chance >= 40:
        print("Global temperatures have risen dramatically.")
        temp_text = font.render("Global temperatures have risen dramatically.", True, (255, 0, 0))
        temp_rect = temp_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
        screen.blit(temp_text, temp_rect)
    elif chance == 2:
        print("Widespread wildfires are devastating forests.")
        fire_text = font.render("Widespread wildfires are devastating forests.", True, (255, 0, 0))
        fire_rect = fire_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
        screen.blit(fire_text, fire_rect)
    else:
        print("A volcanic winter has plunged the world into darkness.")
        volcano_text = font.render("A volcanic winter has plunged the world into darkness.", True, (255, 0, 0))
        volcano_rect = volcano_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
        screen.blit(volcano_text, volcano_rect)
    # You can add more complex behavior here, like reducing health, playing a sound, etc.
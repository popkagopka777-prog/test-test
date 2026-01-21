"""
Графический интерфейс для игры про шарики.
Точка входа для запуска игры одной командой.
"""

import pygame
import sys
from logic import GameLogic

# Конфигурация игры
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
STARTING_BALLS_COUNT = 15  # Стартовое количество шариков

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
DELETE_ZONE_COLOR = (255, 200, 200)  # Светло-красный для зоны удаления
DELETE_ZONE_BORDER = (200, 100, 100)


class Game:
    """Класс для управления игровым окном и отрисовкой."""
    
    def __init__(self):
        """Инициализация игры."""
        pygame.init()
        
        # Создание окна
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Игра про шарики")
        
        # Создание игровой логики
        self.game_logic = GameLogic(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Добавление стартовых шариков
        self.game_logic.add_random_balls(STARTING_BALLS_COUNT)
        
        # Состояние мыши
        self.mouse_pressed = False
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Часы для контроля FPS
        self.clock = pygame.time.Clock()
        
        # Флаг для показа зоны удаления
        self.show_delete_zone = True
        
        # Шрифт для текста
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def rgb_to_pygame_color(self, rgb: tuple) -> tuple:
        """Конвертирует RGB цвет в формат pygame."""
        return rgb
    
    def draw_ball(self, ball):
        """Отрисовывает шарик на экране."""
        color = self.rgb_to_pygame_color(ball.color)
        pygame.draw.circle(self.screen, color, (int(ball.x), int(ball.y)), int(ball.radius))
        
        # Добавляем обводку для лучшей видимости
        pygame.draw.circle(self.screen, BLACK, (int(ball.x), int(ball.y)), int(ball.radius), 2)
    
    def draw_delete_zone(self):
        """Отрисовывает зону удаления."""
        zone_x, zone_y, zone_width, zone_height = self.game_logic.get_delete_zone()
        
        # Рисуем полупрозрачную зону удаления
        delete_surface = pygame.Surface((zone_width, zone_height))
        delete_surface.set_alpha(128)
        delete_surface.fill(DELETE_ZONE_COLOR)
        self.screen.blit(delete_surface, (zone_x, zone_y))
        
        # Рисуем границу зоны удаления
        pygame.draw.rect(self.screen, DELETE_ZONE_BORDER, 
                        (zone_x, zone_y, zone_width, zone_height), 3)
        
        # Текст "Удалить"
        text = self.small_font.render("Удалить", True, BLACK)
        text_rect = text.get_rect(center=(zone_x + zone_width // 2, zone_y + zone_height // 2))
        self.screen.blit(text, text_rect)
    
    def draw_inventory(self):
        """Отрисовывает инвентарь в левом верхнем углу."""
        inventory = self.game_logic.get_inventory()
        inventory_count = len(inventory)
        
        # Фон для инвентаря
        inventory_y = 10
        inventory_x = 10
        inventory_width = 200
        inventory_height = 60
        
        # Рисуем фон инвентаря
        pygame.draw.rect(self.screen, (240, 240, 240), 
                        (inventory_x, inventory_y, inventory_width, inventory_height))
        pygame.draw.rect(self.screen, BLACK, 
                        (inventory_x, inventory_y, inventory_width, inventory_height), 2)
        
        # Текст "Инвентарь"
        text = self.small_font.render(f"Инвентарь: {inventory_count}/{self.game_logic.max_inventory_size}", 
                                     True, BLACK)
        self.screen.blit(text, (inventory_x + 10, inventory_y + 5))
        
        # Отрисовываем миниатюры шариков из инвентаря
        ball_size = 20
        start_x = inventory_x + 10
        start_y = inventory_y + 30
        spacing = 25
        
        for i, ball in enumerate(inventory[:10]):  # Показываем максимум 10
            x = start_x + (i % 5) * spacing
            y = start_y + (i // 5) * spacing
            color = self.rgb_to_pygame_color(ball.color)
            pygame.draw.circle(self.screen, color, (x, y), ball_size // 2)
            pygame.draw.circle(self.screen, BLACK, (x, y), ball_size // 2, 1)
    
    def draw_suction_indicator(self):
        """Отрисовывает индикатор всасывания вокруг курсора мыши."""
        if self.mouse_pressed:
            # Рисуем круг всасывания
            pygame.draw.circle(self.screen, (100, 200, 255, 100), 
                             (int(self.mouse_x), int(self.mouse_y)), 
                             int(self.game_logic.suction_radius), 2)
            
            # Рисуем внутренний круг
            pygame.draw.circle(self.screen, (150, 220, 255, 150), 
                             (int(self.mouse_x), int(self.mouse_y)), 
                             int(self.game_logic.suction_radius * 0.7), 1)
    
    def handle_events(self):
        """Обрабатывает события игры."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.mouse_pressed = True
                    # Проверяем, не кликнули ли в зону удаления
                    if self.game_logic.delete_ball_in_zone(event.pos[0], event.pos[1]):
                        pass  # Шарик уже удалён
                elif event.button == 3:  # Правая кнопка мыши - выплёвывание
                    if self.game_logic.get_inventory_count() > 0:
                        self.game_logic.eject_ball(event.pos[0], event.pos[1])
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Левая кнопка мыши
                    self.mouse_pressed = False
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_x = event.pos[0]
                self.mouse_y = event.pos[1]
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Пробел - добавить случайный шарик
                    self.game_logic.add_ball()
                elif event.key == pygame.K_c:
                    # C - очистить все шарики
                    self.game_logic.clear_all()
                elif event.key == pygame.K_d:
                    # D - переключить отображение зоны удаления
                    self.show_delete_zone = not self.show_delete_zone
        
        return True
    
    def update(self, dt):
        """Обновляет состояние игры."""
        self.game_logic.update(
            dt, 
            self.mouse_x if self.mouse_pressed else None,
            self.mouse_y if self.mouse_pressed else None,
            self.mouse_pressed
        )
    
    def draw(self):
        """Отрисовывает все элементы игры."""
        # Очистка экрана (белый фон)
        self.screen.fill(WHITE)
        
        # Отрисовка зоны удаления
        if self.show_delete_zone:
            self.draw_delete_zone()
        
        # Отрисовка всех шариков
        for ball in self.game_logic.get_balls():
            self.draw_ball(ball)
        
        # Отрисовка индикатора всасывания
        self.draw_suction_indicator()
        
        # Отрисовка инвентаря
        self.draw_inventory()
        
        # Информация об управлении
        info_text = [
            "ЛКМ: Всасывать шарики",
            "ПКМ: Выплёвывать шарик",
            "Пробел: Добавить шарик",
            "C: Очистить всё",
            "D: Показать/скрыть зону удаления"
        ]
        
        y_offset = SCREEN_HEIGHT - 120
        for i, text in enumerate(info_text):
            text_surface = self.small_font.render(text, True, GRAY)
            self.screen.blit(text_surface, (10, y_offset + i * 20))
        
        # Обновление экрана
        pygame.display.flip()
    
    def run(self):
        """Запускает главный игровой цикл."""
        running = True
        
        while running:
            # Обработка событий
            running = self.handle_events()
            
            # Вычисление времени, прошедшего с последнего кадра
            dt = self.clock.tick(FPS) / 1000.0  # Конвертируем миллисекунды в секунды
            
            # Обновление логики игры
            self.update(dt)
            
            # Отрисовка
            self.draw()
        
        # Завершение работы
        pygame.quit()
        sys.exit()


def main():
    """Главная функция для запуска игры."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

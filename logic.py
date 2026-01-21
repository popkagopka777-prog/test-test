"""
Модуль игровой логики для игры про шарики.
Отвечает за движение, столкновения, смешивание цветов и управление инвентарём.
"""

import math
import random
from typing import List, Tuple, Optional, Dict


class Ball:
    """Класс, представляющий шарик в игре."""
    
    def __init__(self, x: float, y: float, radius: float = 20.0, 
                 color: Tuple[int, int, int] = None, 
                 velocity: Tuple[float, float] = None):
        """
        Инициализация шарика.
        
        Args:
            x, y: Позиция центра шарика
            radius: Радиус шарика
            color: RGB цвет (r, g, b) в диапазоне 0-255. Если None, генерируется случайный цвет
            velocity: Скорость (vx, vy). Если None, генерируется случайная скорость
        """
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        
        # Генерация случайного цвета, если не указан
        if color is None:
            # Генерируем яркие цвета, избегая белого
            self.color = self._generate_random_color()
        else:
            self.color = tuple(color)
        
        # Генерация случайной скорости, если не указана
        if velocity is None:
            speed = random.uniform(50, 150)
            angle = random.uniform(0, 2 * math.pi)
            self.vx = speed * math.cos(angle)
            self.vy = speed * math.sin(angle)
        else:
            self.vx, self.vy = velocity
    
    def _generate_random_color(self) -> Tuple[int, int, int]:
        """Генерирует случайный яркий цвет, избегая белого."""
        # Генерируем цвета с высокой насыщенностью
        colors = [
            (255, 0, 0),      # Красный
            (0, 255, 0),      # Зелёный
            (0, 0, 255),      # Синий
            (255, 255, 0),    # Жёлтый
            (255, 0, 255),    # Пурпурный
            (0, 255, 255),    # Голубой
            (255, 165, 0),    # Оранжевый
            (128, 0, 128),    # Фиолетовый
            (255, 192, 203),  # Розовый
            (0, 128, 0),      # Тёмно-зелёный
        ]
        return random.choice(colors)
    
    def update_position(self, dt: float, screen_width: float, screen_height: float):
        """
        Обновляет позицию шарика с учётом скорости и границ экрана.
        
        Args:
            dt: Время, прошедшее с последнего обновления (в секундах)
            screen_width: Ширина экрана
            screen_height: Высота экрана
        """
        # Обновление позиции
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Отражение от границ экрана
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius >= screen_width:
            self.x = screen_width - self.radius
            self.vx = -abs(self.vx)
        
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius >= screen_height:
            self.y = screen_height - self.radius
            self.vy = -abs(self.vy)
    
    def distance_to(self, other: 'Ball') -> float:
        """Вычисляет расстояние между центрами двух шариков."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def is_colliding(self, other: 'Ball') -> bool:
        """Проверяет, сталкиваются ли два шарика."""
        return self.distance_to(other) < (self.radius + other.radius)
    
    def get_color_rgb(self) -> Tuple[int, int, int]:
        """Возвращает RGB цвет шарика."""
        return self.color


class GameLogic:
    """Класс, управляющий игровой логикой."""
    
    def __init__(self, screen_width: float = 800, screen_height: float = 600):
        """
        Инициализация игровой логики.
        
        Args:
            screen_width: Ширина игрового экрана
            screen_height: Высота игрового экрана
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Список всех шариков на экране
        self.balls: List[Ball] = []
        
        # Инвентарь (список шариков, которые были "всосанны")
        self.inventory: List[Ball] = []
        
        # Максимальное количество шариков в инвентаре
        self.max_inventory_size = 10
        
        # Зона удаления (правая нижняя часть экрана)
        # Шарики в этой зоне можно удалить
        self.delete_zone_x = screen_width - 100
        self.delete_zone_y = screen_height - 100
        self.delete_zone_width = 100
        self.delete_zone_height = 100
        
        # Радиус "всасывания" вокруг курсора мыши
        self.suction_radius = 50.0
        
        # Скорость всасывания (пикселей в секунду)
        self.suction_speed = 300.0
    
    def add_ball(self, x: float = None, y: float = None, 
                 radius: float = None, color: Tuple[int, int, int] = None):
        """
        Добавляет новый шарик на экран.
        
        Args:
            x, y: Позиция шарика. Если None, выбирается случайная позиция
            radius: Радиус шарика. Если None, используется случайный радиус
            color: Цвет шарика. Если None, генерируется случайный цвет
        """
        if x is None:
            x = random.uniform(50, self.screen_width - 50)
        if y is None:
            y = random.uniform(50, self.screen_height - 50)
        if radius is None:
            radius = random.uniform(15, 30)
        
        ball = Ball(x, y, radius, color)
        self.balls.append(ball)
    
    def add_random_balls(self, count: int):
        """Добавляет несколько случайных шариков на экран."""
        for _ in range(count):
            self.add_ball()
    
    def update(self, dt: float, mouse_x: float = None, mouse_y: float = None, 
               is_suction_active: bool = False):
        """
        Обновляет состояние игры.
        
        Args:
            dt: Время, прошедшее с последнего обновления (в секундах)
            mouse_x, mouse_y: Позиция курсора мыши
            is_suction_active: Активно ли "всасывание" (зажата ли кнопка мыши)
        """
        # Обновление позиций всех шариков
        for ball in self.balls:
            ball.update_position(dt, self.screen_width, self.screen_height)
        
        # Обработка столкновений и смешивания цветов
        self._handle_collisions()
        
        # Обработка всасывания шариков
        if is_suction_active and mouse_x is not None and mouse_y is not None:
            self._handle_suction(mouse_x, mouse_y, dt)
        
        # Удаление шариков в зоне удаления
        self._check_delete_zone()
    
    def _handle_collisions(self):
        """Обрабатывает столкновения между шариками и смешивает их цвета."""
        # Проверяем все пары шариков
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]
                
                if ball1.is_colliding(ball2):
                    # Смешиваем цвета при касании
                    self._blend_colors(ball1, ball2)
    
    def _blend_colors(self, ball1: Ball, ball2: Ball):
        """
        Смешивает цвета двух шариков при их касании.
        Использует математическое усреднение RGB-компонентов.
        
        Args:
            ball1, ball2: Шарики, цвета которых нужно смешать
        """
        r1, g1, b1 = ball1.color
        r2, g2, b2 = ball2.color
        
        # Простое математическое усреднение RGB-компонентов
        new_r = int((r1 + r2) / 2)
        new_g = int((g1 + g2) / 2)
        new_b = int((b1 + b2) / 2)
        
        # Обеспечиваем, что значения находятся в допустимом диапазоне [0, 255]
        new_r = max(0, min(255, new_r))
        new_g = max(0, min(255, new_g))
        new_b = max(0, min(255, new_b))
        
        # Применяем новый цвет к обоим шарикам
        ball1.color = (new_r, new_g, new_b)
        ball2.color = (new_r, new_g, new_b)
    
    def _handle_suction(self, mouse_x: float, mouse_y: float, dt: float):
        """
        Обрабатывает "всасывание" шариков мышкой.
        
        Args:
            mouse_x, mouse_y: Позиция курсора мыши
            dt: Время, прошедшее с последнего обновления
        """
        if len(self.inventory) >= self.max_inventory_size:
            return
        
        # Находим шарики в радиусе всасывания
        balls_to_remove = []
        for ball in self.balls:
            dx = mouse_x - ball.x
            dy = mouse_y - ball.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < self.suction_radius:
                # Перемещаем шарик к курсору
                if distance > 0:
                    # Нормализуем направление
                    dx_norm = dx / distance
                    dy_norm = dy / distance
                    
                    # Перемещаем шарик
                    move_distance = self.suction_speed * dt
                    ball.x += dx_norm * move_distance
                    ball.y += dy_norm * move_distance
                    
                    # Если шарик достаточно близко к курсору, добавляем в инвентарь
                    new_distance = math.sqrt(
                        (mouse_x - ball.x) ** 2 + (mouse_y - ball.y) ** 2
                    )
                    if new_distance < ball.radius:
                        balls_to_remove.append(ball)
        
        # Перемещаем шарики в инвентарь
        for ball in balls_to_remove:
            self.balls.remove(ball)
            self.inventory.append(ball)
    
    def eject_ball(self, x: float, y: float):
        """
        "Выплёвывает" шарик из инвентаря обратно на экран.
        
        Args:
            x, y: Позиция, куда выплёвывается шарик
        """
        if len(self.inventory) > 0:
            ball = self.inventory.pop(0)
            ball.x = x
            ball.y = y
            
            # Задаём случайную скорость при выплёвывании
            speed = random.uniform(100, 200)
            angle = random.uniform(0, 2 * math.pi)
            ball.vx = speed * math.cos(angle)
            ball.vy = speed * math.sin(angle)
            
            self.balls.append(ball)
    
    def _check_delete_zone(self):
        """Проверяет шарики в зоне удаления и удаляет их."""
        balls_to_remove = []
        for ball in self.balls:
            if (self.delete_zone_x <= ball.x <= self.delete_zone_x + self.delete_zone_width and
                self.delete_zone_y <= ball.y <= self.delete_zone_y + self.delete_zone_height):
                balls_to_remove.append(ball)
        
        for ball in balls_to_remove:
            self.balls.remove(ball)
    
    def delete_ball_in_zone(self, x: float, y: float) -> bool:
        """
        Удаляет шарик в указанной позиции, если он находится в зоне удаления.
        
        Args:
            x, y: Позиция для проверки
            
        Returns:
            True, если шарик был удалён, False иначе
        """
        if not (self.delete_zone_x <= x <= self.delete_zone_x + self.delete_zone_width and
                self.delete_zone_y <= y <= self.delete_zone_y + self.delete_zone_height):
            return False
        
        # Ищем шарик в этой позиции
        for ball in self.balls:
            dx = x - ball.x
            dy = y - ball.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < ball.radius:
                self.balls.remove(ball)
                return True
        
        return False
    
    def get_balls(self) -> List[Ball]:
        """Возвращает список всех шариков на экране."""
        return self.balls.copy()
    
    def get_inventory(self) -> List[Ball]:
        """Возвращает список шариков в инвентаре."""
        return self.inventory.copy()
    
    def get_inventory_count(self) -> int:
        """Возвращает количество шариков в инвентаре."""
        return len(self.inventory)
    
    def get_delete_zone(self) -> Tuple[float, float, float, float]:
        """
        Возвращает координаты зоны удаления.
        
        Returns:
            (x, y, width, height) зоны удаления
        """
        return (self.delete_zone_x, self.delete_zone_y, 
                self.delete_zone_width, self.delete_zone_height)
    
    def clear_all(self):
        """Очищает все шарики с экрана и из инвентаря."""
        self.balls.clear()
        self.inventory.clear()
    
    def set_screen_size(self, width: float, height: float):
        """Устанавливает размер экрана."""
        self.screen_width = width
        self.screen_height = height
        # Обновляем зону удаления
        self.delete_zone_x = width - 100
        self.delete_zone_y = height - 100


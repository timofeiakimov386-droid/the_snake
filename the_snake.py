from random import choice, randint
import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 200, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов"""
    
    def __init__(self, position=None):
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = BOARD_BACKGROUND_COLOR
    
    def draw(self):
        """Абстрактный метод для отрисовки"""
        pass


class Apple(GameObject):
    """Класс для яблока"""
    
    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()
    
    def randomize_position(self, occupied_positions=None):
        """Устанавливает случайную позицию для яблока"""
        if occupied_positions is None:
            occupied_positions = set()
        
        # Генерируем все возможные позиции
        all_positions = set(
            (x * GRID_SIZE, y * GRID_SIZE) 
            for x in range(GRID_WIDTH) 
            for y in range(GRID_HEIGHT)
        )
        
        # Исключаем занятые позиции
        free_positions = all_positions - occupied_positions
        
        if free_positions:
            self.position = choice(list(free_positions))
        else:
            # Если нет свободных мест, ставим в угол
            self.position = (0, 0)
    
    def draw(self):
        """Отрисовывает яблоко"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс для змейки"""
    
    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.reset()
    
    def reset(self):
        """Сбрасывает змейку в начальное состояние"""
        start_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [start_position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.grow_pending = False
    
    def update_direction(self):
        """Обновляет направление движения"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None
    
    def move(self):
        """Двигает змейку"""
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction
        
        # Вычисляем новую позицию головы с учетом прохождения через стены
        new_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        
        new_head = (new_x, new_y)
        self.positions.insert(0, new_head)
        
        # Сохраняем последнюю позицию для затирания
        if not self.grow_pending and len(self.positions) > 1:
            self.last = self.positions.pop()
        else:
            self.grow_pending = False
            self.last = None
    
    def grow(self):
        """Увеличивает длину змейки"""
        self.grow_pending = True
    
    def get_head_position(self):
        """Возвращает позицию головы"""
        return self.positions[0]
    
    def get_occupied_positions(self):
        """Возвращает множество занятых позиций"""
        return set(self.positions)
    
    def check_self_collision(self):
        """Проверяет столкновение с собой"""
        # У змейки длиной меньше 5 не может быть столкновения
        if len(self.positions) < 5:
            return False
        
        head = self.get_head_position()
        return head in self.positions[1:]
    
    def draw(self):
        """Отрисовывает змейку"""
        # Отрисовываем тело змейки
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        
        # Отрисовываем голову другим цветом
        if self.positions:
            head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, SNAKE_HEAD_COLOR, head_rect)
            pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)
        
        # Затираем последний сегмент
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            elif event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция игры"""
    # Инициализация PyGame:
    pygame.init()
    
    # Создание игровых объектов
    snake = Snake()
    apple = Apple()
    
    # Счетчик
    score = 0
    
    while True:
        clock.tick(SPEED)
        
        # Обработка пользовательского ввода
        handle_keys(snake)
        
        # Обновление направления змейки
        snake.update_direction()
        
        # Движение змейки
        snake.move()
        
        # Проверка съедания яблока
        if snake.get_head_position() == apple.position:
            snake.grow()
            score += 1
            pygame.display.set_caption(f'Змейка - Счет: {score}')
            apple.randomize_position(snake.get_occupied_positions())
        
        # Проверка столкновения с собой
        if snake.check_self_collision():
            snake.reset()
            apple.randomize_position()
            score = 0
            pygame.display.set_caption('Змейка')
        
        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
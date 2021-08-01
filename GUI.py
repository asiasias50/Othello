import pygame


class GUI:
    WINDOW_SIZE = 800
    BACKGROUND = (165, 0, 7)
    BUTTONS = (100, 0, 7)
    BUTTONS_HOVER = (20, 0, 0)

    def __init__(self):
        pygame.init()
        self.__screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_SIZE))
        self.__run_gui()

    def __run_gui(self):
        # Initialization
        self.__screen.fill(self.BACKGROUND)

        # Captions
        pygame.display.set_caption("Othello")
        try:
            icon = pygame.image.load("Othello.png")
            pygame.display.set_icon(icon)
        except FileNotFoundError:
            pass
        pygame.font.init()
        logo_font = pygame.font.SysFont("Open Sans", 200)
        text_colour = (0, 165, 158)
        logo_surface = logo_font.render("Othello", False, text_colour)
        self.__screen.blit(logo_surface, ((self.WINDOW_SIZE - logo_surface.get_rect().width) // 2, 0))

        # Buttons
        button_font = pygame.font.SysFont("Open Sans", 80)
        button_surface = button_font.render("PLAY", False, text_colour)
        button_width = 300
        button_height = 50
        play_button_pos_x = (self.WINDOW_SIZE - button_width) // 2
        play_button_pos_y = logo_surface.get_rect().height + 50

        # Game Loop
        while True:
            # Events handling
            for event in pygame.event.get():
                mouse_pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_pos_x <= mouse_pos[0] <= play_button_pos_x + button_width and play_button_pos_y <= mouse_pos[1] <= play_button_pos_y + button_height:
                        self.__run_game(button_width, button_height, button_font, text_colour)

            # Update cycle
            if play_button_pos_x <= mouse_pos[0] <= play_button_pos_x + button_width and play_button_pos_y <= mouse_pos[1] <= play_button_pos_y + button_height:
                pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (play_button_pos_x, play_button_pos_y, button_width, button_height))
            else:
                pygame.draw.rect(self.__screen, self.BUTTONS, (play_button_pos_x, play_button_pos_y, button_width, button_height))
            self.__screen.blit(button_surface, ((self.WINDOW_SIZE - button_surface.get_rect().width) // 2, play_button_pos_y))
            pygame.display.update()

    def __run_game(self, button_width, button_height, button_font, text_colour):
        center = (self.WINDOW_SIZE - button_width) // 2
        initial_y_pos = 50
        step = 2 * button_height

        while True:
            self.__screen.fill(self.BACKGROUND)
            mouse_pos = pygame.mouse.get_pos()

            # Events handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for index in range(0, 4):
                        if center <= mouse_pos[0] <= center + button_width and initial_y_pos + index * step <= mouse_pos[1] <= initial_y_pos + index * step + button_height:
                            print("lol")

            # Update cycle
            lables = ["Resume", "PvP", "PvAI", "Load"]
            for index in range(0, 4):
                if center <= mouse_pos[0] <= center + button_width and initial_y_pos + index * step <= mouse_pos[1] <= initial_y_pos + index * step + button_height:
                    pygame.draw.rect(self.__screen, self.BUTTONS_HOVER, (center, initial_y_pos + index * step, button_width, button_height))
                else:
                    pygame.draw.rect(self.__screen, self.BUTTONS, (center, initial_y_pos + index * step, button_width, button_height))
                button_surface = button_font.render(lables[index], False, text_colour)
                self.__screen.blit(button_surface, ((self.WINDOW_SIZE - button_surface.get_rect().width) // 2, initial_y_pos + index * step))
            pygame.display.update()



gui = GUI()

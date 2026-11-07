from dataclasses import dataclass

import pygame


@dataclass
class ColorPalette:
    """
    Represents a color palette for the application.

    A color palette is responsible for providing colors for various elements
    in the application, such as the background, text, and UI components.
    """

    Background: pygame.Color
    Text: pygame.Color
    Primary: pygame.Color
    Secondary: pygame.Color
    Accent: pygame.Color


DefaultColorPalette = ColorPalette(
    Background=pygame.Color(30, 30, 30),
    Text=pygame.Color(220, 220, 220),
    Primary=pygame.Color(70, 130, 180),
    Secondary=pygame.Color(100, 149, 237),
    Accent=pygame.Color(255, 69, 0),
)

BeachSummerPalette = ColorPalette(
    Background=pygame.Color(47, 72, 88),
    Text=pygame.Color(230, 230, 230),
    Primary=pygame.Color(85, 221, 224),
    Secondary=pygame.Color(51, 101, 138),
    Accent=pygame.Color(246, 174, 45),
)

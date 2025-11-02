# Goblin Slayer — Documentation

## The epic dungeon platformer specifically for killing GOBLINS (Lots of them)

- tech-stack : Python 3.x and pygame
- Run the game: python main.py
- Controls:
  - start_Menu: ENTER = start, ESC = quit


  - Game: A/D or ←/→ = move, SPACE = jump, ESC = quit, Z = Attack, P = Pause, L = level-selector
 
- 

Assets and backgrounds
-level_backgrounds — assets\backgrounds folder -- level_mid/rear images

  level_1
  level_2
  lwvel_3
  
-PLayer/Enemy — Photo folder — Orc/Soldier — Attack/Hit/Idle/Walk/Entity

Project structure
- main.py — entry point, menu + game loop, level loading, camera, debug overlay
- settings.py — screen/FPS, color constants, physics, player size, ground height
- utils.py — draw_text helper
- level.py — Level: loads background image, draws parallax background and a flat ground with tick marks
- player.py — Player: rectangle avatar with left/right movement, jump, gravity
- assets/ — level1.jpg, level2.jpg, or other background images here
- photo/ — player and enemy images here
- game_platform — floating platfrom logic

Runtime flow
- Menu:
  - Low-res pixel menu is rendered to a 256x192 surface then scaled to screen for a crisp look.
  - Animated starfield background with a simple silhouette horizon.
  - ENTER switches to the game.
- Game:
  - Level(level_number) loads matching background image and draws the ground, spawn enemies, loads platforms.
  - Player handles input → applies gravity → resolves ground → renders.
  - Camera follows the player on X with a lead; with background parallax.
Simple
```mermaid
flowchart TD
  %% === Title ===
  %% Dungeon Crawler 2D Platformer — Simplified Game Flow

  %% === Startup Flow ===
  subgraph Startup_Flow["Startup Flow 🕹️"]
    A1([Startup Screen])
    A2[Loading Screen]
    A3[Main Menu]
    A4[Options Menu]
    A5[Controls Screen]
    A6[Settings]
    A7([Quit Game])
  end

  %% === Level Selection ===
  subgraph Level_Selection["Level Selection 🗺️"]
    B1[Level Selector]
    B2[Select Level]
  end

  %% === Gameplay ===
  subgraph Gameplay_Flow["Gameplay 🎮"]
    C1[Gameplay Scene]
    C2[Main Game Loop]
    C3[Pause Menu]
    C4[Save Game]
    C5{{Win Condition}}
    C6{{Lose Condition}}
  end

  %% === End Flow ===
  subgraph End_Flow["End Flow 🏁"]
    D1[Game Over Screen]
    D2[Retry Option]
    D3([End Credits])
    D4[Level Complete]
  end

  %% === Connections ===

  %% Startup
  A1 --> A2
  A2 --> A3
  A3 --> A4
  A3 --> B1
  A3 --> A7
  A4 --> A5
  A4 --> A6
  A5 --> A3
  A7 -.->|Quit| E1((End))

  %% Level Selection
  B1 --> B2
  B2 --> C1

  %% Gameplay
  C1 --> C2
  C1 -->|Pause| C3
  C3 -->|Resume| C2
  C3 -->|Save| C4
  C2 --> C5
  C2 --> C6
  C5 -->|Save Progress| C4
  C4 --> D4
  C5 -->|All Levels Complete| D4
  D4 --> D3
  C6 --> D1

  %% End Flow
  D1 --> D2
  D1 --> A7
  D2 -->|Retry| B1
  D3 --> A1

  %% === Styling ===
  %% Color coding for better readability
  classDef startup fill:#9ec5fe,stroke:#1d3557,stroke-width:1px,color:#000;
  classDef level fill:#ffe066,stroke:#8c6d1f,stroke-width:1px,color:#000;
  classDef gameplay fill:#90ee90,stroke:#2b9348,stroke-width:1px,color:#000;
  classDef endflow fill:#fcb0f1,stroke:#8b1e8f,stroke-width:1px,color:#000;
  classDef danger fill:#ff6b6b,stroke:#c1121f,stroke-width:1px,color:#000;

  class A1,A2,A3,A4,A5,A6,A7 startup;
  class B1,B2 level;
  class C1,C2,C3,C4,C5,C6 gameplay;
  class D1,D2,D3,D4 endflow;
  class C6,D1 danger;

```


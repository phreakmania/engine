# Python 2D Engine

A small Python 2D engine with an Entity Component System (ECS), an OpenGL renderer, and a playable arena shooter prototype. The engine provides window management, input, rendering, camera translation, and basic collision detection. The game builds on these features with enemies, projectiles, health, and wall collisions.

The project is under development. This README describes the implementation currently included in the repository.

## Getting started

### Requirements

- Python with `pip` and `venv`. The current local development environment uses Python 3.14; compatibility with other versions has not been verified.
- A desktop environment and graphics driver supporting OpenGL 3.3, as required by the shaders.
- The dependencies listed in [requirements.txt](requirements.txt).

The engine uses GLFW for window creation and keyboard input, PyOpenGL for rendering, NumPy for graphics data, and Pillow for loading images. `requirements.txt` also includes pyOpenSSL, although the current engine and game do not use it directly.

### Install and run on Windows

Open PowerShell in the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

These commands use the virtual environment directly, so activating it is optional. If an environment already exists, skip its creation.

The application opens a window titled **New Engine** at **1280 × 720**. Close the window to exit.

## Playing the game

Move the blue player through the arena, avoid the red enemies, and fire yellow projectiles to destroy them. The camera follows the player through a world larger than the visible area.

| Input | Action |
| --- | --- |
| W | Move up |
| A | Move left |
| S | Move down |
| D | Move right |
| Space | Fire one projectile upward per key press |
| Window close button | Exit |

Diagonal movement is normalized, so it has the same speed as movement along one axis. Holding Space does not continuously fire; release and press it again for another shot.

### Current game rules

| Setting | Current value |
| --- | --- |
| World size | 3000 × 2000 world units |
| Boundary wall thickness | 32 units |
| Player size | 32 × 32 units |
| Player starting position | (640, 360) |
| Player speed | 200 units per second |
| Player health | 5 |
| Invulnerability after taking damage | 0.5 seconds |
| Enemy spawn interval | 2 seconds |
| Enemy spawn position | (640, 80) with the default game dimensions |
| Enemy speed | 100 units per second |
| Enemy health | 3 |
| Damage per enemy contact or projectile hit | 1 |
| Projectile speed | 500 units per second, upward |

Enemies spawn at a fixed world position and move toward the player's current position. A projectile disappears when it hits an enemy; an enemy disappears when its health reaches zero. Projectiles are also removed once they have moved completely above the world's top edge (`y = 0`).

At zero player health, the game prints `Game Over!` to the console and stops updating gameplay. The last state remains visible until the window is closed. To play again, restart the application.

## Engine features

- **Application loop:** event polling, keyboard state updates, elapsed time calculation, game updates, rendering, and shutdown.
- **ECS:** integer entity IDs, components stored by type, component lookup and removal, entity destruction, and queries requiring multiple component types.
- **2D rendering:** colored or textured quads with position, size, rotation, and alpha blending.
- **Camera:** translation from world coordinates to screen coordinates.
- **Viewport scaling:** a virtual 1280 × 720 view fitted into the framebuffer while preserving its aspect ratio, with borders where needed.
- **Textures:** image loading as RGBA through Pillow and nearest-neighbor texture filtering.
- **Input:** detection of held keys and newly pressed keys.
- **Math and collisions:** basic `Vector2` operations and axis-aligned bounding box (AABB) overlap detection.

World coordinates increase to the right on X and downward on Y. A transform's position is the center of its quad; `scale` stores its full width and height. Rotation is expressed in radians.

The collision helper uses position and size. It ignores rotation, and rectangles that only touch at their edges do not count as overlapping.

## Project structure

```text
.
├── main.py                       # Creates the game and starts the application
├── requirements.txt              # Pinned Python dependencies
├── pyproject.toml                # Currently empty
├── engine/
│   ├── application.py            # Main loop and engine/game integration
│   ├── window.py                 # GLFW window and key mapping
│   ├── input.py                  # Current and previous keyboard states
│   ├── key.py                    # Supported keys
│   ├── renderer.py               # OpenGL shaders, quad drawing, and viewport
│   ├── texture.py                # Image loading and GPU texture lifecycle
│   ├── camera.py                 # World-to-screen translation
│   ├── vector2.py                # Vector arithmetic and normalization
│   ├── collision.py              # AABB overlap checks
│   └── ecs/
│       ├── world.py              # Entity and component storage
│       ├── components/           # Transform, Velocity, QuadRenderable
│       └── systems/              # Movement and quad rendering
├── game/
│   ├── game.py                   # Arena setup and gameplay logic
│   ├── components.py             # Tags, health, damage, invulnerability
│   └── systems.py                # Invulnerability and projectile cleanup
└── tests/                        # unittest tests for engine logic
```

## How the engine and game fit together

`main.py` creates a `Game` and passes it to `Application`. The application expects the game to expose a `camera`, an `update(dt, input)` method, and a `render(renderer)` method. `dt` is elapsed time in seconds; the loop uses a variable time step.

The game owns its ECS `World`. Players, enemies, walls, and projectiles are entities whose behavior is selected through components and tags. Engine systems handle general movement and rendering, while game code handles spawning, damage, and collision responses.

During each active gameplay update, the game:

1. Moves the player and resolves wall overlap separately along X and Y.
2. Spawns projectiles from keyboard input and enemies from the spawn timer.
3. Sets enemy velocities toward the player.
4. Moves entities with `Transform` and `Velocity` components.
5. Centers the camera on the player.
6. Handles projectile/enemy and enemy/player collisions, then checks for game over.
7. Updates invulnerability timers and removes projectiles above the world.

The player is moved directly by the game because its movement includes wall collision handling. Enemies and projectiles use the generic movement system. Rendering queries entities with both `Transform` and `QuadRenderable`.

### ECS example

```python
from engine.ecs.world import World
from engine.ecs.components.transform import Transform
from engine.ecs.components.velocity import Velocity
from engine.ecs.systems.movement import movement_system
from engine.vector2 import Vector2

world = World()
entity = world.create_entity()

world.add_component(entity, Transform(position=Vector2(10.0, 20.0)))
world.add_component(entity, Velocity(Vector2(100.0, 0.0)))

movement_system(world, dt=0.5)

for entity, transform, velocity in world.query(Transform, Velocity):
    print(transform.position.x, transform.position.y)  # 60.0, 20.0
```

Pass **instances** to `add_component`, such as `PlayerTag()`, and **types** to `query`, such as `world.query(PlayerTag, Transform)`. Query results contain the entity ID followed by components in the requested order. An entity has at most one component per type; adding another replaces the existing component of that type.

For drawing, add a `QuadRenderable` with an RGBA color and, optionally, a `Texture`. Create textures after the OpenGL context has been created, and release them with `Texture.shutdown()` before that context is destroyed. The current demo uses colored quads and does not load texture assets.

## Tests

Run the existing tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

With an activated environment, the equivalent command is:

```text
python -m unittest discover -s tests -v
```

The suite covers entity creation, component storage and queries, entity destruction, tag filtering, movement using delta time, and camera coordinate conversion. These tests exercise logic without opening an OpenGL window. They do not cover rendering or the complete gameplay loop.

## Current limitations

- There is no menu, health display, score, pause control, or in-game restart.
- Only the player resolves collisions with walls. Enemies and projectiles do not collide with walls, and enemies do not collide with each other.
- Collision checks are discrete and do not sweep across the movement path. Large time steps can allow objects to pass through obstacles or targets.
- The camera follows the player without smoothing or clamping to world boundaries.
- The renderer's virtual resolution is fixed at 1280 × 720 in `Application`. Changing the game dimensions also requires reviewing the renderer configuration and camera centering.
- The current repository does not include a scene loader, scene files, or an editor. The arena and entities are created in Python code.

## License

See [LICENSE](LICENSE) for the GNU General Public License, version 3.

from engine.application import Application
from game.game import Game


def main():
    GAME_WIDTH = 1280
    GAME_HEIGHT = 720
    game = Game(GAME_WIDTH, GAME_HEIGHT)

    app = Application(
        game,
        width=GAME_WIDTH,
        height=GAME_HEIGHT,
        title="New Engine")
    app.run()


if __name__ == "__main__":
    main()
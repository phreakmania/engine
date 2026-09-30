from engine.application import Application
from game.pong.game import Game


def main():
    GAME_WIDTH = 800
    GAME_HEIGHT = 600
    game = Game(GAME_WIDTH, GAME_HEIGHT)

    app = Application(
        game,
        width=GAME_WIDTH,
        height=GAME_HEIGHT,
        title="Pong")
    app.run()


if __name__ == "__main__":
    main()

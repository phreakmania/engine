import glfw
from engine.application import Application
from game.game import Game

def main():
    game = Game()

    app = Application(
        game,
        width=800,
        height=600,
        title="New Engine")
    app.run()


if __name__ == "__main__":
    main()
import glfw
from engine.application import Application

def main():

    app = Application(
        width=800,
        height=600,
        title="New Engine")
    app.run()


if __name__ == "__main__":
    main()
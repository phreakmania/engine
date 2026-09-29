import glfw

def main():
    if not glfw.init():
        raise RuntimeError("Could not initialize glfw.")
    window = glfw.create_window(1280,720, "My Engine", None, None)

    if not window:
        glfw.terminate()
        raise RuntimeError("Could not create window.")

    glfw.make_context_current(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
def intersects(a, b):
    a_left = a.position.x - a.scale.x * 0.5
    a_right = a.position.x + a.scale.x * 0.5
    a_top = a.position.y - a.scale.y * 0.5
    a_bottom = a.position.y + a.scale.y * 0.5

    b_left = b.position.x - b.scale.x * 0.5
    b_right = b.position.x + b.scale.x * 0.5
    b_top = b.position.y - b.scale.y * 0.5
    b_bottom = b.position.y + b.scale.y * 0.5

    return (
        a_left < b_right
        and a_right > b_left
        and a_top < b_bottom
        and a_bottom > b_top
    )

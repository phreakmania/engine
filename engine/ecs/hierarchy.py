from engine.ecs.components.parent import Parent


def destroy_entity_tree(world, entity):
    children = [
        child
        for child, parent in world.query(Parent)
        if parent.entity == entity
    ]

    for child in children:
        destroy_entity_tree(world, child)

    world.destroy_entity(entity)

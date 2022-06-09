from typing import List, Tuple, Dict, Optional

Block = List[Tuple[int, int]]

BLOCK_I, BLOCK_J, BLOCK_L, BLOCK_S, BLOCK_Z, BLOCK_T, BLOCK_O = range(7)
LEFT, RIGHT, ROTATE_CW, ROTATE_CCW, DOWN, DROP, QUIT = range(7)

WALL = "##"
SQUARE = "[]"
EMPTY = "  "

Arena = Dict[int, List[str]]


def coords(block_type: int) -> Block:
    if block_type == 0:
        coords = [(0, 0), (0, -1), (0, 1), (0, 2)]
    if block_type == 1:
        coords = [(0, 0), (0, -1), (0, 1), (-1, 1)]
    if block_type == 2:
        coords = [(0, 0), (0, -1), (0, 1), (1, 1)]
    if block_type == 3:
        coords = [(0, 0), (-1, 1), (0, 1), (1, 0)]
    if block_type == 4:
        coords = [(0, 0), (-1, 0), (0, 1), (1, 1)]
    if block_type == 5:
        coords = [(0, 0), (-1, 0), (1, 0), (0, 1)]
    if block_type == 6:
        coords = [(0, 0), (1, 0), (0, 1), (1, 1)]
    return coords


def rotate_cw(coords: Block) -> Block:
    new: Block = []
    for x, y in coords:
        new.append((-y, x))
    return new


def rotate_ccw(coords: Block) -> Block:
    new: List[Tuple[int, int]] = []
    for x, y in coords:
        new.append((y, -x))
    return new


def new_arena(cols: int, rows: int) -> Arena:
    arena = {}
    for i in range(rows):
        arena[i] = [EMPTY for col in range(cols)]
    return arena


def is_occupied(arena: Arena, x: int, y: int) -> bool:
    if y < 0 or y > len(arena) - 1 or x < 0 or x > len(arena[0]) - 1:
        return True
    return arena[y][x] == SQUARE


def set_occupied(arena: Arena, x: int, y: int, occupied: bool) -> None:
    if occupied:
        arena[y][x] = SQUARE
    else:
        arena[y][x] = EMPTY


def draw(arena: Arena, score: int) -> None:
    for row in arena:
        print(f'{WALL}{"".join(arena[row])}{WALL}')
    print(WALL * (len(arena[0]) + 2))
    print(f'{EMPTY}Score:', end="")
    indent = 2 * len(arena[0]) - len("Score:") - len(str(score))
    print(f'{" " * indent}{str(score)}')


def next_block() -> Block:
    # change this function as you wish
    return coords(5)


def poll_event() -> int:
    # change this function as you wish
    return int(input("Event number (0-6): "))


def new_block(block: Block, arena: Arena) -> Optional[Block]:
    new_coords = []
    temp_block = block.copy()
    y_min = 0
    x_pos = set()

    for x, y in block:
        if y < y_min:
            y_min = y

    for x, y in block:
        x_pos.add(x)

    for i in range(len(block)):
        x, y = block[i]
        if min(x_pos) < 0:
            temp_block[i] = (x - min(x_pos), y)

    middle = round((max(x_pos) + min(x_pos)) / 2)
    x_pos.clear()

    for x, y in temp_block:
        new_coords.append((x + round(len(arena[0]) / 2) - middle, y - y_min))
        x_pos.add(x + round(len(arena[0]) / 2) - middle)

    while min(x_pos) > (len(arena[0]) - max(x_pos)) - 1:
        x_pos.clear()
        for i in range(len(new_coords)):
            x, y = new_coords[i]
            new_coords[i] = (x - 1, y)
            x_pos.add(x - 1)

    for x, y in new_coords:
        if is_occupied(arena, x, y):
            return None

    for x, y in new_coords:
        set_occupied(arena, x, y, True)

    return new_coords


def left(arena: Arena, block: Block) -> Block:
    current = set(block)
    new = []

    for x, y in block:
        if is_occupied(arena, x - 1, y) and (x - 1, y) not in current:
            return block
        new.append((x - 1, y))

    move_block(arena, block, -1, 0)

    return new


def right(arena: Arena, block: Block) -> Block:
    current = set(block)
    new = []

    for x, y in block:
        if is_occupied(arena, x + 1, y) and (x + 1, y) not in current:
            return block
        new.append((x + 1, y))

    move_block(arena, block, 1, 0)

    return new


def down(arena: Arena, block: Block) -> Tuple[Block, bool]:
    current = set(block)
    new = []

    for x, y in block:
        if is_occupied(arena, x, y + 1) and (x, y + 1) not in current:
            return block, False
        new.append((x, y + 1))

    move_block(arena, block, 0, 1)

    return new, True


def move_block(arena: Arena, block: Block, dx: int, dy: int) -> None:
    for x, y in block:
        set_occupied(arena, x, y, False)
    for x, y in block:
        set_occupied(arena, x + dx, y + dy, True)


def rotate(arena: Arena, block: Block, rotation: str, template: Block) \
           -> Tuple[Block, Block]:
    current = set(block)
    new, difference = [], []

    if rotation == "cw":
        position = rotate_cw(template)
    if rotation == "ccw":
        position = rotate_ccw(template)

    for i in range(len(position)):
        x_dif, y_dif = position[i]
        x, y = template[i]
        difference.append((x_dif - x, y_dif - y))

    for i in range(len(position)):
        x_move, y_move = difference[i]
        x, y = block[i]
        new.append((x + x_move, y + y_move))

    for x, y in new:
        if is_occupied(arena, x, y) and (x, y) not in current:
            return block, template

    for x, y in block:
        set_occupied(arena, x, y, False)
    for x, y in new:
        set_occupied(arena, x, y, True)

    return new, position


def remove_rows(arena: Arena, score: int) -> int:
    amount, original_length, new = 0, len(arena[0]), {}

    for i in range(len(arena)):
        if arena[i].count(SQUARE) == original_length:
            amount += 1
            del arena[i]
    key = amount

    for i in range(key):
        new[i] = [EMPTY] * original_length

    for i in list(arena):
        new[key] = arena.pop(i)
        key += 1

    arena.update(new)
    return score + amount ** 2


def action(event: int, arena: Arena, block: Block,
           template: Block, score: int)\
           -> Tuple[bool, int, Block, Block]:
    if event not in [0, 1, 2, 3, 4, 5]:
        print("Invalid input.")
        exit(1)

    if event == 0:
        new = left(arena, block)
        state = True
    if event == 1:
        new = right(arena, block)
        state = True
    if event == 2:
        new, template = rotate(arena, block, "cw", template)
        state = True
    if event == 3:
        new, template = rotate(arena, block, "ccw", template)
        state = True
    if event == 4:
        new, state = down(arena, block)
    if event == 5:
        state = True
        while state:
            new, state = down(arena, block)
            block = new

    if not state:
        score = remove_rows(arena, score)

    return state, score, new, template


def play(arena: Arena) -> int:
    score = 0

    while True:
        template = next_block()
        block = new_block(template, arena)
        if block is None:
            draw(arena, score)
            return score
        draw(arena, score)
        active = True

        while active:
            event = poll_event()
            if event == QUIT:
                draw(arena, score)
                return score
            active, score, block, template = \
                action(event, arena, block, template, score)
            if not active:
                continue
            draw(arena, score)

    return score

if __name__ == '__main__':
    play(new_arena(7, 7))

from typing import List, Tuple, Optional, Set


class Clue:
    def __init__(self, total: int, position: Tuple[int, int],
                 is_row: bool, length: int):
        self.total = total
        self.position = position
        self.is_row = is_row
        self.length = length


class Kakuro:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.array = [[-1 for _ in range(width)] for _ in range(height)]
        self.clues: List[Clue] = []

    def set(self, x: int, y: int, value: int) -> None:
        self.array[y][x] = value

    def show_board(self) -> None:
        for row in self.array:
            for i, value in enumerate(row):

                if value == -1:
                    print("\\", end="")
                elif value == 0:
                    print(".", end="")
                else:
                    print(value, end="")

                if i == len(row) - 1:
                    print()
                else:
                    print(" ", end="")

    def save(self, filename: str) -> None:
        lines = ""

        for y in range(len(self.array)):
            for x in range(len(self.array[0])):
                item = self.array[y][x]

                if item == 0:
                    lines += ". "

                elif item == -1:
                    clue_str = "\\"

                    for clue in self.clues:
                        if (x, y) == clue.position:
                            if clue.is_row:
                                clue_str += str(clue.total)
                            else:
                                clue_str = str(clue.total) + clue_str

                    lines += clue_str + " "

                else:
                    lines += str(item) + " "

            lines = lines[:-1] + "\n"

        with open(filename, "w") as file:
            file.write(lines)

    def is_valid(self) -> bool:
        for clue in self.clues:

            x, y = clue.position
            total = clue.total
            used, amount = set(), 0

            if clue.is_row:
                for offset in range(1, clue.length + 1):
                    total -= self.array[y][x + offset]
                    if self.array[y][x + offset]:
                        amount += 1
                        used.add(self.array[y][x + offset])

            else:
                for offset in range(1, clue.length + 1):
                    total -= self.array[y + offset][x]
                    if self.array[y + offset][x] != 0:
                        amount += 1
                        used.add(self.array[y + offset][x])

            if total < 0 or amount != len(used):
                return False

        return True

    def pick_clue(self) -> Optional[Clue]:

        if self.clues == []:
            return None

        spaces_left = 100
        result = self.clues[0]
        solved = []

        for clue in self.clues:
            current_spaces = count_spaces(self.array, clue)

            if current_spaces == 0:
                solved.append(clue)
                continue

            if current_spaces == spaces_left:
                if result.position == clue.position:
                    if not clue.is_row:
                        result = clue
                        spaces_left = current_spaces

                        continue

                elif clue.position < result.position:
                    result = clue
                    spaces_left = current_spaces

                    continue

            elif current_spaces < spaces_left:
                result = clue
                spaces_left = current_spaces

        if len(solved) == len(self.clues):
            return None

        return result

    def solve(self) -> bool:
        pass  # TODO


def count_spaces(array: List[List[int]], clue: Clue) -> int:
    x, y = clue.position
    spaces_left = 0

    if clue.is_row:
        for offset in range(1, clue.length + 1):
            if array[y][x + offset] == 0:
                spaces_left += 1

    else:
        for offset in range(1, clue.length + 1):
            if array[y + offset][x] == 0:
                spaces_left += 1

    return spaces_left


def load_kakuro(filename: str) -> Kakuro:
    clues = []
    temp = []

    with open(filename, "r") as file:
        for line in file:
            temp.append(line.split())

    kakuro = Kakuro(len(temp[0]), len(temp))

    for row in range(len(temp)):
        for val in range(len(temp[0])):
            item = temp[row][val]
            if item.isdigit():
                kakuro.set(val, row, int(item))

            elif item == ".":
                kakuro.set(val, row, 0)

            else:
                clues.extend(make_clue(temp, item, val, row))

    kakuro.clues = clues

    return kakuro


def cells_from_empty(total: int, length: int) -> List[List[int]]:

    if total > 45 or length > 9:
        return []

    cells: List[List[int]] = []
    find_cells(total, length, [], cells, set())
    cells.sort()

    return cells


def cells_from_partial(total: int, partial: List[int]) -> List[List[int]]:
    amount = total - sum(partial)
    length = partial.count(0)
    used, result = [], []
    cells: List[List[int]] = []

    for val in partial:
        if val != 0:
            used.append(val)

    if len(used) != len(set(used)):
        return []

    if amount != 0 and length == 0:
        return []

    find_cells(amount, length, [], cells, set(used))
    cells.sort()

    for cell in cells:
        pos = 0
        template = partial[:]

        for i in range(len(template)):
            if template[i] == 0:
                template[i] = cell[pos]
                pos += 1

        result.append(template)
    return result


def find_cells(total: int, length: int, current: List[int],
               cells: List[List[int]], used: Set[int]) -> None:

    if sum(current) == total and len(current) == length:
        cells.append(current.copy())
        return

    elif sum(current) > total or len(current) > length:
        return

    else:
        for val in range(1, 10):
            if val not in used:
                current.append(val)
                used.add(val)
                find_cells(total, length, current, cells, used)
                current.pop()
                used.remove(val)

        return


def make_clue(array: List[List[str]], value: str,
              x: int, y: int) -> List[Clue]:
    clues = []

    if value[0] != "\\":
        length = 0
        total = int(value[:value.find("\\")])
        if y != len(array) - 1:
            for row in array[y + 1:]:

                if row[x].isdigit() or row[x] == ".":
                    length += 1
                else:
                    break

        clues.append(Clue(total, (x, y), False, length))

    if value[-1] != "\\":
        length = 0
        total = int(value[value.find("\\") + 1:])
        if x != len(array[0]) - 1:
            for item in array[y][x + 1:]:

                if item.isdigit() or item == ".":
                    length += 1
                else:
                    break

        clues.append(Clue(total, (x, y), True, length))

    return clues


# --- Tests ---

# Note: If there is a file with the following name in the current working
# directory, running these tests will overwrite that file!

TEST_FILENAME = "_tmp_file_"

EXAMPLE = ("\\   11\\  8\\     \\   \\   7\\ 16\\\n"
           "\\16   .   .   11\\   \\4   .   .\n"
           "\\7    .   .     .  7\\13  .   .\n"
           "\\   15\\ 21\\12   .   .    .   .\n"
           "\\12   .   .     .   .   4\\  6\\\n"
           "\\13   .   .     \\6  .    .   .\n"
           "\\17   .   .     \\   \\6   .   .\n")


def write_example(filename: str) -> None:
    with open(filename, "w") as file:
        file.write(EXAMPLE)


def example() -> Kakuro:
    write_example(TEST_FILENAME)
    return load_kakuro(TEST_FILENAME)


def test_1() -> None:
    kakuro = example()
    assert kakuro.width == 7
    assert kakuro.height == 7
    assert kakuro.array == [
        [-1, -1, -1, -1, -1, -1, -1],
        [-1, 0, 0, -1, -1, 0, 0],
        [-1, 0, 0, 0, -1, 0, 0],
        [-1, -1, -1, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, -1, -1],
        [-1, 0, 0, -1, 0, 0, 0],
        [-1, 0, 0, -1, -1, 0, 0],
    ]

    clue_set = {(clue.total, clue.position, clue.is_row, clue.length)
                for clue in kakuro.clues}
    assert clue_set == {
        (11, (1, 0), False, 2),
        (8, (2, 0), False, 2),
        (7, (5, 0), False, 3),
        (16, (6, 0), False, 3),
        (16, (0, 1), True, 2),
        (11, (3, 1), False, 3),
        (4, (4, 1), True, 2),
        (7, (0, 2), True, 3),
        (7, (4, 2), False, 3),
        (13, (4, 2), True, 2),
        (15, (1, 3), False, 3),
        (21, (2, 3), False, 3),
        (12, (2, 3), True, 4),
        (12, (0, 4), True, 4),
        (4, (5, 4), False, 2),
        (6, (6, 4), False, 2),
        (13, (0, 5), True, 2),
        (6, (3, 5), True, 3),
        (17, (0, 6), True, 2),
        (6, (4, 6), True, 2),
    }


def test_2() -> None:
    kakuro = example()
    kakuro.set(2, 1, 5)

    print("show_board result:")
    kakuro.show_board()
    print("---")

    print("save result:")
    kakuro.save("test")
    with open("test") as file:
        print(file.read(), end="")
    print("---")


def test_3() -> None:
    kakuro = example()
    assert kakuro.is_valid()

    kakuro.set(2, 1, 9)
    assert not kakuro.is_valid()

    kakuro.set(2, 1, 0)
    assert kakuro.is_valid()

    kakuro.set(1, 2, 1)
    kakuro.set(2, 2, 1)
    assert not kakuro.is_valid()

    kakuro.set(1, 2, 0)
    kakuro.set(2, 2, 0)
    assert kakuro.is_valid()

    kakuro.set(5, 5, 4)
    assert kakuro.is_valid()


def test_4() -> None:
    assert cells_from_empty(13, 2) \
        == [[4, 9], [5, 8], [6, 7], [7, 6], [8, 5], [9, 4]]

    assert cells_from_empty(6, 3) \
        == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]

    assert cells_from_partial(12, [0, 0, 6, 0]) \
        == [[1, 2, 6, 3], [1, 3, 6, 2], [2, 1, 6, 3],
            [2, 3, 6, 1], [3, 1, 6, 2], [3, 2, 6, 1]]


def test_5() -> None:
    kakuro = example()
    clue = kakuro.pick_clue()

    assert clue is not None
    assert clue.total == 16
    assert clue.position == (0, 1)
    assert clue.is_row
    assert clue.length == 2

    kakuro.set(6, 5, 1)
    clue = kakuro.pick_clue()

    assert clue is not None
    assert clue.total == 6
    assert clue.position == (6, 4)
    assert not clue.is_row
    assert clue.length == 2

    kakuro.set(6, 6, 5)
    clue = kakuro.pick_clue()

    assert clue is not None
    assert clue.total == 6
    assert clue.position == (4, 6)
    assert clue.is_row
    assert clue.length == 2

    kakuro = load_kakuro("sanity_test")
    clue = kakuro.pick_clue()
    assert clue is None


def test_6() -> None:
    kakuro = example()
    kakuro.solve()
    assert kakuro.array == [
        [-1, -1, -1, -1, -1, -1, -1],
        [-1, 9, 7, -1, -1, 1, 3],
        [-1, 2, 1, 4, -1, 4, 9],
        [-1, -1, -1, 5, 1, 2, 4],
        [-1, 1, 5, 2, 4, -1, -1],
        [-1, 6, 7, -1, 2, 3, 1],
        [-1, 8, 9, -1, -1, 1, 5],
    ]


def test_7() -> None:
    assert cells_from_empty(100, 9) == []
    assert cells_from_empty(5, 10) == []
    assert cells_from_empty(-5, 5) == []
    assert cells_from_empty(5, -5) == []
    assert cells_from_empty(10, 1) == []
    assert cells_from_empty(5, 0) == []
    assert cells_from_empty(0, 5) == []

    assert cells_from_partial(100, [0, 2, 0]) == []
    assert cells_from_partial(12, [2, 2, 0]) == []
    assert cells_from_partial(25, [7, 5]) == []
    assert cells_from_partial(2, [1]) == []
    assert cells_from_partial(2, [1, 1]) == []
    assert cells_from_partial(0, [0]) == []
    assert cells_from_partial(1, [1]) == [[1]]
    assert cells_from_partial(42, [8, 8, 0, 0, 0]) == []
    assert cells_from_partial(4, [2, 2]) == []
    assert cells_from_partial(-5, [0]) == []
    assert cells_from_partial(6, [1, 2, 3]) == [[1, 2, 3]]


if __name__ == '__main__':
    test_1()
    # uncomment to visually check the results:
    test_2()
    test_3()
    test_4()
#     test_5()
#     test_6()
    test_7()

from typing import Dict, List, Optional, Set


class Person:
    def __init__(self, pid: int, name: str) -> None:
        self.pid = pid
        self.name = name
        self.birth_year = 0
        self.parent: Optional["Person"] = None
        self.children: List["Person"] = []

    def is_valid(self) -> bool:
        if not self.name:
            return False

        all_names: Set[str] = set()

        for child in self.children:
            if child.name in all_names:
                return False
            else:
                all_names.add(child.name)

            if child.birth_year <= self.birth_year:
                return False

            if not child.is_valid():
                return False

        return True

    def draw(self, names_only: bool) -> None:
        draw_tree(self, names_only, "")

    def parents_younger_than(self, age_limit: int) -> Set[int]:
        return younger_older(self, age_limit, True)

    def parents_older_than(self, age_limit: int) -> Set[int]:
        return younger_older(self, age_limit, False)

    def childless(self) -> Set[int]:

        result = set()

        if not self.children:
            result.add(self.pid)

        for child in self.children:
            result |= child.childless()

        return result

    def ancestors(self) -> List['Person']:

        ancestors = self.rec_anc()
        ancestors.reverse()

        return ancestors

    def rec_anc(self) -> List['Person']:

        ancestors: List['Person'] = []

        if self.parent is None:
            return ancestors

        ancestors.append(self.parent)

        ancestors += self.parent.rec_anc()

        return ancestors

    def order_of_succession(self, alive: Set[int]) -> Dict[int, int]:

        result = {}
        successors = succ_rec(self, alive)

        for i, successor in enumerate(successors):
            result[successor] = i + 1

        return result

    def remove_extinct_branches(self, alive: Set[int]) -> None:
        remove_rec(self, alive)


def younger_older(person: Person, age_limit: int, decider: bool) -> Set[int]:
    result = set()

    for child in person.children:
        if decider:
            if lt(child.birth_year - person.birth_year, age_limit):
                result.add(person.pid)
            result |= child.parents_younger_than(age_limit)

        else:
            if gt(child.birth_year - person.birth_year, age_limit):
                result.add(person.pid)
            result |= child.parents_older_than(age_limit)

    return result


def gt(age: int, limit: int) -> bool:
    return age > limit


def lt(age: int, limit: int) -> bool:
    return age < limit


def build_family_tree(names: Dict[int, str],
                      children: Dict[int, List[int]],
                      birth_years: Dict[int, int]) -> Optional[Person]:

    if not names or not birth_years:
        return None

    if names.keys() != birth_years.keys():
        return None

    number_of_children = 0
    all_children, all_pid = set(), set()

    for parent, child in children.items():
        number_of_children += len(child)
        all_children.update(child)
        all_pid.update(child)
        all_pid.add(parent)

    if not all_pid.issubset(set(list(names))):
        return None

    if len(all_children) != number_of_children:
        return None

    number_of_oldest = 1

    for pid, name in names.items():
        if pid not in all_children:

            if number_of_oldest != 1:
                return None

            oldest = Person(pid, name)
            oldest.birth_year = birth_years[pid]
            number_of_oldest += 1

    oldest.children = add_children(oldest, names, children, birth_years)

    return oldest


def add_children(parent: Person, names: Dict[int, str],
                 children: Dict[int, List[int]],
                 birth_years: Dict[int, int]) -> List[Person]:

    if parent.pid not in children or children[parent.pid] == []:
        return []

    all_children: List[Person] = []

    for child in children[parent.pid]:
        person = Person(child, names[child])
        person.birth_year = birth_years[child]
        person.parent = parent
        person.children = add_children(person, names, children, birth_years)
        all_children.append(person)

    return all_children


def valid_family_tree(person: Person) -> bool:
    if person.parent is None:
        return person.is_valid()

    return valid_family_tree(person.parent)


def draw_tree(person: Person, names_only: bool, nesting: str = "") -> None:

    if names_only:
        print(person.name)
    else:
        print(f"{person.name} ({person.birth_year}) {[person.pid]}")

    for child in person.children:

        if child == person.children[-1]:
            print(nesting, "└─ ", sep="", end="")
            draw_tree(child, names_only, nesting + "   ")

        else:
            print(nesting, "├─ ", sep="", end="")
            draw_tree(child, names_only, nesting + "│  ")


def succ_rec(person: Person, alive: Set[int]) -> List[int]:

    result, years, ordered_children = [], [], []

    for child in person.children:
        years.append(child.birth_year)

    tmp_children = list(person.children)

    for i in range(len(years)):
        ordered_children.append(tmp_children[years.index(min(years))])
        tmp_children.remove(tmp_children[years.index(min(years))])
        years.remove(min(years))

    for child in ordered_children:
        if child.pid in alive:
            result.append(child.pid)
        result += succ_rec(child, alive)

    return result


def remove_rec(person: Person, alive: Set[int]) -> bool:

    to_remove = set()
    new_children = []

    for child in person.children:
        if remove_rec(child, alive):
            if child.pid not in alive:
                to_remove.add(child)

    for child in person.children:
        if child not in to_remove:
            new_children.append(child)

    person.children = new_children

    return person.children == []


def test_one_person() -> None:
    adam = build_family_tree({1: "Adam"}, {}, {1: 1})
    assert isinstance(adam, Person)
    assert adam.pid == 1
    assert adam.birth_year == 1
    assert adam.name == "Adam"
    assert adam.children == []
    assert adam.parent is None

    assert adam.is_valid()
    assert adam.parents_younger_than(18) == set()
    assert adam.parents_older_than(81) == set()
    assert adam.childless() == {1}
    assert adam.ancestors() == []
    assert adam.order_of_succession({1}) == {}


def example_family_tree() -> Person:
    qempa = build_family_tree(
        {
            17: "Qempa'",
            127: "Thok Mak",
            290: "Worf",
            390: "Worf",
            490: "Mogh",
            590: "Kurn",
            611: "Ag'ax",
            561: "K'alaga",
            702: "Samtoq",
            898: "K'Dhan",
            429: "Grehka",
            1000: "Alexander Rozhenko",
            253: "D'Vak",
            106: "Elumen",
            101: "Ga'ga",
        },
        {
            17: [127, 290],
            390: [898, 1000],
            1000: [253],
            127: [611, 561, 702],
            590: [429, 106, 101],
            490: [390, 590],
            290: [490],
            702: [],
        },
        {
            1000: 2366,
            101: 2366,
            106: 2357,
            127: 2281,
            17: 2256,
            253: 2390,
            290: 2290,
            390: 2340,
            429: 2359,
            490: 2310,
            561: 2302,
            590: 2345,
            611: 2317,
            702: 2317,
            898: 2388,
        }
    )

    assert qempa is not None
    return qempa


def test_example() -> None:
    qempa = example_family_tree()
    assert qempa.name == "Qempa'"
    assert qempa.pid == 17
    assert qempa.birth_year == 2256
    assert qempa.parent is None
    assert len(qempa.children) == 2

    thok_mak, worf1 = qempa.children
    assert worf1.name == "Worf"
    assert worf1.pid == 290
    assert worf1.birth_year == 2290
    assert worf1.parent == qempa
    assert len(worf1.children) == 1

    mogh = worf1.children[0]
    assert mogh.name == "Mogh"
    assert mogh.pid == 490
    assert mogh.birth_year == 2310
    assert mogh.parent == worf1
    assert len(mogh.children) == 2

    worf2 = mogh.children[0]
    assert worf2.name == "Worf"
    assert worf2.pid == 390
    assert worf2.birth_year == 2340
    assert worf2.parent == mogh
    assert len(worf2.children) == 2

    alex = worf2.children[1]
    assert alex.name == "Alexander Rozhenko"
    assert alex.pid == 1000
    assert alex.birth_year == 2366
    assert alex.parent == worf2
    assert len(alex.children) == 1

    assert qempa.is_valid()
    assert alex.is_valid()
    assert valid_family_tree(qempa)
    assert valid_family_tree(alex)

    thok_mak.name = ""
    assert not qempa.is_valid()
    assert alex.is_valid()
    assert not valid_family_tree(qempa)
    assert not valid_family_tree(alex)
    thok_mak.name = "Thok Mak"

    thok_mak.birth_year = 2302
    assert not qempa.is_valid()
    assert alex.is_valid()
    assert not valid_family_tree(qempa)
    assert not valid_family_tree(alex)
    thok_mak.birth_year = 2281

    assert qempa.parents_younger_than(12) == set()
    assert qempa.parents_younger_than(15) == {590}
    assert qempa.parents_younger_than(21) == {290, 590}

    assert qempa.parents_older_than(48) == set()
    assert qempa.parents_older_than(40) == {390}

    assert thok_mak.parents_younger_than(21) == set()
    assert thok_mak.parents_older_than(40) == set()

    assert qempa.childless() == {101, 106, 253, 429, 561, 611, 702, 898}
    assert thok_mak.childless() == {611, 561, 702}

    assert alex.ancestors() == [qempa, worf1, mogh, worf2]
    assert thok_mak.ancestors() == [qempa]
    assert qempa.ancestors() == []

    alive = {17, 101, 106, 127, 253, 290, 390, 429,
             490, 561, 590, 611, 702, 898, 1000}
    succession = {
        101: 14,
        106: 12,
        127: 1,
        253: 9,
        290: 5,
        390: 7,
        429: 13,
        490: 6,
        561: 2,
        590: 11,
        611: 3,
        702: 4,
        898: 10,
        1000: 8,
    }

    assert qempa.order_of_succession(alive) == succession

    alive.remove(17)
    assert qempa.order_of_succession(alive) == succession

    alive -= {127, 290, 490, 590}
    assert qempa.order_of_succession(alive) == {
        561: 1,
        611: 2,
        702: 3,
        390: 4,
        1000: 5,
        253: 6,
        898: 7,
        106: 8,
        429: 9,
        101: 10,
    }

    assert mogh.order_of_succession(alive) == {
        390: 1,
        1000: 2,
        253: 3,
        898: 4,
        106: 5,
        429: 6,
        101: 7,
    }


def draw_example() -> None:
    qempa = example_family_tree()
    print("První příklad:")
    qempa.draw(False)

    print("\nDruhý příklad:")
    qempa.children[1].children[0].draw(True)

    alive1 = {101, 106, 253, 429, 561, 611, 702, 898}
    alive2 = {101, 106, 253, 390, 898, 1000}
    for alive in alive1, alive2:
        print(f"\nRodokmen po zavolání remove_extinct_branches({alive})\n"
              "na výchozí osobě:")
        qempa = example_family_tree()
        qempa.remove_extinct_branches(alive)
        qempa.draw(True)

    print(f"\nRodokmen po zavolání remove_extinct_branches({alive})\n"
          "na osobě jménem Mogh:")
    qempa = example_family_tree()
    qempa.children[1].children[0].remove_extinct_branches(alive2)
    qempa.draw(True)


def test_1() -> None:
    tree = build_family_tree(
      {3432: "K'Vagh", 596: "Wa'Joh'a'", 2149: 'Konmel', 7958: 'Atul'},
      {3432: [596], 596: [2149, 7958], 7958: []},
      {3432: 1943, 596: 2034, 2149: 2039, 7958: 2133})

    assert tree is not None

    tree.draw(False)
    assert tree.parents_older_than(31) == {3432, 596}


if __name__ == '__main__':
    test_one_person()
    test_example()
    draw_example()  # uncomment to run
    test_1()

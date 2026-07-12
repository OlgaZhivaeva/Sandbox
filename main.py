class Range:
    def __init__(self, stop_value: int):
        self._current = -1
        self._stop_value = stop_value - 1

    def __iter__(self):
        return RangeIterator(self)

class RangeIterator:
    def __init__(self, container: Range):
        self._container = container

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self._container._current < self._container._stop_value:
            self._container._current += 1
            return self._container._current
        raise StopIteration

my_range = Range(10)
for i in my_range:
    print(i)

class Range2:
    def __init__(self, stop_value: int):
        self._current = -1
        self._stop_value = stop_value - 1

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self._current < self._stop_value:
            self._current += 1
            return self._current
        raise StopIteration
print('----------')
my_range = Range2(10)
for i in my_range:
    print(i)

print('----------')
iterable = Range2(5)
iterator = iter(iterable)
while True:
    try:
        value = next(iterator)
        print(value)
    except StopIteration:
        break

print('----------')
iterable = Range(5)
iterator = iter(iterable)
while True:
    try:
        value = next(iterator)
        print(value)
    except StopIteration:
        break

# -------------- Как работает цикл for под капотом -----------------

my_iterable = [1, 2, 3, 4, 5]
my_iterator = iter(my_iterable)
while True:
    try:
        value = next(my_iterator)
    except StopIteration:
        break
    print('value:', value)

print('----------')

for value in my_iterable:
    print('value:', value)

print('----------')
# ------------- Проверки типов -----------------------------
from collections.abc import Iterable, Iterator, Sequence

# assert isinstance([], Iterable)
# assert isinstance(iter([]), Iterator)
# assert isinstance((), Sequence)  # последовательность с размером и индексированием

try:
    assert isinstance(my_range, Iterable)
    print('my_range is iterable')
except AssertionError:
    print('my_range is not iterable')

try:
    assert isinstance(my_iterable, Iterable)
    print('my_iterable is iterable')
except AssertionError:
    print('my_iterable is not iterable')

try:
    assert isinstance(my_iterable, Sequence)
    print('my_iterable is sequence')
except AssertionError:
    print('my_iterable is not sequence')

try:
    assert isinstance(my_iterable, Iterator)
    print('my_iterable is iterator')
except AssertionError:
    print('my_iterable is not iterator')

try:
    assert isinstance(my_iterator, Iterator)
    print('my_iterator is iterator')
except AssertionError:
    print('my_iterator is not iterator')

print('----------')
# ----------- Как работает enumerate(iterable, start=0) под капотом ----------------------------
my_iterable = [1, 2, 3, 4, 5]
print(list(enumerate(my_iterable)))

def my_enumerate(iterable, start=0):
    i = start
    for item in iterable:
        yield i, item
        i += 1
enum = my_enumerate(my_iterable)
print(list(enum))

# --------------- генераторы --------------------------------------
print('----------')
def my_gen():
    count = 0
    yield count
    count += 1
    yield count
    return 'end'
gen = my_gen()
print(next(gen))
print(next(gen))
try:
    print(next(gen))
except StopIteration as e:
    print(f'StopIteration {e}')


print('----------')
def echo():
    received = yield "start"
    while True:
        received = yield received

g = echo()
print(next(g))         # 'start'
print(g.send(42))      # 42
print(g.send("hello")) # 'hello'



print('----------')
def echo_2():
    n = 0
    received = yield f"{n} start"
    while n < 3:
        n += 1
        try:
            received = yield f"{n} {received}"
        except ValueError:
            yield "got exception"
    return "end"

gen = echo_2()
print(next(gen))
print(gen.send(42))
print(gen.send("hello"))
print(gen.send("world"))
try:
    print(gen.throw(ValueError))
except Exception as e:
    print(e)
try:
    print(next(gen))
except StopIteration as e:
    print(f'StopIteration {e}')


# ---------------------------- yield from ---------------------------------------------
print('----------')
def subgen():
    yield 1
    yield 2
    return 42  # станет значением выражения `yield from`

def delegating():
    result = yield from subgen()
    yield f"subgen returned: {result}"

it = delegating()
print(next(it))  # 1
print(next(it))  # 2
print(next(it))  # 'subgen returned: 42'

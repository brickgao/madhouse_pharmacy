
def new_offset(init):
    x = [init]
    def inc(length):
        x[0] += length
        return length
    def show():
        return x[0]

    return show, inc


def create_counter(init=0):
    counter = [init]
    def inc(x):
        counter[0] += x
        return x
    def show():
        return counter[0]

    return show, inc



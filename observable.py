import threading
import logging


class State:
    '''Event dispatcher for observable '''

    def __init__(self, event: threading.Event,
                 mutable: list, name: str):
        self._mutable = mutable
        self.event = event
        self.name = name

    @property
    def value(self):
        return self._mutable[-1]

    @value.setter
    def value(self, value):
        if self._mutable[-1] == value:
            # logging.debug((f'{value} is same as state, state {self.name}'
            #                f' isn\'t changed'
            #                ))
            return

        self._mutable.pop()
        self._mutable.append(value)
        # logging.debug(f'new state for {self.name} is set')
        self.event.set()


class Variable:
    '''An object to control changes in its value and
    to inform observers '''

    def __init__(self, callable_, value=None, name="Variable"):
        self.callable = callable_
        self.change_event = threading.Event()
        self.value = [value]
        self.state = State(self.change_event, self.value, name)
        threading.Thread(target=self.observe, daemon=True).start()

    def observe(self):
        self.change_event.wait()
        self.callable(self.value[-1], self)
        self.change_event.clear()
        threading.Thread(target=self.observe, daemon=True).start()
        

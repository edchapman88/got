import json
from enum import Enum, auto
from dataclass_wizard import fromdict
from dataclasses import dataclass


class Action(Enum):
    ToggleGreen = auto()
    ToggleRed = auto()
    Wait = auto()

    @staticmethod
    def parse(info: str):
        match info:
            case 'ToggleGreen':
                Action.ToggleGreen
            case 'ToggleRed':
                Action.ToggleRed
            case 'Wait':
                Action.Wait
            case u:
                raise Exception(f'Action: {u} is unimplemented')


@dataclass
class State:
    ok_rate: float
    green_blocked: bool
    red_blocked: bool
    reward: int

    def __getitem__(self, key):
        return getattr(self, key)


class Blue:
    def __init__(self, log_file_path: str):
        actions = []
        states = []
        with open(log_file_path) as f:
            for line in f.readlines():
                [time, info] = line.split(maxsplit=1, sep=' ')
                time = int(time.replace('[', '').replace(']', ''))

                if info.startswith('{'):
                    states.append((time, fromdict(State, json.loads(info))))
                else:
                    actions.append((time, Action.parse(info.strip('\n'))))
        self.actions, self.states = actions, states

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

    def stats(self, sorted=False):
        half = round((self.states[-1][0] - self.states[0][0]) / 2) + self.states[0][0]
        exploration = [state for (time, state) in self.states if time < half]
        cumulative_reward = {
            'none_blocked': 0,
            'both_blocked': 0,
            'green_blocked': 0,
            'red_blocked': 0,
        }
        for state in exploration:
            if state['green_blocked']:
                if state['red_blocked']:
                    cumulative_reward.update(
                        both_blocked=cumulative_reward.get('both_blocked')
                        + state['reward']
                    )
                else:
                    cumulative_reward.update(
                        green_blocked=cumulative_reward.get('green_blocked')
                        + state['reward']
                    )
            else:
                if state['red_blocked']:
                    cumulative_reward.update(
                        red_blocked=cumulative_reward.get('red_blocked')
                        + state['reward']
                    )
                else:
                    cumulative_reward.update(
                        none_blocked=cumulative_reward.get('none_blocked')
                        + state['reward']
                    )

        items = list(cumulative_reward.items())
        if sorted:
            items.sort(key=lambda x: x[1], reverse=True)
        return items

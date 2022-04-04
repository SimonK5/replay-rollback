from pandas import DataFrame
from parsing.replay import Stage
from parsing import Replay, Character
from collections import Counter


def stage_count(replays):
    """ Counts the occurrences of each stage in a list of Replay instances. """
    count = [0 for _ in range(len(Stage) - 1)]

    for replay in replays:
        if int(replay.stage) < 1:
            raise Exception("Invalid Replay: Incorrect Stage", replay.name)

        count[replay.stage] += 1

    return count


def player_char_count(replays, target_name):

    target_count = [0 for _ in range(len(Character) - 3)]
    other_count = [0 for _ in range(len(Character) - 3)]

    for replay in replays:
        target_player = next(p for p in replay.players if p.name == target_name)
        other_player = next(p for p in replay.players if p.name != target_name)

        if int(target_player.character) < 2 or int(other_player.character) < 2:
            raise Exception("Invalid Character")

        target_count[target_player.character - 2] += 1
        other_count[other_player.character - 2] += 1

    return target_count, other_count


def get_replays(files):
    """ Converts a directory of replay files into Replay instances. """
    replays = []
    for file in files:
        if file.filename.endswith(".roa"):
            replay = Replay(file.read().decode('utf-8'))
            replays.append(replay)

    # reverse to get most recent replays first
    return replays[::-1]


def num_inputs(df):
    """ Calculates the approximate number of inputs by one player over a single replay. """
    count = 0
    prev_row = None
    for row in df.iloc:
        for i in range(1, 17):
            if row[i]:
                if prev_row is None or (not prev_row[i]):
                    count += 1
                    break
        prev_row = row

    return count


def actions_per_minute(df):
    n_inputs = num_inputs(df)

    return (3600 * n_inputs) / df.iloc[-1]["Frame"]


def get_names(players):
    """ Returns the list of names for a list of players. """
    names = []
    for player in players:
        names.append(player.name)

    return names


def avg_apm_recent(target_name, target_replays, num=5):
    cumulative_apm = 0

    iterations = min(num, len(target_replays))

    for i in range(iterations):
        target_player = next(p for p in target_replays[i].players if p.name == target_name)
        df = DataFrame(target_player.states)
        cumulative_apm += actions_per_minute(df)

    return cumulative_apm / iterations


def get_target_player(replays):
    """Determine the player to analyze in given a target set of replays.

    Precondition: The input array is not empty.
    """
    possible_player_names = get_names(replays[0].players)

    for replay in replays:
        replay_names = get_names(replay.players)
        if Counter(replay_names) == Counter(possible_player_names):
            continue
        elif possible_player_names[0] in replay_names:
            return possible_player_names[0]
        elif possible_player_names[1] in replay_names:
            return possible_player_names[1]

    return possible_player_names[0]

if __name__ == "__main__":
    replays = [r for r in get_replays("../replays/salmon-replays") if len(r.players) == 2]

    target_name = get_target_player(replays)
    target_replays = [r for r in replays if any(p.name == target_name for p in r.players)]
    print(len(target_replays))
    print(player_char_count(target_replays, target_name))
    print(stage_count(target_replays))

    print(avg_apm_recent(target_name, target_replays, num=5))

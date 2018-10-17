from test_common import ReplayData, PlayerData, FrameData, LookupTable, Action, ActionType, SAMPLE_PLAYER_DATA
import pytest


@pytest.fixture
def action_table():
    return FrameData.get_action_table(PlayerData.get_frame_data(SAMPLE_PLAYER_DATA))


@pytest.fixture
def raw_action_table():
    return FrameData.get_action_table(PlayerData.get_frame_data(SAMPLE_PLAYER_DATA), raw=True)


class TestFrameData:
    
    def test_convert_token_to_action(self):
        assert FrameData.convert_token_to_action('Z') == Action.ANGLES_ENABLED
        assert FrameData.convert_token_to_action('y327') == 327
        assert FrameData.convert_token_to_action('R') == Action.RIGHT_PRESS

    def test_convert_multiple_tokens_to_actions(self):
        assert FrameData.convert_multiple_tokens_to_actions(['Z']) == [Action.ANGLES_ENABLED]
        assert FrameData.convert_multiple_tokens_to_actions(['z', 'y327', 'R']) == [Action.ANGLES_DISABLED, 327, Action.RIGHT_PRESS]
        assert FrameData.convert_multiple_tokens_to_actions(['C']) == [Action.STRONG_PRESS]
        assert FrameData.convert_multiple_tokens_to_actions(['Z', 'y  0', 'r', 'c']) == [Action.ANGLES_ENABLED, 0, Action.RIGHT_RELEASE, Action.STRONG_RELEASE]
        assert FrameData.convert_multiple_tokens_to_actions(['z', 'y143', 'L', 'U']) == [Action.ANGLES_DISABLED, 143, Action.LEFT_PRESS, Action.UP_PRESS]
        assert FrameData.convert_multiple_tokens_to_actions(['y  0']) == [0]
        assert FrameData.convert_multiple_tokens_to_actions(['Z', 'y180', 'd']) == [Action.ANGLES_ENABLED, 180, Action.DOWN_RELEASE]
        assert FrameData.convert_multiple_tokens_to_actions(['z', 'D']) == [Action.ANGLES_DISABLED, Action.DOWN_PRESS]

    def test_split_frames_into_tokens(self):
        split_frames = FrameData.split_frames_into_tokens(PlayerData.get_frame_data(SAMPLE_PLAYER_DATA))
        assert split_frames[0] == ['1', 'Z']
        assert split_frames[1] == ['101', 'z', 'y327', 'R']
        assert split_frames[-2] == ['2384', 'Z', 'y180', 'd']
        assert split_frames[-1] == ['2385', 'y  0']

    def test_get_action_table(self, action_table):
        assert len(action_table.keys()) == 717
        assert action_table[1] == [Action.ANGLES_ENABLED]
        assert action_table[101] == [Action.ANGLES_DISABLED, 327, Action.RIGHT_PRESS]
        assert action_table[148] == [Action.STRONG_PRESS]
        assert action_table[154] == [Action.ANGLES_ENABLED, 0, Action.RIGHT_RELEASE, Action.STRONG_RELEASE]
        assert action_table[1293] == [Action.ANGLES_DISABLED, 143, Action.LEFT_PRESS, Action.UP_PRESS]
        assert action_table[2366] == [Action.ANGLES_DISABLED, Action.DOWN_PRESS]
        assert action_table[2384] == [Action.ANGLES_ENABLED, 180, Action.DOWN_RELEASE]
        assert action_table[2385] == [0]

    def test_get_action_table_raw(self, raw_action_table):
        assert len(raw_action_table.keys()) == 717
        assert raw_action_table[1] == ['Z']
        assert raw_action_table[101] == ['z', 'y327', 'R']
        assert raw_action_table[148] == ['C']
        assert raw_action_table[154] == ['Z', 'y  0', 'r', 'c']
        assert raw_action_table[1293] == ['z', 'y143', 'L', 'U']
        assert raw_action_table[2366] == ['z', 'D']
        assert raw_action_table[2384] == ['Z', 'y180', 'd']
        assert raw_action_table[2385] == ['y  0']

    def test_get_state_table(self):
        state_p1 = FrameData.get_state_table(PlayerData.get_frame_data(SAMPLE_PLAYER_DATA))
        state = [False]*22 + [-1]
        state[ActionType.ANGLES_ENABLED] = True
        assert state_p1[1] == state

        state[ActionType.ANGLES_ENABLED] = False
        state[ActionType.ANGLE_RIGHT] = True
        state[ActionType.ANGLE_DOWN] = True
        state[ActionType.RIGHT] = True
        state[ActionType.ANGLE] = 327
        assert state_p1[101] == state

        state[ActionType.ANGLE_UP:ActionType.ANGLE] = [False]*8
        state[ActionType.ANGLE] = -1
        state[ActionType.ANGLE_RIGHT] = False
        state[ActionType.STRONG] = True
        assert state_p1[148] == state

        state[ActionType.ANGLE_UP:ActionType.ANGLE] = [False]*8
        state[ActionType.ANGLE] = -1
        state[ActionType.ANGLES_ENABLED] = True
        state[ActionType.ANGLE_RIGHT] = True
        state[ActionType.RIGHT] = False
        state[ActionType.STRONG] = False
        state[ActionType.ANGLE] = 0
        assert state_p1[154] == state

    def test_snap_frame(self, action_table):
        assert FrameData.snap_frame(action_table, 1) == 1
        assert FrameData.snap_frame(action_table, 100) == 1
        assert FrameData.snap_frame(action_table, 101) == 101
        assert FrameData.snap_frame(action_table, 112) == 112
        assert FrameData.snap_frame(action_table, 114) == 112
        assert FrameData.snap_frame(action_table, 115) == 115
        assert FrameData.snap_frame(action_table, 118) == 115
        assert FrameData.snap_frame(action_table, 2385) == 2385
        assert FrameData.snap_frame(action_table, 9999) == 2385

    def test_snap_frame_error(self, action_table):
        with pytest.raises(ValueError): FrameData.snap_frame(action_table, -1)

    def test_snap_frame_transitive(self, raw_action_table):
        assert raw_action_table[FrameData.snap_frame(raw_action_table, 100)] == ['Z']
        assert raw_action_table[FrameData.snap_frame(raw_action_table, 101)] == ['z', 'y327', 'R']

    def test_snap_multiple_frames(self, action_table):
        snapped = FrameData.snap_multiple_frames(action_table, [1, 100, 101, 112, 114, 115, 118, 2385, 9999])
        assert snapped == [1, 1, 101, 112, 112, 115, 115, 2385, 2385]

    def test_snap_angle(self):
        assert FrameData.snap_angle(0) == 0
        assert FrameData.snap_angle(23) == 45
        assert FrameData.snap_angle(45) == 45
        assert FrameData.snap_angle(67) == 45
        assert FrameData.snap_angle(68) == 90
        assert FrameData.snap_angle(180) == 180
        assert FrameData.snap_angle(360) == 0

    def test_get_closest_frame(self, raw_action_table):
        assert FrameData.get_closest_action(raw_action_table, 100) == ['Z']
        assert FrameData.get_closest_action(raw_action_table, 101) == ['z', 'y327', 'R']

    def test_snap_angle_error(self):
        with pytest.raises(ValueError): FrameData.snap_angle(-1)
        with pytest.raises(ValueError): FrameData.snap_angle(361)

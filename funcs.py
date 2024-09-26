from players import Participant
from teams import Team


def dec_cap(player_list: list[Participant], TEAM_NUM: int) -> list[Participant]:
    """プレイヤーリスト, チーム数を受け取って主将を決定
    可能なら主将に決定したプレイヤーをplayer_listから除外しておきたい

    Args:
        player_list (list[Participant]): 参加者リスト
        TEAM_NUM (int): チーム数

    Returns:
        list[Participant]: 主将リスト
    """

    cap_list: list[Participant] = []
    return cap_list


def dec_team_rand(
    player_list: list[Participant], teams: list[Team]
) -> list[Participant]:
    """ランダムにチームを決定するアルゴリズム

    Args:
        player_list (list[Participant]): 主将以外の参加者リスト
        teams (list[Team]): 主将入力済みのチームリスト

    Returns:
        list[Participant]: 決定後のチームリスト
    """

    return teams

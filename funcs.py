from players import Participant
from teams import Team
import copy
import random
import statistics

def dec_cap(
        player_list: list[Participant], 
        TEAM_NUM: int
        ) -> list[Participant]:
    """プレイヤーリスト, チーム数を受け取って主将を決定
    可能なら主将に決定したプレイヤーをplayer_listから除外しておきたい

    Args:
        player_list (list[Participant]): 参加者リスト
        TEAM_NUM (int): チーム数

    Returns:
        list[Participant]: 主将を除いた参加者リスト
        list[captains]: 主将リスト
    """

    cap_list: list[Participant] = []
    cap_num: int = 0
    player_list_copy = copy.deepcopy(player_list)

    #主将の人数を数え、cap_listに入れる
    for i in range(len(player_list_copy)):
        if player_list_copy[i].captain:
            p = player_list_copy.pop(i)
            cap_list.append(p)
            cap_num += 1
    
    #主将が足りない場合に補充
    while cap_num < TEAM_NUM:
        random_cap: int = random.randint(1, len(player_list_copy))
        p = player_list_copy.pop(random_cap)
        p.captain =  True
        cap_list.append(p)
        cap_num += 1

    #主将を除いたplayer_listも返せます
    #return (player_list_copy, cap_list)
    return cap_list


def dec_team_rand(
        player_list: list[Participant], 
        teams: list[Team]
        ) -> list[Participant]:
    """ランダムにチームを決定するアルゴリズム

    Args:
        player_list (list[Participant]): 主将以外の参加者リスト
        teams (list[Team]): 主将入力済みのチームリスト
    Returns:
        list[Participant]: 決定後のチームリスト
    """
    #teamのエリアpwの平均を返す関数
    def team_mean_func(team: list) -> (int, int):
        pw_list = [team[i].zones_pw for i in range(len(team))]
        return statistics.mean(pw_list)
    
    par_num: int = len(player_list) #主将を除いた参加人数
    teams_num: int = len(teams)
    mean_var_max: float = 10**8 #全チームの平均の分散
    m: int = 10**4 #繰り返し調べる回数
    teams_keep = [] #ずっと保存

    for i in range(m):
        teams_keeping = copy.deepcopy(teams) #一時保存
        shuffled_data = random.sample(player_list)
        player_shuffle_list = [shuffled_data[i::teams_num] for i in range(teams_num)]
        mean_list = []
        for team, players in zip(teams_keeping, player_shuffle_list):
            team.append(players)
            mean_list.append(team_mean_func(team))
        mean_var = statistics.variance(mean_list)
        if mean_var_max > mean_var:
            mean_var_max = mean_var
            teams_keep = teams_keeping

    return teams_keep

# プレイヤー基底クラス
class Player:
    def __init__(
        self,
        name: str,
        zones_pw: float = 0,
        tower_pw: float = 0,
        rainmaker_pw: float = 0,
        clam_pw: float = 0,
    ) -> None:
        self.name = name
        self.zones_pw = zones_pw
        self.tower_pw = tower_pw
        self.rainmaker_pw = rainmaker_pw
        self.clam_pw = clam_pw

    def max_power(self) -> float:
        return max(self.zones_pw, self.tower_pw, self.rainmaker_pw, self.clam_pw)

    def ave_power(self) -> float:
        return sum((self.zones_pw, self.tower_pw, self.rainmaker_pw, self.clam_pw)) / 4

    def set_zones_pw(self, zones_pw: float) -> None:
        self.zones_pw = zones_pw

    def set_tower_pw(self, tower_pw: float) -> None:
        self.tower_pw = tower_pw

    def set_rainmaker_pw(self, rainmaker_pw: float) -> None:
        self.rainmaker_pw = rainmaker_pw

    def set_clam_pw(self, clam_pw: float) -> None:
        self.clam_pw = clam_pw


# ドラフト参加者クラス
class Participant(Player):
    def __init__(
        self,
        name: str,
        captain: bool,
        zones_pw: float = 0,
        tower_pw: float = 0,
        rainmaker_pw: float = 0,
        clam_pw: float = 0,
        back_player: bool = False,
    ) -> None:
        super().__init__(name, zones_pw, tower_pw, rainmaker_pw, clam_pw)
        self.captain = captain
        self.back_player = back_player

    def set_captain(self) -> None:
        self.captain = True

    def set_back_player(self) -> None:
        self.back_player = True


if __name__ == "__main__":
    p = Participant("かずら77", False)
    p.set_zones_pw(2704.2)
    print(p.zones_pw)

from logging import getLogger

import numpy as np

from players import Participant

logger = getLogger(__name__)


# チーム基底クラス
class Team:
    def __init__(
        self,
        captain: Participant,
        participant1: Participant = None,
        participant2: Participant = None,
        participant3: Participant = None,
    ) -> None:
        p = [captain, participant1, participant2, participant3]
        if all(p):
            self.members = p
        else:
            self.members = [captain]

        self.captain = captain
        self.LIMIT = 4

    def add_player(self, participant: Participant) -> None:
        if len(self.members) < self.LIMIT:
            self.members.append(participant)
        else:
            logger.info("This team is full.")

    def exist_back(self) -> bool:
        if any([p.back_player for p in self.members]):
            return True
        else:
            return False

    def ave_power(self) -> float:
        # とりあえずルール問わず最大XPの平均を返すよう設定
        return np.average([p.max_power() for p in self.members])

    def show_member(self) -> list[Participant]:
        return [p for p in self.members]


if __name__ == "__main__":
    participants = [
        Participant("かずら77", True, zones_pw=2704),
        Participant("いもけんぴぃ", False, zones_pw=2724),
        Participant("おじろ", False, zones_pw=2858, back_player=True),
        Participant("あ", False, zones_pw=3100),
        Participant("らぷちゃん", False, zones_pw=2737),
    ]

    t = Team(participants[0])
    print(t.ave_power())
    t.add_player(participants[1])
    print(t.ave_power())
    t.add_player(participants[2])
    print(t.exist_back())
    t.add_player(participants[4])
    t.add_player(participants[3])

    print(t.show_member())

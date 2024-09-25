def add_participant() -> dict:
    name, cap = input()  # 名前、主将 or not

    participants = {"name": name, "cap": cap}

    return participants


def add_captain(n: int, participants: list) -> list:
    return participants


def dec_captain(lim: int, participants: list) -> list:
    return participants


def main():
    a = input()  # コマンド受け取り

    if a == "!draft":
        print()  # メッセージ,セレクトメニューto 入力者のみ
        TEAM_NUM = input()  # セレクトメニューからチーム数を取得
    else:
        return

    PARTC_LIM = TEAM_NUM * 4  # 参加者上限

    print()  # メッセージ,ボタン 「主将 or not」

    participants = []
    for i in range(PARTC_LIM):
        participants.append(add_participant(participants))

    partc_num = participants.values()
    if sum(partc_num) < PARTC_LIM:
        add_captain(PARTC_LIM - partc_num, participants=participants)  # 主将を追加
    elif sum(partc_num) > PARTC_LIM:
        dec_captain(PARTC_LIM, participants=participants)  # 主将を確定
    else:
        pass

    for k, v in participants:
        input()  # 全参加者に対してXP入力を要請


if __name__ == "main":
    main()

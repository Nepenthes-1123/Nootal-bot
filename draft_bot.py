import collections
import os
import random
import time

import discord
from discord import ButtonStyle, Client, Intents, Interaction, SelectOption, TextStyle
from discord.app_commands import CommandTree
from discord.ui import Button, Modal, Select, TextInput, View
from dotenv import load_dotenv

import funcs
from players import Participant
from teams import Team

load_dotenv()

name_dict: dict[str, str] = {}


class MyClient(Client):
    def __init__(self, intents: Intents) -> None:
        super().__init__(intents=intents)
        self.tree = CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()

    async def on_ready(self) -> None:
        print("login:", self.user.name, "[", self.user.id, "]")

        for a in client.get_all_members():
            if not a.bot:
                name_dict[str(a.id)] = a.nick if a.nick is not None else a.name


intents = Intents.default()
intents.members = True  # メンバー管理権限
intents.message_content = True  # メッセージ内容を取得する権限

client = MyClient(intents=intents)


class SelectTeatNum(View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.values = 0

    @discord.ui.select(
        cls=Select,
        placeholder="チーム数を選んでください。",
        options=[SelectOption(value=int(i), label=int(i)) for i in range(1, 9)],
    )
    async def selectMenu(self, interaction: Interaction, select: Select) -> None:
        select.disabled = True
        self.values = int(select.values[0])
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("チーム数: " + select.values[0])


class GetPower(Modal):
    def __init__(self, title: str, players: list[Participant], cap: bool) -> None:
        super().__init__(title=title, timeout=None)
        self.player_list = players
        self.cap = cap

        self.zones = TextInput(
            label="ガチエリア", style=TextStyle.short, placeholder="2000", required=True
        )
        self.add_item(self.zones)
        self.tower = TextInput(
            label="ガチヤグラ", style=TextStyle.short, placeholder="2000", required=True
        )
        self.add_item(self.tower)
        self.rainmaker = TextInput(
            label="ガチホコ", style=TextStyle.short, placeholder="2000", required=True
        )
        self.add_item(self.rainmaker)
        self.clam = TextInput(
            label="ガチアサリ", style=TextStyle.short, placeholder="2000", required=True
        )
        self.add_item(self.clam)

    async def on_submit(self, interaction: Interaction) -> None:

        if (
            self.zones.value != ""
            and self.tower.value != ""
            and self.rainmaker.value != ""
            and self.clam.value != ""
        ):
            self.player_list.append(
                Participant(
                    name=str(interaction.user.id),
                    captain=self.cap,
                    zones_pw=float(self.zones.value),
                    tower_pw=float(self.tower.value),
                    rainmaker_pw=float(self.rainmaker.value),
                    clam_pw=float(self.clam.value),
                )
            )

            await interaction.response.send_message(
                "入力ありがとうございました。", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "値が取得できませんでした。", ephemeral=True
            )

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        print("errorった")


class CapButton(Button):
    def __init__(
        self,
        player: list[Participant],
        PLAYER_LIM: int,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: str | None = "主将",
        disabled: bool = False,
        custom_id: str | None = None,
        url: str | None = None,
        emoji: str | discord.Emoji | discord.PartialEmoji | None = None,
        row: int | None = None,
        sku_id: int | None = None,
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            row=row,
            sku_id=sku_id,
        )
        self.player_list = player
        self.PLAYER_LIM = PLAYER_LIM

    async def callback(self, interaction: Interaction) -> None:
        if str(interaction.user.id) not in [p.name for p in self.player_list]:
            modal = GetPower("各ルールのXPを入力してください。", self.player_list, True)
            await interaction.response.send_modal(modal)

            def check_get_power(a: Select) -> bool:
                return bool(
                    modal.zones.value != "" or len(self.player_list) >= self.PLAYER_LIM
                )

            try:
                await client.wait_for("message", check=check_get_power)
            except Exception as e:
                print("select", e)

            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content="現在参加人数: " + str(len(self.player_list)),
            )
            await interaction.followup.send("主将を選択しました。", ephemeral=True)
        else:
            await interaction.response.send_message(
                "すでに参加しています。", ephemeral=True
            )


class PrtcButton(Button):
    def __init__(
        self,
        player: list[Participant],
        PLAYER_LIM: int,
        *,
        style: ButtonStyle = ButtonStyle.secondary,
        label: str | None = "参加者",
        disabled: bool = False,
        custom_id: str | None = None,
        url: str | None = None,
        emoji: str | discord.Emoji | discord.PartialEmoji | None = None,
        row: int | None = None,
        sku_id: int | None = None,
    ):
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            custom_id=custom_id,
            url=url,
            emoji=emoji,
            row=row,
            sku_id=sku_id,
        )
        self.player_list = player
        self.PLAYER_LIM = PLAYER_LIM

    async def callback(self, interaction: Interaction) -> None:
        if str(interaction.user.id) not in [p.name for p in self.player_list]:
            modal = GetPower(
                "各ルールのXPを入力してください。", self.player_list, False
            )
            await interaction.response.send_modal(modal)

            def check_get_power(a: Select) -> bool:
                return bool(
                    modal.zones.value != "" or len(self.player_list) >= self.PLAYER_LIM
                )

            try:
                await client.wait_for("message", check=check_get_power)
            except Exception as e:
                print("select", e)

            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content="現在参加人数: " + str(len(self.player_list)),
            )
            await interaction.followup.send("参加者を選択しました。", ephemeral=True)
        else:
            await interaction.response.send_message(
                "すでに参加しています。", ephemeral=True
            )


class SelectTeatMem(View):
    def __init__(
        self,
        *,
        cap_list: list[Participant],
        player_list: list[Participant],
        timeout: float | None = 180,
    ):
        super().__init__(timeout=timeout)
        self.cap_list = [cap for cap in cap_list]
        self.cap_selected: dict[str, str] = {}
        for cap in self.cap_list:
            self.cap_selected[cap.name] = ""
        self.player_list = player_list

    @discord.ui.select(
        cls=Select,
        placeholder="ドラフトするメンバーを選んでください。",
    )
    async def selectMenu(self, interaction: Interaction, select: Select) -> None:
        if (
            any([str(interaction.user.id) in cap.name for cap in self.cap_list])
            and self.cap_selected[str(interaction.user.id)] == ""
        ):
            print(select.values)
            self.cap_selected[str(interaction.user.id)] = select.values[0]
            await interaction.response.send_message(
                name_dict[select.values[0]] + "を選択しました。", ephemeral=True
            )
        else:
            await interaction.response.send_message("選択済みです。", ephemeral=True)


@client.tree.command()
async def draft(interaction: Interaction) -> None:

    # チーム数取得処理
    view_select = SelectTeatNum()
    await interaction.response.send_message(view=view_select, ephemeral=True)

    def check_select(a: Select) -> bool:
        return view_select.values != 0

    try:
        await client.wait_for("message", check=check_select)
    except Exception as e:
        print("select", e)

    # 参加者募集処理
    TEAM_NUM = view_select.values
    PLAYER_LIM = TEAM_NUM * 2
    players: list[Participant] = []

    view_button = View()
    cb = CapButton(players, PLAYER_LIM, style=ButtonStyle.primary)
    pb = PrtcButton(players, PLAYER_LIM, style=ButtonStyle.grey)
    view_button.add_item(cb)
    view_button.add_item(pb)
    message = await interaction.followup.send(
        "現在参加人数: " + str(len(players)), view=view_button, wait=True
    )

    def check_participant_num(a: Interaction) -> bool:
        return len(players) >= PLAYER_LIM

    try:
        await client.wait_for("message", check=check_participant_num)
    except Exception as e:
        print("participant_num", e)

    time.sleep(5)

    cb.disabled = True
    pb.disabled = True
    view_button = view_button.clear_items()
    view_button.add_item(cb)
    view_button.add_item(pb)
    await interaction.followup.edit_message(
        message.id, content="規定人数に到達したため締め切ります。", view=view_button
    )

    # 主将決定処理
    cap_list: list[Participant] = funcs.dec_cap(player_list=players, TEAM_NUM=TEAM_NUM)

    # 主将登録処理（仮）
    teams = [Team(cap_list[i]) for i in range(TEAM_NUM)]

    # 全参加者表示処理（主将と参加者に分けて表示）
    markdown = "# ドラフト参加者\n- 主将\n"
    for cap in cap_list:
        member = interaction.guild.get_member(int(cap.name))
        markdown += "  - " + member.mention + "\n"
    markdown += "- 参加者\n"
    for player in players:
        member = interaction.guild.get_member(int(player.name))
        markdown += "  - " + member.mention + "\n"
    await interaction.followup.send(content=markdown)

    # チーム分け処理
    # ドロップダウンを3回投げて、主将以外の人の入力をIFで無効化する
    for i in range(1):
        view_select = SelectTeatMem(cap_list=cap_list, player_list=players)
        [
            view_select.selectMenu.add_option(
                label=name_dict[player.name],
                value=player.name,
                description="最高XP: " + str(player.max_power()),
            )
            for player in players
        ]

        await interaction.followup.send(str(i + 1) + "週目指名", view=view_select)
        print(list(view_select.cap_selected.values()))

        def check_select_mem(a: Select) -> bool:
            return all(list(view_select.cap_selected.values()))

        try:
            await client.wait_for("message", check=check_select_mem)
        except Exception as e:
            print("select", e)

        # 重複時処理
        dpl_mens = [
            k
            for k, v in collections.Counter(
                list(view_select.cap_selected.values())
            ).items()
            if v > 1
        ]
        dpl_cap: dict[str, list[str]] = {}
        for d_m in dpl_mens:
            dpl_cap[d_m] = []
        for k, v in view_select.cap_selected.items():
            if v in dpl_mens:
                dpl_cap[v].append(k)

        # 確定プレイヤーをチーム振り分け
        for team in teams:
            player = view_select.cap_selected[team.captain.name]
            if player not in dpl_mens:
                team.add_player([p for p in players if p.name == player][0])
                players = [p for p in players if p.name != player]
                await interaction.followup.send(
                    name_dict[team.captain.name]
                    + "が"
                    + name_dict[player]
                    + "を獲得しました。"
                )

        # Todo
        # duplication_menberが空になるまでドラフトに負けている主将にドラフト
        # を要請するドロップダウンメニューを送り続けるwhile文を書く
        while dpl_mens:
            print(dpl_mens)
            for dpl_men in dpl_mens:
                cap_l = dpl_cap[dpl_men]
                if len(cap_l) > 0:
                    print("in if")
                    winner = cap_l[random.randrange(len(cap_l))]
                    for team in teams:
                        if team.captain.name == winner:
                            team.add_player(
                                [p for p in players if p.name == dpl_men][0]
                            )
                            players = [p for p in players if p.name != dpl_men]
                    dpl_mens.remove(dpl_men)
                    dpl_cap[dpl_men].remove(winner)
                    await interaction.followup.send(
                        name_dict[winner]
                        + "が"
                        + name_dict[dpl_men]
                        + "を獲得しました。"
                    )

            dpl_cap_list: list[Participant] = []
            for cap_l in dpl_cap.values():
                c = [cap for cap in cap_list if cap.name in cap_l]
                print(c, cap_l)
                dpl_cap_list += c

            view_select = SelectTeatMem(cap_list=dpl_cap_list, player_list=players)
            [
                view_select.selectMenu.add_option(
                    label=name_dict[player.name],
                    value=player.name,
                    description="最高XP: " + str(player.max_power()),
                )
                for player in players
            ]
            await interaction.followup.send(
                str(i + 1) + "週目2位指名以降", view=view_select
            )

            try:
                await client.wait_for("message", check=check_select_mem)
            except Exception as e:
                print("select", e)

            # 重複時処理
            dpl_mens = [
                k
                for k, v in collections.Counter(
                    list(view_select.cap_selected.values())
                ).items()
                if v > 1
            ]
            dpl_cap.clear()
            for d_m in dpl_mens:
                dpl_cap[d_m] = []
            for k, v in view_select.cap_selected.items():
                if v in dpl_mens:
                    dpl_cap[v].append(k)

            # 確定プレイヤーをチーム振り分け
            for team in teams:
                if team.captain in dpl_cap_list:
                    player = view_select.cap_selected[team.captain.name]
                    if player not in dpl_mens:
                        team.add_player([p for p in players if p.name == player][0])
                        players = [p for p in players if p.name != player]
                        await interaction.followup.send(
                            name_dict[team.captain.name]
                            + "が"
                            + name_dict[player]
                            + "を獲得しました。"
                        )

        # 編成表示処理
        markdown = "### " + str(i + 1) + "週目ドラフト結果\n"
        i = 1
        for team in teams:
            markdown += "- チーム" + str(i) + "\n"
            i += 1
            for player in team.show_member():
                markdown += "  - " + name_dict[player.name] + "\n"

        await interaction.followup.send(content=markdown)

        # teams = funcs.dec_team_rand(player_list=players, teams=teams)

    # 編成表示処理
    markdown = "# チーム分け\n"
    i = 1
    for team in teams:
        markdown += "- チーム" + str(i) + "\n"
        i += 1
        for player in team.show_member():
            member = interaction.guild.get_member(int(player.name))
            markdown += "  - " + member.mention + "\n"

    await interaction.followup.send(content=markdown)


client.run(os.environ.get("discord_TOKEN"))

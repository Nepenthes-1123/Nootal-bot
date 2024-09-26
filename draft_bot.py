import os

import discord
from discord import ButtonStyle, Client, Intents, Interaction, SelectOption, TextStyle
from discord.app_commands import CommandTree
from discord.ui import Button, Modal, Select, TextInput, View
from dotenv import load_dotenv

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
                name_dict[a.id] = a.nick if a.nick is not None else a.name


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
        options=[SelectOption(value=int(i), label=int(i)) for i in range(2, 9)],
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
                    name=name_dict[interaction.user.id],
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

    async def callback(self, interaction: Interaction) -> None:
        if not name_dict[interaction.user.id] in [p.name for p in self.player_list]:
            modal = GetPower("各ルールのXPを入力してください。", self.player_list, True)
            await interaction.response.send_modal(modal)

            while modal.is_finished():
                pass

            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content="現在参加人数: " + str(len(self.player_list)),
            )
            await interaction.followup.send("主将を選択しました。", ephemeral=True)
        else:
            await interaction.response.edit_message(
                content="現在参加人数: " + str(len(self.player_list)),
            )
            await interaction.followup.send("すでに参加しています。", ephemeral=True)


class PrtcButton(Button):
    def __init__(
        self,
        player: list[Participant],
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

    async def callback(self, interaction: Interaction) -> None:
        if not name_dict[interaction.user.id] in [p.name for p in self.player_list]:
            modal = GetPower(
                "各ルールのXPを入力してください。", self.player_list, False
            )
            await interaction.response.send_modal(modal)

            while modal.is_finished():
                pass

            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content="現在参加人数: " + str(len(self.player_list)),
            )
            await interaction.followup.send("参加者を選択しました。", ephemeral=True)
        else:
            await interaction.response.edit_message(
                content="現在参加人数: " + str(len(self.player_list)),
            )
            await interaction.followup.send("すでに参加しています。", ephemeral=True)


@client.tree.command()
async def draft(interaction: Interaction) -> None:

    view_select = SelectTeatNum()

    await interaction.response.send_message(view=view_select, ephemeral=True)

    def check_select(a: Select) -> bool:
        return view_select.values != 0

    try:
        await client.wait_for("message", check=check_select)
    except Exception as e:
        print("select", e)

    TEAM_NUM = view_select.values
    PLAYER_LIM = TEAM_NUM * 4
    players: list[Participant] = []

    view_button = View()
    cb = CapButton(players, style=ButtonStyle.primary)
    pb = PrtcButton(players, style=ButtonStyle.grey)
    view_button.add_item(cb)
    view_button.add_item(pb)

    message = await interaction.followup.send(
        "現在参加人数: " + str(len(players)), view=view_button, wait=True
    )

    def check_participant_num(a: Interaction) -> bool:
        return len(players) >= 1

    try:
        await client.wait_for("message", check=check_participant_num)
    except Exception as e:
        print("participant_num", e)

    cb.disabled = True
    pb.disabled = True
    view_button = view_button.clear_items()
    view_button.add_item(cb)
    view_button.add_item(pb)
    await interaction.followup.edit_message(
        message.id, content="規定人数に到達したため締め切ります。", view=view_button
    )

    # 主将決定処理

    # 主将登録処理（仮）
    teams = [Team(players[0])] * TEAM_NUM

    # チーム分け処理

    # 編成表示処理
    markdown = "# チーム分け\n"
    i = 1
    for team in teams:
        markdown += "- チーム" + str(i) + "\n"
        i += 1
        for player in team.show_member():
            markdown += "  - " + player + "\n"

    await interaction.followup.send(content=markdown)


client.run(os.environ.get("discord_TOKEN"))

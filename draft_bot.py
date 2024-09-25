import discord
import os
from discord import ButtonStyle, Client, Intents, Interaction, SelectOption, TextStyle
from discord.app_commands import CommandTree
from discord.ui import Button, Select, View, Modal, TextInput

from os.path import join, dirname
from discord.utils import MISSING
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
    def __init__(self, title: str) -> None:
        super().__init__(title=title)

        self.zones = TextInput(
            label="ガチエリア",
            style=TextStyle.short,
            placeholder="2000",
            required=True
        )
        self.add_item(self.zones)
        self.tower = TextInput(
            label="ガチヤグラ",
            style=TextStyle.short,
            placeholder="2000",
            required=True
        )
        self.add_item(self.tower)
        self.rainmaker = TextInput(
            label="ガチホコ",
            style=TextStyle.short,
            placeholder="2000",
            required=True
        )
        self.add_item(self.rainmaker)
        self.clam = TextInput(
            label="ガチアサリ",
            style=TextStyle.short,
            placeholder="2000",
            required=True
        )
        self.add_item(self.clam)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.send_message("入力ありがとうございました。", ephemeral=True)

    async def on_error(self) -> None:
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
            modal = GetPower("各ルールのXPを入力してください。")
            try:
                await interaction.response.send_modal(modal)
            except Exception as e:
                print(e)
            try:
                await client.wait_for("message", check=modal.is_finished())
            except Exception as e:
                print("CapButton: ", e)
            await interaction.followup.edit_message(
                message_id=interaction.message.id ,content="現在参加人数: " + str(len(self.player_list)),
            )
            await interaction.followup.send("主将を選択しました。", ephemeral=True)
            self.player_list.append(
                Participant(
                    name=name_dict[interaction.user.id],
                    captain=True,
                    zones_pw=modal.zones.value,
                    tower_pw=modal.tower.value,
                    rainmaker_pw=modal.rainmaker.value,
                    clam_pw=modal.clam.value,
                )
            )
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
            modal = GetPower("各ルールのXPを入力してください。")
            await interaction.response.send_modal(modal)
            try:
                await client.wait_for("message", check=modal.is_finished())
            except Exception as e:
                print("PrtcButton: ", e)
            await interaction.followup.edit_message(
                message_id=interaction.message.id, content="現在参加人数: " + str(len(self.player_list)),
            )
            await interaction.followup.send("参加者を選択しました。", ephemeral=True)
            self.player_list.append(
                Participant(
                    name=name_dict[interaction.user.id],
                    captain=False,
                    zones_pw=modal.zones.value,
                    tower_pw=modal.tower.value,
                    rainmaker_pw=modal.rainmaker.value,
                    clam_pw=modal.clam.value,
                )
            )
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
    teams = [Team] * TEAM_NUM
    players: list[Participant] = []

    view_button = View()
    view_button.add_item(CapButton(players, style=ButtonStyle.primary))
    view_button.add_item(PrtcButton(players, style=ButtonStyle.grey))

    await interaction.followup.send(
        "現在参加人数: " + str(len(players)), view=view_button
    )

    def check_participant_num(a: Interaction) -> bool:
        return len(players) >= PLAYER_LIM

    try:
        await client.wait_for("message", check=check_participant_num)
    except Exception as e:
        print("participant_num", e)



    # await interaction.followup.send()


client.run(os.environ.get("discord_TOKEN"))

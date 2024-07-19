from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, RichLog, Button, Footer, Label, Markdown
from textual.widget import Widget
from textual.screen import Screen
from textual.reactive import reactive
from textual.css.query import DOMQuery
from textual.binding import Binding
from typing import TYPE_CHECKING, cast



class ChatDial(Widget):
    def compose(self) -> ComposeResult:
        yield Vertical(
            RichLog(classes="richlog_widget"),
            Input(placeholder="Enter chat", classes="input_widget"),
            classes="vertical_layout"
        )

    @on(Input.Submitted)
    def input_submitted_handler(self, event: Input.Submitted):
        log = self.query_one(RichLog)
        log.write(f"1: {event.value}")
        input = self.query_one(Input)
        input.value = ""

class GameHeader(Widget):
    turn = reactive(0)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.app.title, id="app-title")
            yield Label(id="moves")
            yield Label(self.app.version, id="version")
            yield Label(id="turn-player")

    def watch_turn(self, turn: int):
        player = "흑" if turn % 2 == 0 else "백"
        self.query_one("#turn-player", Label).update(f"현재 차례: {player}")
        self.query_one("#moves", Label).update(f"턴 수: {turn}")


class GameCell(Button):

    @staticmethod
    def at(row: int, col: int) -> str:
        return f"cell-{row}-{col}"

    def __init__(self, row: int, col: int, theme = 0) -> None:
        super().__init__("", id=self.at(row, col))
        self.row = row
        self.col = col
        self.label = ""
        if theme == 0:
            self.toggle_class("vkey")
        else:
            self.toggle_class("hkey")


class GameGrid(Widget):
    """The main playable grid of game cells."""

    def compose(self) -> ComposeResult:
        for row in range(Game.SIZE):
            for col in range(Game.SIZE):
                yield GameCell(row, col, (row + col) % 2)


class Game(Screen):

    SIZE = 20

    def compose(self) -> ComposeResult:
        yield GameHeader()
        yield Footer()
        yield Horizontal(
            GameGrid(),
            ChatDial()
        )

    BINDINGS = [
            Binding("n", "new_game", "새 게임"),]
    
    @property
    def filled_cells0(self) -> DOMQuery[GameCell]:
        """DOMQuery[GameCell]: The collection of cells that are currently turned on."""
        return cast(DOMQuery[GameCell], self.query("GameCell.filled-turn0"))
    
    @property
    def filled_cells1(self) -> DOMQuery[GameCell]:
        return cast(DOMQuery[GameCell], self.query("GameCell.filled-turn1"))
    
    def cell(self, row: int, col: int) -> GameCell:
        """Get the cell at a given location.

        Args:
            row (int): The row of the cell to get.
            col (int): The column of the cell to get.

        Returns:
            GameCell: The cell at that location.
        """
        return self.query_one(f"#{GameCell.at(row,col)}", GameCell)
    
    def toggle_cell(self, row: int, col: int) -> None:
        if 0 <= row <= (self.SIZE - 1) and 0 <= col <= (self.SIZE - 1):
            if self.query_one(GameHeader).turn % 2 == 0:
                self.cell(row, col).toggle_class("filled-turn0")
                # self.cell(row, col).label = "●"
            elif self.query_one(GameHeader).turn % 2 != 0:
                self.cell(row, col).toggle_class("filled-turn1")
                # self.cell(row, col).label = "○"

    def make_move_on(self, cell: GameCell) -> None:
        self.toggle_cell(cell.row, cell.col)
        self.query_one(GameHeader).turn += 1

    def on_button_pressed(self, event: GameCell.Pressed) -> None:
        """버튼을 눌렀을 때 
        
        Args:
            event 
            turn: 현재 턴플레이어
        """
        self.make_move_on(cast(GameCell, event.button))
    
    def action_new_game(self) -> None:
        """Start a new game."""
        self.filled_cells0.remove_class("filled-turn0")
        self.filled_cells1.remove_class("filled-turn1")


    def on_mount(self) -> None:
        """시작 시 새 게임"""
        self.action_new_game()

class Omok(App):
    TITLE = "□사각오목■"
    CSS_PATH = "Omok.css"
    version = 'beta 1'

    def on_mount(self) -> None:
        """Set up the application on startup."""
        self.push_screen(Game())

    """메인 앱 클래스"""

    # BINDINGS = [("ctrl+d")]


if __name__ == "__main__":
    Omok().run()

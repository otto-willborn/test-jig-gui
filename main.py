# main.py — Textual TUI: two jigs, 3 stages each, with input support for prompts

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Static, RichLog, Button, Input
from textual import work

from runner import StageRunner
from stages import STAGES
import config

STATUS_ICONS = {
    "pending": "○",
    "running": "◐",
    "passed": "✓",
    "failed": "✗",
}

STATUS_CLASSES = {
    "pending": "status-pending",
    "running": "status-running",
    "passed": "status-passed",
    "failed": "status-failed",
}


class StagePanel(Vertical):
    """One card: title + Run button + live log + input/continue for prompts."""

    def __init__(self, jig_id: str, stage: dict):
        super().__init__(id=f"panel-{jig_id}-{stage['id']}", classes="stage-panel")
        self.jig_id = jig_id
        self.stage = stage
        self.channel = None  # active paramiko channel, set while running

    def compose(self) -> ComposeResult:
        with Horizontal(classes="stage-header"):
            yield Static(
                f"{STATUS_ICONS['pending']} {self.stage['name']}",
                id=f"title-{self.jig_id}-{self.stage['id']}",
                classes="stage-title status-pending",
            )
            yield Button("Run", id=f"run-{self.jig_id}-{self.stage['id']}", variant="primary")
        yield RichLog(id=f"log-{self.jig_id}-{self.stage['id']}", max_lines=200, wrap=True)
        with Horizontal(classes="stage-input-row"):
            yield Input(placeholder="Response...", id=f"input-{self.jig_id}-{self.stage['id']}")
            yield Button("Continue", id=f"continue-{self.jig_id}-{self.stage['id']}", variant="success")

    def set_status(self, status: str) -> None:
        title = self.query_one(f"#title-{self.jig_id}-{self.stage['id']}", Static)
        title.update(f"{STATUS_ICONS[status]} {self.stage['name']}")
        for cls in STATUS_CLASSES.values():
            title.remove_class(cls)
        title.add_class(STATUS_CLASSES[status])


class JigColumn(Vertical):
    """One jig: header + its 3 stage panels."""

    def __init__(self, jig: dict):
        super().__init__(id=f"jig-{jig['id']}", classes="jig-column")
        self.jig = jig

    def compose(self) -> ComposeResult:
        yield Static(self.jig["name"], classes="jig-title")
        yield Static("Connecting...", id=f"conn-status-{self.jig['id']}", classes="conn-status")
        for stage in STAGES:
            yield StagePanel(self.jig["id"], stage)


class DashboardApp(App):
    CSS_PATH = "dashboard.tcss"
    TITLE = "Multi-Jig Test Suite"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="jig-row"):
            for jig in config.JIGS:
                yield JigColumn(jig)
        yield Footer()

    def on_mount(self) -> None:
        self.runners = {}
        for jig in config.JIGS:
            runner = StageRunner(
                host=jig["host"], user=jig["user"], key_path=jig["key_path"],
                password=jig["password"], port=jig["port"],
            )
            self.runners[jig["id"]] = runner
            self.connect_to_jig(jig)

    @work(thread=True)
    def connect_to_jig(self, jig: dict) -> None:
        runner = self.runners[jig["id"]]
        conn_status = self.query_one(f"#conn-status-{jig['id']}", Static)
        try:
            runner.connect()
            self.call_from_thread(conn_status.update, f"[green]Connected — {jig['host']}[/]")
        except Exception as e:
            self.call_from_thread(conn_status.update, f"[red]Connection failed: {e}[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id.startswith("run-"):
            _, jig_id, stage_id = button_id.split("-", 2)
            stage = next(s for s in STAGES if s["id"] == stage_id)
            self.run_stage(jig_id, stage)
        elif button_id.startswith("continue-"):
            _, jig_id, stage_id = button_id.split("-", 2)
            self.send_input(jig_id, stage_id)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Enter key in the input field does the same as clicking Continue
        input_id = event.input.id  # input-{jig_id}-{stage_id}
        _, jig_id, stage_id = input_id.split("-", 2)
        self.send_input(jig_id, stage_id)

    def send_input(self, jig_id: str, stage_id: str) -> None:
        panel = self.query_one(f"#panel-{jig_id}-{stage_id}", StagePanel)
        input_field = self.query_one(f"#input-{jig_id}-{stage_id}", Input)

        if panel.channel is None:
            self.notify("No active process waiting for input.", severity="warning")
            return

        text = input_field.value
        panel.channel.send(text + "\n")  # blank input just sends Enter (accepts default)
        input_field.value = ""

    @work(thread=True)
    def run_stage(self, jig_id: str, stage: dict) -> None:
        runner = self.runners[jig_id]
        panel = self.query_one(f"#panel-{jig_id}-{stage['id']}", StagePanel)
        log = panel.query_one(RichLog)
        run_button = panel.query_one(f"#run-{jig_id}-{stage['id']}", Button)

        self.call_from_thread(setattr, run_button, "disabled", True)
        self.call_from_thread(panel.set_status, "running")
        self.call_from_thread(log.clear)

        exit_code = None
        for kind, payload in runner.run_stage(stage["command"]):
            if kind == "channel":
                self.call_from_thread(setattr, panel, "channel", payload)
            elif kind == "line":
                self.call_from_thread(log.write, payload)
            elif kind == "done":
                exit_code = payload

        self.call_from_thread(setattr, panel, "channel", None)
        self.call_from_thread(panel.set_status, "passed" if exit_code == 0 else "failed")
        self.call_from_thread(setattr, run_button, "disabled", False)


if __name__ == "__main__":
    app = DashboardApp()
    app.run()
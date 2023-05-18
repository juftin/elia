import os
from pathlib import Path
from typing import NamedTuple

import openai
from textual import on, log
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Input, Footer

from elia_chat.widgets.agent_is_typing import AgentIsTyping
from elia_chat.widgets.conversation import Conversation
from elia_chat.widgets.conversation_header import ConversationHeader
from elia_chat.widgets.conversation_options import ModelPanel, ModelSet


class ConversationScreen(Screen):
    BINDINGS = [
        Binding(key="ctrl+k", action="focus('chat-input')", description="Focus Input"),
    ]

    def compose(self) -> ComposeResult:
        yield Conversation()
        yield Input(placeholder="[Ctrl+K] Enter your message here...", id="chat-input")
        yield AgentIsTyping()
        yield Footer()

    @on(Input.Submitted, "#chat-input")
    def submit_message(self, event: Input.Submitted) -> None:
        user_message = event.value
        event.input.value = ""
        conversation = self.query_one(Conversation)
        conversation.new_user_message(user_message)

    @on(Conversation.AgentResponseStarted)
    def start_awaiting_response(self) -> None:
        agent_is_typing = self.query_one(AgentIsTyping)
        agent_is_typing.display = "block"

    @on(Conversation.AgentResponseComplete)
    def finish_awaiting_response(self) -> None:
        agent_is_typing = self.query_one(AgentIsTyping)
        agent_is_typing.display = "none"

    @on(ModelSet.Selected)
    def update_model(self, event: ModelPanel.Selected) -> None:
        model = event.model

        try:
            conversation_header = self.query_one(ConversationHeader)
        except NoMatches:
            log.error("Couldn't find ConversationHeader to update model name.")
        else:
            conversation_header.update_model(model)

        try:
            conversation = self.query_one(Conversation)
        except NoMatches:
            log.error("Couldn't find the Conversation")
        else:
            conversation.chosen_model = model


class Elia(App):
    CSS_PATH = Path(__file__).parent / "elia.scss"

    def __init__(self):
        super().__init__()
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def on_mount(self) -> None:
        self.push_screen(ConversationScreen())


app = Elia()


def run():
    app.run()


if __name__ == "__main__":
    app.run()

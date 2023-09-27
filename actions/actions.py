# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import ReminderScheduled, ReminderCancelled

import requests


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Get user message from Rasa tracker
        user_message = tracker.latest_message.get("text")
        print("latest user message:", user_message)

        # def get_chatgpt_response(self, message):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "Act as a customer support representative. Answer the question as truthfully as possible using the provided text, and if the answer is not contained within the text below, truthfully say ```I need to check that and get back to you```. \n Context: ```- The store currently sells different toy brands, such as Barbie, Fisher Price, and many more. - Keimen Kids deliver across the whole of Bangkok. - There are 2 subscription plans, that gives you coins, that can be utilized to rent out toys.````",
                },
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 100,
        }
        response = requests.post(url, headers=headers, json=data)
        # response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            chatgpt_response = response.json()
            print("chatgpt_response:", chatgpt_response)
            message = chatgpt_response["choices"][0]["message"]["content"]
            print("message:", message)
            dispatcher.utter_message(template="utter_message", message=str(message))
        else:
            # Handle error
            return "Sorry, I couldn't generate a response at the moment. Please try again later."

            # Revert user message which led to fallback.
        return [UserUtteranceReverted()]


class ActionSayShirtSize(Action):
    def name(self) -> Text:
        return "action_say_shirt_size"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        shirt_size = tracker.get_slot("shirt_size")
        if not shirt_size:
            dispatcher.utter_message(text="I don't know your shirt size.")
        else:
            dispatcher.utter_message(text=f"Your shirt size is {shirt_size}!")
        return []


class ActionSetReminder(Action):
    """Schedules a reminder, supplied with the last message's entities."""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("I will remind you in 5 seconds.")

        date = datetime.datetime.now() + datetime.timedelta(seconds=5)
        entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            entities=entities,
            name="my_reminder",
            kill_on_user_message=False,
        )

        return [reminder]


class ActionReactToReminder(Action):
    """Reminds the user to call someone."""

    def name(self) -> Text:
        return "action_react_to_reminder"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # name = next(tracker.get_slot("PERSON"), "someone")
        # dispatcher.utter_message(f"Remember to call {name}!")

        name = tracker.get_slot("PERSON")
        print("name extracted:", name)
        if not name:
            dispatcher.utter_message(text="You wanted to call someone?")
        else:
            dispatcher.utter_message(text=f"Remember to call {name}!")

        return []


class ActionTellID(Action):
    """Informs the user about the conversation ID."""

    def name(self) -> Text:
        return "action_tell_id"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        conversation_id = tracker.sender_id

        dispatcher.utter_message(f"The ID of this conversation is '{conversation_id}'.")
        dispatcher.utter_message(
            f"Trigger an intent with: \n"
            f'curl -H "Content-Type: application/json" '
            f'-X POST -d \'{{"name": "EXTERNAL_dry_plant", '
            f'"entities": {{"plant": "Orchid"}}}}\' '
            f'"http://localhost:5005/conversations/{conversation_id}'
            f'/trigger_intent?output_channel=latest"'
        )

        return []


class ActionWarnDry(Action):
    """Informs the user that a plant needs water."""

    def name(self) -> Text:
        return "action_warn_dry"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        plant = next(tracker.get_latest_entity_values("plant"), "someone")
        dispatcher.utter_message(f"Your {plant} needs some water!")

        return []


class ForgetReminders(Action):
    """Cancels all reminders."""

    def name(self) -> Text:
        return "action_forget_reminders"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("Okay, I'll cancel all your reminders.")

        # Cancel all reminders
        return [ReminderCancelled()]

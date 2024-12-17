# Example: reuse your existing OpenAI setup
from openai import OpenAI
import subprocess
import time
import argparse
import os


from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage


def tail_file(filepath):
    while True:
        process = subprocess.Popen(
            ["tail", "-F", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            assert process.stdout is not None
            for line in iter(process.stdout.readline, ""):
                yield line
        except KeyboardInterrupt:
            process.terminate()
            raise
        except Exception:
            print("exception tailing")
            time.sleep(0.5)


def make_message(role: str, content: str) -> ChatCompletionMessageParam:
    match role:
        case "system":
            return ChatCompletionSystemMessageParam(role="system", content=content)
        case "user":
            return ChatCompletionUserMessageParam(role="user", content=content)
    raise Exception()


def make_system_message(content: str) -> ChatCompletionMessageParam:
    return ChatCompletionSystemMessageParam(role="system", content=content)


def make_user_message(name: str, content: str) -> ChatCompletionMessageParam:
    return ChatCompletionUserMessageParam(role="user", name=name, content=content)


def make_assistant_message(name: str, content: str) -> ChatCompletionMessageParam:
    return ChatCompletionAssistantMessageParam(
        name=name, role="assistant", content=content
    )


def get_next(
    system_prompt: ChatCompletionMessageParam,
    conversation: list[ChatCompletionMessageParam],
) -> ChatCompletionMessage:
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    completion = client.chat.completions.create(
        model="llama-3.2-3b-instruct",
        messages=[system_prompt, *conversation],
        temperature=0.8,
    )

    new_message = completion.choices[0].message
    return new_message


def speak(text: str, voice: str):
    subprocess.call(["say", "-v", voice, text])


def load_system_prompt(
    character_directory: str, own_name: str, other_name: str
) -> ChatCompletionMessageParam:
    name_prefix = f"Your name is {own_name}."
    my_character_path = os.path.join(character_directory, f"{own_name}.character.txt")
    with open(my_character_path, "r") as f:
        self_description = " ".join(f.readlines())

    # todo: send description of other to an llm to change from first to third person
    context_about_other = f"You are chatting with {other_name}."
    return make_system_message(
        f"{name_prefix} {self_description} {context_about_other}"
    )


def chat(
    name: str,
    voice: str,
    other: str,
    chat_directory: str,
    character_directory: str,
    start: bool,
):
    time.sleep(5)
    my_file_path = os.path.join(chat_directory, f"{name}.txt")
    other_file_path = os.path.join(chat_directory, f"{other}.txt")
    my_system_prompt = load_system_prompt(
        own_name=name, other_name=other, character_directory=character_directory
    )
    print(f"Running as {name} talking to {other}.")
    with open(my_file_path, "w") as my_file:
        other_response = tail_file(other_file_path)

        conversation = []
        if start:
            print("starting the conversation")
            my_file.writelines(["Hi"])
            my_file.flush()
            conversation.append(make_assistant_message(name, "Hi"))
            print("Waiting for first reply...")
            other_reply = next(other_response)
            conversation.append(make_user_message(other, "other_reply"))

        while True:
            print(f"Generating message...")
            my_message = get_next(my_system_prompt, conversation)
            content = my_message.content
            assert content is not None
            content = f'{content.replace(os.linesep, "")}{os.linesep}'
            print(content)
            speak(content, voice=voice)
            conversation.append(make_assistant_message(name, content))
            my_file.writelines([content])
            my_file.flush()
            print(f"Waiting for {other} to reply...")
            other_reply = next(other_response)
            conversation.append(make_user_message(other, other_reply))


def main():
    parser = argparse.ArgumentParser(description="Parse chat parameters.")
    parser.add_argument("--name", type=str, required=True, help="This persons name")
    parser.add_argument(
        "--voice",
        type=str,
        required=True,
        help="This persons voice name (as recognised by say)",
    )
    parser.add_argument(
        "--other", type=str, required=True, help="The other persons name"
    )
    parser.add_argument(
        "--chat-directory", type=str, required=True, help="The chat output directory"
    )
    parser.add_argument(
        "--character-directory",
        default="./characters",
        type=str,
        required=False,
        help="The directory containing character descriptions",
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Boolean flag to indicate whether this party starts the conversation",
    )

    args = parser.parse_args()

    chat(
        name=args.name,
        voice=args.voice,
        other=args.other,
        chat_directory=args.chat_directory,
        character_directory=args.character_directory,
        start=args.start,
    )
    # Point to the local server


if __name__ == "__main__":
    main()

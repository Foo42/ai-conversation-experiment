# LLM Conversation Experiment

Fun experiment to play around with simulating my two kids ~~arguing~~ conversing with each other.

Expects:
- An OpenAI flavoured api at `http://localhost:1234/v1` (I'm using LM Studio to host).
- The llama-3.2-3b-instruct model to be available at that endpoint (nothing special about this, it's just what I had)
- A directory with character descriptions with file names like `{name}.character.txt`

## How to run
Run two instances pointing to opposite characters (alice, and bob in the below) with one selected as the initiator via the `--start` flag

Runs the alice agent (Using a description in `./characters/alice.character.txt`):
`uv run hello.py --name alice --start --voice Moira --other bob  --chat-directory /tmp/chat1`

Runs the bob agent (Using a description in `./characters/bob.character.txt`):
`uv run hello.py --name bob --voice Daniel --other alice  --chat-directory /tmp/chat1`

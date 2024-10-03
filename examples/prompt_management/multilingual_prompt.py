import argparse

import base64

from five9 import five9_session


# function to take a wav file and convert to base64
def convert_audio_to_base64(filename):
    with open(filename, "rb") as audio_file:
        audio_content = audio_file.read()
    return base64.b64encode(audio_content).decode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="uploads prompt audio")

    parser.add_argument(
        "--filename",
        metavar="filename",
        type=str,
        required=True,
        help="filename of the prompt audio",
    )

    parser.add_argument(
        "--hostalias",
        type=str,
        default="us",
        help="Five9 host alias (us, ca, eu, frk, in)",
    )
    parser.add_argument(
        "--language_code",
        metavar="language_code",
        type=str,
        required=True,
        help="language code for the prompt audio",
    )

    args = parser.parse_args()

    prompt_name = args["name"] or "QRL"
    filename = args["filename"] or "QRL.wav"
    language_code = args["language_code"] or "en-US"

    encoded_audio = convert_audio_to_base64(filename)

    client = five9_session.Five9Client(api_hostname_alias=args.hostalias)

    prompt = {"name": prompt_name, "languages": [language_code]}

    r = client.service.modifyPromptWavInline(prompt=prompt, wavFile=encoded_audio)

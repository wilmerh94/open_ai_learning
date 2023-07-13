import os
import argparse
import openai
from dotenv import dotenv_values, load_dotenv

config = dotenv_values(".env")
openai.api_key = config["OPENAI_API_KEY"]


def main():
    """
    Purpose: on this function we will create the arguments pass on shell to the chatbot GPT
    """

    # end def
    parser = argparse.ArgumentParser(description="Simple command line chatbot with GPT")
    parser.add_argument(
        "--personality",
        type=str,
        help="A brief summary of the chatbot`s personality",
        default="friendly and helpful chatbot",
    )
    parser.add_argument(
        "-envfile",
        type=str,
        default=".env",
        required=False,
        help="A dotenv file with your environment variables: 'OPENAI_API_KEY'",
    )
    args = parser.parse_args()
    load_dotenv(args.envfile)
    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError(
            "error: missing API KEY from environment. please check your file"
        )
    openai.api_key = os.environ["OPENAI_API_KEY"]
    initial_prompt = "you are a conversational chatbot"
    if personality := args.personality:
        # comment:
        initial_prompt += f"Your personality is : {personality}"
    else:
        # comment:
        initial_prompt += "Your personality is : helpful and friendly"
    # end if
    messages = [{"role": "system", "content": initial_prompt}]
    while True:
        try:
            user_input = input("You:")
            messages.append({"role": "user", "content": user_input})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )
            messages.append(response["choices"][0]["message"].to_dict())
            print(response["choices"][0]["message"]["content"])
        except KeyboardInterrupt:
            print("Exiting...")
            break
    print(messages)


if __name__ == "__main__":
    main()

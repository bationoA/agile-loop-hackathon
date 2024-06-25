import json
import os

import requests
import yaml
from requests import Response


class ChatModel:
    config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
    _scenarios_list = config["SCENARIOS_LIST"]
    os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
    os.environ["OPENAI_MODEL"] = config["OPENAI_MODEL"]
    del config

    _url = "https://api.openai.com/v1/chat/completions"
    _headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    def __init__(self, user_content: str | list = "", prompt: str | None = None, model: str = os.environ["OPENAI_MODEL"]):
        self.user_content = user_content
        self.prompt = prompt
        self.model = model

    @property
    def url(self) -> str:
        return self._url

    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def context_message(self) -> list:
        return self.context_message

    def get_response(self) -> Response | None:  # str | None:
        if self.user_content == "":
            print("Error: Please provide `user_content`")
            return None

        # if self.prompt is not None:
        #     self.user_content = self.prompt + self.user_content

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.prompt
                },
                {
                    "role": "user",
                    "content": self.user_content
                }
            ],
            "temperature": 0
        }
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        else:
            print("Error:", response.status_code)
            print(response.json())

        return None


class ScenarioSelector:
    config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
    _scenarios_list = config["SCENARIOS_LIST"]
    del config

    # Context message
    _context_message_template = {
        "role": "system",
        "content": """You are a useful plateforme identifier. 
        You have access to a list of plateformes. Never give the name of a plateforme that is not in that list.
        When a user provide a request, you always identify the unique plateforme associated to that request.
        
        
        Here is the list of plateformes you should always use:
        {plateformes_list}
        
        Your answer should always given as a list. Follow the below examples:
         {examples}
         
         If you are unable to identify the plateforme from the list then return ["None"].
         
         identify the plateforme associated to the below query:
         
         
        """
    }

    def __init__(self, user_content: str, image_size: str = "1024x1024", quality: str = "standard"):
        self.user_content = user_content
        self.image_size = image_size
        self.quality = quality

    @property
    def context_message_template(self) -> dict:
        return self._context_message_template

    @property
    def scenarios_list(self) -> list:
        return self._scenarios_list

    def extract_user_queries_from_api_selector_text(self) -> list[dict]:
        """
        :return: list of [[scenario: query], ...]
        """
        scenarios_queries = []
        for scenario in self.scenarios_list:
            # Write the updated content back to the file
            with open(os.path.join("icl_examples", "api_selector", f"{scenario}_base.txt"), 'r') as file:
                lines = file.readlines()
            no_print = True
            for line in lines:
                if "User query:" in line:
                    query = line.replace("User query:", "")
                    query = query.strip()
                    # query = query.removeprefix('"').removesuffix('"')

                    scenarios_queries.append(
                        {scenario: query}
                    )
        return scenarios_queries

    def get_examples(self) -> list[dict]:
        examples = []
        scenarios_queries = self.extract_user_queries_from_api_selector_text()

        for scenario_query in scenarios_queries:
            scenario = list(scenario_query.keys())[0]
            query = scenario_query[scenario]
            example = [
                {"role": "user", "content": query},
                {"role": "assistant", "content": f'["{scenario}"]'},
            ]
            examples += example
        print(f"examples: {examples}")
        return examples

    def get_response(self) -> str | None:
        if self.user_content == "":
            print("Error: Please provide `user_content`")
            return None

        context_message = self.context_message_template.copy()
        context_message["content"] = context_message["content"]. \
            replace("{plateformes_list}", json.dumps(self.scenarios_list)). \
            replace("{examples}", json.dumps(self.get_examples()))

        messages = [context_message] + self.get_examples() + [{"role": "user", "content": self.user_content}]

        llm = ChatModel(user_content=messages)
        identified_scenario = llm.get_response()

        return json.loads(identified_scenario)[0]


class Dalle3Model:
    config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
    os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
    del config

    _url = "https://api.openai.com/v1/images/generations"
    _headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }
    _prompt = "You are Facebook content creator. you always generate an image captivating social image based " \
              "on a text provided by the user. generate a social media image for a Facebook post based on the" \
              " below text. \n"

    def __init__(self, user_content: str, image_size: str = "1024x1024", quality: str = "standard"):
        self.user_content = user_content
        self.image_size = image_size
        self.quality = quality

    @property
    def url(self) -> str:
        return self._url

    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def prompt(self) -> str:
        return self._prompt

    def get_images_url(self) -> str | None:
        if self.prompt == "" and self.user_content == "":
            print("Error: Please provide `prompt` and/or `user_content`")
            return None

        data = {
            "model": "dall-e-3",
            "prompt": self.prompt + self.user_content,
            "size": self.image_size,
            "quality": self.quality,
            "n": 1
        }
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            return response_data['data'][0]['url']
        else:
            print("Error in generating image. Error code:", response.status_code)
            print(response.json())

        return None

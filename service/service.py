import base64

import requests

from custom_package import include_board_id_in_query
from custom_package.llm import ScenarioSelector
from helper import *
import mysql.connector
import random
import os
from dotenv import load_dotenv


logger = logging.getLogger()


def run(query: str, scenario: str):
    config = yaml.load(open("config.yaml", "r"), Loader=yaml.FullLoader)
    os.environ["OPENAI_MODEL"] = config["OPENAI_MODEL"]  # TODO: We added this line
    os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

    logging.basicConfig(
        format="%(message)s",
        handlers=[logging.StreamHandler(ColorPrint())],
    )
    logger.setLevel(logging.INFO)

    # scenario_selector = ScenarioSelector(user_content=query)
    #
    # scenario = scenario_selector.get_response()

    # scenario = input(
    #     "Please select a scenario (facebook/trello/jira/salesforce): "
    # )
    # scenario = "clockify"

    scenario = scenario.lower()
    api_spec, headers = None, None

    # database connection details
    db_config = {
        'host': 'localhost',
        'port': 3333,
        'database': 'synapse-copilot',
        'user': 'root',
        # 'password': '123456',
    }

    # Connect to the MySQL server
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    user_id = 1
    # user_id = int(input("Enter the user id: "))

    # query = input(
    #     "Please input an instruction (Press ENTER to use the example instruction): "
    # )

    if scenario == "tmdb":
        os.environ["TMDB_ACCESS_TOKEN"] = config["tmdb_access_token"]
        api_spec, headers = process_spec_file(
            file_path="specs/tmdb_oas.json", token=os.environ["TMDB_ACCESS_TOKEN"]
        )
        query_example = "Give me the number of movies directed by Sofia Coppola"

    elif scenario == "spotify":
        os.environ["SPOTIPY_CLIENT_ID"] = config["spotipy_client_id"]
        os.environ["SPOTIPY_CLIENT_SECRET"] = config["spotipy_client_secret"]
        os.environ["SPOTIPY_REDIRECT_URI"] = config["spotipy_redirect_uri"]

        api_spec, headers = process_spec_file(file_path="specs/spotify_oas.json")

        query_example = "Add Summertime Sadness by Lana Del Rey in my first playlist"

    elif scenario == "discord":
        os.environ["DISCORD_CLIENT_ID"] = config["discord_client_id"]

        api_spec, headers = process_spec_file(
            file_path="specs/discord_oas.json", token=os.environ["DISCORD_CLIENT_ID"]
        )
        query_example = "List all of my connections"

    elif scenario == "stable":
        api_spec, headers = process_spec_file(
            file_path="specs/stablediffiusion_oas.json", token=os.environ["API_KEY"]
        )
        query_example = "Create cat image"

    elif scenario == "calendar":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                res_t = res[1]
                print(f"your token {res_t}")
                os.environ["GOOGLE_TOKEN"] = res_t
                dic = {
                    "user_id": user_id,
                    "your_token": res_t
                }
                print(dic)
            except:
                print("Key is not present in the database")
                return ""

        else:
            print("Your id is incorrect.")

        api_spec, headers = process_spec_file(
            file_path="specs/calendar_oas.json", token=os.environ["GOOGLE_TOKEN"]
        )
        query_example = "What events do I have today?"

    elif scenario == "sheets":
        os.environ["GOOGLE_TOKEN"] = config["google_token"]

        api_spec, headers = process_spec_file(
            file_path="specs/sheets_oas.json", token=os.environ["GOOGLE_TOKEN"]
        )
        query_example = 'Create a new Spreadsheet with title: "Exercise Logs". Print the complete api response result as it is.'

    elif scenario == "notion":
        os.environ["NOTION_KEY"] = config["NOTION_KEY"]
        query_example = "Get me my page on notion"

    elif scenario == "upclick":
        os.environ["UPCLICK_KEY"] = config["UPCLICK_KEY"]

        api_spec, headers = process_spec_file(
            file_path="specs/upclick_oas.json", token=os.environ["UPCLICK_KEY"]
        )

        headers["Content-Type"] = "application/json"
        query_example = "Get me my spaces of team on upclick"

    elif scenario == "jira":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM jira_credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                token = res[1]
                host = res[2]
                username = res[3]

                print(f"Fetched Jira token: {token}")
                print(f"Fetched Jira host: {host}")
                print(f"Fetched Jira username: {username}")

                os.environ["JIRA_TOKEN"] = token
                os.environ["jira_HOST"] = host

                dic = {
                    "user_id": user_id,
                    "user_token": token,
                    "user_host": host,
                    "user_name": username
                }
                print(dic)

                replace_api_credentials(
                    model="api_selector",
                    scenario=scenario,
                    actual_key=username,
                    actual_token=token
                )
                replace_api_credentials(
                    model="planner",
                    scenario=scenario,
                    actual_key=username,
                    actual_token=token
                )
            except Exception as e:
                print(f"key is not present in the database due to: {e}")
                return ""

            # Call the jira specific method to change the host and token with actual values
            replace_api_credentials_in_jira_json(
                scenario=scenario,
                actual_token=token,
                actual_host=host,
                actual_username=username
            )
            api_spec, headers = process_spec_file(
                ### to make the specs file minify or smaller for better processing
                file_path="specs/jira_oas.json",
                token=token,
                username=username
            )
        query_example = "Create a new Project with name 'abc_project'"

    elif scenario == "trello":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM trello_credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                key = res[1]
                token = res[2]

                os.environ["TRELLO_API_KEY"] = key
                os.environ["TRELLO_TOKEN"] = token

                # dic = {
                #     "user_id": user_id,
                #     "user_key": key,
                #     "user_token": token
                # }
                # print(dic)
            except:
                print("Key is not present in the database")
                return ""

        query = include_board_id_in_query(query)

        replace_api_credentials_in_json(
            # ## to replace all the key and token variables in the specs file with real values
            scenario=scenario,
            actual_key=os.environ["TRELLO_API_KEY"],
            actual_token=os.environ["TRELLO_TOKEN"]
        )
        api_spec, headers = process_spec_file(  ### to make the specs file minfy or smaller for for better processing
            file_path="specs/trello_oas.json",
            token=os.environ["TRELLO_TOKEN"],
            key=os.environ["TRELLO_API_KEY"]
        )

        replace_api_credentials(
            model="api_selector",
            scenario=scenario,
            actual_key=os.environ["TRELLO_API_KEY"],
            actual_token=os.environ["TRELLO_TOKEN"]
        )
        replace_api_credentials(
            model="planner",
            scenario=scenario,
            actual_key=os.environ["TRELLO_API_KEY"],
            actual_token=os.environ["TRELLO_TOKEN"]
        )

        query_example = "Create a new board with name 'abc_board'"

    elif scenario == "salesforce":
        credentials_fetch_query = f"SELECT * FROM salesforce_credentials WHERE user_id = {user_id};"
        cursor.execute(credentials_fetch_query)
        query_result = cursor.fetchone()

        domain = query_result[1]
        version = query_result[2]
        client_id = query_result[3]
        client_secret = query_result[4]
        access_token = query_result[5]

        print(f"Salesforce Domain: {domain}")
        print(f"Salesforce Version: {version}")
        print(f"Salesforce Client ID: {client_id}")
        print(f"Salesforce Client Secret: {client_secret}")
        print(f"Salesforce Access Token: {access_token}")

        replace_credentials_salesforce_json(
            scenario=scenario,
            actual_domain=domain,
            actual_version=version,
            actual_client_id=client_id,
            actual_client_secret=client_secret,
            actual_access_token=access_token
        )

        api_spec, headers = process_spec_file(
            file_path="specs/salesforce_oas.json",
            token=access_token,
        )
        query_example = "Create a new folder with name 'abc_folder'"

    # TODO -------------- WE STARTED HERE ----------------------------------
    elif scenario == "facebook":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM facebook_credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                access_token = res[1]

                os.environ["FACEBOOK_ACCESS_TOKEN"] = access_token

                dic = {
                    "user_id": user_id,
                    "user_access_token": access_token
                }
                # print(dic)
            except:
                print("Key is not present in the database")
                return ""

            replace_api_credentials_in_json(
                # ## to replace all the key and token variables in the specs file with real values
                scenario=scenario,
                actual_token=os.environ["FACEBOOK_ACCESS_TOKEN"]
            )

            api_spec, headers = process_spec_file(
                # to make the specs file minfy or smaller for better processing
                file_path="specs/facebook_oas.json",
                token=os.environ["FACEBOOK_ACCESS_TOKEN"]
            )

            query_example = "Create return my facebook user id"

            replace_api_credentials(
                model="api_selector",
                scenario=scenario,
                actual_token=os.environ["FACEBOOK_ACCESS_TOKEN"]
            )
            replace_api_credentials(
                model="planner",
                scenario=scenario,
                actual_token=os.environ["FACEBOOK_ACCESS_TOKEN"]
            )

        # ----------- END facebook scenario ---------------

    elif scenario == "clockify":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM clockify_credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                access_token = res[1]

                os.environ["CLOCKIFY_ACCESS_TOKEN"] = access_token
            except:
                print("Key is not present in the database")
                return ""

            replace_api_credentials_in_json(
                # ## to replace all the key and token variables in the specs file with real values
                scenario=scenario,
                actual_token=os.environ["CLOCKIFY_ACCESS_TOKEN"]
            )

            api_spec, headers = process_spec_file(
                # to make the specs file minfy or smaller for better processing
                file_path=f"specs/{scenario}_oas.json",
                token=os.environ["CLOCKIFY_ACCESS_TOKEN"]
            )

            endpoints = [
                ('POST /workspaces/667eeaee004df9127d441c4c/clients',
                 'Add a new client to a workspace using a name, email and a physical address',
                 {
                     'description': 'Add a new client to a workspace using a name, email and a physical address',
                     'requestBody': {'content':
                                         {'application/json': {'schema': {'type': 'object',
                                                                          'example': {'name': 'Client X2',
                                                                                      'address': "Ground Floor, ABC Bldg., Palo Alto, California, USA 94020",
                                                                                      'email': 'clientx@example.com'}}}}},
                     'parameters': [{'name': 'x-api-key', 'in': 'header', 'schema': {'type': 'string'},
                                     'example': os.environ['CLOCKIFY_ACCESS_TOKEN']}],
                     'responses': {'description': 'Successful response', 'content': {'application/json': {}}}}),

                ('POST /workspaces/667eeaee004df9127d441c4c/projects',
                 'Create a new project in the workspace',
                 {
                     'description': 'Create a new project in the workspace',
                     'requestBody': {'content':
                                         {'application/json': {'schema': {'type': 'object',
                                                                          'example': {'name': 'Software Development',
                                                                                      'note': 'This is a sample note for the project'}}}}},
                     'parameters': [{'name': 'x-api-key', 'in': 'header', 'schema': {'type': 'string'},
                                     'example': os.environ['CLOCKIFY_ACCESS_TOKEN']}],
                     'responses': {'description': 'Successful response', 'content': {'application/json': {}}}})
            ]

            api_spec.endpoints += endpoints

            # print(f"api_spec-api_spec: {api_spec}")

            query_example = "example query to be removed"

            replace_api_credentials(
                model="api_selector",
                scenario=scenario,
                actual_token=os.environ["CLOCKIFY_ACCESS_TOKEN"]
            )
            replace_api_credentials(
                model="planner",
                scenario=scenario,
                actual_token=os.environ["CLOCKIFY_ACCESS_TOKEN"]
            )

        # ----------- END Clockify scenario ---------------
    elif scenario == "todoist":
        if user_id is not None:
            try:
                ser_qu = f"SELECT * FROM todoist_credentials WHERE user_id = {user_id};"
                cursor.execute(ser_qu)
                res = cursor.fetchone()
                access_token = res[1]

                os.environ["TODOIST_ACCESS_TOKEN"] = "Bearer" + access_token
            except:
                print("Key is not present in the database")
                return ""

            replace_api_credentials_in_json(
                # ## to replace all the key and token variables in the specs file with real values
                scenario=scenario,
                actual_token=os.environ["TODOIST_ACCESS_TOKEN"]
            )

            api_spec, headers = process_spec_file(
                # to make the specs file minfy or smaller for better processing
                file_path=f"specs/{scenario}_oas.json",
                token=os.environ["TODOIST_ACCESS_TOKEN"]
            )

            query_example = "Create return my facebook user id"

            replace_api_credentials(
                model="api_selector",
                scenario=scenario,
                actual_token=os.environ["TODOIST_ACCESS_TOKEN"]
            )
            replace_api_credentials(
                model="planner",
                scenario=scenario,
                actual_token=os.environ["TODOIST_ACCESS_TOKEN"]
            )

            # ----------- END todoist scenario ---------------
        # TODO -------------- WE FINISHED HERE ----------------------------------
    else:
        raise ValueError(f"Unsupported scenario: {scenario}")

    populate_api_selector_icl_examples(scenario=scenario)
    populate_planner_icl_examples(scenario=scenario)

    requests_wrapper = Requests(headers=headers)

    # text-davinci-003

    llm = OpenAI(model_name=os.environ["OPENAI_MODEL"], temperature=0.0, max_tokens=1024)
    api_llm = ApiLLM(
        llm,
        api_spec=api_spec,
        scenario=scenario,
        requests_wrapper=requests_wrapper,
        simple_parser=False
    )

    print(f"Example instruction: {query_example}")
    # query = input(
    #     "Please input an instruction (Press ENTER to use the example instruction): "
    # )
    if query == "":
        query = query_example

    logger.info(f"Query: {query}")

    api_llm.our_user_query = query

    start_time = time.time()
    result = api_llm.run(query)
    # logger.info(f"Execution Time: {time.time() - start_time}")

    return result




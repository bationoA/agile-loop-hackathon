import json
import os.path

from custom_package.llm import ChatModel

PROMPT_GET_BOARD_ID = """Your board identifier. You always modify the user query by first, identifying the board 
mentioned in the query, extract its id, replace the board's name by its id in the query, then return the modified  query.

You must always use the below list to identify the board that's mentioned in the query.

Boards list:
{board_list}

Example 1:
    background: [{"id": "658d2272d02bb8b7918d140f", "name": "Postman board"}]
    user query: "Create a label "Completed" in blue color for the board "Postman board".
    your response: "Create a label "Completed" in blue color for the board of id "658d2272d02bb8b7918d140f"
    
Example 2:
    background: [{"id": "658d2272d02bb8b7918d140f", "name": "Movies"}]
    user query: "Delete the board Movies"
    your response: "Delete the board with id "658d2272d02bb8b7918d140f"
    
    
Example 3:
    background: []
    user query: "Create a board Buildings"
    your response: "Create a board Buildings"

If the query is about creating a board, then do not perform any task, just return the query as it was.

else if the provided board list is empty, then do not perform any task, just return the query as it was.

"""


def get_trello_board_identifier_prompt() -> str:

    with open(os.path.join("custom_package", "trello_boards_list.json"), "r") as f:
        boards_list = f.read()

    return PROMPT_GET_BOARD_ID.replace("{board_list}", boards_list)


def include_board_id_in_query(query: str) -> str:

    board_identifier = ChatModel(prompt=get_trello_board_identifier_prompt(),
                                 user_content=query
                                 )

    raw_response = board_identifier.get_response()
    response = raw_response.json()

    return response['choices'][0]['message']['content']

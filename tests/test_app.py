from fastapi.testclient import TestClient

from app.main import app

from app.schemas import PromptRequest


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text

    assert "Story Prompt" in response.text


def test_prompt_validation():

    data = {
        "story_prompt":
            "A fox explores a magical forest.",

        "character_name":
            "Lumi",

        "setting":
            "Forest",

        "tone":
            "Funny",

        "art_style":
            "Comic book",
    }


    request = PromptRequest(
        **data
    )


    assert (
        request.character_name
        == "Lumi"
    )


def test_short_prompt_rejected():

    response = client.post(
        "/generate-comic/json",

        json={
            "story_prompt": "x",

            "character_name":
                "Lumi",

            "setting":
                "Forest",

            "tone":
                "Funny",

            "art_style":
                "Comic book",
        }
    )


    assert response.status_code == 422
"""CR-0: tēma PARKS un tēmu saraksts (GET /topics)."""

EXPECTED_TOPICS = [
    {"code": "ROADS", "name": "Ceļi un ielas"},
    {"code": "WASTE", "name": "Atkritumi"},
    {"code": "PLANNING", "name": "Teritorijas plānošana"},
    {"code": "PARKS", "name": "Parki un skvēri"},
    {"code": "OTHER", "name": "Cits"},
]


def test_cr0_ac1_topics_list(client):
    response = client.get("/topics")
    assert response.status_code == 200
    assert response.json() == EXPECTED_TOPICS


def test_cr0_ac2_parks_submission_created(client, valid_payload):
    valid_payload["topic"] = "PARKS"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201


def test_cr0_ac3_unknown_topic_rejected(client, valid_payload):
    valid_payload["topic"] = "ZOO"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert [d["field"] for d in error["details"]] == ["topic"]


def test_cr0_ac4_existing_topics_unchanged(client, valid_payload):
    topics = client.get("/topics").json()
    existing = [
        {"code": "ROADS", "name": "Ceļi un ielas"},
        {"code": "WASTE", "name": "Atkritumi"},
        {"code": "PLANNING", "name": "Teritorijas plānošana"},
        {"code": "OTHER", "name": "Cits"},
    ]
    for item in existing:
        assert item in topics
        valid_payload["topic"] = item["code"]
        assert client.post("/submissions", json=valid_payload).status_code == 201

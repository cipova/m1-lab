"""CR-1: personas koda pārbaude iesniegumā. Personas kodi ir sintētiski."""

import logging

import pytest


@pytest.mark.parametrize(
    ("value", "stored"),
    [
        ("32000000001", "32000000001"),  # 1
        ("320000-00001", "32000000001"),  # 2
        (" 32000000001 ", "32000000001"),  # 3
        ("311299-21233", "31129921233"),  # 8
    ],
)
def test_valid_personal_code_is_saved_without_dash(
    client, valid_payload, value, stored
):
    valid_payload["personalCode"] = value
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    saved = client.get(f"/submissions/{response.json()['id']}").json()
    assert saved["personalCode"] == stored


def test_omd_receives_normalized_code(client, valid_payload, fake_omd):
    valid_payload["personalCode"] = " 320000-00001 "
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    assert fake_omd.calls == ["32000000001"]
    assert response.json()["replyChannel"] == "E_ADDRESS"


@pytest.mark.parametrize(
    "value",
    [
        "3200000000",  # 4: 10 cipari
        "320000000012",  # 5: 12 cipari
        "32000000O01",  # 6: burts O
        "3200-0000001",  # 9: defise nepareizā vietā
        "320000 00001",  # atstarpe vidū
        "32000-000001",
        "320000-0001",
        "320000--00001",
        "٣٢٠٠٠٠٠٠٠٠١",  # ne-ASCII cipari
        32000000001,  # skaitlis, nevis virkne
    ],
)
def test_invalid_personal_code_returns_400_invalid_format(client, valid_payload, value):
    valid_payload["personalCode"] = value
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": [{"field": "personalCode", "issue": "INVALID_FORMAT"}],
        }
    }


@pytest.mark.parametrize("value", ["", "   ", None])
def test_empty_personal_code_returns_400_required(client, valid_payload, value):
    valid_payload["personalCode"] = value
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    details = response.json()["error"]["details"]
    assert details == [{"field": "personalCode", "issue": "REQUIRED"}]


def test_missing_personal_code_returns_400_required(client, valid_payload):  # 7
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    details = response.json()["error"]["details"]
    assert details == [{"field": "personalCode", "issue": "REQUIRED"}]


def test_invalid_code_is_not_saved(client, valid_payload):
    valid_payload["personalCode"] = "3200000000"
    client.post("/submissions", json=valid_payload)
    valid_payload["personalCode"] = "32000000101"
    created = client.post("/submissions", json=valid_payload).json()
    assert created["id"] == "IES-2026-000001"


def test_error_does_not_echo_personal_code(client, valid_payload):
    valid_payload["personalCode"] = "32000000O01"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    assert "32000000O01" not in response.text


def test_log_has_no_personal_code_or_body(client, valid_payload, caplog):
    caplog.set_level(logging.INFO, logger="ezermala.submissions")
    valid_payload["personalCode"] = "320000-00001"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    assert response.json()["id"] in caplog.text
    for secret in ("32000000001", "320000-00001", valid_payload["body"]):
        assert secret not in caplog.text

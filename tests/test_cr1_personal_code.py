"""CR-1 · Personas koda pārbaude iesniegumā.

Sagaidāmās vērtības ņemtas no tracker/CR-1.md pieņemšanas kritērijiem un precizējumiem.
Visi personas kodi ir sintētiski un ņemti no pieteikuma.
"""

import logging


def _create_and_fetch(client, payload):
    response = client.post("/submissions", json=payload)
    assert response.status_code == 201, response.text
    created = response.json()
    stored = client.get(f"/submissions/{created['id']}")
    assert stored.status_code == 200
    return stored.json()


def _assert_validation_error(response, issue):
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "personalCode", "issue": issue} in error["details"]


# --- Pieņemšanas kritēriji 1–9 ---


def test_cr1_ac1_eleven_digits_accepted(client, valid_payload):
    valid_payload["personalCode"] = "32000000001"
    stored = _create_and_fetch(client, valid_payload)
    assert stored["personalCode"] == "32000000001"


def test_cr1_ac2_hyphen_normalised(client, valid_payload):
    valid_payload["personalCode"] = "320000-00001"
    stored = _create_and_fetch(client, valid_payload)
    assert stored["personalCode"] == "32000000001"


def test_cr1_ac3_surrounding_spaces_stripped(client, valid_payload):
    valid_payload["personalCode"] = " 32000000001 "
    stored = _create_and_fetch(client, valid_payload)
    assert stored["personalCode"] == "32000000001"


def test_cr1_ac4_ten_digits_invalid_format(client, valid_payload):
    valid_payload["personalCode"] = "3200000000"
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "INVALID_FORMAT")


def test_cr1_ac5_twelve_digits_invalid_format(client, valid_payload):
    valid_payload["personalCode"] = "320000000012"
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "INVALID_FORMAT")


def test_cr1_ac6_letter_o_invalid_format(client, valid_payload):
    valid_payload["personalCode"] = "32000000O01"
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "INVALID_FORMAT")


def test_cr1_ac7_missing_field_required(client, valid_payload):
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "REQUIRED")


def test_cr1_ac8_old_format_hyphen_normalised(client, valid_payload):
    valid_payload["personalCode"] = "311299-21233"
    stored = _create_and_fetch(client, valid_payload)
    assert stored["personalCode"] == "31129921233"


def test_cr1_ac9_hyphen_wrong_position_invalid_format(client, valid_payload):
    valid_payload["personalCode"] = "3200-0000001"
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "INVALID_FORMAT")


# --- Papildu testi no precizējumiem ---


def test_cr1_clar_empty_string_required(client, valid_payload):
    valid_payload["personalCode"] = ""
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "REQUIRED")


def test_cr1_clar_only_spaces_required(client, valid_payload):
    valid_payload["personalCode"] = "   "
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "REQUIRED")


def test_cr1_clar_ac4_input_not_echoed_in_response(client, valid_payload):
    valid_payload["personalCode"] = "3200000000"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    assert "3200000000" not in response.text


def test_cr1_clar_ac6_input_not_echoed_in_response(client, valid_payload):
    valid_payload["personalCode"] = "32000000O01"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    assert "32000000O01" not in response.text


def test_cr1_clar_personal_code_not_logged(client, valid_payload, caplog):
    valid_payload["personalCode"] = "32000000001"
    with caplog.at_level(logging.INFO):
        response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    assert "32000000001" not in caplog.text


def test_cr1_clar_unicode_digits_invalid_format(client, valid_payload):
    valid_payload["personalCode"] = "٣٢٠٠٠٠٠٠٠٠١"
    response = client.post("/submissions", json=valid_payload)
    _assert_validation_error(response, "INVALID_FORMAT")


def test_cr1_existing_record_with_old_code_still_readable(client):
    # Esošie ieraksti ar nepareizu kodu ir ārpus tvēruma, bet GET tos nelauž.
    from app import storage

    record = storage.add(
        {
            "personalCode": "12345",
            "fullName": "Jānis Bērziņš",
            "email": "janis@example.com",
            "preferredChannel": "EMAIL",
            "topic": "ROADS",
            "subject": "Vecs iesniegums",
            "body": "Teksts",
            "status": "RECEIVED",
            "receivedAt": "2026-10-01T09:15:00+00:00",
            "dueDate": "2026-10-31",
            "replyChannel": "EMAIL",
            "reasonCode": None,
        }
    )
    response = client.get(f"/submissions/{record['id']}")
    assert response.status_code == 200

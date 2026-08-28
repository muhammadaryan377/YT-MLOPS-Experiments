from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_process_order_detects_stock_and_credit_problem():
    response = client.post(
        "/v1/messages/process",
        json={
            "customer_id": "ali-general-store",
            "message": "10 carton Pepsi 500 ml, 5 Dew aur 2 carton Sting bhej dena. pichla balance bhi check kar lena",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["balance_requested"] is True
    assert len(data["order_lines"]) == 3
    sting = next(x for x in data["order_lines"] if x["sku"] == "STING-250ML")
    assert sting["stock_status"] == "partial"
    assert sting["fulfill_qty"] == 1
    assert data["decision"]["status"] == "credit_hold"
    assert data["minimum_payment_required"] > 0


def test_city_mart_can_prepare_normal_order():
    response = client.post(
        "/v1/messages/process",
        json={"customer_id": "city-mart", "message": "2 carton Pepsi 500ml aur 1 Dew"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"]["status"] == "ready_for_confirmation"
    assert data["order_total"] == 9700

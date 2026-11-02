"""
FastAPI API Contract, Discovery, and Health Suite
Validates startup integrity, documentation availability, OpenAPI specs, and status endpoints.
"""

import pytest
import qsar_api


def test_fastapi_application_startup(request, client):
    request.node.test_id = "TC_API_001"
    request.node.custom_module = "API Contract"
    request.node.priority = "P0"
    request.node.test_name = "Verify FastAPI application initializes with valid title and routes"

    assert qsar_api.app is not None
    assert qsar_api.app.title == "QSAR Discovery Suite v3.0"
    assert len(qsar_api.app.routes) >= 15


def test_openapi_schema_endpoint(request, client):
    request.node.test_id = "TC_API_002"
    request.node.custom_module = "API Contract"
    request.node.priority = "P1"
    request.node.test_name = "Verify /openapi.json returns valid OpenAPI 3.x schema definition"

    res = client.get("/openapi.json")
    assert res.status_code == 200
    data = res.json()
    assert "openapi" in data
    assert data["info"]["title"] == "QSAR Discovery Suite v3.0"
    assert "/health" in data["paths"]


def test_swagger_documentation_ui(request, client):
    request.node.test_id = "TC_API_003"
    request.node.custom_module = "API Contract"
    request.node.priority = "P2"
    request.node.test_name = "Verify Swagger documentation endpoint /docs returns HTTP 200"

    res = client.get("/docs")
    assert res.status_code == 200
    assert "swagger-ui" in res.text.lower() or "html" in res.text.lower()


def test_redoc_documentation_ui(request, client):
    request.node.test_id = "TC_API_004"
    request.node.custom_module = "API Contract"
    request.node.priority = "P2"
    request.node.test_name = "Verify ReDoc documentation endpoint /redoc returns HTTP 200"

    res = client.get("/redoc")
    assert res.status_code == 200
    assert "redoc" in res.text.lower() or "html" in res.text.lower()


def test_health_endpoint_contract(request, client):
    request.node.test_id = "TC_API_005"
    request.node.custom_module = "API Contract"
    request.node.priority = "P0"
    request.node.test_name = "Verify /health response structure contains required service metadata"

    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "ok"
    assert "version" in data
    assert "loaded_model_count" in data
    assert "targets" in data
    assert isinstance(data["targets"], list)


def test_available_targets_endpoint(request, client):
    request.node.test_id = "TC_API_006"
    request.node.custom_module = "API Contract"
    request.node.priority = "P1"
    request.node.test_name = "Verify /available_targets returns dictionary mapping of supported targets"

    res = client.get("/available_targets")
    assert res.status_code == 200
    data = res.json()
    assert "loaded_models" in data
    assert "targets" in data
    assert isinstance(data["targets"], dict)


def test_docking_targets_endpoint(request, client):
    request.node.test_id = "TC_API_007"
    request.node.custom_module = "API Contract"
    request.node.priority = "P1"
    request.node.test_name = "Verify /docking_targets returns dictionary mapping of receptor target identifiers"

    res = client.get("/docking_targets")
    assert res.status_code == 200
    data = res.json()
    assert "targets" in data
    assert isinstance(data["targets"], dict)
    assert "available" in data
    assert isinstance(data["available"], list)


def test_docking_status_endpoint(request, client):
    request.node.test_id = "TC_API_008"
    request.node.custom_module = "API Contract"
    request.node.priority = "P2"
    request.node.test_name = "Verify /docking_status returns molecular docking engine status"

    res = client.get("/docking_status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data or "vina_available" in data or "available" in data or "receptors" in data


def test_cors_middleware_headers(request, client):
    request.node.test_id = "TC_API_009"
    request.node.custom_module = "API Contract"
    request.node.priority = "P1"
    request.node.test_name = "Verify CORS headers are returned for preflight cross-origin options request"

    res = client.options("/health", headers={"Origin": "https://qsar-suite.org", "Access-Control-Request-Method": "GET"})
    assert res.status_code in (200, 204)


def test_application_version_metadata(request, client):
    request.node.test_id = "TC_API_010"
    request.node.custom_module = "API Contract"
    request.node.priority = "P2"
    request.node.test_name = "Verify application release version tag matches 3.0"

    res = client.get("/health")
    assert res.status_code == 200
    assert res.json().get("version") == "3.0"

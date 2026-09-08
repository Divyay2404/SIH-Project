"""
Unit and integration tests for FastAPI REST Gateway Setup & CORS Config (Issue #5).
Verifies:
- FastAPI initialization and metadata
- CORS middleware configuration allowing http://localhost:5173
- Asynchronous router mounting and route handler coroutine types
- Health check endpoints (/ and /health and /api/health)
- Pydantic schema validation for request and response contracts
- Error handling and export query parameter validation
"""

import inspect
import os
import sys
import unittest

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from app.main import app, ALLOWED_ORIGINS
from app.api.routes import router
from app.schemas.api_schemas import (
    HealthCheckResponse,
    RootHealthResponse,
    IngestResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    QuizQuestionResponse,
    QuizSubmissionRequest,
    DiagnosticResponse,
    ReadinessResponse,
    ErrorResponse,
)


class TestFastAPIGatewaySetup(unittest.TestCase):
    """Verifies FastAPI initialization, CORS configuration, and router mounting."""

    def setUp(self):
        self.client = TestClient(app)

    def test_app_initialization_metadata(self):
        """Verify FastAPI instance initializes with proper metadata and OpenAPI docs."""
        self.assertEqual(app.title, "StudyCopilot & StudyForge Unified Learning OS API")
        self.assertEqual(app.version, "1.0.0")
        self.assertEqual(app.docs_url, "/docs")
        self.assertEqual(app.redoc_url, "/redoc")

    def test_cors_middleware_configuration(self):
        """Verify CORS middleware is active and allows http://localhost:5173."""
        self.assertIn("http://localhost:5173", ALLOWED_ORIGINS)
        self.assertIn("http://127.0.0.1:5173", ALLOWED_ORIGINS)

        # Inspect middleware stack
        cors_middlewares = [m for m in app.user_middleware if m.cls == CORSMiddleware]
        self.assertGreater(len(cors_middlewares), 0, "CORSMiddleware should be configured on app")

        # Test preflight CORS request from http://localhost:5173
        response = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:5173")
        self.assertEqual(response.headers.get("access-control-allow-credentials"), "true")

    def test_asynchronous_router_mounting(self):
        """Verify router is mounted and all primary endpoints are asynchronous coroutine functions."""
        # Check router routes with prefix /api
        router_paths = [r.path for r in router.routes if hasattr(r, "path")]
        expected_router_endpoints = [
            "/api/health",
            "/api/ingest",
            "/api/query",
            "/api/quiz",
            "/api/diagnose",
            "/api/readiness",
            "/api/export/ppt",
            "/api/export/pdf",
        ]
        for ep in expected_router_endpoints:
            self.assertIn(ep, router_paths, f"Endpoint {ep} must be registered in router routes")

        # Check app root routes
        app_paths = [r.path for r in app.routes if hasattr(r, "path")]
        self.assertIn("/", app_paths)
        self.assertIn("/health", app_paths)

        # Verify async router handlers
        for route in router.routes:
            endpoint_fn = getattr(route, "endpoint", None)
            if endpoint_fn:
                self.assertTrue(
                    inspect.iscoroutinefunction(endpoint_fn),
                    f"Route handler {endpoint_fn.__name__} for {route.path} should be async"
                )

    def test_root_health_endpoints(self):
        """Verify root and health check endpoints conform to Pydantic schemas."""
        # Root endpoint
        root_res = self.client.get("/")
        self.assertEqual(root_res.status_code, 200)
        root_data = RootHealthResponse(**root_res.json())
        self.assertIn("StudyCopilot", root_data.message)
        self.assertEqual(root_data.docs_url, "/docs")
        self.assertEqual(root_data.health_check, "/api/health")

        # Root /health
        health_res = self.client.get("/health")
        self.assertEqual(health_res.status_code, 200)
        health_data = HealthCheckResponse(**health_res.json())
        self.assertEqual(health_data.status, "online")
        self.assertEqual(health_data.version, "1.0.0")

        # Router /api/health
        api_health_res = self.client.get("/api/health")
        self.assertEqual(api_health_res.status_code, 200)
        api_health_data = HealthCheckResponse(**api_health_res.json())
        self.assertEqual(api_health_data.status, "online")

    def test_rag_query_pydantic_validation(self):
        """Verify /api/query request and response validation via Pydantic schemas."""
        # Valid 5-mark query
        payload = {"question": "Explain Binary Search Tree deletion algorithm", "marks": 5}
        res = self.client.post("/api/query", json=payload)
        self.assertEqual(res.status_code, 200)
        parsed = RAGQueryResponse(**res.json())
        self.assertEqual(parsed.status, "success")
        self.assertEqual(parsed.marks, 5)
        self.assertFalse(parsed.abstain)
        self.assertIsNotNone(parsed.citation)

        # Evidence-or-abstain gate
        unsupported_payload = {"question": "How to bake a chocolate cake?", "marks": 2}
        res_abstain = self.client.post("/api/query", json=unsupported_payload)
        self.assertEqual(res_abstain.status_code, 200)
        parsed_abstain = RAGQueryResponse(**res_abstain.json())
        self.assertEqual(parsed_abstain.status, "abstain")
        self.assertTrue(parsed_abstain.abstain)

        # Invalid request validation (missing required question)
        invalid_res = self.client.post("/api/query", json={"marks": 5})
        self.assertEqual(invalid_res.status_code, 422)

    def test_diagnostic_quiz_and_evaluation_validation(self):
        """Verify /api/quiz and /api/diagnose schema contracts."""
        # GET /api/quiz
        res_quiz = self.client.get("/api/quiz")
        self.assertEqual(res_quiz.status_code, 200)
        quiz_data = QuizQuestionResponse(**res_quiz.json())
        self.assertEqual(quiz_data.question_id, "q_bst_del_01")
        self.assertEqual(len(quiz_data.options), 4)

        # POST /api/diagnose - Correct Answer
        correct_payload = {"question_id": "q_bst_del_01", "selected_option": 0, "topic_id": "bst_deletion"}
        res_diag = self.client.post("/api/diagnose", json=correct_payload)
        self.assertEqual(res_diag.status_code, 200)
        diag_data = DiagnosticResponse(**res_diag.json())
        self.assertEqual(diag_data.status, "correct")
        self.assertTrue(diag_data.is_correct)

        # POST /api/diagnose - Conceptual Gap Error
        incorrect_payload = {"question_id": "q_bst_del_01", "selected_option": 1, "topic_id": "bst_deletion"}
        res_err = self.client.post("/api/diagnose", json=incorrect_payload)
        self.assertEqual(res_err.status_code, 200)
        err_data = DiagnosticResponse(**res_err.json())
        self.assertEqual(err_data.status, "diagnosed")
        self.assertFalse(err_data.is_correct)
        self.assertEqual(err_data.error_category, "conceptual_gap")
        self.assertTrue(err_data.rescue_mission_triggered)
        self.assertIsNotNone(err_data.rescue_mission)

        # Validation error on negative selected_option
        invalid_payload = {"question_id": "q_bst_del_01", "selected_option": -1}
        res_invalid = self.client.post("/api/diagnose", json=invalid_payload)
        self.assertEqual(res_invalid.status_code, 422)

    def test_readiness_heatmap_schema(self):
        """Verify /api/readiness returns validated structure."""
        res = self.client.get("/api/readiness")
        self.assertEqual(res.status_code, 200)
        readiness_data = ReadinessResponse(**res.json())
        self.assertGreaterEqual(readiness_data.overall_readiness, 0)
        self.assertGreater(len(readiness_data.topic_heatmap), 0)
        self.assertIn("Conceptual Gap", readiness_data.class_error_distribution)

    def test_ingest_file_validation(self):
        """Verify /api/ingest input validation for file types and empty content."""
        # Non-PDF rejection
        res_txt = self.client.post(
            "/api/ingest",
            files={"file": ("test.txt", b"Non-PDF test file content", "text/plain")}
        )
        self.assertEqual(res_txt.status_code, 400)
        self.assertIn("PDF documents only", res_txt.json()["detail"])

        # Empty PDF rejection
        res_empty = self.client.post(
            "/api/ingest",
            files={"file": ("empty.pdf", b"", "application/pdf")}
        )
        self.assertEqual(res_empty.status_code, 400)
        self.assertIn("empty", res_empty.json()["detail"].lower())

    def test_export_endpoints_parameter_validation(self):
        """Verify /api/export/ppt and /api/export/pdf parameter and 404 validation."""
        # Missing document_id parameter (422 Unprocessable Entity)
        ppt_no_param = self.client.get("/api/export/ppt")
        self.assertEqual(ppt_no_param.status_code, 422)

        pdf_no_param = self.client.get("/api/export/pdf")
        self.assertEqual(pdf_no_param.status_code, 422)

        # Non-existent document_id (404 Not Found)
        ppt_missing = self.client.get("/api/export/ppt?document_id=doc_nonexistent_123")
        self.assertEqual(ppt_missing.status_code, 404)

        pdf_missing = self.client.get("/api/export/pdf?document_id=doc_nonexistent_123")
        self.assertEqual(pdf_missing.status_code, 404)


if __name__ == "__main__":
    unittest.main()


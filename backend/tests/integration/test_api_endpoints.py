import os
import json
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import Base, engine
from backend.app.services.graph.models import LegalEntity, LegalRelationship
from backend.app.services.graph.engine import get_graph_engine

@pytest.fixture(scope="module")
def client():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client

def test_system_endpoints(client):
    res_root = client.get("/")
    assert res_root.status_code == 200
    data = res_root.json()
    assert "NyayaSaathi AI" in data["project"]
    assert data["docs_url"] == "/docs"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_ready = client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"
    assert res_ready.json()["database_connected"] is True


def test_complaints_classify_and_draft_flow(client):
    # 1. Classify
    classify_payload = {
        "grievance_description": "I ordered a laptop from Amazon for Rs 45,000 but it was never delivered and seller refused refund.",
        "transaction_amount": 45000.0,
        "platform_or_company": "Amazon India"
    }
    res_classify = client.post("/api/v1/complaints/classify", json=classify_payload)
    assert res_classify.status_code == 200
    cdata = res_classify.json()
    assert "E-Commerce" in cdata["category"]
    assert "District" in cdata["recommended_forum"]
    assert len(cdata["applicable_provisions"]) > 0

    # 2. Draft Formal Complaint
    draft_payload = {
        "complainant_name": "Rohan Sharma",
        "complainant_contact": "+91-9876543210",
        "complainant_address": "42 Connaught Place, New Delhi",
        "opposite_party_name": "Cloudtail India Pvt Ltd",
        "opposite_party_address": "Brigade Gateway, Bengaluru",
        "transaction_amount": 45000.0,
        "transaction_date": "15-10-2023",
        "order_or_invoice_number": "OD402910391039",
        "facts_of_case": "The complainant purchased a laptop via online marketplace. Payment of Rs 45,000 was debited. The product was never dispatched and refund requests were ignored.",
        "relief_sought": "Full refund of Rs 45,000 with 18% interest and Rs 25,000 for mental harassment."
    }
    res_draft = client.post("/api/v1/complaints/draft", json=draft_payload)
    assert res_draft.status_code == 200
    ddata = res_draft.json()
    draft_id = ddata["id"]
    assert draft_id is not None
    assert "BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION" in ddata["full_draft_text"]
    assert "Rohan Sharma" in ddata["full_draft_text"]
    assert len(ddata["citations"]) > 0

    # 3. List Complaints
    res_list = client.get("/api/v1/complaints")
    assert res_list.status_code == 200
    assert any(d["id"] == draft_id for d in res_list.json())

    # 4. Get Single Complaint
    res_get = client.get(f"/api/v1/complaints/{draft_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == draft_id

    # 5. Export Complaint
    res_export = client.get(f"/api/v1/complaints/{draft_id}/export")
    assert res_export.status_code == 200
    assert "BEFORE THE HON'BLE" in res_export.text
    assert "attachment" in res_export.headers.get("content-disposition", "")


def test_document_analysis_flow(client):
    # 1. Direct text analysis
    invoice_text = """
    TAX INVOICE / CASH MEMO
    Amazon Retail India Pvt Ltd
    Invoice No: INV-2023-88910
    Date: 12/10/2023
    Customer: Anita Roy
    Item: Sony Wireless Headphones WH-1000XM4
    Total Amount: Rs. 24,990.00
    TERMS: Non-refundable item. No return accepted once open.
    """
    res_direct = client.post("/api/v1/documents/analyze", json={"text": invoice_text, "filename": "sample_invoice.txt"})
    assert res_direct.status_code == 200
    data = res_direct.json()
    assert data["merchant_name"] == "Amazon"
    assert data["invoice_amount"] == 24990.0
    assert data["invoice_date"] == "12/10/2023"
    assert any("No return policy" in ind for ind in data["potential_grievance_indicators"])
    assert len(data["suggested_legal_claims"]) > 0

    # 2. File upload analysis
    file_content = invoice_text.encode("utf-8")
    files = {"file": ("test_invoice.txt", file_content, "text/plain")}
    res_upload = client.post("/api/v1/documents/upload", files=files)
    assert res_upload.status_code == 200
    up_data = res_upload.json()
    doc_id = up_data["id"]
    assert doc_id is not None

    # 3. List documents
    res_docs = client.get("/api/v1/documents")
    assert res_docs.status_code == 200
    assert any(d["id"] == doc_id for d in res_docs.json())

    # 4. Get document details
    res_doc_get = client.get(f"/api/v1/documents/{doc_id}")
    assert res_doc_get.status_code == 200
    assert res_doc_get.json()["id"] == doc_id


def test_knowledge_base_endpoints(client):
    # 1. Sources Manifest
    res_sources = client.get("/api/v1/knowledge/sources")
    assert res_sources.status_code == 200
    sources_data = res_sources.json()
    assert "documents" in sources_data or "categories" in sources_data

    # 2. Stats
    res_stats = client.get("/api/v1/knowledge/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert "graph_entities_count" in stats
    assert "max_hops_configured" in stats

    # 3. Knowledge Search (hybrid)
    res_search = client.post("/api/v1/knowledge/search", json={"query": "e-commerce refund seller duties", "top_k": 3})
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["total_found"] >= 0
    assert "candidates" in search_data

    # 4. Knowledge Graph Entity
    graph_engine = get_graph_engine()
    # Insert a dummy entity to test retrieval
    test_ent = LegalEntity(
        id="test_act_sec_99",
        entity_type="Section",
        name="Section 99 Test Provision",
        canonical_citation="Section 99, CPA 2019",
        document_id="cpa_2019",
        category="1_statutory",
        summary="Test section for graph endpoint validation.",
        provenance_chunk_id="chunk_test_99"
    )
    graph_engine.sync_to_db([test_ent], [])
    graph_engine.entities["test_act_sec_99"] = test_ent
    graph_engine.graph.add_node("test_act_sec_99")

    res_entity = client.get("/api/v1/knowledge/graph/test_act_sec_99")
    assert res_entity.status_code == 200
    ent_data = res_entity.json()
    assert ent_data["entity"]["id"] == "test_act_sec_99"
    assert ent_data["entity"]["name"] == "Section 99 Test Provision"

    # 404 for nonexistent entity
    res_nonexistent = client.get("/api/v1/knowledge/graph/nonexistent_xyz_123")
    assert res_nonexistent.status_code == 404


def test_chat_and_conversation_flow(client):
    # 1. Chat Consultation
    chat_payload = {
        "query": "What are my rights if an online seller delivers a broken product and refuses to refund?",
        "mode": "hybrid",
        "top_k": 4
    }
    res_chat = client.post("/api/v1/chat", json=chat_payload)
    assert res_chat.status_code == 200
    cdata = res_chat.json()
    conv_id = cdata["conversation_id"]
    msg_id = cdata["message_id"]
    assert conv_id is not None
    assert msg_id is not None
    assert "response" in cdata
    assert "disclaimer" in cdata["response"]
    assert len(cdata["response"]["disclaimer"]) > 20

    # 2. Get Conversations
    res_convs = client.get("/api/v1/conversations")
    assert res_convs.status_code == 200
    assert any(c["id"] == conv_id for c in res_convs.json())

    # 3. Get Conversation Messages
    res_msgs = client.get(f"/api/v1/conversations/{conv_id}")
    assert res_msgs.status_code == 200
    msgs = res_msgs.json()
    assert len(msgs) >= 2  # user and assistant
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"

    # 4. Message Feedback
    res_fb = client.post(f"/api/v1/messages/{msg_id}/feedback", json={"rating": 5, "feedback_text": "Very accurate citation of E-Commerce Rules!"})
    assert res_fb.status_code == 200
    assert res_fb.json()["rating"] == 5

    # 5. SSE Chat Stream
    stream_payload = {
        "query": "How can I register a consumer grievance on National Consumer Helpline?",
        "conversation_id": conv_id
    }
    with client.stream("POST", "/api/v1/chat/stream", json=stream_payload) as stream_res:
        assert stream_res.status_code == 200
        assert "text/event-stream" in stream_res.headers.get("content-type", "")
        lines = [line for line in stream_res.iter_lines()]
        assert len(lines) > 0
        has_token_or_complete = any("token" in l or "complete" in l or "status" in l for l in lines)
        assert has_token_or_complete

    # 6. Delete Conversation
    res_del = client.delete(f"/api/v1/conversations/{conv_id}")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "success"

    # Confirm deletion
    res_confirm = client.get(f"/api/v1/conversations/{conv_id}")
    assert res_confirm.status_code == 404

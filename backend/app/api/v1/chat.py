import json
import uuid
import asyncio
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.entities import Conversation, Message, User
from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    MessageItem,
    FeedbackRequest,
)
from backend.app.api.deps import get_optional_current_user
from backend.app.services.rag.generation import get_generation_service, RAGGenerationService

router = APIRouter()

def get_or_create_conversation(
    db: Session,
    conversation_id: Optional[str],
    initial_title: str,
    user: Optional[User] = None
) -> Conversation:
    if conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            # Enforce tenant isolation if conversation has an owner
            if conv.user_id and (not user or conv.user_id != user.id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this consultation.")
            # If conversation is unowned and user signs in, claim it
            if not conv.user_id and user:
                conv.user_id = user.id
                db.commit()
            return conv

    title = (initial_title[:45] + "...") if len(initial_title) > 45 else initial_title
    new_conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=user.id if user else None,
        title=title or "Consumer Consultation",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv


@router.post("/chat", response_model=ChatResponse, summary="Submit a consumer query and get structured legal response")
def chat_endpoint(
    req: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
    gen_service: RAGGenerationService = Depends(get_generation_service)
):
    conv = get_or_create_conversation(db, req.conversation_id, req.query, user=current_user)

    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="user",
        content=req.query,
        created_at=datetime.datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()

    structured_res = gen_service.generate_response(
        query=req.query,
        top_k=req.top_k or 6,
        mode=req.mode or "hybrid_graph",
        filter_category=req.filter_category
    )

    asst_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="assistant",
        content=structured_res.summary,
        structured_data=structured_res.model_dump(),
        created_at=datetime.datetime.utcnow()
    )
    db.add(asst_msg)
    conv.updated_at = datetime.datetime.utcnow()
    db.commit()

    return ChatResponse(
        conversation_id=conv.id,
        message_id=asst_msg.id,
        response=structured_res,
        created_at=asst_msg.created_at
    )


@router.post("/chat/stream", summary="Stream structured legal consultation via Server-Sent Events (SSE)")
async def chat_stream_endpoint(
    req: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
    gen_service: RAGGenerationService = Depends(get_generation_service)
):
    conv = get_or_create_conversation(db, req.conversation_id, req.query, user=current_user)

    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv.id,
        role="user",
        content=req.query,
        created_at=datetime.datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()

    async def sse_generator():
        yield f"data: {json.dumps({'type': 'status', 'stage': 'crag_retrieval', 'message': 'Retrieving statutory provisions and official SOPs...'})}\n\n"
        await asyncio.sleep(0.02)

        structured_res = gen_service.generate_response(
            query=req.query,
            top_k=req.top_k or 6,
            mode=req.mode or "hybrid_graph",
            filter_category=req.filter_category
        )

        yield f"data: {json.dumps({'type': 'status', 'stage': 'verification', 'message': 'Verifying citations and statutory grounds...'})}\n\n"
        await asyncio.sleep(0.02)

        words = structured_res.summary.split()
        for i in range(0, len(words), 3):
            token_slice = " ".join(words[i:i+3]) + " "
            yield f"data: {json.dumps({'type': 'token', 'token': token_slice})}\n\n"
            await asyncio.sleep(0.01)

        asst_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conv.id,
            role="assistant",
            content=structured_res.summary,
            structured_data=structured_res.model_dump(),
            created_at=datetime.datetime.utcnow()
        )
        db.add(asst_msg)
        conv.updated_at = datetime.datetime.utcnow()
        db.commit()

        complete_payload = {
            "type": "complete",
            "conversation_id": conv.id,
            "message_id": asst_msg.id,
            "response": structured_res.model_dump()
        }
        yield f"data: {json.dumps(complete_payload)}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")


@router.get("/conversations", response_model=List[ConversationSummary], summary="List all consultations")
def list_conversations(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Conversation)
    if current_user:
        query = query.filter(Conversation.user_id == current_user.id)
    else:
        query = query.filter(Conversation.user_id == None)

    convs = query.order_by(Conversation.updated_at.desc()).all()
    summaries = []
    for c in convs:
        summaries.append(
            ConversationSummary(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=len(c.messages)
            )
        )
    return summaries


@router.get("/conversations/{conversation_id}", response_model=List[MessageItem], summary="Get messages in a consultation")
def get_conversation_messages(
    conversation_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if conv.user_id and (not current_user or conv.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this consultation.")

    return [
        MessageItem(
            id=m.id,
            role=m.role,
            content=m.content,
            structured_data=m.structured_data,
            created_at=m.created_at
        )
        for m in conv.messages
    ]


@router.delete("/conversations/{conversation_id}", summary="Delete a consultation session")
def delete_conversation(
    conversation_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if conv.user_id and (not current_user or conv.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to delete this consultation.")

    db.delete(conv)
    db.commit()
    return {"status": "success", "deleted_id": conversation_id}


@router.post("/messages/{message_id}/feedback", summary="Submit feedback for an assistant response")
def submit_message_feedback(
    message_id: str,
    req: FeedbackRequest,
    db: Session = Depends(get_db)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    msg.feedback_rating = req.rating
    msg.feedback_text = req.feedback_text
    db.commit()

    return {"status": "success", "message_id": message_id, "rating": req.rating}

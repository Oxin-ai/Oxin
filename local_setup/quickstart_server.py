import os
import asyncio
import uuid
import traceback
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from dotenv import load_dotenv
from bolna.helpers.utils import store_file
from bolna.prompts import *
from bolna.helpers.logger_config import configure_logger
from bolna.models import *
from bolna.llms import LiteLLM
from bolna.agent_manager.assistant_manager import AssistantManager
from bolna.auth import auth_router, get_current_user, get_db
from bolna.auth.models import User
from bolna.agent_management import agent_router
from bolna.agent_management.service import AgentService
from sqlalchemy.orm import Session

load_dotenv()
logger = configure_logger(__name__)

redis_pool = redis.ConnectionPool.from_url(os.getenv('REDIS_URL'), decode_responses=True)
redis_client = redis.Redis.from_pool(redis_pool)
active_websockets: List[WebSocket] = []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include auth routes
app.include_router(auth_router)
# Include agent management routes
app.include_router(agent_router)


# Agent management endpoints are now handled by agent_router


############################################################################################# 
# Websocket 
#############################################################################################
@app.websocket("/chat/v1/{agent_id}")
async def websocket_endpoint(agent_id: str, websocket: WebSocket, user_agent: str = Query(None)):
    logger.info("Connected to ws")
    await websocket.accept()
    active_websockets.append(websocket)
    agent_config, context_data = None, None
    
    # Get database session
    db = next(get_db())
    
    try:
        # For now, we'll allow unauthenticated websocket access but this should be secured
        # In production, implement proper websocket authentication
        
        # Try to get agent from database (assuming tenant_id = 1 for now)
        # TODO: Implement proper websocket authentication to get real tenant_id
        agent_data = AgentService.get_agent_for_execution(db, agent_id, tenant_id=1)
        
        if not agent_data:
            # Fallback to Redis for backward compatibility during migration
            retrieved_agent_config = await redis_client.get(agent_id)
            if not retrieved_agent_config:
                raise HTTPException(status_code=404, detail="Agent not found")
            agent_config = json.loads(retrieved_agent_config)
        else:
            agent_config, prompt_data = agent_data
            logger.info(f"Retrieved agent config from MySQL: {agent_config}")
            
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=404, detail="Agent not found")
    finally:
        db.close()

    assistant_manager = AssistantManager(agent_config, websocket, agent_id)

    try:
        async for index, task_output in assistant_manager.run(local=True):
            logger.info(task_output)
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"error in executing {e}")

import uuid
import json
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from pydantic import BaseModel

from bolna.auth.database import get_db
from bolna.auth.dependencies import get_current_user
from bolna.auth.models import User
from bolna.agent_management.models import Agent, AgentConfiguration, AgentPrompt
from bolna.models import AgentModel

router = APIRouter(prefix="/agent", tags=["agents"])


class CreateAgentPayload(BaseModel):
    agent_config: AgentModel
    agent_prompts: Optional[Dict[str, Dict[str, str]]] = None


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    agent_type: str
    status: str
    created_at: str
    updated_at: str


@router.post("")
async def create_agent(
    agent_data: CreateAgentPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new agent for the current user's tenant."""
    try:
        agent_uuid = str(uuid.uuid4())
        config_data = agent_data.agent_config.model_dump()
        config_data["assistant_status"] = "seeding"
        
        # Process extraction tasks if present
        if len(config_data.get('tasks', [])) > 0:
            for index, task in enumerate(config_data['tasks']):
                if task.get('task_type') == "extraction":
                    # Handle extraction prompt generation here if needed
                    pass
        
        # Create agent record
        db_agent = Agent(
            uuid=agent_uuid,
            tenant_id=current_user.tenant_id,
            created_by_user_id=current_user.id,
            name=config_data.get("agent_name", "Unnamed Agent"),
            agent_type=config_data.get("agent_type", "other"),
            welcome_message=config_data.get("agent_welcome_message")
        )
        db.add(db_agent)
        db.flush()  # Get the agent ID
        
        # Create configuration
        db_config = AgentConfiguration(
            agent_id=db_agent.id,
            configuration_data=config_data,
            version=1,
            is_active=True
        )
        db.add(db_config)
        
        # Create prompts if provided
        if agent_data.agent_prompts:
            db_prompt = AgentPrompt(
                agent_id=db_agent.id,
                prompt_data=agent_data.agent_prompts,
                version=1,
                is_active=True
            )
            db.add(db_prompt)
        
        db.commit()
        
        return {"agent_id": agent_uuid, "state": "created"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent by ID within user's tenant."""
    agent = db.query(Agent).filter(
        and_(
            Agent.tenant_id == current_user.tenant_id,
            Agent.uuid == agent_id,
            Agent.status != "deleted"
        )
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get active configuration
    config = db.query(AgentConfiguration).filter(
        and_(
            AgentConfiguration.agent_id == agent.id,
            AgentConfiguration.is_active == True
        )
    ).first()
    
    # Get active prompts
    prompts = db.query(AgentPrompt).filter(
        and_(
            AgentPrompt.agent_id == agent.id,
            AgentPrompt.is_active == True
        )
    ).first()
    
    result = config.configuration_data if config else {}
    if prompts:
        result["agent_prompts"] = prompts.prompt_data
    
    return result


@router.put("/{agent_id}")
async def update_agent(
    agent_id: str,
    agent_data: CreateAgentPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update agent within user's tenant."""
    try:
        # Find agent
        agent = db.query(Agent).filter(
            and_(
                Agent.tenant_id == current_user.tenant_id,
                Agent.uuid == agent_id,
                Agent.status != "deleted"
            )
        ).first()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        config_data = agent_data.agent_config.model_dump()
        config_data["assistant_status"] = "updated"
        
        # Process extraction tasks if present
        if len(config_data.get('tasks', [])) > 0:
            for index, task in enumerate(config_data['tasks']):
                if task.get('task_type') == "extraction":
                    # Handle extraction prompt generation here if needed
                    pass
        
        # Get current version numbers
        current_config = db.query(AgentConfiguration).filter(
            and_(
                AgentConfiguration.agent_id == agent.id,
                AgentConfiguration.is_active == True
            )
        ).first()
        
        current_prompt = db.query(AgentPrompt).filter(
            and_(
                AgentPrompt.agent_id == agent.id,
                AgentPrompt.is_active == True
            )
        ).first()
        
        # Deactivate current configurations
        if current_config:
            current_config.is_active = False
        if current_prompt:
            current_prompt.is_active = False
        
        # Create new configuration version
        new_version = (current_config.version + 1) if current_config else 1
        db_config = AgentConfiguration(
            agent_id=agent.id,
            configuration_data=config_data,
            version=new_version,
            is_active=True
        )
        db.add(db_config)
        
        # Create new prompt version if provided
        if agent_data.agent_prompts:
            prompt_version = (current_prompt.version + 1) if current_prompt else 1
            db_prompt = AgentPrompt(
                agent_id=agent.id,
                prompt_data=agent_data.agent_prompts,
                version=prompt_version,
                is_active=True
            )
            db.add(db_prompt)
        
        # Update agent metadata
        agent.name = config_data.get("agent_name", agent.name)
        agent.agent_type = config_data.get("agent_type", agent.agent_type)
        agent.welcome_message = config_data.get("agent_welcome_message", agent.welcome_message)
        
        db.commit()
        
        return {"agent_id": agent_id, "state": "updated"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete agent within user's tenant."""
    agent = db.query(Agent).filter(
        and_(
            Agent.tenant_id == current_user.tenant_id,
            Agent.uuid == agent_id,
            Agent.status != "deleted"
        )
    ).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Soft delete
    agent.status = "deleted"
    agent.deleted_at = func.now()
    
    db.commit()
    
    return {"agent_id": agent_id, "state": "deleted"}


@router.get("")
async def list_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all agents in user's tenant."""
    agents = db.query(Agent).filter(
        and_(
            Agent.tenant_id == current_user.tenant_id,
            Agent.status != "deleted"
        )
    ).order_by(Agent.created_at.desc()).all()
    
    agent_list = []
    for agent in agents:
        agent_list.append({
            "agent_id": agent.uuid,
            "name": agent.name,
            "agent_type": agent.agent_type,
            "status": agent.status,
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat()
        })
    
    return {"agents": agent_list}
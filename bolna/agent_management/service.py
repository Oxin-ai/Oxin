from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from bolna.agent_management.models import Agent, AgentConfiguration, AgentPrompt


class AgentService:
    """Service layer for agent database operations."""
    
    @staticmethod
    def get_agent_for_execution(db: Session, agent_uuid: str, tenant_id: int) -> Optional[Dict[str, Any]]:
        """Get agent configuration for runtime execution."""
        agent = db.query(Agent).filter(
            and_(
                Agent.tenant_id == tenant_id,
                Agent.uuid == agent_uuid,
                Agent.status == "active"
            )
        ).first()
        
        if not agent:
            return None
        
        # Get active configuration
        config = db.query(AgentConfiguration).filter(
            and_(
                AgentConfiguration.agent_id == agent.id,
                AgentConfiguration.is_active == True
            )
        ).first()
        
        if not config:
            return None
        
        # Get active prompts
        prompts = db.query(AgentPrompt).filter(
            and_(
                AgentPrompt.agent_id == agent.id,
                AgentPrompt.is_active == True
            )
        ).first()
        
        result = config.configuration_data.copy()
        result["agent_name"] = agent.name
        result["agent_welcome_message"] = agent.welcome_message
        
        return result, prompts.prompt_data if prompts else None
    
    @staticmethod
    def get_agent_prompts(db: Session, agent_uuid: str, tenant_id: int) -> Optional[Dict[str, Any]]:
        """Get agent prompts for runtime execution."""
        agent = db.query(Agent).filter(
            and_(
                Agent.tenant_id == tenant_id,
                Agent.uuid == agent_uuid,
                Agent.status == "active"
            )
        ).first()
        
        if not agent:
            return None
        
        prompts = db.query(AgentPrompt).filter(
            and_(
                AgentPrompt.agent_id == agent.id,
                AgentPrompt.is_active == True
            )
        ).first()
        
        return prompts.prompt_data if prompts else None
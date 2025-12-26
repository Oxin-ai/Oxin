import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class AgentCallInitiator:
    def __init__(self):
        # Twilio configuration from environment
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Bolna server configuration
        self.bolna_server_url = os.getenv('BOLNA_SERVER_URL', 'http://localhost:5001')
        self.twilio_server_url = os.getenv('TWILIO_SERVER_URL', 'http://localhost:8001')
        
        # Validate required environment variables
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required environment variables are set"""
        required_vars = [
            'TWILIO_ACCOUNT_SID', 
            'TWILIO_AUTH_TOKEN', 
            'TWILIO_PHONE_NUMBER'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    def create_airbnb_agent(self):
        """Create an Airbnb customer service agent"""
        agent_config = {
            "agent_config": {
                "agent_name": "Airbnb Customer Service",
                "agent_type": "other",
                "tasks": [
                    {
                        "task_type": "conversation",
                        "toolchain": {
                            "execution": "parallel",
                            "pipelines": [["transcriber", "llm", "synthesizer"]]
                        },
                        "tools_config": {
                            "input": {"format": "wav", "provider": "twilio"},
                            "output": {"format": "wav", "provider": "twilio"},
                            "transcriber": {
                                "encoding": "mulaw",
                                "language": "en",
                                "provider": "deepgram",
                                "stream": True,
                                "model": "nova-2"
                            },
                            "llm_agent": {
                                "agent_type": "simple_llm_agent",
                                "agent_flow_type": "streaming",
                                "llm_config": {
                                    "provider": "openai",
                                    "model": "gpt-4o-mini",
                                    "temperature": 0.3,
                                    "request_json": True
                                }
                            },
                            "synthesizer": {
                                "audio_format": "wav",
                                "provider": "elevenlabs",
                                "stream": True,
                                "provider_config": {
                                    "voice": "George",
                                    "model": "eleven_turbo_v2_5",
                                    "voice_id": "JBFqnCBsd6RMkjVDRZzb"
                                },
                                "buffer_size": 100.0
                            }
                        },
                        "task_config": {
                            "hangup_after_silence": 30.0
                        }
                    }
                ],
                "agent_welcome_message": "Hello! I'm your Airbnb customer service assistant. How can I help you today?"
            },
            "agent_prompts": {
                "task_1": {
                    "system_prompt": "You are a helpful Airbnb customer service representative. Assist customers with booking inquiries, property questions, cancellations, and general support. Be friendly, professional, and solution-oriented."
                }
            }
        }
        
        try:
            response = requests.post(
                f"{self.bolna_server_url}/agent",
                json=agent_config,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                agent_data = response.json()
                print(f"✅ Agent created successfully!")
                print(f"Agent ID: {agent_data['agent_id']}")
                return agent_data['agent_id']
            else:
                print(f"❌ Failed to create agent: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            return None
    
    def make_call(self, agent_id, recipient_phone_number):
        """Initiate a call using the created agent"""
        call_payload = {
            "agent_id": agent_id,
            "recipient_phone_number": recipient_phone_number
        }
        
        try:
            response = requests.post(
                f"{self.twilio_server_url}/call",
                json=call_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ Call initiated successfully!")
                print(f"Calling: {recipient_phone_number}")
                return True
            else:
                print(f"❌ Failed to initiate call: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error making call: {e}")
            return False

def main():
    """Main function to create agent and make call"""
    print("🚀 Airbnb Agent Call Initiator")
    print("=" * 40)
    
    # Initialize the call initiator
    initiator = AgentCallInitiator()
    
    # Get user input
    recipient_number = input("📞 Enter recipient phone number (with country code, e.g., +919301958764): ").strip()
    
    if not recipient_number:
        print("❌ Phone number is required!")
        return
    
    # Option 1: Create new agent
    print("\n🤖 Creating Airbnb customer service agent...")
    agent_id = initiator.create_airbnb_agent()
    
    if not agent_id:
        print("❌ Failed to create agent. Exiting...")
        return
    
    # Option 2: Use existing agent ID (uncomment if you have one)
    agent_id = input("🆔 Enter existing Agent ID (or press Enter to create new): ").strip()
    if not agent_id:
        agent_id = initiator.create_airbnb_agent()
    
    if agent_id:
        print(f"\n📞 Initiating call with Agent ID: {agent_id}")
        success = initiator.make_call(agent_id, recipient_number)
        
        if success:
            print("\n✅ Call initiated! Check your phone.")
            print("💡 The agent will introduce itself and assist with Airbnb queries.")
        else:
            print("\n❌ Call initiation failed!")
    else:
        print("❌ No agent ID available!")

if __name__ == "__main__":
    main()
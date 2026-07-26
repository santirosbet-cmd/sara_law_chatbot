"""
Tool definitions for the chatbot — in OpenAI format.
Claude provider converts these automatically.
"""

# All tools available to the AI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_client_info",
            "description": (
                "Save or update client information to the database. Call this silently "
                "when the client provides their name, phone, email, or other personal details "
                "during the conversation. Also call to record intake type, situation summary, "
                "and urgency once those are known."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "description": "Client's first name"},
                    "last_name": {"type": "string", "description": "Client's last name"},
                    "email": {"type": "string", "description": "Client's real email address (captured during chat)"},
                    "phone": {"type": "string", "description": "Client's phone number"},
                    "intake_type": {
                        "type": "string",
                        "enum": ["Personal Injury", "Criminal Defense"],
                        "description": "Practice area for this intake",
                    },
                    "situation_summary": {
                        "type": "string",
                        "description": "Brief summary of the client's situation or case",
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["Low", "Normal", "High", "Urgent"],
                        "description": "How urgent is this matter — use Urgent for active criminal cases or emergency injuries",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Any additional notes about the client's situation",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "flag_for_review",
            "description": (
                "Flag your response for lawyer review before sending to the client. "
                "Use this when the client asks for specific legal advice, case outcome "
                "predictions, or anything that requires an attorney's judgment. "
                "The client will receive a placeholder message."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why this needs lawyer review",
                    },
                    "draft_response": {
                        "type": "string",
                        "description": "Your draft response for the lawyer to review/edit",
                    },
                },
                "required": ["reason", "draft_response"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_case",
            "description": (
                "Create a new case for the client when enough information has been gathered. "
                "Call this after understanding the client's situation during intake."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title for the case (e.g., 'Car Accident on I-10', 'DWI Charge in Harris County')",
                    },
                    "description": {
                        "type": "string",
                        "description": "Summary of the case details gathered so far",
                    },
                },
                "required": ["title"],
            },
        },
    },
]

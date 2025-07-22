import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    AssistantMessage,
    ChatCompletionsToolDefinition,
    CompletionsFinishReason,
    FunctionDefinition,
    SystemMessage,
    ToolMessage,
    UserMessage,
)
from azure.identity import DefaultAzureCredential

# Configure logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Represents a single conversation exchange."""

    user_input: str
    assistant_response: str
    timestamp: str
    thinking_techniques_used: List[str]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the critical thinking assistant."""
    parser = argparse.ArgumentParser(
        description="Critical Thinking Chat Assistant - Challenge assumptions, promote critical thinking, and facilitate deeper analysis",
        epilog="Example: python critical_thinking_chat.py --question 'I think social media is bad for society' --interactive",
    )
    parser.add_argument(
        "--question", "-q", type=str, help="Initial question/statement to analyze"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Enable interactive mode for extended conversations",
    )
    parser.add_argument(
        "--endpoint", type=str, help="Override PROJECT_ENDPOINT environment variable"
    )
    parser.add_argument(
        "--model", type=str, help="Override MODEL_DEPLOYMENT_NAME environment variable"
    )
    return parser.parse_args()


def load_environment() -> None:
    """Load environment variables from .env file if available."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
        logger.info("Environment variables loaded from .env file")
    except ImportError:
        logger.info("python-dotenv not available, using system environment variables")


def initialize_client(endpoint: Optional[str] = None) -> ChatCompletionsClient:
    """
    Initialize and test the Azure AI Inference client.

    Args:
        endpoint: Optional override for PROJECT_ENDPOINT

    Returns:
        ChatCompletionsClient: Configured client for AI inference

    Raises:
        SystemExit: If connection fails or required environment variables are missing
    """
    load_environment()

    # Get project endpoint from argument or environment
    project_endpoint = endpoint or os.environ.get("PROJECT_ENDPOINT")
    if not project_endpoint:
        logger.error(
            "PROJECT_ENDPOINT environment variable is required or must be provided via --endpoint argument"
        )
        print(
            "Error: PROJECT_ENDPOINT environment variable is required or must be provided via --endpoint argument"
        )
        sys.exit(1)

    # Configure authentication using DefaultAzureCredential
    credential = DefaultAzureCredential()

    try:
        # Create the Azure AI Inference client with proper credential scopes
        # For Azure AI Foundry projects, use the ai.azure.com scope
        # Let the SDK use the default/latest supported API version
        client = ChatCompletionsClient(
            endpoint=project_endpoint,
            credential=credential,
            credential_scopes=["https://ai.azure.com/.default"]
        )

        logger.info("Created ChatCompletionsClient for endpoint: %s", project_endpoint)
        print(f"Connected to Azure AI Foundry project: {project_endpoint}")

        # Test the connection by attempting a simple validation
        # Note: We'll test the actual inference capability when making the first request
        return client

    except Exception as e:
        logger.error("Failed to initialize client: %s", e)
        print(f"Connection failed: {e}")
        print("Please check your PROJECT_ENDPOINT and authentication.")
        sys.exit(1)


def get_critical_thinking_system_prompt() -> str:
    """
    Get the system prompt that defines the critical thinking assistant behavior.

    Returns:
        str: System prompt for the critical thinking assistant
    """
    return """You are a Critical Thinking Assistant, designed to help users develop deeper analytical skills and examine their assumptions through thoughtful questioning. Your role is to:

**Core Principles:**
1. Challenge assumptions by asking clarifying questions
2. Provide alternative perspectives without taking sides
3. Guide users through evidence-based reasoning
4. Encourage examination of biases and preconceptions
5. Use Socratic questioning to stimulate deeper inquiry

**Tool Usage:**
- When users present logical arguments or reasoning structures, you can use the evaluate_syllogism tool to analyze their logical validity
- Use tool results to enhance your critical thinking guidance and identify logical fallacies
- Integrate tool analysis into your questioning and discussion to promote deeper understanding

**Questioning Techniques:**
- Ask "What evidence supports this view?"
- Explore "What might someone who disagrees say?"
- Inquire "How did you arrive at this conclusion?"
- Challenge with "What assumptions are you making?"
- Probe with "What are the implications of this belief?"
- Investigate "Have you considered alternative explanations?"

**Conversation Approach:**
- Build upon previous exchanges to maintain context
- Use structured frameworks like "5 Whys" when appropriate
- Encourage users to think through problems systematically
- Present counterarguments respectfully and constructively
- Help users identify logical fallacies in their reasoning

**Response Style:**
- Be respectful but intellectually challenging
- Ask follow-up questions that deepen analysis
- Avoid simply providing answers; instead, guide users to discover insights
- Use examples and analogies to illustrate different perspectives
- Maintain a supportive tone while promoting rigorous thinking

Remember: Your goal is not to convince users of any particular viewpoint, but to help them think more critically and thoroughly about complex topics."""


def evaluate_syllogism(major_premise: str, minor_premise: str, conclusion: str) -> str:
    """
    Evaluate the logical validity of a syllogism.

    This function analyzes the logical structure of a syllogism consisting of
    a major premise, minor premise, and conclusion to determine validity and
    identify logical errors or fallacies.

    Args:
        major_premise: The major premise statement (universal statement)
        minor_premise: The minor premise statement (specific statement)
        conclusion: The conclusion statement (derived statement)

    Returns:
        JSON string containing detailed validity analysis including:
        - valid: boolean indicating logical validity
        - form: type of syllogism (categorical, conditional, disjunctive)
        - analysis: detailed explanation of the logical structure
        - errors: list of identified logical fallacies or errors
    """
    try:
        # Analyze syllogism structure and validity
        analysis_result = {
            "major_premise": major_premise,
            "minor_premise": minor_premise,
            "conclusion": conclusion,
            "valid": False,
            "form": "categorical",  # Default to categorical
            "analysis": "",
            "errors": []
        }

        # Basic validation checks
        if not all([major_premise.strip(), minor_premise.strip(), conclusion.strip()]):
            analysis_result["errors"].append("incomplete_premises")
            analysis_result["analysis"] = "One or more premises are empty or missing."
            return json.dumps(analysis_result, indent=2)

        # Identify syllogism type based on structure
        if any(word in major_premise.lower() for word in ["if ", "then ", "implies"]):
            analysis_result["form"] = "conditional"
        elif any(word in major_premise.lower() for word in [" either ", " or ", " neither "]):
            analysis_result["form"] = "disjunctive"
        else:
            analysis_result["form"] = "categorical"

        # Check for common logical fallacies and patterns
        major_lower = major_premise.lower()

        # Check for overgeneralization (hasty generalization)
        if any(word in major_lower for word in ["all", "every", "always", "never", "no one", "everyone"]):
            if not _has_sufficient_evidence(major_premise):
                analysis_result["errors"].append("hasty_generalization")

        # Check for affirming the consequent (if conditional)
        if analysis_result["form"] == "conditional":
            if "if" in major_lower and "then" in major_lower:
                # Basic check for affirming consequent pattern
                if _is_affirming_consequent(major_premise, minor_premise, conclusion):
                    analysis_result["errors"].append("affirming_consequent")
                    analysis_result["valid"] = False
                elif _is_valid_modus_ponens(major_premise, minor_premise, conclusion):
                    analysis_result["valid"] = True

        # Check for undistributed middle term (categorical syllogisms)
        elif analysis_result["form"] == "categorical":
            if _has_undistributed_middle(major_premise, minor_premise, conclusion):
                analysis_result["errors"].append("undistributed_middle")
                analysis_result["valid"] = False
            elif _is_valid_categorical_syllogism(major_premise, minor_premise, conclusion):
                analysis_result["valid"] = True

        # Generate analysis text based on findings
        if analysis_result["valid"] and not analysis_result["errors"]:
            analysis_result["analysis"] = f"This is a valid {analysis_result['form']} syllogism. The logical structure is sound and the conclusion follows from the premises."
        elif analysis_result["errors"]:
            error_descriptions = {
                "hasty_generalization": "The major premise makes a sweeping generalization without sufficient evidence",
                "affirming_consequent": "This commits the fallacy of affirming the consequent in conditional reasoning",
                "undistributed_middle": "The middle term is not properly distributed, making the conclusion invalid",
                "incomplete_premises": "One or more premises are missing or incomplete"
            }

            error_details = [error_descriptions.get(error, error) for error in analysis_result["errors"]]
            analysis_result["analysis"] = f"This {analysis_result['form']} syllogism contains logical errors: {', '.join(error_details)}. The conclusion does not necessarily follow from the premises."
        else:
            analysis_result["analysis"] = f"This {analysis_result['form']} syllogism requires further analysis to determine validity."

        return json.dumps(analysis_result, indent=2)

    except Exception as e:
        logger.error("Error in evaluate_syllogism: %s", e)
        error_result = {
            "major_premise": major_premise,
            "minor_premise": minor_premise,
            "conclusion": conclusion,
            "valid": False,
            "form": "unknown",
            "analysis": f"Error occurred during analysis: {str(e)}",
            "errors": ["analysis_error"]
        }
        return json.dumps(error_result, indent=2)


def _has_sufficient_evidence(premise: str) -> bool:
    """Check if a universal statement has qualifying language that suggests sufficient evidence."""
    premise_lower = premise.lower()

    # Check for qualifying words that indicate careful consideration
    qualifying_words = ["most", "many", "some", "typically", "generally", "usually", "often"]
    has_qualifiers = any(word in premise_lower for word in qualifying_words)

    # Check for well-established universal truths that don't require qualification
    established_truths = [
        "all humans are mortal",
        "all living things die",
        "all circles are round",
        "all bachelors are unmarried",
        "all mothers are female"
    ]

    is_established_truth = any(truth in premise_lower for truth in established_truths)

    # A premise has sufficient evidence if it has qualifiers OR is an established truth
    return has_qualifiers or is_established_truth


def _is_affirming_consequent(major: str, minor: str, conclusion: str) -> bool:
    """Basic check for affirming the consequent fallacy pattern."""
    # Affirming consequent: If P then Q, Q, therefore P
    # This is a very simplified check
    if not ("if" in major.lower() and "then" in major.lower()):
        return False

    # Extract rough consequent from major premise (after "then")
    major_parts = major.lower().split("then")
    if len(major_parts) < 2:
        return False

    consequent_words = major_parts[1].strip().split()[:3]  # First few words
    minor_words = minor.lower().split()

    # Check if minor premise affirms the consequent rather than antecedent
    return any(word in minor_words for word in consequent_words if len(word) > 2)


def _is_valid_modus_ponens(major: str, minor: str, conclusion: str) -> bool:
    """Check for valid modus ponens pattern (If P then Q, P, therefore Q)."""
    if not ("if" in major.lower() and "then" in major.lower()):
        return False

    # Extract antecedent (between "if" and "then")
    major_lower = major.lower()
    if_pos = major_lower.find("if")
    then_pos = major_lower.find("then")

    if if_pos == -1 or then_pos == -1 or then_pos <= if_pos:
        return False

    antecedent = major_lower[if_pos + 2:then_pos].strip()
    antecedent_words = antecedent.split()[:3]  # First few key words
    minor_words = minor.lower().split()

    # Check if minor premise affirms the antecedent
    return any(word in minor_words for word in antecedent_words if len(word) > 2)


def _has_undistributed_middle(major: str, minor: str, conclusion: str) -> bool:
    """Check for undistributed middle term fallacy in categorical syllogisms."""
    # Simplified check for common patterns like "Some A are B, Some B are C, therefore Some A are C"
    return ("some" in major.lower() and "some" in minor.lower() and
            not any(word in major.lower() for word in ["all", "every"]))


def _is_valid_categorical_syllogism(major: str, minor: str, conclusion: str) -> bool:
    """Check for valid categorical syllogism patterns."""
    major_lower = major.lower()
    minor_lower = minor.lower()
    conclusion.lower()

    # Pattern 1: "All A are B, X is A, therefore X is B" (Barbara syllogism)
    if ("all" in major_lower or "every" in major_lower) and " is " in minor_lower:
        return True

    # Pattern 2: "All A are B, All B are C, therefore All A are C"
    if (("all" in major_lower or "every" in major_lower) and
        ("all" in minor_lower or "every" in minor_lower)):
        return True

    # Pattern 3: "No A are B, X is A, therefore X is not B"
    if "no " in major_lower and " is " in minor_lower:
        return True

    return False


def create_syllogism_tool() -> ChatCompletionsToolDefinition:
    """
    Create the syllogism evaluation tool definition for the AI model.

    Returns:
        ChatCompletionsToolDefinition: Tool definition for syllogism evaluation
    """
    return ChatCompletionsToolDefinition(
        function=FunctionDefinition(
            name="evaluate_syllogism",
            description="Evaluates the logical validity of a syllogism consisting of major premise, minor premise, and conclusion. Returns detailed analysis including validity, logical form, and identification of any logical fallacies or errors.",
            parameters={
                "type": "object",
                "properties": {
                    "major_premise": {
                        "type": "string",
                        "description": "The major premise of the syllogism (universal statement)"
                    },
                    "minor_premise": {
                        "type": "string",
                        "description": "The minor premise of the syllogism (specific statement)"
                    },
                    "conclusion": {
                        "type": "string",
                        "description": "The conclusion of the syllogism (derived statement)"
                    }
                },
                "required": ["major_premise", "minor_premise", "conclusion"]
            }
        )
    )


def create_conversation_memory() -> List[Any]:
    """
    Create initial conversation memory with system prompt.

    Returns:
        List[Any]: Initial conversation history with system message
    """
    system_prompt = get_critical_thinking_system_prompt()
    return [SystemMessage(content=system_prompt)]


def add_to_conversation(
    conversation: List[Any], role: str, content: str
) -> None:
    """
    Add a message to the conversation history.

    Args:
        conversation: The conversation history list
        role: The role of the message sender ('user' or 'assistant')
        content: The message content
    """
    if role == "user":
        conversation.append(UserMessage(content=content))
    elif role == "assistant":
        conversation.append(AssistantMessage(content=content))
    else:
        raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'.")

    logger.debug("Added %s message to conversation: %s...", role, content[:50])


def get_ai_response(
    client: ChatCompletionsClient, conversation: List[Any], model_name: str
) -> str:
    """
    Get a response from the AI model using the conversation history.
    Handles tool calling for syllogism evaluation when requested by the model.

    Args:
        client: The ChatCompletionsClient instance
        conversation: The conversation history
        model_name: The model deployment name

    Returns:
        str: The AI assistant's response

    Raises:
        RuntimeError: If the API call fails
    """
    try:
        # Create the syllogism evaluation tool
        syllogism_tool = create_syllogism_tool()

        # Make the API call with standard parameters and tool support
        response = client.complete(
            messages=conversation,
            model=model_name,
            tools=[syllogism_tool],
            max_tokens=800,
            temperature=1.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Check if the model wants to use tools
        if response.choices[0].finish_reason == CompletionsFinishReason.TOOL_CALLS:
            logger.info("Model requested tool calls, processing syllogism evaluation")

            # Add the assistant's tool call message to conversation
            conversation.append(AssistantMessage(tool_calls=response.choices[0].message.tool_calls))

            # Process each tool call
            if response.choices[0].message.tool_calls is not None:
                for tool_call in response.choices[0].message.tool_calls:
                    if tool_call.function.name == "evaluate_syllogism":
                        logger.info("Executing syllogism evaluation tool")

                        try:
                            # Parse tool arguments
                            function_args = json.loads(tool_call.function.arguments)
                            logger.debug("Tool arguments: %s", function_args)

                            # Execute the syllogism evaluation function
                            tool_result = evaluate_syllogism(**function_args)
                            logger.debug("Tool result: %s", tool_result[:200] + "..." if len(tool_result) > 200 else tool_result)

                            # Add tool response to conversation
                            conversation.append(ToolMessage(content=tool_result, tool_call_id=tool_call.id))

                        except json.JSONDecodeError as e:
                            logger.error("Failed to parse tool arguments: %s", e)
                            error_result = json.dumps({
                                "error": "Invalid tool arguments provided",
                                "details": str(e)
                            })
                            conversation.append(ToolMessage(content=error_result, tool_call_id=tool_call.id))

                        except Exception as e:
                            logger.error("Tool execution failed: %s", e)
                            error_result = json.dumps({
                                "error": f"Tool execution failed: {str(e)}"
                            })
                            conversation.append(ToolMessage(content=error_result, tool_call_id=tool_call.id))

            # Get the final response with tool results incorporated
            final_response = client.complete(
                messages=conversation,
                model=model_name,
                tools=[syllogism_tool],
                max_tokens=800,
                temperature=1.0,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            # Extract and return final response content
            if (
                hasattr(final_response, "choices")
                and final_response.choices
                and len(final_response.choices) > 0
            ):
                choice = final_response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    return choice.message.content
        else:
            # Standard response without tool calls
            if (
                hasattr(response, "choices")
                and response.choices
                and len(response.choices) > 0
            ):
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    return choice.message.content

        raise RuntimeError("No response received from the model")

    except Exception as e:
        logger.error("Failed to get AI response: %s", e)
        raise RuntimeError(f"Unable to get response from AI: {e}") from e


def process_single_question(
    client: ChatCompletionsClient, question: str, model_name: str
) -> None:
    """
    Process a single question in non-interactive mode.

    Args:
        client: The ChatCompletionsClient instance
        question: The user's question or statement
        model_name: The model deployment name
    """
    print("\n=== CRITICAL THINKING ANALYSIS ===")
    print(f"Your statement: {question}")
    print("=" * 50)

    try:
        # Create conversation memory
        conversation = create_conversation_memory()
        add_to_conversation(conversation, "user", question)

        # Get AI response
        response = get_ai_response(client, conversation, model_name)

        print("\nCritical Thinking Assistant:")
        print(response)
        print("\n" + "=" * 50)

    except Exception as e:
        print(f"Error processing question: {e}")
        logger.error("Error in process_single_question: %s", e)


def interactive_mode(
    client: ChatCompletionsClient,
    model_name: str,
    initial_question: Optional[str] = None,
) -> None:
    """
    Run the assistant in interactive mode for extended conversations.

    Args:
        client: The ChatCompletionsClient instance
        model_name: The model deployment name
        initial_question: Optional initial question to start the conversation
    """
    print("\n" + "=" * 60)
    print("           CRITICAL THINKING CHAT ASSISTANT")
    print("=" * 60)
    print("I'm here to help you think more deeply about complex topics.")
    print("I'll challenge your assumptions and guide you through critical analysis.")
    print("\nType 'quit', 'exit', or 'q' to end our conversation.")
    print("Press Ctrl+C at any time to exit cleanly.")
    print("=" * 60)

    # Create conversation memory
    conversation = create_conversation_memory()
    conversation_turns: List[ConversationTurn] = []

    try:
        # Handle initial question if provided
        if initial_question:
            print(f"\nStarting with your statement: {initial_question}")
            add_to_conversation(conversation, "user", initial_question)

            try:
                response = get_ai_response(client, conversation, model_name)
                add_to_conversation(conversation, "assistant", response)

                print("\nCritical Thinking Assistant:")
                print(response)

                # Record the turn
                turn = ConversationTurn(
                    user_input=initial_question,
                    assistant_response=response,
                    timestamp=datetime.now().isoformat(),
                    thinking_techniques_used=[
                        "Socratic questioning",
                        "Assumption challenging",
                    ],
                )
                conversation_turns.append(turn)

            except Exception as e:
                print(f"Error processing initial question: {e}")

        # Main interactive loop
        while True:
            try:
                print("\n" + "-" * 50)
                user_input = input("\nYour response or new statement: ").strip()

                # Check for exit commands
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\nThank you for engaging in critical thinking!")
                    print("Remember to question assumptions and examine evidence.")
                    break

                # Skip empty input
                if not user_input:
                    print("Please provide a statement or question to analyze.")
                    continue

                # Add user input to conversation
                add_to_conversation(conversation, "user", user_input)

                # Get AI response
                response = get_ai_response(client, conversation, model_name)
                add_to_conversation(conversation, "assistant", response)

                print("\nCritical Thinking Assistant:")
                print(response)

                # Record the turn
                turn = ConversationTurn(
                    user_input=user_input,
                    assistant_response=response,
                    timestamp=datetime.now().isoformat(),
                    thinking_techniques_used=[
                        "Evidence-based reasoning",
                        "Alternative perspectives",
                    ],
                )
                conversation_turns.append(turn)

                # Limit conversation length to prevent token overflow
                if (
                    len(conversation) > 20
                ):  # Keep last 18 messages + system prompt + current
                    conversation = [conversation[0]] + conversation[-17:]
                    logger.info(
                        "Trimmed conversation history to prevent token overflow"
                    )

            except KeyboardInterrupt:
                print("\n\nThank you for the thoughtful discussion!")
                break
            except Exception as e:
                print(f"Error processing your input: {e}")
                logger.error("Error in interactive mode: %s", e)
                continue

    except KeyboardInterrupt:
        print("\n\nGoodbye!")

    # Display conversation summary
    if conversation_turns:
        print(f"\nConversation Summary: {len(conversation_turns)} exchanges completed")
        logger.info(
            "Interactive session completed with %d turns", len(conversation_turns)
        )


def main() -> None:
    """
    Main entry point for the Critical Thinking Chat Assistant.
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()

        # Get model deployment name from environment or command line
        model_deployment_name = args.model or os.environ.get(
            "MODEL_DEPLOYMENT_NAME", "gpt-4o"
        )

        # Initialize the client
        client = initialize_client(endpoint=args.endpoint)

        # Determine execution mode
        if args.interactive:
            # Interactive mode with optional initial question
            interactive_mode(client, model_deployment_name, args.question)
        elif args.question:
            # Single question mode
            process_single_question(client, args.question, model_deployment_name)
        else:
            # No question provided, start interactive mode
            print("No question provided. Starting interactive mode...")
            interactive_mode(client, model_deployment_name)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error("Unexpected error in main: %s", e)
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

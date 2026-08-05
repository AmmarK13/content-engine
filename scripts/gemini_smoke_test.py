import asyncio
import json
import google.generativeai as genai
from orchestrator.provider_config import load_provider_config
from contracts.prompts.script_generation_prompt import SCRIPT_GENERATION_SYSTEM_PROMPT, build_script_prompt
def main():
    print("Loading config...")
    config = load_provider_config('script_generation')
    
    if not config.get('api_key'):
        print("Error: No API key found in configs/providers/script_generation.yaml")
        return
    print("Configuring Gemini...")
    genai.configure(api_key=config['api_key'])
    
    model = genai.GenerativeModel(
        model_name=config.get('model_id', 'gemini-1.5-flash'),
        system_instruction=SCRIPT_GENERATION_SYSTEM_PROMPT,
    )
    
    topic = "The history of artificial intelligence"
    print(f"Generating script for topic: '{topic}'...")
    
    response = model.generate_content(build_script_prompt(topic))
    
    raw = response.text.strip()
    print("\n--- Raw Response from Gemini ---")
    print(raw)
    print("--------------------------------\n")
    
    try:
        parsed = json.loads(raw)
        print("Success! The response is valid JSON.")
        print(f"Number of scenes generated: {len(parsed.get('scenes', []))}")
    except json.JSONDecodeError:
        print("Error: The response was not valid JSON.")
if __name__ == "__main__":
    main()
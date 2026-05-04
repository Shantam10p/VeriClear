"""
Prepare the customer support dataset for VeriClear fine-tuning.
Maps the dataset to VeriClear's intent and emotion labels.
"""
from datasets import load_dataset
import json
import re
from typing import Dict, List

# VeriClear label mappings
INTENT_LABELS = ["billing", "tech_support", "account_management"]
EMOTION_LABELS = ["neutral", "happy", "frustrated", "confused", "threatening"]

def detect_intent(text: str) -> str:
    """Heuristic intent detection from customer message."""
    text_lower = text.lower()
    
    # Billing keywords
    if any(word in text_lower for word in ["bill", "charge", "payment", "invoice", "fee", "cost", "price", "overage", "plan", "subscription"]):
        return "billing"
    
    # Tech support keywords
    if any(word in text_lower for word in ["not working", "broken", "error", "issue", "problem", "down", "service", "network", "connection", "technical", "fix", "repair"]):
        return "tech_support"
    
    # Account management keywords
    if any(word in text_lower for word in ["account", "password", "login", "update", "change", "profile", "settings", "cancel", "close", "owner"]):
        return "account_management"
    
    return "billing"  # Default

def detect_emotion(text: str) -> str:
    """Heuristic emotion detection from customer message."""
    text_lower = text.lower()
    
    # Threatening/escalation
    if any(word in text_lower for word in ["lawsuit", "lawyer", "cancel", "complaint", "manager", "unacceptable", "ridiculous", "switching"]):
        return "threatening"
    
    # Frustrated
    if any(word in text_lower for word in ["frustrated", "angry", "annoyed", "third time", "again", "still", "why", "terrible", "awful"]):
        return "frustrated"
    
    # Confused
    if any(word in text_lower for word in ["confused", "don't understand", "unclear", "what does", "explain", "help me understand"]):
        return "confused"
    
    # Happy
    if any(word in text_lower for word in ["thank", "thanks", "appreciate", "great", "awesome", "perfect", "excellent"]):
        return "happy"
    
    return "neutral"

def prepare_training_data(dataset_name: str = "syncora/customer_support_conversations_dataset", output_file: str = "vericlear_training_data.jsonl"):
    """
    Load the dataset and prepare it for VeriClear fine-tuning.
    """
    print(f"Loading dataset: {dataset_name}")
    dataset = load_dataset(dataset_name)
    
    # Use train split or first available split
    split_name = 'train' if 'train' in dataset else list(dataset.keys())[0]
    data = dataset[split_name]
    
    print(f"Processing {len(data)} examples from '{split_name}' split...")
    
    prepared_examples = []
    
    for idx, example in enumerate(data):
        # Extract customer message (adjust based on actual dataset schema)
        # Common column names: 'text', 'message', 'customer_message', 'query', 'input'
        customer_message = None
        for col in ['text', 'message', 'customer_message', 'query', 'input', 'conversation']:
            if col in example:
                customer_message = str(example[col])
                break
        
        if not customer_message or len(customer_message.strip()) < 10:
            continue
        
        # Detect intent and emotion
        intent = detect_intent(customer_message)
        emotion = detect_emotion(customer_message)
        
        # Create training example in VeriClear format
        training_example = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an intent classification service for Verizon-style support queries. Return only valid JSON with keys intent, emotion, confidence. intent must be one of billing, tech_support, account_management. emotion must be one of neutral, happy, frustrated, confused, threatening. confidence must be a number between 0 and 1."
                },
                {
                    "role": "user",
                    "content": f"Customer message: {customer_message}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps({
                        "intent": intent,
                        "emotion": emotion,
                        "confidence": 0.9
                    })
                }
            ]
        }
        
        prepared_examples.append(training_example)
        
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1} examples...")
    
    # Write to JSONL file
    print(f"\nWriting {len(prepared_examples)} examples to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in prepared_examples:
            f.write(json.dumps(example) + '\n')
    
    # Print statistics
    intents = [json.loads(ex['messages'][2]['content'])['intent'] for ex in prepared_examples]
    emotions = [json.loads(ex['messages'][2]['content'])['emotion'] for ex in prepared_examples]
    
    print("\n=== Dataset Statistics ===")
    print(f"Total examples: {len(prepared_examples)}")
    print("\nIntent distribution:")
    for intent in INTENT_LABELS:
        count = intents.count(intent)
        print(f"  {intent}: {count} ({count/len(intents)*100:.1f}%)")
    
    print("\nEmotion distribution:")
    for emotion in EMOTION_LABELS:
        count = emotions.count(emotion)
        print(f"  {emotion}: {count} ({count/len(emotions)*100:.1f}%)")
    
    print(f"\n✓ Training data saved to {output_file}")
    return prepared_examples

if __name__ == "__main__":
    prepare_training_data()

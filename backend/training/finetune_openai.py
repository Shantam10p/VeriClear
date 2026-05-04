"""
Fine-tune gpt-4o-mini using OpenAI's fine-tuning API.
Requires OpenAI API key with fine-tuning access.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

def upload_training_file(client: OpenAI, file_path: str):
    """Upload training data to OpenAI."""
    print(f"Uploading training file: {file_path}")
    with open(file_path, "rb") as f:
        response = client.files.create(
            file=f,
            purpose="fine-tune"
        )
    print(f"✓ File uploaded: {response.id}")
    return response.id

def create_fine_tune_job(client: OpenAI, file_id: str, model: str = "gpt-4o-mini-2024-07-18"):
    """Create a fine-tuning job."""
    print(f"Creating fine-tune job for model: {model}")
    response = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=model,
        hyperparameters={
            "n_epochs": 3  # Adjust based on dataset size
        }
    )
    print(f"✓ Fine-tune job created: {response.id}")
    return response.id

def monitor_fine_tune_job(client: OpenAI, job_id: str):
    """Monitor the fine-tuning job status."""
    print(f"\nMonitoring fine-tune job: {job_id}")
    print("This may take 10-30 minutes depending on dataset size...")
    
    while True:
        job = client.fine_tuning.jobs.retrieve(job_id)
        status = job.status
        
        print(f"Status: {status}")
        
        if status == "succeeded":
            print(f"\n✓ Fine-tuning completed!")
            print(f"Fine-tuned model: {job.fine_tuned_model}")
            return job.fine_tuned_model
        
        elif status == "failed":
            print(f"\n✗ Fine-tuning failed!")
            print(f"Error: {job.error}")
            return None
        
        elif status in ["validating_files", "queued", "running"]:
            time.sleep(30)  # Check every 30 seconds
        
        else:
            print(f"Unknown status: {status}")
            time.sleep(30)

def main():
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ Error: OPENAI_API_KEY not found in environment")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Training file path
    training_file = "vericlear_training_data.jsonl"
    
    if not os.path.exists(training_file):
        print(f"✗ Error: Training file not found: {training_file}")
        print("Run prepare_data.py first to generate the training data.")
        return
    
    print("=== VeriClear Model Fine-Tuning ===\n")
    
    # Step 1: Upload training file
    file_id = upload_training_file(client, training_file)
    
    # Step 2: Create fine-tune job
    job_id = create_fine_tune_job(client, file_id)
    
    # Step 3: Monitor job
    fine_tuned_model = monitor_fine_tune_job(client, job_id)
    
    if fine_tuned_model:
        print("\n=== Next Steps ===")
        print(f"1. Update your .env file:")
        print(f"   VERICLEAR_SHARED_MODEL={fine_tuned_model}")
        print(f"\n2. Restart your backend server")
        print(f"\n3. Test the fine-tuned model with your chat interface")

if __name__ == "__main__":
    main()

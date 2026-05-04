# VeriClear Model Training

This directory contains scripts for fine-tuning models on customer support data for VeriClear.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your OpenAI API key:**
   Make sure your `.env` file in the backend directory contains:
   ```
   OPENAI_API_KEY=your_key_here
   ```

## Training Pipeline

### Step 1: Explore the Dataset

First, understand the dataset structure:

```bash
python explore_dataset.py
```

This will show you:
- Dataset splits and sizes
- Sample examples
- Column names and features
- Existing labels (if any)

### Step 2: Prepare Training Data

Convert the dataset to VeriClear's format:

```bash
python prepare_data.py
```

This creates `vericlear_training_data.jsonl` with:
- Intent labels (billing, tech_support, account_management)
- Emotion labels (neutral, happy, frustrated, confused, threatening)
- Proper OpenAI fine-tuning format

### Step 3: Fine-tune the Model

#### Option A: Fine-tune gpt-4o-mini (Recommended)

```bash
python finetune_openai.py
```

**Requirements:**
- OpenAI API key with fine-tuning access
- Training data in JSONL format
- ~$10-50 depending on dataset size

**Time:** 10-30 minutes

**Result:** A fine-tuned gpt-4o-mini model ID

#### Option B: Train a local small model (Advanced)

For local deployment or cost optimization:

```bash
python train_local_model.py
```

This uses LoRA/QLoRA to fine-tune a smaller model like:
- Phi-3-mini
- Llama-3.1-8B
- Mistral-7B

**Requirements:**
- GPU with 8GB+ VRAM (or CPU with patience)
- More technical setup

### Step 4: Update Your Backend

After fine-tuning completes, update your `.env`:

```env
VERICLEAR_SHARED_MODEL=ft:gpt-4o-mini-2024-07-18:your-org:vericlear:xxxxx
```

Restart your backend:

```bash
uvicorn app.main:app --reload
```

## Dataset Information

**Source:** `syncora/customer_support_conversations_dataset`

**Format:** Customer support conversations with various intents and tones

**Mapping to VeriClear:**
- Billing keywords → `billing` intent
- Technical issues → `tech_support` intent
- Account changes → `account_management` intent
- Emotional tone → emotion labels

## Cost Estimates

### OpenAI Fine-tuning (gpt-4o-mini)
- Training: ~$0.003 per 1K tokens
- Inference: ~$0.0003 per 1K tokens (input), ~$0.0012 per 1K tokens (output)
- Total for 1000 examples: ~$5-10

### Local Model
- Training: Free (but requires GPU time)
- Inference: Free (but slower without GPU)

## Troubleshooting

**"Dataset not found"**
- Check internet connection
- Verify dataset name: `syncora/customer_support_conversations_dataset`

**"OpenAI API error"**
- Verify API key is valid
- Check if you have fine-tuning access
- Ensure billing is set up

**"Out of memory"**
- For local training, reduce batch size
- Use smaller model variant
- Enable gradient checkpointing

## Next Steps

After fine-tuning:

1. **Test the model** with your demo scenarios
2. **Compare performance** vs base gpt-4o-mini
3. **Collect real usage data** to improve further
4. **Iterate** with more training data

## Files

- `explore_dataset.py` - Dataset exploration script
- `prepare_data.py` - Data preparation and labeling
- `finetune_openai.py` - OpenAI fine-tuning script
- `train_local_model.py` - Local model training (TODO)
- `requirements.txt` - Python dependencies

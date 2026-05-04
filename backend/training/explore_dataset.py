"""
Explore the syncora customer support dataset and map it to VeriClear's schema.
"""
from datasets import load_dataset
import pandas as pd
from collections import Counter

def explore_dataset():
    print("Loading dataset...")
    dataset = load_dataset("syncora/customer_support_conversations_dataset")
    
    print("\n=== Dataset Info ===")
    print(dataset)
    
    print("\n=== Dataset Splits ===")
    for split_name in dataset.keys():
        print(f"{split_name}: {len(dataset[split_name])} examples")
    
    print("\n=== Sample Examples ===")
    train_data = dataset['train'] if 'train' in dataset else dataset[list(dataset.keys())[0]]
    
    for i in range(min(5, len(train_data))):
        print(f"\n--- Example {i+1} ---")
        example = train_data[i]
        for key, value in example.items():
            print(f"{key}: {value}")
    
    print("\n=== Column Names ===")
    print(train_data.column_names)
    
    print("\n=== Dataset Features ===")
    print(train_data.features)
    
    # Analyze text lengths
    if 'text' in train_data.column_names or 'message' in train_data.column_names:
        text_col = 'text' if 'text' in train_data.column_names else 'message'
        lengths = [len(str(example[text_col])) for example in train_data]
        print(f"\n=== Text Length Stats ===")
        print(f"Min: {min(lengths)}, Max: {max(lengths)}, Avg: {sum(lengths)/len(lengths):.1f}")
    
    # Check for existing labels
    label_columns = [col for col in train_data.column_names if 'label' in col.lower() or 'category' in col.lower() or 'intent' in col.lower()]
    if label_columns:
        print(f"\n=== Existing Label Columns ===")
        for col in label_columns:
            unique_values = Counter([example[col] for example in train_data])
            print(f"\n{col}:")
            for value, count in unique_values.most_common(10):
                print(f"  {value}: {count}")
    
    return dataset

if __name__ == "__main__":
    dataset = explore_dataset()
    print("\n✓ Dataset exploration complete!")

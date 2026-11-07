import torch

# Load the file safely on CPU
checkpoint = torch.load('epoch_160.pth', map_location='cpu')

# Check what type of object was saved
print(f"File contents type: {type(checkpoint)}")

# If it's a state_dict (dictionary), list the layers and their tensor shapes
if isinstance(checkpoint, dict):
    print(f"Total keys found: {len(checkpoint)}")
    print("\n--- Model Layers and Shapes ---")
    for key, value in checkpoint.items():
        if hasattr(value, 'shape'):
            print(f"{key}: {value.shape}")
        else:
            print(f"{key}: {type(value)}")
else:
    # If the entire model class object was saved instead of just weights
    print(checkpoint)

from torchvision.models import ResNet18_Weights
from torchvision import models
from torchvision import transforms
from PIL import Image
import torch

# Define preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to ResNet's input size
    transforms.ToTensor(),         # Convert to tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize for ImageNet
])

# Load ResNet and remove the classification layer
model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove the final classification layer
model.eval()  # Set the model to evaluation mode

def get_embedding(image_path):
    # Preprocess the image
    image = Image.open(image_path).convert("RGB")
    tensor = preprocess(image).unsqueeze(0)  # Add batch dimension
    # Get the embedding
    with torch.no_grad(): embeddings = model(tensor).squeeze().numpy()
    return embeddings

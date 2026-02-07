import grpc
from concurrent import futures
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import os

import ai_pb2 as service_pb2
import ai_pb2_grpc as service_pb2_grpc

MODEL_PATH = "./.model/hashtag_model.pth"
TAGS_PATH = "./.model/tags.txt"
DEVICE = torch.device("cpu")

class AIService(service_pb2_grpc.AIServiceServicer):
    def __init__(self):
        print("Initializing AI Service...")
        self.tags = self.load_tags()
        self.model = self.load_model()
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        print("AI Service Ready.")

    def load_tags(self):
        try:
            with open(TAGS_PATH, "r") as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print("CRITICAL ERROR: tags.txt not found!")
            return []

    def load_model(self):
        model = models.resnet18(pretrained=False)
        num_ftrs = model.fc.in_features
        
        model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, len(self.tags))
        )
        
        try:
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
            model.to(DEVICE)
            model.eval()
            return model
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to load model weights: {e}")
            return None

    def PredictHashtags(self, request, context):
        if self.model is None:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Model not loaded correctly')
            return service_pb2.PredictResponse()

        try:
            image = Image.open(io.BytesIO(request.image_data)).convert('RGB')
            tensor = self.transform(image).unsqueeze(0).to(DEVICE)

            with torch.no_grad():
                outputs = self.model(tensor)
                probs = torch.sigmoid(outputs)

            recommended = []
            probs_np = probs.cpu().numpy()[0]
            
            for i, prob in enumerate(probs_np):
                if prob > 0.3: 
                    recommended.append(self.tags[i])

            return service_pb2.PredictResponse(hashtags=recommended)

        except Exception as e:
            print(f"Prediction Error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return service_pb2.PredictResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    service_pb2_grpc.add_AIServiceServicer_to_server(AIService(), server)
    
    server.add_insecure_port('[::]:50051')
    print("AI Service listening on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
from .base import BaseModel
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset, DataLoader
import os
import json
import numpy as np

class LicenseDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

class SoulReader(BaseModel):
    def __init__(self, model_name_or_path="microsoft/MiniLM-L12-H384-uncased", candidate_labels=None):
        print("The AI License Soul-Reader™ is materializing from the ether...")
        self.model_name_or_path = model_name_or_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        
        if candidate_labels:
            self.candidate_labels = candidate_labels
        else:
            self.candidate_labels = [
                "MIT", "Apache-2.0", "GPL-3.0-only", "GPL-2.0-only", "LGPL-3.0-only",
                "BSD-3-Clause", "BSD-2-Clause", "ISC", "MPL-2.0", "CC-BY-4.0",
            ]
        
        self.label_to_id_ci = {label.lower(): i for i, label in enumerate(self.candidate_labels)}
        self.id_to_label = {i: label for i, label in enumerate(self.candidate_labels)}
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path, num_labels=len(self.candidate_labels))
        self.model.to('cpu')
        self.trained = os.path.exists(os.path.join(model_name_or_path, 'pytorch_model.bin')) or os.path.exists(os.path.join(model_name_or_path, 'model.safetensors'))

    def train(self, X_train: list, y_train: list):
        print("Training the AI License Soul-Reader™...")
        train_encodings = self.tokenizer(X_train, truncation=True, padding=True, max_length=512)
        train_labels = [self.label_to_id_ci[label.lower()] for label in y_train]
        train_dataset = LicenseDataset(train_encodings, train_labels)

        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=3,
            per_device_train_batch_size=8,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=10,
            no_cuda=True,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
        )

        trainer.train()
        self.trained = True
        print("AI License Soul-Reader™ trained successfully!")

    def evaluate(self, X_val: list, y_val: list, compute_metrics):
        print("Evaluating the AI License Soul-Reader™...")
        val_encodings = self.tokenizer(X_val, truncation=True, padding=True, max_length=512)
        val_labels = [self.label_to_id_ci[label.lower()] for label in y_val]
        val_dataset = LicenseDataset(val_encodings, val_labels)
        
        predictions = []
        with torch.no_grad():
            for item in val_dataset:
                inputs = {key: val.unsqueeze(0) for key, val in item.items() if key != 'labels'}
                logits = self.model(**inputs).logits
                pred = torch.argmax(logits, dim=1).item()
                predictions.append(pred)

        return compute_metrics(predictions=np.array(predictions), labels=np.array(val_labels))


    def save_model(self, path: str):
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        with open(os.path.join(path, "candidate_labels.json"), "w") as f:
            json.dump(self.candidate_labels, f)

    @classmethod
    def from_pretrained(cls, path: str):
        with open(os.path.join(path, "candidate_labels.json"), "r") as f:
            candidate_labels = json.load(f)
        return cls(model_name_or_path=path, candidate_labels=candidate_labels)

    def predict(self, text: str) -> str:
        if not self.trained:
            print("Warning: This model has not been fine-tuned. Predictions are based on the base model and may be inaccurate.")

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to('cpu')
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probabilities = F.softmax(logits, dim=1)
        predicted_id = torch.argmax(probabilities, dim=1).item()
        return self.id_to_label[predicted_id]

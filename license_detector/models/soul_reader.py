from .base import BaseModel
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset

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
    def __init__(self, model_name="microsoft/MiniLM-L12-H384-uncased"):
        print("The AI License Soul-Reader™ is materializing from the ether...")
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.candidate_labels = [
            "MIT",
            "Apache-2.0",
            "GPL-3.0-only",
            "GPL-2.0-only",
            "LGPL-3.0-only",
            "BSD-3-Clause",
            "BSD-2-Clause",
            "ISC",
            "MPL-2.0",
            "CC-BY-4.0",
        ]
        self.label_to_id_ci = {label.lower(): i for i, label in enumerate(self.candidate_labels)} # Case-insensitive mapping
        self.id_to_label = {i: label for i, label in enumerate(self.candidate_labels)}
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(self.candidate_labels))
        self.model.to('cpu') # Ensure model is on CPU
        self.trained = False

    def train(self, X_train: list, y_train: list):
        print("Training the AI License Soul-Reader™...")
        self.model.to('cpu') # Ensure model is on CPU for training too if not already
        train_encodings = self.tokenizer(X_train, truncation=True, padding=True, max_length=512)
        
        train_labels = []
        for label in y_train:
            if label.lower() in self.label_to_id_ci:
                train_labels.append(self.label_to_id_ci[label.lower()])
            else:
                print(f"Warning: Training label '{label}' not found in candidate labels. Skipping.")

        if not train_labels:
            raise ValueError("No valid training labels found. Cannot train the model.")

        train_dataset = LicenseDataset(train_encodings, train_labels)

        training_args = TrainingArguments(
            output_dir='./results',          # output directory
            num_train_epochs=3,              # total number of training epochs
            per_device_train_batch_size=8,   # batch size per device during training
            warmup_steps=500,                # number of warmup steps for learning rate scheduler
            weight_decay=0.01,               # strength of weight decay
            logging_dir='./logs',            # directory for storing logs
            logging_steps=10,
            no_cuda=True, # Explicitly tell Trainer to not use CUDA (and by extension, MPS)
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
        )

        trainer.train()
        self.trained = True
        print("AI License Soul-Reader™ trained successfully!")

    def predict(self, text: str) -> str:
        if not self.trained:
            print("Warning: Soul-Reader has not been trained. Performing untrained prediction (might be inaccurate).")
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to('cpu')
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probabilities = F.softmax(logits, dim=1)
            predicted_id = torch.argmax(probabilities, dim=1).item()
            return self.id_to_label[predicted_id]

        print("Gazing into the soul of the text with trained wisdom...")
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to('cpu')
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probabilities = F.softmax(logits, dim=1)
        predicted_id = torch.argmax(probabilities, dim=1).item()
        return self.id_to_label[predicted_id]

import torch
from transformers import (
    GPT2LMHeadModel, 
    GPT2Tokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import pandas as pd
import json
from pathlib import Path
import logging
from typing import List, Dict
import os
from dotenv import load_dotenv

class TweetTrainer:
    def __init__(self, model_name: str = "gpt2", cache_dir: str = "data"):
        """
        Inicializa el entrenador de modelos para generar tweets.
        
        Args:
            model_name: Nombre del modelo base a usar
            cache_dir: Directorio para guardar modelos y datos
        """
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('model_training.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Configurar directorio de caché
        self.cache_dir = Path(cache_dir)
        
        # Detectar dispositivo
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger.info(f"Usando dispositivo: {self.device}")
        
        if self.device.type == "cuda":
            self.logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        
        # Cargar modelo y tokenizer
        self._load_model(model_name)
    
    def _load_model(self, model_name: str):
        """Carga el modelo y tokenizer."""
        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            self.model = GPT2LMHeadModel.from_pretrained(model_name)
            
            # Mover modelo a GPU si está disponible
            self.model.to(self.device)
            
            # Configurar tokenizer
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.logger.info(f"Modelo {model_name} cargado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error cargando el modelo: {e}")
            raise

    def load_training_data(self, username: str) -> List[Dict]:
        """Carga tweets desde el archivo de caché."""
        cache_file = self.cache_dir / f"tweets_{username}.json"
        if not cache_file.exists():
            raise FileNotFoundError(f"No se encontró el archivo de tweets: {cache_file}")
            
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            return cache_data["tweets"]

    def prepare_training_data(self, tweets: List[Dict]) -> Dataset:
        """Prepara los datos para entrenamiento."""
        # Preparar textos para entrenamiento
        training_texts = [
            f"Tweet: {tweet['text']}\nEND"
            for tweet in tweets
        ]
        
        # Convertir a dataset
        return Dataset.from_pandas(
            pd.DataFrame({"text": training_texts})
        )

    def train(self, dataset: Dataset, output_dir: str = "trained_model"):
        """
        Entrena el modelo con los tweets proporcionados.
        
        Args:
            dataset: Dataset de entrenamiento
            output_dir: Directorio donde guardar el modelo entrenado
        """
        output_path = self.cache_dir / output_dir
        
        # Configurar argumentos de entrenamiento
        training_args = TrainingArguments(
            output_dir=str(output_path),
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            save_steps=500,
            save_total_limit=2,
            learning_rate=2e-5,
            weight_decay=0.01,
            logging_dir=str(self.cache_dir / 'logs'),
            fp16=self.device.type == "cuda",
            gradient_checkpointing=True,
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=100,
            warmup_steps=100,
            report_to=["tensorboard"],
        )
        
        # Configurar data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Crear trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )
        
        # Entrenar modelo
        try:
            self.logger.info("Iniciando entrenamiento...")
            trainer.train()
            
            # Guardar modelo y tokenizer
            trainer.save_model(output_path)
            self.tokenizer.save_pretrained(output_path)
            self.logger.info(f"Modelo guardado en: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error durante el entrenamiento: {e}")
            raise

    def generate_tweet(self, prompt: str = "") -> str:
        """
        Genera un nuevo tweet usando el modelo entrenado.
        
        Args:
            prompt: Texto inicial para generar el tweet
            
        Returns:
            Tweet generado
        """
        try:
            # Preparar input
            input_text = f"Tweet: {prompt}" if prompt else "Tweet:"
            inputs = self.tokenizer(input_text, return_tensors="pt", truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generar texto
            with torch.cuda.amp.autocast() if self.device.type == "cuda" else nullcontext():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=280,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                )
            
            # Decodificar y limpiar resultado
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return generated_text.replace("Tweet:", "").strip()
            
        except Exception as e:
            self.logger.error(f"Error generando tweet: {e}")
            return ""

def main():
    # Configurar trainer
    trainer = TweetTrainer()
    
    # Obtener nombre de usuario
    username = os.getenv('TWITTER_USERNAME', 'ITAM_mx')
    
    try:
        # Cargar tweets de entrenamiento
        tweets = trainer.load_training_data(username)
        print(f"Cargados {len(tweets)} tweets para entrenamiento")
        
        # Preparar datos
        dataset = trainer.prepare_training_data(tweets)
        
        # Entrenar modelo
        trainer.train(dataset)
        
        # Generar algunos tweets de ejemplo
        print("\nTweets generados de ejemplo:")
        for _ in range(3):
            tweet = trainer.generate_tweet()
            print(f"\n{tweet}")
            
    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    main()
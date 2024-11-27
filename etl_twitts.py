import json
from typing import List, Dict
from pathlib import Path
import logging
from datetime import datetime

class TwitterCleaner:
    def __init__(self, input_file: str, output_dir: str = "data"):
        """
        Inicializa el limpiador de tweets.
        
        Args:
            input_file: Ruta al archivo JS con los tweets
            output_dir: Directorio donde se guardarán los tweets procesados
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('twitter_cleaning.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _read_js_file(self) -> List[Dict]:
        """Lee el archivo JS y retorna la lista de tweets."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extraer el array JSON después de la asignación
            json_str = content.replace('window.YTD.tweets.part0 = ', '')
            return json.loads(json_str)
            
        except Exception as e:
            self.logger.error(f"Error leyendo archivo JS: {e}")
            raise

    def clean_tweets(self, limit: int = 300) -> List[Dict]:
        """
        Limpia y extrae los primeros N tweets.
        
        Args:
            limit: Número de tweets a extraer
            
        Returns:
            Lista de tweets procesados
        """
        try:
            # Leer y extraer tweets
            tweets = self._read_js_file()
            
            # Tomar los primeros N tweets
            tweets = tweets[:limit]
            
            # Limpiar y estructurar tweets
            cleaned_tweets = []
            for tweet_obj in tweets:
                tweet = tweet_obj['tweet']  # Acceder al objeto tweet interno
                cleaned_tweet = {
                    "text": tweet['full_text'].strip(),
                    "created_at": tweet['created_at'],
                    "id": tweet['id_str'],
                    "metrics": {
                        "retweet_count": tweet.get('retweet_count', 0),
                        "favorite_count": tweet.get('favorite_count', 0),
                        "reply_count": tweet.get('reply_count', 0)
                    }
                }
                cleaned_tweets.append(cleaned_tweet)
            
            self.logger.info(f"Procesados {len(cleaned_tweets)} tweets")
            return cleaned_tweets
            
        except Exception as e:
            self.logger.error(f"Error procesando tweets: {e}")
            return []

    def save_tweets(self, tweets: List[Dict], filename: str = None) -> None:
        """
        Guarda los tweets procesados en un archivo JSON.
        
        Args:
            tweets: Lista de tweets procesados
            filename: Nombre del archivo de salida (opcional)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cleaned_tweets_{timestamp}.json"
        
        output_file = self.output_dir / filename
        
        try:
            data = {
                "tweet_count": len(tweets),
                "processed_date": datetime.now().isoformat(),
                "tweets": tweets
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Tweets guardados en: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error guardando tweets: {e}")
            raise

def main():
    # Configurar rutas
    input_file = "tweets.js"  # Ajusta esto a tu nombre de archivo
    output_dir = "data"
    
    try:
        # Crear instancia del limpiador
        cleaner = TwitterCleaner(input_file, output_dir)
        
        # Procesar tweets
        print("Procesando tweets...")
        tweets = cleaner.clean_tweets(limit=300)
        
        if tweets:
            # Guardar tweets procesados
            cleaner.save_tweets(tweets)
            
            # Mostrar algunas estadísticas
            print(f"\nEstadísticas:")
            print(f"Total de tweets procesados: {len(tweets)}")
            
            # Mostrar algunos ejemplos
            print("\nEjemplos de tweets procesados:")
            for tweet in tweets[:3]:
                print(f"\nTexto: {tweet['text']}")
                print(f"Fecha: {tweet['created_at']}")
                print(f"Métricas: {tweet['metrics']}")
                
    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    main()
import tweepy
import json
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import logging
import time
from typing import List, Dict

class TwitterExtractor:
    def __init__(self, cache_dir: str = "data"):
        """
        Inicializa el extractor de tweets.
        
        Args:
            cache_dir: Directorio donde se guardarán los tweets
        """
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('twitter_extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Cargar variables de entorno
        load_dotenv()
        
        # Configurar directorio de caché
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar cliente de Twitter
        self._setup_twitter_client()
    
    def _setup_twitter_client(self):
        """Configura el cliente de Twitter usando variables de entorno."""
        try:
            self.client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
            self.logger.info("Cliente de Twitter configurado exitosamente")
        except Exception as e:
            self.logger.error(f"Error configurando cliente de Twitter: {e}")
            raise

    def get_cache_file(self, username: str) -> Path:
        """Obtiene la ruta del archivo de caché para un usuario."""
        return self.cache_dir / f"tweets_{username}.json"

    def save_tweets_to_cache(self, username: str, tweets: List[Dict]) -> None:
        """
        Guarda tweets en archivo JSON.
        
        Args:
            username: Nombre de usuario de Twitter
            tweets: Lista de tweets con sus metadatos
        """
        cache_data = {
            "username": username,
            "fetch_date": datetime.now().isoformat(),
            "tweet_count": len(tweets),
            "tweets": tweets
        }
        
        cache_file = self.get_cache_file(username)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Tweets guardados en: {cache_file}")

    def load_tweets_from_cache(self, username: str) -> List[Dict]:
        """
        Carga tweets desde el archivo de caché.
        
        Args:
            username: Nombre de usuario de Twitter
            
        Returns:
            Lista de tweets o None si no existe caché
        """
        cache_file = self.get_cache_file(username)
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                self.logger.info(f"Tweets cargados desde: {cache_file}")
                return cache_data["tweets"]
        return None
    
    def extract_tweets(self, username: str, count: int = 100, use_cache: bool = True, start_from_token: str = None) -> tuple[List[Dict], str]:
        """
        Extrae tweets de un usuario.
        
        Args:
            username: Nombre de usuario de Twitter
            count: Número de tweets a obtener por petición
            use_cache: Si se debe usar caché existente
            start_from_token: Token de paginación para continuar desde una extracción anterior
            
        Returns:
            Tupla de (lista de tweets, siguiente token de paginación)
        """
        username = username.strip()
        
        if not username or not username.replace('_', '').isalnum():
            self.logger.error(f"Nombre de usuario inválido: '{username}'")
            return [], None

        try:
            user = self.client.get_user(username=username)
            if not user.data:
                self.logger.error(f"Usuario @{username} no encontrado")
                return [], None

            # Obtener tweets con paginación
            response = self.client.get_users_tweets(
                id=user.data.id,
                max_results=min(count, 100),
                exclude=['retweets', 'replies'],
                tweet_fields=['created_at', 'public_metrics'],
                pagination_token=start_from_token
            )

            if not response.data:
                self.logger.warning(f"No se encontraron tweets para @{username}")
                return [], None

            tweets = [
                {
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat(),
                    "metrics": tweet.public_metrics,
                    "id": tweet.id
                }
                for tweet in response.data
            ]

            # Obtener el token para la siguiente página
            next_token = response.meta.get('next_token')
            
            self.logger.info(f"Extraídos {len(tweets)} tweets de @{username}")
            if next_token:
                self.logger.info("Hay más tweets disponibles")
            
            return tweets, next_token

        except Exception as e:
            self.logger.error(f"Error extrayendo tweets: {e}")
            return [], None

    def extract_all_available_tweets(self, username: str, max_requests: int = 5) -> List[Dict]:
        """
        Extrae todos los tweets disponibles haciendo múltiples peticiones.
        
        Args:
            username: Nombre de usuario de Twitter
            max_requests: Número máximo de peticiones a realizar
            
        Returns:
            Lista de todos los tweets extraídos
        """
        all_tweets = []
        next_token = None
        request_count = 0
        
        while request_count < max_requests:
            tweets, next_token = self.extract_tweets(
                username=username,
                count=100,
                use_cache=False,
                start_from_token=next_token
            )
            
            if not tweets:
                break
                
            all_tweets.extend(tweets)
            request_count += 1
            
            self.logger.info(f"Petición {request_count}: Obtenidos {len(tweets)} tweets")
            self.logger.info(f"Total acumulado: {len(all_tweets)} tweets")
            
            if not next_token:
                break
                
            # Esperar un poco entre peticiones para no exceder límites
            time.sleep(1)
        
        # Guardar todos los tweets en caché
        self.save_tweets_to_cache(username, all_tweets)
        
        return all_tweets

def main():
    # Configurar extractor
    extractor = TwitterExtractor()
    
    # Obtener y limpiar nombre de usuario
    username = os.getenv('TWITTER_USERNAME', 'ITAM_mx').strip()
    
    print(f"Extrayendo tweets para el usuario: '{username}'")
    
    # Extraer todos los tweets disponibles
    tweets = extractor.extract_all_available_tweets(username, max_requests=5)
    
    # Mostrar estadísticas
    if tweets:
        print(f"\nEstadísticas de extracción para @{username}:")
        print(f"Total de tweets extraídos: {len(tweets)}")
        
        # Mostrar fechas del primer y último tweet
        dates = [tweet['created_at'] for tweet in tweets]
        print(f"Período: {min(dates)} a {max(dates)}")
        
        # Agrupar tweets por mes
        from collections import defaultdict
        from datetime import datetime
        
        tweets_por_mes = defaultdict(int)
        for tweet in tweets:
            fecha = datetime.fromisoformat(tweet['created_at'])
            mes_año = fecha.strftime('%Y-%m')
            tweets_por_mes[mes_año] += 1
            
        print("\nDistribución de tweets por mes:")
        for mes, cantidad in sorted(tweets_por_mes.items()):
            print(f"{mes}: {cantidad} tweets")
        
        # Mostrar algunos ejemplos
        print("\nEjemplos de tweets más recientes:")
        for tweet in sorted(tweets[:3], key=lambda x: x['created_at'], reverse=True):
            print(f"\nFecha: {tweet['created_at']}")
            print(f"Texto: {tweet['text']}")
            print(f"Métricas: {tweet['metrics']}")

if __name__ == "__main__":
    main()
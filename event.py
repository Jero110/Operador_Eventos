# event.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Event:
    title: str
    description: str
    image_url: Optional[str]
    event_url: str
    date: str
    time: str
    location: str
    created_at: datetime = datetime.now()

    def __str__(self):
        return f"""
Event: {self.title}
Date: {self.date}
Time: {self.time}
Location: {self.location}
Description: {self.description}
URL: {self.event_url}
Image: {self.image_url or 'No image'}
Created: {self.created_at}
"""
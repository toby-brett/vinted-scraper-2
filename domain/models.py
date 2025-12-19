from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass(frozen=True)
class Listing:
    """Represents a raw vinted listing as scraped from this site"""
    listing_id: str         # Unique Identifier
    title: str
    price: float
    image_url: str          # Link to the image
    size: str
    brand: str
    condition: str
    url: str                # link to the listing
    discovered_at: datetime # time when scraped

@dataclass(frozen=True)
class EvaluatedListing:
    """Represents a listing after model evaluation"""
    listing: Listing        # original Listing object
    predicted_value: float
    model_type: str         # classification or regression
    evaluated_at: datetime
    confidence: Optional[float] = None

@dataclass(frozen=True)
class Decision:
    """Represents the outcome of business logic"""
    evaluated_listing: EvaluatedListing
    action: str             # ALERT or IGNORE
    reason: str            # explanation
    profit: float
    threshold_used: float
    decided_at: datetime = datetime.now()

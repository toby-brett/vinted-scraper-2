from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import torch

from scraper import browser
from storage import storer


@dataclass(frozen=True)
class Listing:
    """Represents a raw vinted listing as scraped from this site"""
    listing_id: str         # Unique Identifier
    title: str
    price: float
    image_url: str          # Link to the image
    size: Optional[str]
    brand: Optional[str]
    condition: Optional[str]
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

@dataclass(frozen=True)
class JobObject:
    search: str
    brand: str
    task: str
    criteria: str
    threshold: int
    id_path: str
    price_threshold: Optional[float]
    model: Optional[torch.nn.Module]
    population_metrics: Optional[str]
    data_storer: storer.HDF5Storer
    max_price: Optional[float]
    min_condition: Optional[str]
    price_offset: Optional[float]

@dataclass(frozen=True)
class TickResult:
    """Represents the outcome of a single tick"""
    new: int
    stored: int
    return_status: str
    error: Optional[str] = None
    warnings: List[str] = None

@dataclass()
class JobRuntime:
    job: JobObject
    session: browser.BrowserSession
    seen_ids: set
    data_storer: storer.HDF5Storer
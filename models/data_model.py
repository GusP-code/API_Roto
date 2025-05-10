from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Option(BaseModel):
    name: str
    value: str

class Article(BaseModel):
    ref: str
    location: Optional[str] = None
    side: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    colors: Optional[List[Dict[str, Any]]] = None

class Operation(BaseModel):
    name: str
    referencePoint: str
    x: str
    location: Optional[str] = None

class SetDescription(BaseModel):
    position: Optional[str] = None
    referencePoint: Optional[str] = None
    inverted: Optional[bool] = None
    x: Optional[float] = None
    alternative: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None

class ColorArticle(BaseModel):
    ref: str
    final: str

class Color(BaseModel):
    name: str
    articles: List[ColorArticle]

class ParentInfo(BaseModel):
    parent_fitting_id: str
    parent_ref: str
    location: str
    side: str
    options: List[Option]
    set_description: SetDescription

class Fitting(BaseModel):
    fitting_id: str
    ref: str
    description: Optional[str] = None
    fittingType: Optional[str] = None
    location: Optional[str] = None
    handUseable: Optional[bool] = None
    colors: Optional[List[Dict[str, Any]]] = None
    parent_info: Optional[Dict[str, Any]] = None
    articles: Optional[List[Article]] = None
    operations: Optional[List[Dict[str, Any]]] = None
    set_description: Optional[SetDescription] = None

class ResponseModel(BaseModel):
    set_id: str
    width: int
    height: int
    applicable_fittings: List[Fitting]
    options_summary: Dict[str, List[str]] 
    total_fittings: int
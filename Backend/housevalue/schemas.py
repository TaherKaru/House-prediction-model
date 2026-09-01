from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class SignUpRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


class AuthResponse(BaseModel):
    message: str
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserResponse


class PredictionRequest(BaseModel):
    location: str = Field(min_length=2, max_length=150)
    bhk: int = Field(ge=1, le=10)
    bathrooms: int = Field(ge=1, le=10)
    area: float = Field(gt=100, le=20000)
    property_type: Literal["Apartment", "Villa", "Independent House"]
    address: str = Field(default="", max_length=250)
    pincode: str = Field(pattern=r"^\d{6}$")
    furnished: Literal["Unfurnished", "Semi-Furnished", "Furnished"] = "Unfurnished"
    total_floors: int = Field(default=1, ge=1, le=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("location")
    @classmethod
    def clean_location(cls, value: str) -> str:
        return " ".join(value.split())

    @model_validator(mode="after")
    def coordinate_pair_is_complete(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Provide both latitude and longitude, or neither.")
        return self


class FeedbackRequest(BaseModel):
    prediction_id: str = Field(min_length=8, max_length=36)
    actual_price: float = Field(gt=100000, le=1_000_000_000)
    verified: bool = False
    property_payload: dict

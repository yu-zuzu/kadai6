from fastapi import FastAPI
from pydantic import BaseModel, validator
from typing import List, Dict
from fastapi.responses import FileResponse
import os

from kadai_functions import fit_trendline, country_trendline, generate_image

app = FastAPI()

@app.get("/say_hi/", summary="Say Hi")
def say_hi() -> Dict[str, str]:
    return {"Hi": "There"}

@app.get("/say_hello/{name}", summary="Say Hello to someone")
def say_hello(name: str) -> Dict[str, str]:
    return {"Hello": name}

class TrendlineInput(BaseModel):
    timestamps: List[int]
    data: List[float]

    @validator('timestamps')
    def timestamps_not_empty(cls, v):
        if not v:
            raise ValueError('timestamps must not be empty')
        return v

    @validator('data')
    def data_not_empty(cls, v):
        if not v:
            raise ValueError('data must not be empty')
        return v

    @validator('timestamps')
    def timestamps_sorted(cls, v):
        if sorted(v) != v:
            raise ValueError('timestamps must be sorted in ascending order')
        return v

    @validator('data')
    def data_no_negative(cls, v):
        if any(x < 0 for x in v):
            raise ValueError('data values must be non-negative')
        return v

    @validator('data')
    def length_match(cls, v, values):
        if 'timestamps' in values and len(v) != len(values['timestamps']):
            raise ValueError('timestamps and data must have the same length')
        return v

@app.post(
    "/fit_trendline/",
    summary="Fit a trendline to any data",
    description="Provide a list of integer timestamps and a list of floats",
)
def calculate_trendline(trendline_input: TrendlineInput) -> Dict[str, float]:
    slope, r_squared = fit_trendline(trendline_input.timestamps, trendline_input.data)
    return {"slope": slope, "r_squared": r_squared}

@app.get("/country_trendline/{country}", summary="Get trendline stats for a country")
def calculate_country_trendline(country: str) -> Dict[str, float]:
    slope, r_squared, intercept = country_trendline(country)
    return {"slope": slope, "r_squared": r_squared, "intercept": intercept}

@app.get("/country_image/{country}", summary="Get trendline image for a country")
def generate_country_image(country: str):
    try:
        image_path = generate_image(country)
        abs_path = os.path.abspath(image_path)  # 画像の絶対パスに変換
        print(f"画像の場所はここです: {abs_path}")
        if os.path.exists(abs_path):
            return FileResponse(abs_path, media_type="image/png")
        else:
            return {"error": f"画像ファイルが見つかりません: {abs_path}"}
    except Exception as e:
        return {"error": str(e)}

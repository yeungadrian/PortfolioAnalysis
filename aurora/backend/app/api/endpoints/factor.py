from app import schemas
from app.modules.data_loader import DataLoader
from app.modules.factor_analysis import FactorAnalysis
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def factor_regression(item: schemas.factor):

    fund_codes = item.dict()["funds"]
    start_date = item.dict()["start_date"]
    end_date = item.dict()["end_date"]
    regression_factors = item.dict()["factors"]
    frequency = item.dict()["frequency"].lower()

    ff_factors = DataLoader().load_ff_factors(
        regression_factors=regression_factors,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
    )

    historical_returns = DataLoader().load_historical_returns(
        fund_codes=fund_codes,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
    )

    external_data = {
        "fund_codes": fund_codes,
        "start_date": start_date,
        "end_date": end_date,
        "factors": item.dict()["factors"],
        "fund_returns": historical_returns,
        "ff_factors": ff_factors,
    }

    output = FactorAnalysis(**external_data).regress_funds()

    return output
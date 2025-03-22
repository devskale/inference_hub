from datetime import date, timedelta

def generate_epex_url(date_param=None):
    """
    Generates the EPEX Spot market results API URL for a specific trading date and the next day's delivery date.

    Parameters:
        date_param (datetime.date): The trading date. If not provided, defaults to yesterday's date.

    Returns:
        str: The generated API URL.
    """
    if date_param is None:
        date_param = date.today() - timedelta(days=1)

    base_url = "https://www.epexspot.com/en/market-results"
    market_area = "AT"
    auction = "MRC"
    modality = "Auction"
    sub_modality = "DayAhead"
    data_mode = "table"

    trading_date = date_param.strftime("%Y-%m-%d")
    delivery_date = (date_param + timedelta(days=1)).strftime("%Y-%m-%d")

    url = f"{base_url}?" \
          f"market_area={market_area}&" \
          f"auction={auction}&" \
          f"trading_date={trading_date}&" \
          f"delivery_date={delivery_date}&" \
          f"underlying_year=&" \
          f"modality={modality}&" \
          f"sub_modality={sub_modality}&" \
          f"technology=&" \
          f"data_mode={data_mode}&" \
          f"period=&" \
          f"production_period="
    return url


if __name__ == '__main__':
    # Example usage
    today_url = generate_epex_url()
    print("URL for today:", today_url)

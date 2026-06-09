import pandas as pd
import logging
from settings import BASE_DIR, DATA_DIR


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()


def extract(file):
    df = pd.read_csv(file, encoding="latin-1")
    return df


def transform(df):
    extracted_data = df
    
    #rename columns
    new_cols = {
        'Row ID': 'row_id',
        'Order ID': 'order_id',
        'Order Date': 'order_date',
        'Ship Date': 'ship_date',
        'Ship Mode': 'ship_mode',
        'Customer ID': 'customer_id',     
        'Customer Name': 'customer_name',  
        'Segment': 'segment',
        'Country': 'country',
        'City': 'city',
        'State': 'state',
        'Postal Code': 'postal_code',
        'Region': 'region',
        'Product ID': 'product_id',
        'Category': 'category',
        'Sub-Category': 'sub_category',
        'Product Name': 'product_name',
        'Sales': 'sales',
        'Quantity':'quantity',
        'Discount':'discount',
        'Profit':'profit'
    }
    
    extracted_data.rename(columns=new_cols, inplace=True)

    extracted_data["order_date"] = pd.to_datetime(extracted_data["order_date"])
    extracted_data["ship_date"] = pd.to_datetime(extracted_data["ship_date"])

    #removing duplicates, empty rows and sorting the data 
    extracted_data = extracted_data.drop_duplicates()
    extracted_data = extracted_data.dropna()
    extracted_data = extracted_data.sort_values('sales', ascending = False)
    
    return  extracted_data


def load_product(df):
    try:
        fields = ['product_id', 'product_name', 'category', 'sub_category']
        product = df[fields]
        product = product.drop_duplicates(subset=['product_id'])
        return product
    except Exception as e:
        logger.error(f"Erreur product: {e}")


def load_customer(df):
    try:
        fields = ['customer_id', 'customer_name', 'segment',
                  'country', 'city', 'state', 'postal_code', 'region']
        customer = df[fields]
        customer = customer.drop_duplicates(subset=['customer_id'])
        return customer
    except Exception as e:
        logger.error(f"Erreur customer: {e}")


def load_order(df):
    try:
        fields = ['order_id', 'order_date', 'ship_date', 'ship_mode']
        order = df[fields]
        order = order.drop_duplicates(subset=['order_id'])
        return order
    except Exception as e:
        logger.error(f"Erreur order: {e}")


def load_sales(df):
    try:
        fields = ['row_id', 'order_id', 'product_id', 'customer_id', 'sales', 'quantity', 'discount', 'profit']
        sales = df[fields]
        return sales
     
    except Exception as e:
        logger.error(f"Erreur sales: {e}")


if __name__ == "__main__":
    logger.info("Extracting data")
    df = extract(DATA_DIR / 'superstore.csv')
    
    logger.info("Transforming data")
    df = transform(df)
    
    logger.info("Loading data")
    order = load_order(df)
    product = load_product(df)
    customer = load_customer(df)
    sales = load_sales(df)

    order.to_csv(DATA_DIR / "order.csv", index=False)
    product.to_csv(DATA_DIR / "product.csv", index=False)
    customer.to_csv(DATA_DIR / "customer.csv", index=False)
    sales.to_csv(DATA_DIR / "sales.csv", index=False)
        
    logger.info("ETL finished !")
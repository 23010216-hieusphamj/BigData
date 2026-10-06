import csv
import os
import random
from datetime import datetime, timedelta

from faker import Faker
from tqdm import tqdm


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "sql", "data")

os.makedirs(DATA_DIR, exist_ok=True)

fake = Faker("en_US")

random.seed(42)
Faker.seed(42)


CUSTOMER_COUNT = 100_000
PRODUCT_COUNT = 10_000
ORDER_COUNT = 1_000_000

MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 5


def random_datetime(start_year=2023, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)

    delta = end - start
    random_seconds = random.randint(
        0,
        int(delta.total_seconds())
    )

    return start + timedelta(seconds=random_seconds)


def generate_customers():
    path = os.path.join(DATA_DIR, "customers.csv")

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "country",
            "created_at"
        ])

        for customer_id in tqdm(
            range(1, CUSTOMER_COUNT + 1),
            desc="Generating customers"
        ):
            first_name = fake.first_name()
            last_name = fake.last_name()

            phone = fake.numerify("###########")
            city = fake.city()[:50]
            country = fake.country()[:100]

            writer.writerow([
                customer_id,
                first_name,
                last_name,
                f"customer{customer_id}@example.com",
                phone,
                city,
                country,
                random_datetime().strftime("%Y-%m-%d %H:%M:%S")
            ])


def generate_products():
    path = os.path.join(DATA_DIR, "products.csv")

    categories = [
        "Electronics",
        "Computers",
        "Phones",
        "Clothing",
        "Shoes",
        "Home",
        "Books",
        "Sports",
        "Beauty",
        "Toys"
    ]

    product_prices = {}

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "product_id",
            "product_name",
            "category",
            "price",
            "stock_quantity",
            "created_at"
        ])

        for product_id in tqdm(
            range(1, PRODUCT_COUNT + 1),
            desc="Generating products"
        ):
            price = round(random.uniform(5, 2000), 2)

            product_prices[product_id] = price

            writer.writerow([
                product_id,
                fake.catch_phrase()[:150],
                random.choice(categories),
                price,
                random.randint(0, 1000),
                random_datetime().strftime("%Y-%m-%d %H:%M:%S")
            ])

    return product_prices


def generate_orders_and_items(product_prices):
    orders_path = os.path.join(DATA_DIR, "orders.csv")
    items_path = os.path.join(DATA_DIR, "order_items.csv")

    statuses = [
        "pending",
        "processing",
        "completed",
        "cancelled"
    ]

    with open(
        orders_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as orders_file, open(
        items_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as items_file:

        order_writer = csv.writer(orders_file)
        item_writer = csv.writer(items_file)

        order_writer.writerow([
            "order_id",
            "customer_id",
            "order_date",
            "status",
            "total_amount"
        ])

        item_writer.writerow([
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price"
        ])

        order_item_id = 1

        for order_id in tqdm(
            range(1, ORDER_COUNT + 1),
            desc="Generating orders and order_items"
        ):
            customer_id = random.randint(
                1,
                CUSTOMER_COUNT
            )

            order_date = random_datetime().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            status = random.choice(statuses)

            item_count = random.randint(
                MIN_ITEMS_PER_ORDER,
                MAX_ITEMS_PER_ORDER
            )

            selected_products = random.sample(
                range(1, PRODUCT_COUNT + 1),
                item_count
            )

            total_amount = 0

            for product_id in selected_products:
                quantity = random.randint(1, 5)

                unit_price = product_prices[product_id]

                item_total = quantity * unit_price

                total_amount += item_total

                item_writer.writerow([
                    order_item_id,
                    order_id,
                    product_id,
                    quantity,
                    unit_price
                ])

                order_item_id += 1

            total_amount = round(total_amount, 2)

            order_writer.writerow([
                order_id,
                customer_id,
                order_date,
                status,
                total_amount
            ])


if __name__ == "__main__":
    print("Starting BIG DATA generation...")
    print(f"Output directory: {DATA_DIR}")
    print()
    print(f"Customers: {CUSTOMER_COUNT:,}")
    print(f"Products: {PRODUCT_COUNT:,}")
    print(f"Orders: {ORDER_COUNT:,}")
    print(
        f"Items per order: "
        f"{MIN_ITEMS_PER_ORDER}-{MAX_ITEMS_PER_ORDER}"
    )
    print()

    generate_customers()

    product_prices = generate_products()

    generate_orders_and_items(product_prices)

    print()
    print("BIG DATA generation completed.")
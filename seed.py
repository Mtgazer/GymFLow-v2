from data.database import Database

db = Database()

plans = [
    ("Basic", 30, 250),
    ("Premium", 30, 350),
    ("Gold", 30, 500),
]

for name, duration, price in plans:
    success, message = db.add_plan(
        name,
        duration,
        price
    )

    print(name, "->", message)
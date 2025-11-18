import csv


def save_to_csv(data, filename="products.csv"):
    fieldnames = ["title", "price", "rating", "seller", "image", "description"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            writer.writerow({key: item.get(key, "") for key in fieldnames})

    print(f"💾 Saved {len(data)} products → {filename}")

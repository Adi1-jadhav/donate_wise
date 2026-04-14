def should_recommend_pickup(quantity, category, description):
    # Categories that justify pickup even if quantity = 1
    important_categories = ["Winter Wear", "Electronics", "Furniture", "Medical Equipment"]

    # Sanitize inputs to prevent Exceptions (e.g. from None)
    desc_str = str(description).strip() if description else ""
    cat_str = str(category) if category else ""
    
    try:
        qty = int(quantity) if quantity is not None else 0
    except (ValueError, TypeError):
        qty = 1

    # Basic description quality signal
    desc_words = desc_str.split()
    is_good_description = len(desc_words) > 5 or any(keyword in desc_str.lower() for keyword in ["usable", "working", "gently used", "durable"])

    # Pickup recommendation logic
    if qty > 1:
        return True  # Quantity alone justifies pickup
    elif cat_str in important_categories and is_good_description:
        return True
    else:
        return False


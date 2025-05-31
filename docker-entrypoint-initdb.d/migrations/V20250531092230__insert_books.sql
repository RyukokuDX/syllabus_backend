ON CONFLICT (isbn) DO UPDATE SET
    title = EXCLUDED.title,
    publisher = EXCLUDED.publisher,
    price = EXCLUDED.price,
    role = EXCLUDED.role; 
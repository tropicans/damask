import io
import math
import random
import string
import pandas as pd
from faker import Faker

def is_empty_or_nan(x) -> bool:
    if x is None:
        return True
    if isinstance(x, float) and math.isnan(x):
        return True
    if pd.isna(x):
        return True
    val_str = str(x).strip()
    if val_str == "" or val_str.lower() == "nan":
        return True
    return False

def mask_phone() -> str:
    # Indonesian phone: dynamic mix of local format '08...' and international '+628...'
    prefix = random.choice(["08", "+628"])
    suffix = "".join(random.choices(string.digits, k=random.randint(8, 10)))
    return f"{prefix}{suffix}"

def perturb_numeric(val):
    if is_empty_or_nan(val):
        return val
    
    val_str = str(val).strip()
    try:
        # Check if it has a decimal point to apply Smart Typing
        if '.' in val_str:
            original_float = float(val_str)
            decimals = len(val_str.split('.')[1])
            factor = random.uniform(0.8, 1.2)
            new_val = original_float * factor
            return f"{new_val:.{decimals}f}"
        else:
            original_int = int(val_str)
            factor = random.uniform(0.8, 1.2)
            new_val = round(original_int * factor)
            return str(new_val)
    except ValueError:
        # Non-numeric value, skip and keep as is
        return val

def scramble_id(val, cache: dict[str, str]) -> str:
    if is_empty_or_nan(val):
        return val
    
    val_str = str(val)
    if val_str in cache:
        return cache[val_str]
    
    scrambled_chars = []
    for char in val_str:
        if char.isdigit():
            scrambled_chars.append(random.choice(string.digits))
        elif char.islower():
            scrambled_chars.append(random.choice(string.ascii_lowercase))
        elif char.isupper():
            scrambled_chars.append(random.choice(string.ascii_uppercase))
        else:
            scrambled_chars.append(char)
            
    scrambled_str = "".join(scrambled_chars)
    cache[val_str] = scrambled_str
    return scrambled_str

def mask_dataframe(df: pd.DataFrame, rules: dict[str, str]) -> pd.DataFrame:
    df_copy = df.copy()
    
    # Validate columns exist
    for col in rules.keys():
        if col not in df_copy.columns:
            raise ValueError(f"Kolom '{col}' tidak ditemukan di dalam berkas.")
            
    scramble_cache = {}
    fake = Faker(locale=['id_ID', 'en_US'])
    
    for col, rule in rules.items():
        if rule == "No Masking":
            continue
        elif rule == "Fake Name":
            df_copy[col] = df_copy[col].apply(lambda x: fake.name() if not is_empty_or_nan(x) else x)
        elif rule == "Fake Email":
            df_copy[col] = df_copy[col].apply(lambda x: fake.ascii_free_email() if not is_empty_or_nan(x) else x)
        elif rule == "Fake Phone":
            df_copy[col] = df_copy[col].apply(lambda x: mask_phone() if not is_empty_or_nan(x) else x)
        elif rule == "Anonymize ID/Number":
            df_copy[col] = df_copy[col].apply(lambda x: scramble_id(x, scramble_cache))
        elif rule == "Perturb Numeric":
            df_copy[col] = df_copy[col].apply(perturb_numeric)
        else:
            raise ValueError(f"Aturan masking '{rule}' tidak dikenal.")
            
    return df_copy

"""
Data Masker Service module for SecureData Web.
Implements the Strategy Pattern to mask, scramble, perturb, or fake different data fields
inside pandas DataFrames while handling empty cells and keeping data types intact.
"""

import io
import math
import random
import string
import pandas as pd
from faker import Faker

def is_empty_or_nan(x) -> bool:
    """
    Checks if a cell value is empty, None, NaN, or whitespace.
    Args:
        x: Cell value.
    Returns:
        bool: True if the cell is empty or NaN, False otherwise.
    """
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
    """
    Generates a mock Indonesian phone number.
    Uses a dynamic mix of local '08...' and international '+628...' formats.
    Returns:
        str: Synthetic phone number.
    """
    prefix = random.choice(["08", "+628"])
    suffix = "".join(random.choices(string.digits, k=random.randint(8, 10)))
    return f"{prefix}{suffix}"

def perturb_numeric(val):
    """
    Perturbs numeric and financial values by a random factor between -20% and +20%.
    Applies Smart Typing to maintain decimal formatting where applicable.
    Args:
        val: Input number (integer, float, or string).
    Returns:
        str/int/float: Perturbed value or original if non-numeric.
    """
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
    """
    Scrambles alphanumeric IDs while keeping formatting and casing (e.g. A-123 -> X-842).
    Maintains consistencies within the same dataset using a cache dictionary.
    Args:
        val: Original ID.
        cache (dict): Dictionary tracking original-to-scrambled mappings.
    Returns:
        str: Scrambled identifier.
    """
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
    """
    Orchestrates the masking of a pandas DataFrame using the selected rules per column.
    Args:
        df (pd.DataFrame): Input DataFrame to mask.
        rules (dict[str, str]): Column name to masking rule name mapping.
    Raises:
        ValueError: If a column specified in rules does not exist or the rule is invalid.
    Returns:
        pd.DataFrame: A safely masked copy of the original DataFrame.
    """
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

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

def mask_dataframe(
    df: pd.DataFrame, 
    rules: dict[str, str], 
    return_mappings: bool = False
) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, dict[str, str]]]:
    """
    Orchestrates the masking of a pandas DataFrame using the selected rules per column.
    Args:
        df (pd.DataFrame): Input DataFrame to mask.
        rules (dict[str, str]): Column name to masking rule name mapping.
        return_mappings (bool): Whether to generate and return 1-to-1 mappings.
    Raises:
        ValueError: If a column specified in rules does not exist or the rule is invalid.
    Returns:
        pd.DataFrame or (pd.DataFrame, dict): Masked copy of the DataFrame, and optionally the mappings.
    """
    df_copy = df.copy()
    
    # Validate columns exist
    for col in rules.keys():
        if col not in df_copy.columns:
            raise ValueError(f"Kolom '{col}' tidak ditemukan di dalam berkas.")
            
    scramble_cache = {}
    fake = Faker(locale=['id_ID', 'en_US'])
    
    mappings = {}
    
    for col, rule in rules.items():
        if rule == "No Masking":
            continue
            
        if return_mappings:
            # Generate bijective mappings
            unique_original_vals = [
                str(val) for val in df_copy[col].unique() 
                if not is_empty_or_nan(val)
            ]
            col_mapping = {}
            used_values = set()
            
            for orig_val in unique_original_vals:
                success = False
                for _ in range(100):
                    if rule == "Fake Name":
                        candidate = fake.name()
                    elif rule == "Fake Email":
                        candidate = fake.ascii_free_email()
                    elif rule == "Fake Phone":
                        candidate = mask_phone()
                    elif rule == "Anonymize ID/Number":
                        candidate = scramble_id(orig_val, {})
                    elif rule == "Perturb Numeric":
                        candidate = perturb_numeric(orig_val)
                    else:
                        raise ValueError(f"Aturan masking '{rule}' tidak dikenal.")
                    
                    candidate_str = str(candidate)
                    if candidate_str not in used_values:
                        used_values.add(candidate_str)
                        col_mapping[orig_val] = candidate_str
                        success = True
                        break
                
                if not success:
                    counter = 1
                    base_candidate = candidate_str
                    while True:
                        candidate_with_suffix = f"{base_candidate}_{counter}"
                        if candidate_with_suffix not in used_values:
                            used_values.add(candidate_with_suffix)
                            col_mapping[orig_val] = candidate_with_suffix
                            break
                        counter += 1
                        
            mappings[col] = col_mapping
            
            # Apply mapping to column
            df_copy[col] = df_copy[col].apply(
                lambda x: col_mapping[str(x)] if not is_empty_or_nan(x) else x
            )
        else:
            # Original code logic
            if rule == "Fake Name":
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
                
    if return_mappings:
        return df_copy, mappings
    return df_copy

def revert_dataframe(df: pd.DataFrame, mappings: dict[str, dict[str, str]]) -> pd.DataFrame:
    """
    Reverts a masked DataFrame back to its original values using the provided mapping.
    Args:
        df (pd.DataFrame): The masked DataFrame.
        mappings (dict[str, dict[str, str]]): Column name to (original -> masked) value mapping.
    Raises:
        ValueError: If a column in mappings is missing from df, or a value is missing from the mapping.
    Returns:
        pd.DataFrame: The restored original DataFrame.
    """
    df_copy = df.copy()
    
    # 1. Validate that all columns present in mappings exist in the DataFrame
    missing_cols = [col for col in mappings.keys() if col not in df_copy.columns]
    if missing_cols:
        raise ValueError(f"Kolom berikut tidak ditemukan di dalam berkas: {', '.join(missing_cols)}")
        
    # 2. Invert the mappings and prepare for reversion
    inverted_mappings = {}
    for col, col_map in mappings.items():
        inverted_map = {}
        for orig, masked in col_map.items():
            inverted_map[str(masked)] = str(orig)
        inverted_mappings[col] = inverted_map
        
    # 3. For each column and cell: check if the value (as string) is present in the inverted map
    for col, inverted_map in inverted_mappings.items():
        mismatched_vals = []
        for val in df_copy[col]:
            if is_empty_or_nan(val):
                continue
            val_str = str(val)
            if val_str not in inverted_map:
                if val_str not in mismatched_vals:
                    mismatched_vals.append(val_str)
                    
        if mismatched_vals:
            shown_vals = mismatched_vals[:5]
            raise ValueError(
                f"Nilai tidak cocok pada kolom '{col}': {', '.join(shown_vals)}"
                + (" (dan lainnya)" if len(mismatched_vals) > 5 else "")
            )
            
        # 4. Replace cell values with original values
        df_copy[col] = df_copy[col].apply(
            lambda x: inverted_map[str(x)] if not is_empty_or_nan(x) else x
        )
        
    return df_copy

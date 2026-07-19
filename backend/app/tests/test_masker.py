import math
import pandas as pd
import pytest
from app.services.masker import mask_phone, perturb_numeric, scramble_id, mask_dataframe

def test_mask_phone():
    for _ in range(50):
        phone = mask_phone()
        assert phone.startswith("08") or phone.startswith("+628")
        # Check all other characters are digits
        rest = phone[2:] if phone.startswith("08") else phone[4:]
        assert rest.isdigit()
        assert 8 <= len(rest) <= 10

def test_perturb_numeric():
    # Test integer rounding
    for _ in range(20):
        perturbed = perturb_numeric("100")
        val = int(perturbed)
        assert 80 <= val <= 120
        assert str(val) == perturbed  # integer, no decimals

    # Test float precision preservation
    for _ in range(20):
        perturbed = perturb_numeric("12.345")
        assert "." in perturbed
        decimals = len(perturbed.split('.')[1])
        assert decimals == 3
        val = float(perturbed)
        assert 12.345 * 0.8 <= val <= 12.345 * 1.2

    # Test skipping empty / non-numeric
    assert perturb_numeric(None) is None
    assert perturb_numeric("") == ""
    assert perturb_numeric("N/A") == "N/A"
    assert perturb_numeric("abc") == "abc"
    
    # Test math.nan preservation
    nan_val = float('nan')
    assert math.isnan(perturb_numeric(nan_val))

def test_scramble_id():
    cache = {}
    
    # Test scrambling preserves structure and case
    original = "ABC-123-xyz"
    scrambled = scramble_id(original, cache)
    assert len(scrambled) == len(original)
    assert scrambled[3] == "-"
    assert scrambled[7] == "-"
    assert scrambled[0:3].isupper()
    assert scrambled[4:7].isdigit()
    assert scrambled[8:11].islower()
    
    # Test determinism (cache hits)
    assert scramble_id(original, cache) == scrambled
    
    # Test other values
    assert scramble_id(None, cache) is None
    assert scramble_id("", cache) == ""
    
    # Test different value is scrambled differently
    other = "ABC-123-xyz"
    assert scramble_id(other, cache) == scrambled
    different = "XYZ-999-abc"
    assert scramble_id(different, cache) != scrambled

def test_mask_dataframe():
    data = {
        "Nama": ["Budi", "Siti", ""],
        "Email": ["budi@gmail.com", "siti@yahoo.com", None],
        "Telepon": ["0812345678", "+6289999999", ""],
        "ID": ["EMP001", "EMP002", "EMP001"],
        "Gaji": ["10000000", "12500.50", "N/A"],
        "Normal": ["tetap", "tetap", "tetap"]
    }
    df = pd.DataFrame(data)
    
    rules = {
        "Nama": "Fake Name",
        "Email": "Fake Email",
        "Telepon": "Fake Phone",
        "ID": "Anonymize ID/Number",
        "Gaji": "Perturb Numeric",
        "Normal": "No Masking"
    }
    
    masked_df = mask_dataframe(df, rules)
    
    # Check that dimensions are preserved
    assert masked_df.shape == df.shape
    
    # Normal column remains unchanged
    assert list(masked_df["Normal"]) == list(df["Normal"])
    
    # Empty/None values remain empty/None/unchanged
    assert masked_df["Nama"].iloc[2] == ""
    assert pd.isna(masked_df["Email"].iloc[2])
    assert masked_df["Telepon"].iloc[2] == ""
    assert masked_df["Gaji"].iloc[2] == "N/A"
    
    # Names, emails and phones are masked
    assert masked_df["Nama"].iloc[0] != "Budi"
    assert masked_df["Email"].iloc[0] != "budi@gmail.com"
    assert masked_df["Telepon"].iloc[0] != "0812345678"
    
    # Determinism per file check for ID
    assert masked_df["ID"].iloc[0] == masked_df["ID"].iloc[2]
    assert masked_df["ID"].iloc[0] != masked_df["ID"].iloc[1]
    
    # Numeric perturbation checks
    gaji_0 = int(masked_df["Gaji"].iloc[0])
    assert 8000000 <= gaji_0 <= 12000000
    
    gaji_1 = float(masked_df["Gaji"].iloc[1])
    assert 12500.50 * 0.8 <= gaji_1 <= 12500.50 * 1.2
    assert len(masked_df["Gaji"].iloc[1].split('.')[1]) == 2

def test_mask_dataframe_missing_col():
    df = pd.DataFrame({"A": [1, 2]})
    rules = {"B": "Fake Name"}
    with pytest.raises(ValueError, match="Kolom 'B' tidak ditemukan"):
        mask_dataframe(df, rules)

def test_mask_dataframe_unknown_rule():
    df = pd.DataFrame({"A": [1, 2]})
    rules = {"A": "Unknown Rule"}
    with pytest.raises(ValueError, match="Aturan masking 'Unknown Rule' tidak dikenal"):
        mask_dataframe(df, rules)

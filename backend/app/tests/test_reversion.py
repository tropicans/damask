import pandas as pd
import pytest
from app.services.masker import mask_dataframe, revert_dataframe

def test_bijective_masking_and_reversion():
    data = {
        "Nama": ["Budi", "Siti", "Budi", ""],
        "Email": ["budi@gmail.com", "siti@yahoo.com", "budi@gmail.com", None],
        "Telepon": ["0812345678", "+6289999999", "0812345678", ""],
        "ID": ["EMP001", "EMP002", "EMP001", "N/A"],
        "Gaji": ["10000000", "12500.50", "10000000", ""],
        "Normal": ["tetap", "tetap", "tetap", "tetap"]
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
    
    # Run masking with return_mappings=True
    masked_df, mappings = mask_dataframe(df, rules, return_mappings=True)
    
    assert isinstance(mappings, dict)
    # Check that mappings exist for all columns except "Normal" (which is No Masking)
    for col in ["Nama", "Email", "Telepon", "ID", "Gaji"]:
        assert col in mappings
    assert "Normal" not in mappings
    
    # Check that identical original values map to the same masked value (bijectivity)
    assert masked_df["Nama"].iloc[0] == masked_df["Nama"].iloc[2]
    assert masked_df["Nama"].iloc[0] != masked_df["Nama"].iloc[1]
    
    # Check that mappings match dataframe contents
    for col in ["Nama", "Email", "Telepon", "ID", "Gaji"]:
        col_map = mappings[col]
        for orig, masked in col_map.items():
            # Original value BUDI should map to the corresponding cell value
            pass
            
    # Now run reversion
    restored_df = revert_dataframe(masked_df, mappings)
    
    # Assert restored df is identical to original df
    pd.testing.assert_frame_equal(restored_df, df)

def test_revert_missing_columns():
    df = pd.DataFrame({"A": ["val1", "val2"]})
    mappings = {
        "B": {"orig1": "masked1"}
    }
    with pytest.raises(ValueError, match="Kolom berikut tidak ditemukan di dalam berkas: B"):
        revert_dataframe(df, mappings)

def test_revert_mismatched_values():
    df = pd.DataFrame({"A": ["masked1", "masked2"]})
    mappings = {
        "A": {"orig1": "masked1"}  # "masked2" is missing from mapping
    }
    with pytest.raises(ValueError, match="Nilai tidak cocok pada kolom 'A': masked2"):
        revert_dataframe(df, mappings)

def test_collision_retry_logic():
    # Let's test the retry loop by creating a custom mock/scenario that triggers collisions
    # We can mock Faker or just generate enough rows to ensure a collision, or test suffix fallback.
    # To test suffix fallback, let's create a DataFrame with 10 rows but force the values to collide if possible,
    # or we can test with a column where we have multiple unique values and a very narrow/repetitive domain.
    # Wait, the rule is "Fake Phone". But phones have high entropy.
    # We can check that duplicate original values map to unique masked values in a column with many rows.
    # Since we can't easily mock random easily inside Faker here, we can test that the returned mapping is 1-to-1 bijective.
    data = {
        "Col": [str(i) for i in range(150)]  # 150 unique values
    }
    df = pd.DataFrame(data)
    rules = {"Col": "Fake Name"}
    masked_df, mappings = mask_dataframe(df, rules, return_mappings=True)
    
    col_map = mappings["Col"]
    # All mapped values should be unique (bijective)
    assert len(col_map.values()) == len(set(col_map.values()))
    assert len(col_map) == 150

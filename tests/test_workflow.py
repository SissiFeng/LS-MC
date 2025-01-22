def test_full_workflow():
    """Test the complete workflow with a sample file"""
    # Test parameters
    sample_id = "TEST001"
    smiles = "NCCC(NCc(cc1)cc(CN2C(CCC(N3)=O)C3=O)c1C2=O)=O"
    raw_file = Path("tests/data/sample.raw")
    
    # Initialize processor
    processor = DataProcessor()
    
    # Process sample
    result = processor.process_sample(raw_file, sample_id, smiles)
    
    # Verify results
    assert result.sample_id == sample_id
    assert result.formula is not None
    assert result.monoisotopic_mass > 0
    assert isinstance(result.product_detected, bool)
    assert result.purity >= 0 and result.purity <= 100 
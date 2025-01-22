def test_memory_usage():
    """Test memory usage with large files"""
    memory_monitor = MemoryMonitor()
    processor = DataProcessor()
    
    # Process large file
    memory_monitor.log_memory_usage('Start')
    result = processor.process_sample(large_raw_file, "TEST002", smiles)
    memory_monitor.log_memory_usage('End')
    
    # Verify memory usage is within limits
    final_usage = memory_monitor.get_memory_usage()
    assert final_usage['percent'] < 80  # Memory usage should not exceed 80% 
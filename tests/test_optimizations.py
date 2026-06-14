import sys
import time
from PyQt6.QtWidgets import QApplication
from ui.file_model import CustomOrderProxyModel

def test_proxy_model_performance():
    print("Running CustomOrderProxyModel performance test...")
    app = QApplication(sys.argv)
    
    proxy = CustomOrderProxyModel()
    custom_order = [f"file_{i}.txt" for i in range(1000)]
    proxy.set_custom_order(custom_order)
    
    # Simulate a mock source index
    class MockIndex:
        def __init__(self, name, row_idx):
            self.name = name
            self.r = row_idx
        def row(self): return self.r

    class MockModel:
        def fileName(self, idx):
            return idx.name
            
    class MockProxy(CustomOrderProxyModel):
        def sourceModel(self):
            return MockModel()
            
    proxy = MockProxy()
    proxy.set_custom_order(custom_order)
    
    idx1 = MockIndex("file_500.txt", 500)
    idx2 = MockIndex("file_999.txt", 999)
    idx3 = MockIndex("not_in_list.txt", 1000)
    
    # Warmup
    proxy.lessThan(idx1, idx2)
    
    start = time.time()
    for _ in range(10000):
        proxy.lessThan(idx1, idx2)
        proxy.lessThan(idx2, idx3)
        proxy.lessThan(idx3, idx1)
    end = time.time()
    
    print(f"10000 comparisons took {end - start:.4f} seconds")
    if (end - start) < 0.1:
        print("PASS: lessThan is very fast (O(1) lookup working)")
    else:
        print("FAIL: lessThan is slow")

if __name__ == "__main__":
    test_proxy_model_performance()

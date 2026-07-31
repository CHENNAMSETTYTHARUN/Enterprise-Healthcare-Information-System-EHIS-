from app.models.lab_pharmacy import (
    LabTest, LabOrder, LabSample, LabResult, Medicine, StockBatch, MedicineDispensing, InventoryItem
)
from app.repositories.base import BaseRepository

class LabTestRepository(BaseRepository[LabTest]):
    def __init__(self):
        super().__init__(LabTest)

class LabOrderRepository(BaseRepository[LabOrder]):
    def __init__(self):
        super().__init__(LabOrder)

class LabSampleRepository(BaseRepository[LabSample]):
    def __init__(self):
        super().__init__(LabSample)

class LabResultRepository(BaseRepository[LabResult]):
    def __init__(self):
        super().__init__(LabResult)

class MedicineRepository(BaseRepository[Medicine]):
    def __init__(self):
        super().__init__(Medicine)

class StockBatchRepository(BaseRepository[StockBatch]):
    def __init__(self):
        super().__init__(StockBatch)

class DispensingRepository(BaseRepository[MedicineDispensing]):
    def __init__(self):
        super().__init__(MedicineDispensing)

class InventoryItemRepository(BaseRepository[InventoryItem]):
    def __init__(self):
        super().__init__(InventoryItem)

lab_test_repository = LabTestRepository()
lab_order_repository = LabOrderRepository()
lab_sample_repository = LabSampleRepository()
lab_result_repository = LabResultRepository()
medicine_repository = MedicineRepository()
stock_batch_repository = StockBatchRepository()
dispensing_repository = DispensingRepository()
inventory_item_repository = InventoryItemRepository()

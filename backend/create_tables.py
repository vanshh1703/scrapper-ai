from core.database import Base, engine
import models.user
import models.product
import models.history

print("Attempting to create all tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: Tables created.")
except Exception as e:
    import traceback
    traceback.print_exc()

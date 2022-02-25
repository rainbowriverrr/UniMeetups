from website import create_app
import os
from website.mongo_helpers import find_meetups



app = create_app()

if __name__ == "__main__":
  app.run(host="0.0.0.0",port=8080)
  
    
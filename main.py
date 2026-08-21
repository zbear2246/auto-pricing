from sys import exception

import uvicorn



if __name__ == "__main__":
    try:
        uvicorn.run(
            "src.auto_pricing.main:app",
            host="localhost",
            port=8000,
            reload=True
        )
    except KeyboardInterrupt:
        print("user quit")

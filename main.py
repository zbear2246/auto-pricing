import argparse
import uvicorn

def arpar():
    parser = argparse.ArgumentParser(description="om nom nom nom")
    
    parser.add_argument(
        "-H", "--host",
        default="localhost",
        type=str,
        required=False,
        help="Must be any valid host type"
    )
    
    parser.add_argument(
        "-p", "--port",
        default=8000,
        type=int,
        required=False
    )
    
    args = parser.parse_args()
    
    host = args.host
    port = args.port
    
    return host, port

if __name__ == "__main__":
    host, port = arpar()
    
    try:
        uvicorn.run(
            "src.auto_pricing.main:app",
            host=host,
            port=port,
            reload=True
        )
    except KeyboardInterrupt:
        print("user quit")

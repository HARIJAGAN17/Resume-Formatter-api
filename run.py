import subprocess

def run_uvicorn():
    try:
        subprocess.run(["uvicorn", "app.main:app", "--reload"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Uvicorn: {e}")

if __name__ == "__main__":
    run_uvicorn()

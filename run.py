import sys
from core.sp2n_pipeline import sp2n_pipeline

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong number of arguments passed. Usage: python run.py <n>")
        sys.exit(1)
    
    n = int(sys.argv[1])
    csv_save_path = f"results/{n}.csv"
    sp2n_pipeline(n, csv_save_path).run()

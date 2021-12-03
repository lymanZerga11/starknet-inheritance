from recursive_inheritance import recursive_inheritance
from writer import write

def main():
    child = dict()
    x = recursive_inheritance(child, "A.cairo")
    write(x, "A_final.cairo")


if __name__ == "__main__":
    main()
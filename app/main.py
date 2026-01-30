from db import insert_diaper_changes 
from user_input import user_input
from fastapi import FastAPI


app = FastAPI()


def main():
    insert_diaper_changes()



if __name__ == "__main__":
    main()



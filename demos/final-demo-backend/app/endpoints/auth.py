from fastapi import APIRouter

router = APIRouter(prefix="/auth")


@router.post("/login")
def login():
    pass


@router.post("/register")
def register():
    pass

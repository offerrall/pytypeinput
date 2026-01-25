from pytypeinput import Field, Label, Description, Annotated, Email

from visual_test_base import run_visual_test


def create_order(
    id: Annotated[int, Field(ge=1), Label("Product ID")],
    customer_email: Annotated[Email, Description("Customer's email address"), Label("Email")],
    shipping_address: Annotated[str, Description("Full shipping address")],
    quantity: Annotated[int, Field(ge=1, le=999), Label("Quantity (1-999)")] = 1,
    express_delivery: bool = False,
    notes: str | None = None
):
    pass


if __name__ == "__main__":
    run_visual_test(create_order, "Function to GUI")
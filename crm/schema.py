import re
import graphene
from django.db import transaction
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from crm.models import Customer, Product, Order
from crm.filters import CustomerFilter, ProductFilter, OrderFilter

# GraphQL Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


## Mutations
# CreateCustomer Mutation
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")

        if phone and not re.match(r"^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$", phone):
            raise Exception("Invalid phone format. Use +1234567890 or 123-456-7890.")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()

        return CreateCustomer(customer=customer, message="Customer created successfully.")

# BulkCreateCustomers Mutation
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(
            graphene.NonNull(
                graphene.InputObjectType(
                    "CustomerInput",
                    name=graphene.String(required=True),
                    email=graphene.String(required=True),
                    phone=graphene.String(),
                )
            )
        )

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, customers):
        created_customers = []
        errors = []

        for data in customers:
            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")

            if Customer.objects.filter(email=email).exists():
                errors.append(f"Duplicate email: {email}")
                continue

            if phone and not re.match(r"^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$", phone):
                errors.append(f"Invalid phone for {email}")
                continue

            customer = Customer(name=name, email=email, phone=phone)
            customer.save()
            created_customers.append(customer)

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# CreateProduct Mutation
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

# CreateOrder Mutation
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)

    @transaction.atomic
    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        if not product_ids:
            raise Exception("At least one product ID is required.")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more product IDs are invalid.")

        total_amount = sum(p.price for p in products)

        order = Order.objects.create(
            customer=customer, total_amount=total_amount, order_date=order_date
        )
        order.products.set(products)
        order.save()

        return CreateOrder(order=order)

# UpdateLowStockProducts Mutation
class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        if not low_stock_products.exists():
            return UpdateLowStockProducts(updated_products=[], message="No low-stock products found.")

        updated = []
        for product in low_stock_products:
            product.stock += 10  # Simulate restocking
            product.save()
            updated.append(product)

        return UpdateLowStockProducts(
            updated_products=updated,
            message=f"{len(updated)} product(s) restocked successfully."
        )

# Combine Mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

# Filterable Query Setup
class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerNode, order_by=graphene.String())
    all_products = DjangoFilterConnectionField(ProductNode, order_by=graphene.String())
    all_orders = DjangoFilterConnectionField(OrderNode, order_by=graphene.String())

    def resolve_all_customers(root, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_products(root, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_orders(root, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

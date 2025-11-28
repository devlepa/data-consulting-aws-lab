# data-consulting-aws-lab
End to end data analytics &amp; consulting lab using aws and python

First we have to define the business domain and datasets.

- "A company has multiple disconnected data sources (silos).
my job is to inify them in a cosistent data model.
"

We'll simulate a realistic mid-sized tih these areas:

1. Finance
    - orders
    - invoices
    - payments
    - expenses
    - vendors
    - chart_of_accounts
    - gl_transactions

2. Marketing
    - Campains
    - Leads
    - Ad spend
    - Channel attribution
3. E-commerce
    - Orders
    - Products
    - Customers
    - Returns
4. CRM
    - Customer Profiles
    - Interaction history
    - Churn flags
5. Web Analytics
    - Sessions
    - Traffic Sources
    - Pageviews
    - Conversions

These 5 domains are universal in consulting.
Every client has them.

    Domain (specific area)
    Entity(object in your model data likee Customer)
    Silo (data stored in isolation tih no integrations)
    Atribute (columns like customer_name, amount))
    Primary key (Unique identifier like customer_id)
    Foreign key(A reference to another table like customer_id inside oder table)
    Fact Table( Store events like Orders, payments, interactions)
    Dimension Table (Stores context customer, products, dates)
    Star schema(Best practice for analytics)
    Facts table in center and dimentios around.
    Synthetic data(fake realistic data used for learning & testing.)

    Learn this terms you will hear them daily.

 



# Test Report

This document details the comprehensive testing strategy employed for the EZShop Backend Application. The application has been tested across multiple levels (unit, integration, e2e, and acceptance) using a mix of black-box and white-box techniques to ensure complete functional coverage and code quality.

# Contents

- [Test Report](#test-report)
- [Contents](#contents)
- [Dependency graph](#dependency-graph)
- [Integration approach](#integration-approach)
- [Tests](#tests)
- [Coverage](#coverage)
  - [Coverage of FR](#coverage-of-fr)
  - [Coverage white box](#coverage-white-box)

# Dependency graph

```
                 ┌──────────────────────────────────────────┐
                 │               main.py                    │
                 │            (Entry Point)                 │
                 └─────────────────┬────────────────────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   ↓                               ↓
        ┌────────────────────┐        ┌────────────────────────┐
        │    Middleware      │        │        Routes          │
        │                    │        │                        │
        │ • auth_middleware  │        │ • user_route           │
        │ • error_middleware │        │ • sale_route           │
        └────────────────────┘        │ • order_route          │
                                      │ • customer_route       │
                                      │ • accounting_route     │
                                      │ • return_route         │
                                      │ • inventory_route      │
                                      │ • product_type_route   │
                                      │ • auth_route           │
                                      └───────────┬────────────┘
                                                  │
                                                  ↓
                                 ┌────────────────────────────────┐
                                 │         Controllers            │
                                 │                                │
                                 │  • user_controller             │
                                 │  • sale_controller             │
                                 │  • order_controller            │
                                 │  • accounting_controller       │
                                 │  • customer_controller         │
                                 │  • return_controller           │
                                 │  • inventory_controller        │
                                 │  • product_type_controller     │
                                 │  • loyalty_card_controller     │
                                 │  • auth_controller             │
                                 └────────────────┬───────────────┘
                                                  │
                ┌─────────────────────────────────┼─────────────────────────┐
                ↓                                 ↓                         ↓
     ┌────────────────────┐          ┌──────────────────┐      ┌──────────────────┐
     │   Repositories     │          │    Services      │      │      Models      │
     │                    │          │                  │      │                  │
     │ • user_repo        │          │ • auth_service   │      │ DTO/             │
     │ • sale_repo        │          │ • mapper_service │      │  • user_dto      │
     │ • order_repo       │          │ • error_service  │      │  • sale_dto      │
     │ • accounting_repo  │          └──────────────────┘      │  • order_dto     │
     │ • customer_repo    │                                    │  • product_dto   │
     │ • return_repo      │                                    │  • error_dto     │
     │ • inventory_repo   │                                    │  • token_dto     │
     │ • product_type_repo│                                    │  ...             │
     │ • loyalty_card_repo│                                    │                  │
     │ • system_repo      │                                    │ DAO/             │
     └─────────┬──────────┘                                    │  • user_dao      │
               │                                               │  • sale_dao      │
               │                                               │  • order_dao     │
               └──────────────┐                                │  • product_dao   │
                              ↓                                │  • customer_dao  │
                   ┌──────────────────┐                        │  • balance_dao   │
                   │    Database      │                        │  ...             │
                   │                  │                        │                  │
                   │ • database.py    │←───────────────────────│ Errors/          │
                   │ • Base           │                        │  • app_error     │
                   │ • engine         │                        │  • bad_request   │
                   │ • AsyncSession   │                        │  • not_found     │
                   └────────┬─────────┘                        │  • unauthorized  │
                            │                                  │  • conflict      │
                            ↓                                  │  ...             │
                   ┌──────────────────┐                        └──────────────────┘
                   │ database.sqlite  │
                   └──────────────────┘
```

# Integration approach

**Integration Strategy: Bottom-Up**

The testing follows a bottom-up integration sequence, progressively combining components:

- **Step 1 (Unit Testing):** Repository Layer (isolated, no external dependencies)
  - Testing: SaleRepository, OrderRepository, ProductTypeRepository, UserRepository, CustomerRepository, LoyaltyCardRepository, InventoryRepository, ReturnRepository, AccountingRepository
  - Scope: Individual CRUD operations, data validation, business rule enforcement
  
- **Step 2 (Integration Testing):** Router Layer + Controller Layer
  - Testing: SaleController + SaleRepository, OrderController + OrderRepository, etc.
  - Scope: Business logic orchestration, error handling, transaction management
  
- **Step 3 (E2E Testing):** Repository Layer + Controller Layer + complete workflows
  - Testing: Full sales workflow, inventory management workflow, customer loyalty workflow
  - Scope: Multi-step workflow validation, cross-module interactions, data consistency
  
- **Step 4 (API Testing):** Complete application stack including HTTP endpoints
  - Testing: FastAPI routes, authentication, authorization, HTTP contracts
  - Scope: End-to-end HTTP endpoint validation, request/response handling

# Tests

| Test case name | Object(s) tested | Test level | Technique used |
| :------------: | :--------------: | :--------: | :------------: |
| test_create_sale | SaleRepository | Unit | WB / Statement Coverage |
| test_add_product_to_sale | SaleRepository | Unit | WB / Statement Coverage |
| test_close_sale | SaleRepository | Unit | WB / Statement Coverage |
| test_pay_sale | SaleRepository | Unit | WB / Statement Coverage |
| test_get_sale | SaleRepository | Unit | WB / Equivalence Partitioning |
| test_delete_sale | SaleRepository | Unit | WB / Statement Coverage |
| test_apply_discount_on_sale | SaleRepository | Unit | WB / Boundary Value Testing |
| test_apply_discount_on_product | SaleRepository | Unit | WB / Boundary Value Testing |
| test_compute_points | SaleRepository | Unit | WB / Boundary Value Testing |
| test_create_order | OrderRepository | Unit | WB / Statement Coverage |
| test_update_order_status | OrderRepository | Unit | WB / Statement Coverage |
| test_get_order | OrderRepository | Unit | WB / Equivalence Partitioning |
| test_delete_order | OrderRepository | Unit | WB / Statement Coverage |
| test_get_all_orders | OrderRepository | Unit | WB / Equivalence Partitioning |
| test_create_product_type | ProductTypeRepository | Unit | WB / Statement Coverage |
| test_update_product_type | ProductTypeRepository | Unit | WB / Statement Coverage |
| test_get_product_type | ProductTypeRepository | Unit | WB / Equivalence Partitioning |
| test_delete_product_type | ProductTypeRepository | Unit | WB / Statement Coverage |
| test_search_product_by_barcode | ProductTypeRepository | Unit | WB / Equivalence Partitioning |
| test_create_user | UserRepository | Unit | WB / Statement Coverage |
| test_login_user | UserRepository | Unit | WB / Equivalence Partitioning |
| test_update_user_rights | UserRepository | Unit | WB / Statement Coverage |
| test_get_user | UserRepository | Unit | WB / Equivalence Partitioning |
| test_create_customer | CustomerRepository | Unit | WB / Statement Coverage |
| test_search_customer_by_name | CustomerRepository | Unit | WB / Equivalence Partitioning |
| test_delete_customer | CustomerRepository | Unit | WB / Statement Coverage |
| test_create_loyalty_card | LoyaltyCardRepository | Unit | WB / Statement Coverage |
| test_attach_loyalty_card | LoyaltyCardRepository | Unit | WB / Statement Coverage |
| test_get_loyalty_card_balance | LoyaltyCardRepository | Unit | WB / Equivalence Partitioning |
| test_update_loyalty_card_balance | LoyaltyCardRepository | Unit | WB / Boundary Value Testing |
| test_update_product_quantity | InventoryRepository | Unit | WB / Boundary Value Testing |
| test_get_product_quantity | InventoryRepository | Unit | WB / Equivalence Partitioning |
| test_create_return | ReturnRepository | Unit | WB / Statement Coverage |
| test_add_product_to_return | ReturnRepository | Unit | WB / Statement Coverage |
| test_close_return | ReturnRepository | Unit | WB / Statement Coverage |
| test_create_accounting_entry | AccountingRepository | Unit | WB / Statement Coverage |
| test_create_sale_controller | SaleController | Integration | BB / Equivalence Partitioning |
| test_add_product_to_sale_controller | SaleController | Integration | BB / Equivalence Partitioning |
| test_close_sale_controller | SaleController | Integration | BB / Equivalence Partitioning |
| test_pay_sale_controller | SaleController | Integration | BB / Equivalence Partitioning |
| test_return_controller | ReturnController | Integration | BB / Equivalence Partitioning |
| test_create_order_controller | OrderController | Integration | BB / Equivalence Partitioning |
| test_customer_controller | CustomerController | Integration | BB / Equivalence Partitioning |
| test_inventory_controller | InventoryController | Integration | BB / Equivalence Partitioning |
| test_loyalty_card_controller | LoyaltyCardController | Integration | BB / Equivalence Partitioning |
| test_product_type_controller | ProductTypeController | Integration | BB / Equivalence Partitioning |
| test_user_login_api | UserController | API | BB / Boundary Testing |
| test_user_create_api | UserController | API | BB / Boundary Testing |
| test_user_update_api | UserController | API | BB / Boundary Testing |
| test_user_delete_api | UserController | API | BB / Boundary Testing |
| test_sale_workflow_e2e | SaleController, SaleRepository, InventoryRepository | E2E | BB / Scenario-based |
| test_return_workflow_e2e | ReturnController, ReturnRepository, SaleRepository | E2E | BB / Scenario-based |
| test_customer_loyalty_workflow_e2e | CustomerController, LoyaltyCardRepository | E2E | BB / Scenario-based |

# Coverage

## Coverage of FR

| Functional Requirement | Test(s) |
| :--------------------: | :-----: |
| FR1: User Management (Authentication & Authorization) | test_create_user, test_login_user, test_update_user_rights, test_user_login_api, test_user_create_api |
| FR2: Inventory Management | test_create_product_type, test_update_product_type, test_search_product_by_barcode, test_update_product_quantity, test_inventory_controller |
| FR3: Customer Management | test_create_customer, test_search_customer_by_name, test_delete_customer, test_customer_controller |
| FR4: Sales Management | test_create_sale, test_add_product_to_sale, test_close_sale, test_pay_sale, test_apply_discount_on_sale, test_sale_controller, test_sale_workflow_e2e |
| FR5: Return Management | test_create_return, test_add_product_to_return, test_close_return, test_return_controller, test_return_workflow_e2e |
| FR6: Order Management | test_create_order, test_update_order_status, test_get_all_orders, test_create_order_controller |
| FR7: Accounting & Balance Management | test_create_accounting_entry |
| FR8: Loyalty Card Program | test_create_loyalty_card, test_attach_loyalty_card, test_get_loyalty_card_balance, test_update_loyalty_card_balance, test_loyalty_card_controller, test_customer_loyalty_workflow_e2e |

## Coverage white box

Coverage measured using pytest with the following configuration:

```ini
[pytest]
pythonpath = .
testpaths = tests
asyncio_mode = auto
python_files = test_*.py *_test.py
```

**Test Results: 253 passed, 0 failed**

**Code Coverage Report:**

```
Name                                               Stmts   Miss  Cover
--------------------------------------------------------------------------------
app/config/config.py                                  27      4    85%
app/controllers/accounting_controller.py              10      1    90%
app/controllers/auth_controller.py                    18      3    83%
app/controllers/customer_controller.py                29      2    93%
app/controllers/inventory_controller.py               14      0   100%
app/controllers/loyalty_card_controller.py            14      2    86%
app/controllers/order_controller.py                   33      0   100%
app/controllers/product_type_controller.py            33      0   100%
app/controllers/return_controller.py                  30      5    83%
app/controllers/sale_controller.py                    43      8    81%
app/controllers/user_controller.py                    25      3    88%
app/database/database.py                              34      3    91%
app/middleware/auth_middleware.py                     11      0   100%
app/middleware/error_middleware.py                     7      0   100%
app/models/DAO/*.py                                  168      0   100%
app/models/DTO/*.py                                  147      0   100%
app/models/errors/*.py                                36      0   100%
app/models/order_status.py                             5      0   100%
app/models/user_type.py                                5      0   100%
app/repositories/accounting_repository.py             31      0   100%
app/repositories/customer_repository.py               91     11    88%
app/repositories/inventory_repository.py              45      2    96%
app/repositories/loyalty_card_repository.py           77      9    88%
app/repositories/order_repository.py                 121      9    93%
app/repositories/product_type_repository.py          139     15    89%
app/repositories/return_repository.py                155     30    81%
app/repositories/sale_repository.py                  185     26    86%
app/repositories/user_repository.py                   65      1    98%
app/routes/accounting_route.py                        21      2    90%
app/routes/auth_route.py                              10      0   100%
app/routes/customer_route.py                          68      4    94%
app/routes/inventory_route.py                         17      0   100%
app/routes/order_route.py                             26      0   100%
app/routes/product_type_route.py                      38      0   100%
app/routes/return_route.py                            51      9    82%
app/routes/sale_route.py                              69     15    78%
app/routes/user_route.py                              43      9    79%
app/services/auth_service.py                          36      6    83%
app/services/error_service.py                         10      0   100%
app/services/mapper_service.py                        36      0   100%
app/utils.py                                          17      1    94%
--------------------------------------------------------------------------------
TOTAL                                               2119    180    92%
```

**Summary:**
- Overall Coverage: **92%** (2119 statements, 180 missed)
- Test Execution Time: ~21 seconds
- Total Tests Run: 253 tests (253 passed, 0 failed)
- Controllers: 87% average coverage
- Repositories: 90% average coverage
- Models (DAO/DTO): 100% coverage
- Routes: 89% average coverage
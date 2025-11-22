---
title: Graphical User Interface Prototype

---

# Graphical User Interface Prototype


Date: 23/11/2025

Version: 2.0.0

- [Use Cases](#use-cases)
    - [UC1 Authenticate](#uc1-authenticate)
        - [Scenario 1.1: Nominal scenario (Employee authenticates)](#scenario-11-nominal-scenario-employee-authenticates)
        - [Scenario 1.2: Shop Manager authenticates](#scenario-12-shop-manager-authenticates)
        - [Scenario 1.3: Accountant authenticates](#scenario-13-accountant-authenticates)
        - [Scenario 1.4: IT authenticates](#scenario-14-it-authenticates)
        - [Scenario 1.5: First time Shop Login](#scenario-15-first-time-shop-login)
        - [Scenario 1.6: Normal Shop Login](#scenario-16-normal-shop-login)
    - [UC2 Process Sale](#uc2-process-sale)
        - [Scenario 2.1: Nominal scenario (Cash Payment)](#scenario-21-nominal-scenario-cash-payment)
        - [Scenario 2.2: Credit/debit card payment](#scenario-22-creditdebit-card-payment)
        - [Scenario 2.3: Remove Product](#scenario-23-remove-Product)
        - [Scenario 2.4: Modify quantity](#scenario-24-modify-quantity)
        - [Scenario 2.5: Cancel Sale](#scenario-25-cancel-sale)
    - [UC3 Handle Return](#uc3-handle-return)
        - [Scenario 3.1: Nominal Scenario (Cash Refund)](#scenario-31-nominal-scenario-cash-refund)
        - [Scenario 3.2: Card Refund](#scenario-32-card-refund)
    - [UC4 End-of-Day Reconciliation](#uc4-end-of-day-reconciliation)
        - [Scenario 4.1: Nominal Scenario (Open Register)](#scenario-41-nominal-scenario-open-register)
        - [Scenario 4.2: Close Register](#scenario-42-close-register)
    - [UC5 Manage Products and Inventory](#uc5-manage-Products-and-inventory)
        - [Scenario 5.1: Nominal Scenario (Manage Product Definitions)](#scenario-51-nominal-scenario-manage-Product-definitions)
        - [Scenario 5.2: Adjust Stock quantity](#scenario-52-adjust-stock-quantity)
        - [Scenario 5.3: Record delivery](#scenario-53-record-delivery)
    - [UC6 Manage Supplier Information](#uc6-manage-Supplier-information)
        - [Scenario 6.1: Nominal Scenario (Create New Supplier)](#scenario-61-nominal-scenario-create-new-Supplier)
        - [Scenario 6.2: Update Supplier Information](#scenario-62-update-Supplier-information)
        - [Scenario 6.3: Deactivate Supplier](#scenario-63-deactivate-Supplier)
    - [UC7 Place Supplier Order](#uc7-place-Supplier-order)
        - [Scenario 7.1: Nominal Scenario (Create and Send PO)](#scenario-71-nominal-scenario-create-and-send-po)
        - [Scenario 7.2: Create and Save as Draft](#scenario-72-create-and-save-as-draft)
    - [UC8 Generate Report](#uc8-generate-report)
        - [Scenario 8.1: Nominal Scenario (Generate Inventory Valuation Report)](#scenario-81-nominal-scenario-generate-inventory-valuation-report)
        - [Scenario 8.2: Generate unfiltered sales report](#scenario-82-generate-unfiltered-sales-report)
        - [Scenario 8.3: Generate Sales Report filtered by Register ID](#scenario-83-generate-sales-report-filtered-by-register-id)
        - [Scenario 8.4: Generate sales report filtered by Employee ID](#scenario-84-generate-sales-report-filtered-by-employee-id)
        - [Scenario 8.5: Generate PO Report](#scenario-85-generate-po-report)
    - [UC9 Manage Account Passcodes and Shop Password](#uc9-manage-account-passcodes-and-shop-password)
        - [Scenario 9.1: Nominal Scenario (Change Passcode/Password)](#scenario-91-nominal-scenario-change-passcodepassword)
    - [UC10 Manage Registers](#uc10-manage-registers)
        - [Scenario 10.1: Nominal scenario (Add Cash Register)](#scenario-101-nominal-scenario-add-cash-register)
        - [Scenario 10.2: Change Payment Terminal connected to a register](#scenario-102-change-payment-terminal-connected-to-a-register)
    - [UC11 Manage Employees](#uc11-manage-employees)
        - [Scenario 11.1: Nominal Scenario (Create new employee)](#scenario-111-nominal-scenario-create-new-employee)
        - [Scenario 11.2: Update Employee](#scenario-112-update-employee)
        - [Scenario 11.3: Deactivate Employee](#scenario-113-deactivate-employee)
    - [UC12 Perform System Maintenance](#uc12-perform-system-maintenance)
        - [Scenario 12.1: Nominal Scenario (View and Export Logs)](#scenario-121-nominal-scenario-view-and-export-logs)
        - [Scenario 12.2: Apply Software Update](#scenario-122-apply-software-update)
        - [Scenario 12.3: View System Diagnostics](#scenario-123-view-system-diagnostics)

# Use cases

## UC1 Authenticate

### Scenario 1.1: Nominal Scenario (Employee Authenticates)

![alt text](./Prototype/EmployeeAuthetication.png)

![alt text](./Prototype/POSMainMenu.png)

### Scenario 1.2: Shop Manager Authenticates 

![alt text](./Prototype/AdministrationAuthentication.png)

![alt text](./Prototype/ManagerAdministrationArea.png)

### Scenario 1.3: Accountant Authenticates 

![alt text](./Prototype/AdministrationAuthentication.png)

![alt text](./Prototype/AccountantAdministrationArea.png)

### Scenario 1.4: IT Authenticates 

![alt text](./Prototype/AdministrationAuthentication.png)

![alt text](./Prototype/ITAdministrationArea.png)

### Scenario 1.5: First time SHop Login 

![alt text](./Prototype/NormalAuthentication.png)

![alt text](./Prototype/FirstTimeShopPasswordChange.png)

![alt text](./Prototype/RoleSelectionScreen.png)

### Scenario 1.5: Normal Shop Login

![alt text](./Prototype/NormalAuthentication.png)

![alt text](./Prototype/RoleSelectionScreen.png)

## UC2 Process Sale

### Scenario 2.1: Nominal scenario (Cash Payment)
![alt text](./Prototype/NewSale.png)
![alt text](./Prototype/ProductSearch.png)
![alt text](./Prototype/ProductAddedToSale.png)
![alt text](./Prototype/AnotherProductAddedToSale.png)
![alt text](./Prototype/PaymentSelection.png)
![alt text](./Prototype/CashPayment1.png)
![alt text](./Prototype/CashPayment2.png)

### Scenario 2.2: Credit/debit card payment

![alt text](./Prototype/CardPayment1.png)

![alt text](./Prototype/CashPayment2.png)

### Scenario 2.3: Remove Product

![alt text](./Prototype/RemoveProductFromSale.png)

### Scenario 2.4: Modify quantity

![alt text](./Prototype/ChangeProductQuantity.png)

### Scenario 2.5: Cancel Sale
The Employee should simply press the "Cancel Sale" button to cancel the sale. 

![alt text](./Prototype/AnotherProductAddedToSale.png)

## UC3 Handle Return

### Scenario 3.2: Card Refund

![alt text](./Prototype/InsertTransactionID.png)

![alt text](./Prototype/ReturnScreen.png)

![alt text](./Prototype/ReturnScreen1.png)

## UC4 End-of-Day Reconciliation

### Scenario 4.1: Nominal Scenario (Open Register)

![alt text](./Prototype/OpenRegister1.png)

![alt text](./Prototype/OpenRegister2.png)

### Scenario 4.2: Close Register

![alt text](./Prototype/CloseRegister1.png)

![alt text](./Prototype/CloseRegister2.png)

## UC5 Manage Products and Inventory

### Scenario 5.1: Nominal Scenario (Manage Product Definitions)

![alt text](./Prototype/ManageProductsSection.png)

![alt text](./Prototype/NewProduct.png)

![alt text](./Prototype/EditProduct.png)

### Scenario 5.2: Adjust Stock quantity

![alt text](./Prototype/ManageInventorySection.png)

![alt text](./Prototype/AdjustStockQuantity.png)

### Scenario 5.3: Record delivery

![alt text](./Prototype/RecordDelivery1.png)

![alt text](./Prototype/DeliveryFromExistingOrder.png)

![alt text](./Prototype/DeliveryWithoutSupplier.png)

## UC6 Manage Supplier Information

### Scenario 6.1: Nominal Scenario (Create New Supplier)

![alt text](./Prototype/ManageSuppliersScreen.png)
![alt text](./Prototype/AddNewSupplier.png)

### Scenario 6.2: Update Supplier Information
![alt text](./Prototype/UpdateSupplierInformation.png)

### Scenario 6.3: Deactivate Supplier
The Shop Manager should simply press the "Deactivate" button.
![alt text](./Prototype/ManageSuppliersScreen.png)

## UC7 Place Supplier Order

### Scenario 7.1: Nominal Scenario (Create and Send PO)

![alt text](./Prototype/ManagePurchaseOrdersScreen.png)

![alt text](./Prototype/SelectSupplier.png)

![alt text](./Prototype/SearchProducts.png)

![alt text](./Prototype/SearchProductsAdd.png)

![alt text](./Prototype/LowStockReport.png)

![alt text](./Prototype/LowStockReportAdd.png)
To send to PO, the Shop Manager should export the PO and send it to the Supplier manually. Then he can manually "Mark as sent" the PO. 

### Scenario 7.2: Create and Save as Draft
The images are the same as above. To save as draft the PO, the Shop Manager should press the "Mark as draft" button. 

## UC8 Generate Report

### Scenario 8.1: Nominal Scenario (Generate Inventory Valuation Report)

![alt text](./Prototype/SupportAccountingScreen.png)

![alt text](./Prototype/GenerateInventoryValuationReport.png)

### Scenario 8.2: Generate unfiltered sales report

![alt text](./Prototype/GenerateUnfilteredSalesReport.png)

### Scenario 8.3: Generate Sales Report filtered by Register ID

![alt text](./Prototype/GenerateSalesReportByRegister.png)

### Scenario 8.4: Generate sales report filtered by Employee ID

![alt text](./Prototype/GenerateSalesReportByEmployee.png)

### Scenario 8.5: Generate PO Report

![alt text](./Prototype/GeneratePOReport.png)

## UC9 Manage Account Passcodes and Shop Password

### Scenario 9.1: Nominal Scenario (Change Passcode/Password)

![alt text](./Prototype/ManageAccountsScreen.png)
![alt text](./Prototype/ChangePassword.png)
![alt text](./Prototype/ChangePasscode.png)

## UC10 Manage Registers

### Scenario 10.1: Nominal scenario (Add Cash Register)
![alt text](./Prototype/ManageRegistersScreen.png)
![alt text](./Prototype/AddNewCashRegister.png)

### Scenario 10.2: Change Payment Terminal connected to a register
![alt text](./Prototype/ModifyPaymentTerminal.png)

## UC11 Manage Employees

### Scenario 11.1: Nominal Scenario (Create new employee)
![alt text](./Prototype/ManageEmployeesScreen.png)
![alt text](./Prototype/CreateNewEmployee.png)

### Scenario 11.2: Update Employee
![alt text](./Prototype/UpdateEmployee.png)

### Scenario 11.3: Deactivate Employee
![alt text](./Prototype/DeactivateEmployee.png)
To deactivate an Employee, the Shop Manager should simply switch the status in the update section. 

## UC12 Perform System Maintenance

### Scenario 12.1: Nominal Scenario (View and Export Logs)
![alt text](./Prototype/SystemMaintenanceScreen.png)
![alt text](./Prototype/ViewAndExportLogs.png)

### Scenario 12.2: Apply Software Update
The IT should apply the software update by pressing the "Apply Software Update" button. 

### Scenario 12.3: View System Diagnostics
![alt text](./Prototype/ViewSystemDiagnostics.png)
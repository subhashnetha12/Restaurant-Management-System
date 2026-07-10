# Restaurant Management System - Inventory Plan

## Purpose

This plan defines the inventory module separately from the main restaurant role plan.

Inventory is included because the current Django models already contain:

- `app2.models.Inventory`
- `Staff.ROLE_CHOICES` value: `inventory`

The inventory version should work as a stock master, purchase tracker, vendor tracker, stock movement audit, and daily kitchen stock movement report. It should also show stock transfer amount compared with sale value for daily stock movement to the kitchen.

## Existing Model

`app2.models.Inventory`

- `item_name`: stock item name.
- `quantity`: current available stock quantity.
- `min_quantity`: minimum stock level.
- `unit`: unit of measurement, such as kg, liter, packet, box, piece.
- `last_updated`: automatically updated timestamp.

Related existing fields:

- `Staff.role` already supports `inventory`.
- `MenuItems.stock_quantity` exists, but it should be treated as menu-item availability/count, not raw ingredient inventory.

## Current Gap

- Inventory CRUD is not yet documented as an application process.
- No inventory screens are defined.
- No access control is defined for inventory staff.
- No relationship exists between `Inventory` and `MenuItems`.
- No recipe/BOM model exists to map menu items to ingredients.
- No stock movement model exists for purchase, wastage, adjustment, return, or order-based deduction.
- No purchase order model exists.
- No vendor model exists.
- No daily stock movement report exists for kitchen issue, purchase amount paid, and sale value.

## Required Scope

### Admin

- View all stock items.
- Add new stock items.
- Edit stock item quantity, minimum quantity, and unit.
- Delete stock items if no stock history is required yet.
- View low-stock items.
- Manage vendors.
- Create and manage purchase orders.
- Record purchase amount paid.
- View stock movement audit trail.
- View daily kitchen stock movement report.
- Compare daily purchase amount paid against sale value.

### Inventory Staff

- Login as inventory role.
- View inventory dashboard.
- Add stock items.
- Edit stock quantities.
- Track low-stock items.
- Maintain item units and minimum quantity.
- Manage vendors if permitted by Admin.
- Create purchase orders.
- Record stock received from purchase.
- Record stock issued to kitchen.
- Record wastage, returns, and manual adjustments.
- Review daily stock movement to kitchen.

### Receptionist

- Optional read-only inventory visibility for daily operations.
- No edit/delete access unless separately required.

### Kitchen / KOT

- Kitchen receives stock from inventory through daily stock issue entries.
- Chef/KOT can continue working from KOT records for preparation flow.
- Kitchen stock movement should be tracked separately from KOT until recipe mapping is implemented.

## Additional Required Modules

### Vendor Management

Vendor management should store supplier details used for purchases.

Recommended fields:

- Vendor name
- Contact person
- Phone number
- Email
- Address
- GST number, if required
- Active/inactive status

### Purchase Order Management

Purchase order management should track stock purchased from vendors.

Recommended purchase order fields:

- Purchase order number
- Vendor
- Purchase date
- Purchase status: Draft, Ordered, Received, Cancelled
- Total purchase amount
- Amount paid
- Balance amount
- Payment method
- Payment date
- Notes

Recommended purchase order item fields:

- Purchase order
- Inventory item
- Quantity ordered
- Quantity received
- Unit
- Unit cost
- Line total

When purchase stock is received, inventory quantity should increase.

### Stock Movement Audit Trail

Every inventory quantity change should create a stock movement entry.

Recommended movement types:

- Purchase Received
- Kitchen Issue
- Wastage
- Return to Vendor
- Stock Adjustment
- Opening Stock

Recommended stock movement fields:

- Inventory item
- Movement date and time
- Movement type
- Quantity in
- Quantity out
- Unit
- Reference type, such as purchase order, kitchen issue, adjustment
- Reference number
- Purchase cost amount, where applicable
- Sale value, where applicable
- Created by
- Notes

## Daily Kitchen Stock Movement Report

This is the main inventory report required for operations.

The report should show stock moved to the kitchen each day and compare purchase amount paid against sale value.

Required report fields:

- Date
- Inventory item
- Opening stock
- Purchased quantity
- Purchase amount paid
- Quantity issued to kitchen
- Wastage quantity
- Closing stock
- Related sale quantity or menu sale reference, when available
- Sale value
- Difference between sale value and purchase amount paid

Recommended summary totals:

- Total purchase amount paid for the day
- Total sale value for the day
- Total stock issued to kitchen
- Total wastage
- Gross difference: `sale value - purchase amount paid`

Important implementation note:

- Purchase amount paid comes from purchase orders/payments.
- Sale value comes from completed orders, invoices, or payments.
- Until recipe mapping exists, sale value can be shown at daily total level instead of exact ingredient-level sale value.
- Exact item-wise profit requires recipe/BOM mapping between `MenuItems` and `Inventory`.

## Inventory Workflow

1. Admin or Inventory staff opens inventory list.
2. User adds a stock item with name, quantity, minimum quantity, and unit.
3. User creates vendors for suppliers.
4. User creates purchase orders for stock purchases.
5. User records purchase amount paid and received stock quantity.
6. System increases inventory quantity after stock is received.
7. User records stock issued to kitchen as a kitchen issue movement.
8. User records wastage, returns, or manual adjustments when needed.
9. System marks items as low stock when `quantity <= min_quantity`.
10. Admin or Inventory staff reviews daily kitchen stock movement, purchase amount paid, sale value, and difference.

## Low Stock Rule

An item is low stock when:

```text
quantity <= min_quantity
```

Example:

- Tomato: quantity `4`, min quantity `5` -> Low stock.
- Rice: quantity `25`, min quantity `10` -> Available.

## Implementation Plan

### Phase 1 - Inventory Access

1. Keep `inventory` as a valid staff role.
2. Add inventory role handling in staff dashboard routing.
3. Add inventory-only access helper/check.
4. Allow Admin access to inventory management.
5. Optionally allow Receptionist read-only access.

### Phase 2 - Inventory CRUD

1. Add inventory list view.
2. Add inventory create view.
3. Add inventory edit view.
4. Add inventory delete view.
5. Validate required fields:
   - Item name
   - Quantity
   - Minimum quantity
   - Unit

### Phase 3 - Low Stock

1. Show low-stock status in inventory list.
2. Add separate low-stock filter/list.
3. Highlight rows where `quantity <= min_quantity`.
4. Add dashboard count for low-stock items if needed.

### Phase 4 - Navigation

1. Add Inventory menu for Admin.
2. Add Inventory dashboard/menu for inventory staff.
3. Keep receptionist inventory link read-only if enabled.
4. Do not show inventory edit/delete actions to unauthorized roles.

### Phase 5 - Vendor Management

1. Add vendor list view.
2. Add vendor create/edit/delete views.
3. Link vendors to purchase orders.
4. Keep inactive vendors hidden from new purchase orders.

### Phase 6 - Purchase Order Management

1. Add purchase order list view.
2. Add purchase order create/edit/detail views.
3. Add purchase order items for inventory stock.
4. Track total purchase amount, amount paid, and balance.
5. Increase inventory quantity when purchased stock is received.
6. Create stock movement audit entries for received purchases.

### Phase 7 - Stock Movement Audit

1. Add stock movement model.
2. Record every quantity change as a movement.
3. Support movement types: purchase received, kitchen issue, wastage, return, adjustment, opening stock.
4. Show stock movement history by item and date.
5. Prevent silent inventory quantity changes without audit entry.

### Phase 8 - Daily Kitchen Stock Movement Report

1. Add daily report by date.
2. Show stock issued to kitchen.
3. Show purchase amount paid for the selected day.
4. Show sale value for the selected day.
5. Show gross difference: `sale value - purchase amount paid`.
6. Show item-level movement where possible.
7. Show daily totals for purchase paid, sale value, stock issued, and wastage.

### Phase 9 - Future Recipe Mapping

Only add this after the basic inventory module works.

Planned future models may include:

- Recipe or BOM model linking `MenuItems` to `Inventory`.
- Ingredient quantity per menu item and size.
- Automatic deduction when KOT or order status reaches a confirmed stage.

## Files Likely To Be Updated

- `app2/models.py` for vendor, purchase order, purchase order item, stock movement, and future recipe mapping models.
- `app1/views.py` for inventory list, add, edit, delete, low-stock view, vendor management, purchase orders, stock movement, daily kitchen stock report, and access checks.
- `app1/urls.py` for inventory, vendor, purchase order, stock movement, and daily report routes.
- `templates/Rest-Admin/` for admin inventory screens or links.
- `templates/Staff/` for inventory staff dashboard and screens.

## Out Of Scope For First Version

- Automatic stock deduction from orders.
- Automatic stock deduction from KOT.
- Recipe/BOM mapping.
- Barcode scanning.
- Expiry-date tracking.
- Batch-wise inventory.

## Acceptance Criteria

- Admin can view, add, edit, and delete inventory items.
- Inventory staff can view, add, edit, and delete inventory items.
- Admin or Inventory staff can manage vendors.
- Admin or Inventory staff can create purchase orders.
- Purchase orders can track total amount, amount paid, and balance amount.
- Receiving a purchase order increases inventory quantity.
- Every purchase receipt, kitchen issue, wastage, return, and adjustment creates a stock movement audit entry.
- Daily kitchen stock movement report shows purchase amount paid and sale value.
- Daily report shows gross difference between sale value and purchase amount paid.
- Receptionist can only view inventory if read-only access is enabled.
- Low-stock items are identifiable using `quantity <= min_quantity`.
- Inventory quantities are updated through purchases, kitchen issues, wastage, returns, and adjustments.
- Order, KOT, waiter, receptionist, and online order flows are not changed by automatic deduction until recipe mapping exists.
- `MenuItems.stock_quantity` is not treated as raw material inventory.

# Restaurant Management System - Project Plan

## Purpose

This plan aligns the existing Django restaurant management implementation with the required role-based scope only:

- Admin
- Waiter
- Chef / KOT
- Receptionist
- Manager

No extra modules or features should be added beyond the scope below.

## Current Codebase Summary

### Project Structure

- `rms/` contains Django project settings and root URLs.
- `app1/` contains most application views, URL routes, session login logic, and admin/reception/waiter/chef workflows.
- `app2/` contains the main restaurant operation models.
- `templates/Rest-Admin/` contains admin screens.
- `templates/Staff/` contains receptionist and chef/KOT screens.
- `templates/Waiter/` contains waiter screens.
- `templates/Customer/` and `templates/online_orders/` contain customer-facing QR and online order screens.
- `static/` and `media/` contain UI assets, uploaded images, QR codes, and generated bills.

### Existing Models

`app1.models`

- `Restaurants`: restaurant profile and payment metadata.
- `Admin`: custom admin login record with hashed password.

`app2.models`

- `Staff`: staff users with role choices.
- `Categories`: menu categories.
- `MenuItems`: menu item header/details such as category, image, GST, availability.
- `Menuitems_details`: item size and channel-specific prices.
- `Table_list`: table number, capacity, status, occupied order, QR code.
- `Orders`: dine-in and takeaway orders.
- `OrderItems`: items for `Orders`.
- `KOT`: kitchen order ticket per order/update.
- `KOTItems`: items attached to a KOT.
- `Payments`, `bill_pdf`, `Invoices`: billing/payment records.
- `Online_Orders`, `Online_OrderItems`: online order records.
- Other currently unused or out-of-scope models: `Customer`, `CustomerAddress`, `RestaurantInfo`, `Notifications`, `OffersDiscounts`, `Inventory`.

### Existing Login and Role Flow

- `signin` checks `Admin` first, then `Staff`, using phone number and password.
- Admin users are redirected to `Admin_Dashboard`.
- Staff users are redirected to `staff_dashboard`.
- `staff_dashboard` renders different dashboards for `Receptionist`, `Chef`, and `Waiter`.
- Manager exists in staff role options and admin UI, but there is no manager-specific dashboard or scope implemented.

Important implementation note: `Staff.ROLE_CHOICES` stores lowercase values such as `manager`, `receptionist`, `chef`, and `waiter`, while views/templates currently compare against capitalized values such as `Manager`, `Receptionist`, `Chef`, and `Waiter`. The role values must be standardized before role-based access can be reliable.

## Required Scope Compared With Existing Features

### Admin

Required:

- User Management
- Dashboard

Existing:

- `Admin_Dashboard` exists and shows staff count, order count, and payment total.
- Staff CRUD exists through `add_staff`, `edit_staff`, and `delete_staff`.
- Admin base template links dashboard, profile, and staff table.

Gap:

- Admin access is not strictly enforced on admin-only views.
- Staff role values need cleanup so user management creates valid roles consistently.
- Restaurant profile exists, but it is outside the requested admin login scope unless retained as existing profile maintenance.

Plan:

- Keep admin scope focused on dashboard and user management.
- Ensure only admin sessions can access admin dashboard and staff CRUD.
- Keep staff creation/edit roles limited to Manager, Receptionist, Chef, and Waiter.
- Remove or hide out-of-scope role options such as Cashier and Inventory from user-facing role selection.

### Waiter

Required:

- View table status: occupied / available
- Take customer orders from tables

Existing:

- `Waiter/waiter_dashboard.html` shows table overview.
- `waiter_place_order` creates dine-in orders and KOT records.
- `w_addmore_items` updates existing dine-in orders and creates additional KOT records.
- Tables are marked occupied when a dine-in order is placed.

Gap:

- Waiter access is not enforced at the view level.
- Waiter templates use a separate minimal base and should remain limited to table status and dine-in order actions.

Plan:

- Restrict waiter routes to staff users with the Waiter role.
- Keep waiter dashboard limited to table status and active table orders.
- Keep waiter order flow dine-in only.
- Ensure table status changes from Available to Occupied when the waiter places an order.

### Chef / KOT

Required:

- Receive KOT after an order is taken by waiter or receptionist.
- Update KOT/order preparation status.

Existing:

- `KOT` and `KOTItems` are created from receptionist dine-in/takeaway orders, waiter dine-in orders, QR orders, and online orders.
- `KOT_dashboard.html`, `pending_kots`, and `kot_management` exist.
- Chef can mark KOT entries Ready.
- Order status is updated to Served or Ready for Pickup depending on order type.

Gap:

- KOT status choices include Pending, Preparing, Ready, Cancelled, but current screens mostly jump from Pending to Ready.
- Chef access is not enforced at the view level.
- Online order KOT currently uses status `Placed`, which is not in the `KOT.status` choices.

Plan:

- Restrict KOT routes to staff users with the Chef role.
- Use existing `KOT` and `KOTItems` as the kitchen queue.
- Support practical status updates within existing choices: Pending, Preparing, Ready, Cancelled.
- When a KOT becomes Ready, update the related order status:
  - Dine-In: Served
  - Takeaway: Ready for Pickup
  - Online Order: Ready for Pickup or equivalent existing online status
- Standardize online KOT creation to use a valid KOT status.

### Receptionist

Required:

- Table Management CRUD
- Menu Management: categories and items
- Take orders for takeaway, online orders, and dine-in restaurant orders

Existing:

- Table CRUD exists through `add_table`, `edit_table`, `delete_table`, and `view_qr_code`.
- Category CRUD exists through `add_category`, `edit_category`, and `delete_category`.
- Menu item CRUD exists through `add_menuitem`, `edit_menuitem`, and `delete_menuitem`.
- Receptionist order flow exists through `place_order`.
- Takeaway order list exists through `takeaway_orders`.
- Dine-in orders set table status to Occupied.
- `all_orders`, `addmore_items`, `cancel_order`, `shift_table`, billing, and invoice generation exist.
- Customer-facing online order screens exist separately.

Gap:

- Receptionist access is not enforced at the view level.
- `place_order` currently supports Dine-In and Takeaway; online order intake is currently customer-facing, not clearly receptionist-facing.
- `Online_Orders` model and `online_place_order` view are inconsistent because the view passes `address` while the model does not define an `address` field.

Plan:

- Restrict receptionist routes to staff users with the Receptionist role.
- Keep receptionist table CRUD as the single table management surface.
- Keep receptionist category and menu item CRUD as the single menu management surface.
- Keep receptionist order entry in the existing `place_order` workflow and support required order types:
  - Dine-In
  - Takeaway
  - Online Order
- For receptionist-created online orders, choose one practical implementation path:
  - Prefer using the existing `Orders` and `OrderItems` tables with `order_type='Online Order'` so KOT and billing behavior stays consistent.
  - Use `Online_Orders` only if the model/view mismatch is corrected and the screen is intentionally separated from normal staff order entry.

### Manager

Required:

- Role/profile exists.

Existing:

- Manager appears in staff role choices and admin staff form.
- No manager-specific dashboard or permissions are implemented.

Gap:

- The requested scope does not define Manager features.

Plan:

- Keep Manager as a valid staff role/profile.
- Do not add manager features until scope is defined.
- Prevent Manager users from accidentally receiving unrestricted receptionist, chef, waiter, or admin access.
- If a manager logs in before scope is defined, show a minimal authenticated page or redirect with a clear "No assigned module" message.

## Implementation Plan

### Phase 1 - Role Standardization and Access Control

1. Standardize `Staff.role` values across models, forms, templates, and views.
2. Use one consistent set of role values:
   - `manager`
   - `receptionist`
   - `chef`
   - `waiter`
3. Update comparisons in `staff_dashboard`, templates, and route checks to use the standardized values.
4. Add simple helper checks for:
   - Admin-only views
   - Receptionist-only views
   - Chef-only views
   - Waiter-only views
5. Apply checks to existing views instead of creating duplicate views.

### Phase 2 - Admin Scope

1. Keep `Admin_Dashboard` as the admin dashboard.
2. Keep staff user management through existing staff CRUD.
3. Limit role choices shown in admin staff forms to Manager, Receptionist, Chef, and Waiter.
4. Keep admin navigation focused on Dashboard and User Management.

### Phase 3 - Receptionist Scope

1. Keep existing table CRUD screens and routes.
2. Keep existing category and menu item CRUD screens and routes.
3. Keep `place_order` as the receptionist order entry screen.
4. Ensure receptionist can create:
   - Dine-In orders with table assignment
   - Takeaway orders
   - Online orders
5. Ensure every receptionist-created order creates:
   - Order header
   - Order items
   - KOT
   - KOT items
6. Ensure dine-in orders mark the selected table as Occupied.

### Phase 4 - Waiter Scope

1. Keep `waiter_dashboard` for table status.
2. Keep `waiter_place_order` for dine-in table orders.
3. Keep `w_addmore_items` for adding items to active table orders.
4. Prevent waiter users from accessing menu CRUD, table CRUD, admin screens, billing screens, and KOT management.

### Phase 5 - Chef / KOT Scope

1. Keep `KOT_dashboard`, `pending_kots`, and `kot_management`.
2. Show KOTs created by waiter and receptionist order flows.
3. Allow chef to update preparation status using existing KOT statuses.
4. Keep order status updates synchronized with KOT status.
5. Ensure KOT screens do not expose receptionist or admin actions.

### Phase 6 - Manager Profile Handling

1. Keep Manager as a valid role in staff management.
2. Do not add manager modules until requirements are provided.
3. Add a safe login destination for Manager that does not expose other roles' actions.

## Files Likely To Be Updated Later

This plan update does not change application code. Based on the current implementation, future code work should mainly touch:

- `app2/models.py` for role choices and, if needed, online order model consistency.
- `app1/views.py` for role checks, dashboard routing, and order type handling.
- `app1/urls.py` only if route names need cleanup; avoid unnecessary URL churn.
- `templates/Rest-Admin/add_staff.html` for role options.
- `templates/Rest-Admin/base.html` for admin navigation scope.
- `templates/Staff/base.html` for receptionist and chef navigation scope.
- `templates/Waiter/base.html` only if waiter navigation needs polish.
- Existing order templates if receptionist online order entry is added to `place_order`.

## Out Of Scope

Do not add these unless separately requested:

- Inventory management
- Offers and discounts
- Notifications
- Cashier role
- Delivery tracking
- New reporting modules
- New customer account management
- New payment gateway integration
- New manager features beyond preserving the Manager profile

## Practical Acceptance Criteria

- Admin can log in and access only dashboard and staff user management.
- Admin can create/edit/delete Manager, Receptionist, Chef, and Waiter users.
- Waiter can view table availability and create dine-in table orders.
- Waiter-created orders immediately create KOT records for the kitchen.
- Chef can see KOT records from waiter and receptionist orders.
- Chef can update KOT preparation status and the related order status updates correctly.
- Receptionist can manage tables, categories, and menu items.
- Receptionist can create dine-in, takeaway, and online orders.
- Receptionist-created orders create KOT records.
- Manager remains a valid staff profile but does not receive undefined access.
- Users cannot access routes outside their role by entering URLs manually.

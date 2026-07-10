from django.urls import path
from .views import *
from . import inventory_views

urlpatterns = [    
    path('',signin,name='signin'),
    path('signin',signin,name='signin'),
    path('signup',signup,name='signup'),
    path('signout',signout,name='signout'),
    path('Admin_Dashboard',Admin_Dashboard,name='Admin_Dashboard'),
    
    path('update_restaurant', update_restaurant, name='update_restaurant'),
    path('restaurant_mgmt',restaurant_mgmt, name='restaurant_mgmt'),

    path('add_staff', add_staff, name='add_staff'),
    path('edit_staff/<str:id>/', edit_staff, name='edit_staff'),
    path('delete_staff/<str:id>', delete_staff, name='delete_staff'),

    path('staff_dashboard',staff_dashboard,name='staff_dashboard'),
    path('inventory/', inventory_views.inventory_dashboard, name='inventory_dashboard'),
    path('inventory/items/', inventory_views.inventory_list, name='inventory_list'),
    path('inventory/items/add/', inventory_views.inventory_edit, name='inventory_add'),
    path('inventory/items/<int:pk>/edit/', inventory_views.inventory_edit, name='inventory_edit'),
    path('inventory/items/<int:pk>/delete/', inventory_views.inventory_delete, name='inventory_delete'),
    path('inventory/vendors/', inventory_views.vendor_list, name='vendor_list'),
    path('inventory/vendors/add/', inventory_views.vendor_edit, name='vendor_add'),
    path('inventory/vendors/<int:pk>/edit/', inventory_views.vendor_edit, name='vendor_edit'),
    path('inventory/vendors/<int:pk>/delete/', inventory_views.vendor_delete, name='vendor_delete'),
    path('inventory/purchases/', inventory_views.purchase_order_list, name='purchase_order_list'),
    path('inventory/purchases/add/', inventory_views.purchase_order_edit, name='purchase_order_add'),
    path('inventory/purchases/<int:pk>/', inventory_views.purchase_order_detail, name='purchase_order_detail'),
    path('inventory/purchases/<int:pk>/edit/', inventory_views.purchase_order_edit, name='purchase_order_edit'),
    path('inventory/purchases/<int:pk>/receive/', inventory_views.purchase_order_receive, name='purchase_order_receive'),
    path('inventory/purchase-items/<int:pk>/edit/', inventory_views.purchase_order_item_edit, name='purchase_order_item_edit'),
    path('inventory/movements/', inventory_views.movement_list, name='movement_list'),
    path('inventory/movements/add/', inventory_views.movement_create, name='movement_add'),
    path('inventory/movements/add/<int:item_pk>/', inventory_views.movement_create, name='movement_add_for_item'),
    path('inventory/report/daily/', inventory_views.daily_inventory_report, name='daily_inventory_report'),

    path('add_category', add_category, name='add_category'),
    path('edit_category/<str:id>/', edit_category, name='edit_category'),
    path('delete_category/<str:id>', delete_category, name='delete_category'),

    path('add_menuitem', add_menuitem, name='add_menuitem'),
    path('edit_menuitem/<str:id>/', edit_menuitem, name='edit_menuitem'),
    path('delete_menuitem/<str:id>', delete_menuitem, name='delete_menuitem'),

    path('add_table', add_table, name='add_table'),
    path('view_qr_code/<str:id>/', view_qr_code, name='view_qr_code'),
    path('edit_table/<str:id>/', edit_table, name='edit_table'),
    path('delete_table/<str:id>', delete_table, name='delete_table'),

    path('place_order', place_order, name='place_order'),
    path('cancel_order/<str:order_no>', cancel_order, name='cancel_order'),
    path('takeaway_orders', takeaway_orders, name='takeaway_orders'),
    path('all_orders', all_orders, name='all_orders'),

    path('addmore_items/<str:order_no>', addmore_items, name='addmore_items'),

    path('kot_management',kot_management,name='kot_management'),

    path('bill_generate/', bill_generate, name="bill_generate"),  
    path('bill_generate/<str:order_no>/', bill_generate, name="bill_generate_with_order"),
    path('order_invoice/<str:order_no>/', generate_order_pdf, name='order_invoice'),

    path('pending_kots', pending_kots, name='pending_kots'),

    path('shift_table/<str:order_no>/<str:new_table_no>/', shift_table, name='shift_table'),

    path('waiter_table_status/', waiter_table_status, name='waiter_table_status'),
    path('waiter_place_order', waiter_place_order, name='waiter_place_order'),

    path('w_addmore_items/<str:order_no>', w_addmore_items, name='w_addmore_items'),
    path('waiter_ready_kots', waiter_ready_kots, name='waiter_ready_kots'),

    
    path('landing_page/', landing_page, name='landing_page'),

    path('self_order/', self_order, name='self_order'),

    path('qr_orders/', qr_orders, name='qr_orders'),
    path('confirm_page/', confirm_page, name='confirm_page'),

    path('generate_order_bill/<str:order_no>/', generate_order_bill, name='generate_order_bill'),

    path('online_landing_page/', online_landing_page, name='online_landing_page'),
    path('online_categories/', online_categories_view, name='online_categories'),
    path('menu_items/<int:category_id>/', menu_items_by_category, name='menu_items'),
    
    path('online_menuitems/', online_menuitems, name='online_menuitems'),
    path('send_email_otp/', send_email_otp, name='send_email_otp'),
    path('verify_email_otp/', verify_email_otp, name='verify_email_otp'),
    path('online_place_order/', online_place_order, name='online_place_order'),
    path('online_confirm_page/<str:order_no>/', online_confirm_page, name='online_confirm_page'),
    path('generate_online_order_bill/<str:order_no>/', generate_online_order_bill, name='generate_online_order_bill'),
]

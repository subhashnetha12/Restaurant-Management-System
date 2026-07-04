// navbar for the notification and message and profile show 

document.addEventListener("DOMContentLoaded", () => {
    const searchIcon = document.querySelector(".search-icon .header-search");
    const searchBox = document.querySelector(".input-box");
    const closeIcon = document.querySelector(".input-box .close-icon");
    const dropdowns = [
        {
            trigger: document.querySelector(".notification-box"),
            dropdown: document.querySelector(".notification-dropdown"),
        },
        {
            trigger: document.querySelector(".messages-box"),
            dropdown: document.querySelector(".messages-dropdown"),
        },
        {
            trigger: document.querySelector(".profile-nav"),
            dropdown: document.querySelector(".profile-dropdown"),
        },
    ];

    dropdowns.forEach(({ trigger, dropdown }) => {
        if (trigger && dropdown) {
            // Toggle dropdown visibility on click
            trigger.addEventListener("click", (e) => {
                e.stopPropagation(); // Prevent bubbling to the document
                // Close all other dropdowns and the search box
                dropdowns.forEach(({ dropdown: otherDropdown }) => {
                    if (otherDropdown !== dropdown) {
                        otherDropdown.classList.remove("active");
                    }
                });
                searchBox.classList.remove("open"); // Close the search box
                // Toggle the current dropdown
                dropdown.classList.toggle("active");
            });
        }
    });

    // Close dropdowns when clicking outside
    document.addEventListener("click", () => {
        dropdowns.forEach(({ dropdown }) => {
            dropdown.classList.remove("active");
        });
        searchBox.classList.remove("open"); // Close the search box
    });

    if (searchIcon && searchBox) {
        // Toggle search box visibility on click
        searchIcon.addEventListener("click", (e) => {
            e.stopPropagation(); // Prevent event bubbling
            // Close all dropdowns when the search box is toggled
            dropdowns.forEach(({ dropdown }) => {
                dropdown.classList.remove("active");
            });
            searchBox.classList.toggle("open"); // Toggle the `open` class
        });

        // Close the search box when the close icon is clicked
        if (closeIcon) {
            closeIcon.addEventListener("click", (e) => {
                e.stopPropagation();
                searchBox.classList.remove("open");
            });
        }

        // Close the search box when clicking outside
        document.addEventListener("click", () => {
            if (searchBox.classList.contains("open")) {
                searchBox.classList.remove("open");
            }
        });

        // Prevent the search box from closing when clicking inside it
        searchBox.addEventListener("click", (e) => {
            e.stopPropagation();
        });
    }
});


// toggle button to side and show 
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggles = document.querySelectorAll('.sidebar-toggle'); // Sidebar toggle buttons (both in sidebar and content)
    const content = document.getElementById('content');

    function toggleSidebar() {
        if (window.innerWidth > 768) {
            // Large screens: Toggle between 260px and 60px
            sidebar.classList.toggle('hide');
        } else {
            // Small screens: Show or hide sidebar completely
            sidebar.classList.toggle('show');
        }
    }

    sidebarToggles.forEach(toggle => {
        toggle.addEventListener('click', toggleSidebar);
    });

    // Hide sidebar when clicking outside of it on small screens
    content.addEventListener('click', function (event) {
        if (window.innerWidth <= 768 && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show'); // Hide sidebar when clicking outside
        }
    });

    // Ensure sidebar is hidden by default on small screens
    function checkScreenSize() {
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('hide'); 
            sidebar.classList.remove('show'); 
        } else {
            sidebar.classList.remove('show'); 
        }
    }

    // Initial check and on resize
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
});


// submenu open and close 
document.addEventListener("DOMContentLoaded", function () {
    let menuItems = document.querySelectorAll(".sidebar-list > .sidebar-title");

    menuItems.forEach(function (menuItem) {
        menuItem.addEventListener("click", function () {
            let parentLi = this.parentElement;
            let submenu = parentLi.querySelector(".sidebar-submenu");
            let arrowIcon = parentLi.querySelector(".according-menu i");

            if (submenu) {
                let isActive = submenu.classList.contains("open");

                // Close all other open submenus
                document.querySelectorAll(".sidebar-submenu").forEach(function (sub) {
                    if (sub !== submenu) {
                        sub.style.maxHeight = "0px";
                        sub.classList.remove("open");
                    }
                });

                document.querySelectorAll(".according-menu i").forEach(function (icon) {
                    if (icon !== arrowIcon) {
                        icon.classList.remove("ri-arrow-down-s-line");
                        icon.classList.add("ri-arrow-right-s-line");
                    }
                });

                // Toggle submenu with smooth animation
                if (isActive) {
                    submenu.style.maxHeight = "0px";
                    submenu.classList.remove("open");
                } else {
                    submenu.style.maxHeight = submenu.scrollHeight + "px";
                    submenu.classList.add("open");
                }

                arrowIcon.classList.toggle("ri-arrow-right-s-line", isActive);
                arrowIcon.classList.toggle("ri-arrow-down-s-line", !isActive);
            }
        });
    });
});




// document.addEventListener("DOMContentLoaded", function () {
//     let menuItems = document.querySelectorAll(".sidebar-list > a");
//     let submenuItems = document.querySelectorAll(".sidebar-submenu li a");

//     function removeSelectedClass(elements) {
//         elements.forEach(item => item.classList.remove("selected"));
//     }

//     menuItems.forEach(function (menuItem) {
//         menuItem.addEventListener("click", function () {
//             removeSelectedClass(menuItems); // Remove highlight from other menu items
//             this.classList.add("selected"); // Highlight the clicked menu item
//         });
//     });

//     submenuItems.forEach(function (submenuItem) {
//         submenuItem.addEventListener("click", function () {
//             removeSelectedClass(submenuItems); // Remove highlight from other submenu items
//             this.classList.add("selected"); // Highlight the clicked submenu item
//         });
//     });
// });


document.addEventListener("DOMContentLoaded", function () {
    const menuItems = document.querySelectorAll(".sidebar-list > .sidebar-title");
    const subMenuItems = document.querySelectorAll(".sidebar-submenu li a");

    function closeAllMenus() {
        menuItems.forEach(item => item.classList.remove("active"));
        document.querySelectorAll(".sidebar-submenu").forEach(submenu => {
            submenu.classList.remove("open");
            submenu.style.maxHeight = "0px";
        });
    }

    function closeAllSubmenus() {
        subMenuItems.forEach(subItem => {
            subItem.classList.remove("active");
            const icon = subItem.querySelector("i");
            if (icon) {
                icon.style.color = ""; // Reset icon color
            }
        });
    }

    // Toggle Main Menu
    menuItems.forEach(menuItem => {
        menuItem.addEventListener("click", function () {
            let parentLi = this.parentElement;
            let submenu = parentLi.querySelector(".sidebar-submenu");

            // Close all other menus
            closeAllMenus();

            // Highlight Clicked Main Menu
            this.classList.add("active");

            // Toggle submenu
            if (submenu) {
                let isActive = submenu.classList.contains("open");

                if (isActive) {
                    submenu.classList.remove("open");
                    submenu.style.maxHeight = "0px";
                } else {
                    submenu.classList.add("open");
                    submenu.style.maxHeight = submenu.scrollHeight + "px";
                }
            }
        });
    });

    // Submenu Click
    subMenuItems.forEach(subMenuItem => {
        subMenuItem.addEventListener("click", function (event) {
            event.stopPropagation(); // Prevent closing parent menu
            closeAllSubmenus();
            this.classList.add("active");

            // Change Icon Color
            const icon = this.querySelector("i");
            if (icon) {
                icon.style.color = "var(--theme-color)";
            }
        });
    });
});

var menu, menuItems, panelSnapInstance;

document.addEventListener("DOMContentLoaded", function () {
    menu = document.querySelector('.menu');
    menuItems = menu.querySelectorAll('button');

    panelSnapInstance = new PanelSnap();
    panelSnapInstance.on('activatePanel', activateMenuItem);

    menuItems.forEach(function (menuItem) {
      menuItem.addEventListener('click', onButtonClick);
    })
});

function activateMenuItem(panel) {
    menuItems.forEach(function (menuItem) {
      menuItem.classList.remove('active');
    });

    var panelName = panel.getAttribute('data-panel')
    var menuItem = menu.querySelector('button[data-panel="' + panelName + '"]');
    menuItem.classList.add('active');
}

function onButtonClick(e) {
    var panelName = e.target.getAttribute('data-panel')
    var panel = document.querySelector('section[data-panel="' + panelName + '"]');
    panelSnapInstance.snapToPanel(panel);
}

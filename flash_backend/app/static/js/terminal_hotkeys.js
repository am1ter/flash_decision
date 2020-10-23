// Hotkeys to make decisions in terminal

document.addEventListener('keydown', function(event) {
  if (event.code == 'ArrowUp') {
    document.getElementById("btn_buy").click()
  } else if (event.code == 'ArrowDown') {
    document.getElementById("btn_sell").click()
  } else if (event.code == 'ArrowRight') {
    document.getElementById("btn_skip").click()
  }
});
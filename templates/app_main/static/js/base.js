const body = document.querySelector('body'),
      toggle = body.querySelector(".toggle"),
      modeSwitch = body.querySelector(".toggle-switch"),
      modeText = body.querySelector(".mode-text");

let arrow = document.querySelectorAll(".arrow");
 for (var i = 0; i < arrow.length; i++) {
     arrow[i].addEventListener("click", (e)=>{
         let arrowParent = e.target.parentElement.parentElement;//selecting main parent of arrow
    arrowParent.classList.toggle("showMenu");
    });
}

let sidebar = document.querySelector(".sidebar");
let sidebarBtn = document.querySelector(".bx-menu");
sidebarBtn.addEventListener("click", ()=>{
    sidebar.classList.toggle("close");
});

function saveThemePreference(isDarkMode) {
    localStorage.setItem("themePreference", isDarkMode ? "dark" : "light");
  }
  
  function applyThemePreference() {
    const themePreference = localStorage.getItem("themePreference");
  
    if (themePreference) {
      body.classList.add(themePreference);
  
      if (themePreference === "dark") {
        modeText.innerText = "Modo claro";
      } else {
        modeText.innerText = "Modo escuro";
      }
    }
  }
  
  applyThemePreference();
  
  modeSwitch.addEventListener("click", () => {
    body.classList.toggle("dark");
  
    const isDarkMode = body.classList.contains("dark");
    saveThemePreference(isDarkMode);
  
    if (isDarkMode) {
      modeText.innerText = "Modo claro";
    } else {
      modeText.innerText = "Modo escuro";
    }
  });